import requests
import re
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def fetch_detail_page(url):
    """获取商品详情页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://weidian.com/"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"获取详情页失败: {url}, 错误: {e}")
        return None

def parse_detail_page_html(html):
    """从HTML解析商品详情"""
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    detail_info = {}
    
    try:
        # 尝试提取详细描述
        description_div = soup.find('div', class_=re.compile(r'(detail|description|content)'))
        if description_div:
            detail_info['详细描述'] = description_div.get_text(strip=True)
        
        # 尝试提取规格信息
        specs_div = soup.find('div', class_=re.compile(r'(spec|parameter|attribute)'))
        if specs_div:
            specs = []
            for spec in specs_div.find_all(['li', 'div'], class_=re.compile(r'(item|spec-item)')):
                specs.append(spec.get_text(strip=True))
            detail_info['规格参数'] = '; '.join(specs)
        
        # 尝试提取评价数据
        reviews_div = soup.find('div', class_=re.compile(r'(review|comment|evaluation)'))
        if reviews_div:
            detail_info['评价数量'] = reviews_div.get_text(strip=True)
    
    except Exception as e:
        print(f"解析HTML详情失败: {e}")
    
    # 尝试从页面中提取JSON数据
    try:
        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.string
            if script_text and ('itemInfo' in script_text or 'itemData' in script_text or 'detailInfo' in script_text):
                # 尝试提取JSON
                json_matches = re.findall(r'var\s+(\w+)\s*=\s*({.*?});', script_text, re.DOTALL)
                for var_name, json_str in json_matches:
                    if var_name in ['itemInfo', 'itemData', 'detailInfo', 'window.itemInfo']:
                        try:
                            data = json.loads(json_str)
                            if isinstance(data, dict):
                                # 提取可能的详情字段
                                if 'description' in data:
                                    detail_info['详细描述'] = data['description']
                                if 'specs' in data and isinstance(data['specs'], list):
                                    detail_info['规格参数'] = '; '.join([f"{s.get('name', '')}: {s.get('value', '')}" for s in data['specs']])
                                # 添加其他有用字段
                                for key, value in data.items():
                                    if isinstance(value, (str, int, float)) and key not in ['id', 'itemId', 'price']:
                                        detail_info[key] = value
                        except:
                            pass
    except Exception as e:
        print(f"提取页面JSON数据失败: {e}")
    
    return detail_info

def extract_detail_api(url):
    """使用Selenium提取商品详情API"""
    print(f"正在分析商品详情API: {url}")
    
    # 设置Chrome选项
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 启用性能日志记录
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = None
    detail_api = None
    api_data = {}
    
    try:
        # 初始化WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 访问页面
        driver.get(url)
        print("页面加载中，等待5秒...")
        time.sleep(5)  # 等待页面加载
        
        # 获取性能日志
        logs = driver.get_log("performance")
        
        # 从日志中提取详情API
        detail_api_responses = []
        
        for log in logs:
            try:
                log_entry = json.loads(log["message"])["message"]
                
                if "Network.responseReceived" in log_entry["method"]:
                    if "response" in log_entry["params"]:
                        response = log_entry["params"]["response"]
                        response_url = response["url"]
                        
                        # 寻找可能的详情API
                        if ("item" in response_url or "detail" in response_url or "goods" in response_url) and (
                            "api" in response_url or "json" in response_url):
                            if "mimeType" in response and "json" in response["mimeType"].lower():
                                # 尝试获取响应内容
                                request_id = log_entry["params"]["requestId"]
                                try:
                                    response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                                    if "body" in response_body:
                                        detail_api = response_url
                                        detail_api_responses.append({
                                            "url": response_url,
                                            "content": response_body["body"]
                                        })
                                except:
                                    pass
            except:
                continue
        
        # 解析API响应
        for response in detail_api_responses:
            try:
                data = json.loads(response["content"])
                if isinstance(data, dict):
                    # 商品详情通常在result中
                    if "result" in data and isinstance(data["result"], dict):
                        result = data["result"]
                        
                        # 提取可能有用的信息
                        if "item" in result:
                            item_data = result["item"]
                            api_data.update(extract_fields(item_data))
                        elif "itemInfo" in result:
                            item_data = result["itemInfo"]
                            api_data.update(extract_fields(item_data))
                        elif "detail" in result:
                            detail_data = result["detail"]
                            api_data.update(extract_fields(detail_data))
                        else:
                            # 直接从result提取
                            api_data.update(extract_fields(result))
            except Exception as e:
                print(f"解析API响应失败: {e}")
    
    except Exception as e:
        print(f"提取详情API失败: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return api_data

def extract_fields(data):
    """从数据中提取有用字段"""
    fields = {}
    
    if not isinstance(data, dict):
        return fields
    
    # 可能的详细字段映射
    field_mappings = {
        "desc": "详细描述",
        "description": "详细描述",
        "detail": "详细描述",
        "specs": "规格参数",
        "parameters": "规格参数",
        "attributes": "规格参数",
        "stock": "库存",
        "sales": "销量",
        "commentCount": "评价数量",
        "commentNum": "评价数量",
        "shopName": "店铺名称",
        "sellerName": "卖家名称",
        "brand": "品牌",
        "material": "材质",
        "size": "尺寸"
    }
    
    # 提取常见字段
    for key, display_name in field_mappings.items():
        if key in data:
            value = data[key]
            # 处理不同类型的值
            if isinstance(value, (str, int, float)):
                fields[display_name] = value
            elif isinstance(value, list) and key == "specs":
                # 处理规格参数列表
                specs = []
                for spec in value:
                    if isinstance(spec, dict):
                        name = spec.get("name", "")
                        value = spec.get("value", "")
                        specs.append(f"{name}: {value}")
                fields[display_name] = "; ".join(specs)
    
    # 尝试提取其他可能有用的字段
    for key, value in data.items():
        if key not in field_mappings.keys() and isinstance(value, (str, int, float)):
            # 忽略常见的无用字段
            if key not in ["id", "itemId", "shopId", "status", "url", "updatedTime", "createdTime"]:
                fields[key] = value
    
    return fields

def crawl_item_detail(item_url, delay=1.0):
    """爬取单个商品的详情信息"""
    print(f"开始爬取商品详情: {item_url}")
    
    # 确保URL是有效的
    if not item_url or not isinstance(item_url, str) or not item_url.startswith("http"):
        print(f"无效的商品URL: {item_url}")
        return {}
    
    # 获取详情页HTML
    html = fetch_detail_page(item_url)
    
    # 解析HTML获取详情
    html_details = parse_detail_page_html(html)
    
    # 使用Selenium提取详情API数据
    api_details = extract_detail_api(item_url)
    
    # 合并详情数据
    details = {**html_details, **api_details}
    
    # 添加延迟
    if delay > 0:
        time.sleep(delay)
        
    return details 