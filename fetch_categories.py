import os
import time
import json
import re
import requests
import pandas as pd
import xlrd
import xlwt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def read_xls(xls_file):
    """读取XLS文件为Pandas DataFrame"""
    try:
        # 使用xlrd直接读取xls
        workbook = xlrd.open_workbook(xls_file)
        sheet = workbook.sheet_by_index(0)
        
        # 读取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 读取数据
        data = []
        for row in range(1, sheet.nrows):
            row_data = {}
            for col in range(sheet.ncols):
                row_data[headers[col]] = sheet.cell_value(row, col)
            data.append(row_data)
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        print(f"成功读取 {len(df)} 条商品数据")
        return df
    
    except Exception as e:
        print(f"读取XLS文件失败: {e}")
        return pd.DataFrame()

def save_to_xls(df, filename):
    """将DataFrame保存为XLS文件"""
    try:
        # 创建工作簿和工作表
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Items')
        
        # 写入表头
        headers = df.columns.tolist()
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 写入数据
        for row, item in enumerate(df.to_dict('records'), 1):
            for col, header in enumerate(headers):
                value = item.get(header, '')
                # 确保值是字符串、数字或布尔值
                if isinstance(value, (str, int, float, bool)):
                    sheet.write(row, col, value)
                else:
                    sheet.write(row, col, str(value))
        
        # 保存文件
        workbook.save(filename)
        print(f"成功保存 {len(df)} 条数据到 {filename}")
        return True
    
    except Exception as e:
        print(f"保存XLS文件失败: {e}")
        return False

def fetch_product_detail(url, use_selenium=False):
    """获取商品详情页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://weidian.com/"
    }
    
    if not use_selenium:
        try:
            # 直接使用requests获取页面
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"获取详情页失败(Requests): {url}, 错误: {e}")
            return None
    else:
        # 使用Selenium获取页面
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # 启用性能日志记录，用于捕获API请求
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        driver = None
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(url)
            print(f"访问商品页面: {url}")
            time.sleep(5)  # 增加等待时间到5秒
            
            # 尝试点击可能的"更多"或"详情"按钮
            try:
                buttons = driver.find_elements("xpath", "//button[contains(text(), '详情') or contains(text(), '规格') or contains(text(), '参数')]")
                for button in buttons:
                    button.click()
                    time.sleep(1)
            except:
                pass
                
            html = driver.page_source
            
            # 提取API请求数据
            api_data = extract_api_data(driver)
            
            return {"html": html, "api_data": api_data}
        except Exception as e:
            print(f"获取详情页失败(Selenium): {url}, 错误: {e}")
            return None
        finally:
            if driver:
                driver.quit()

def extract_api_data(driver):
    """从Selenium中提取API响应数据"""
    api_data = []
    try:
        logs = driver.get_log("performance")
        for log in logs:
            try:
                log_entry = json.loads(log["message"])["message"]
                
                if "Network.responseReceived" in log_entry["method"]:
                    if "response" in log_entry["params"]:
                        response = log_entry["params"]["response"]
                        response_url = response["url"]
                        
                        # 寻找可能包含商品详情的API
                        if ("item" in response_url or "detail" in response_url or "goods" in response_url) and (
                            "api" in response_url or "json" in response_url):
                            if "mimeType" in response and "json" in response["mimeType"].lower():
                                # 尝试获取响应内容
                                request_id = log_entry["params"]["requestId"]
                                try:
                                    response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                                    if "body" in response_body:
                                        api_data.append({
                                            "url": response_url,
                                            "content": response_body["body"]
                                        })
                                except:
                                    pass
            except:
                continue
    except Exception as e:
        print(f"提取API数据失败: {e}")
    
    return api_data

def extract_category_from_html(response_data):
    """从HTML和API数据中提取商品分类"""
    if not response_data:
        return ""
    
    html = response_data.get("html", "")
    api_data = response_data.get("api_data", [])
    
    category = ""
    
    # 1. 先尝试从API数据中提取
    for api_response in api_data:
        try:
            data = json.loads(api_response["content"])
            if isinstance(data, dict):
                # 常见的分类字段
                if "result" in data and isinstance(data["result"], dict):
                    result = data["result"]
                    
                    # 尝试不同的可能字段名
                    for key in ["category", "cateName", "cate", "categoryName"]:
                        if key in result and result[key]:
                            category = result[key]
                            print(f"从API中提取到分类: {category}")
                            return category
                    
                    # 尝试在商品信息中查找
                    for key in ["item", "itemInfo", "goods", "product"]:
                        if key in result and isinstance(result[key], dict):
                            item_data = result[key]
                            for cat_key in ["category", "cateName", "cate", "categoryName"]:
                                if cat_key in item_data and item_data[cat_key]:
                                    category = item_data[cat_key]
                                    print(f"从商品API数据中提取到分类: {category}")
                                    return category
        except Exception as e:
            print(f"解析API数据失败: {e}")
    
    # 2. 如果API中没有找到，尝试从HTML中提取
    if not category and html:
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # 方法1: 寻找页面中的itemData或者itemInfo变量
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # 尝试提取商品数据变量
                    data_matches = [
                        re.search(r'var\s+itemData\s*=\s*({.*?});', script.string, re.DOTALL),
                        re.search(r'var\s+itemInfo\s*=\s*({.*?});', script.string, re.DOTALL),
                        re.search(r'var\s+goods\s*=\s*({.*?});', script.string, re.DOTALL),
                        re.search(r'var\s+product\s*=\s*({.*?});', script.string, re.DOTALL)
                    ]
                    
                    for match in data_matches:
                        if match:
                            try:
                                data = json.loads(match.group(1))
                                if isinstance(data, dict):
                                    for key in ["category", "cateName", "cate", "categoryName"]:
                                        if key in data and data[key]:
                                            category = data[key]
                                            print(f"从页面变量中提取到分类: {category}")
                                            return category
                            except:
                                pass
            
            # 方法2: 寻找包含"分类"字样的元素
            category_elements = soup.find_all(string=re.compile(r'分类|类别|品类|产品类型'))
            for element in category_elements:
                parent = element.parent
                if parent:
                    category_text = parent.get_text(strip=True)
                    category_match = re.search(r'[：:]\s*([^：:]+)', category_text)
                    if category_match:
                        category = category_match.group(1).strip()
                        print(f"从'分类'标签中提取到分类: {category}")
                        return category
            
            # 方法3: 寻找面包屑导航
            breadcrumb_selectors = [
                'div.breadcrumb', 'div.crumbs', 'div.bread-crumb', 
                'div.path', 'div.nav-path', 'div.location',
                'div[class*="breadcrumb"]', 'div[class*="crumb"]', 'ol.breadcrumb'
            ]
            
            for selector in breadcrumb_selectors:
                breadcrumb = soup.select_one(selector)
                if breadcrumb:
                    links = breadcrumb.find_all('a')
                    if len(links) > 1:  # 通常第二个链接是分类
                        category = links[1].get_text(strip=True)
                        print(f"从面包屑导航中提取到分类: {category}")
                        return category
            
            # 方法4: 寻找可能的分类标签元素
            category_selectors = [
                'span.category', 'div.category', 'span.cate', 'div.cate',
                'span[class*="category"]', 'div[class*="category"]',
                'span[class*="cate"]', 'div[class*="cate"]'
            ]
            
            for selector in category_selectors:
                category_elem = soup.select_one(selector)
                if category_elem:
                    category = category_elem.get_text(strip=True)
                    print(f"从分类标签中提取到分类: {category}")
                    return category
            
            # 方法5: 从商品标签中提取
            tag_selectors = [
                'div.tags', 'span.tag', 'div.tag', 
                'div[class*="tag"]', 'span[class*="tag"]'
            ]
            
            for selector in tag_selectors:
                tags = soup.select(selector)
                if tags:
                    for tag in tags:
                        tag_text = tag.get_text(strip=True)
                        if len(tag_text) < 20:  # 标签通常较短
                            category = tag_text
                            print(f"从商品标签中提取到分类: {category}")
                            return category
        
        except Exception as e:
            print(f"从HTML提取分类失败: {e}")
    
    return category

def fetch_categories_for_products(input_file, output_file, max_items=None, delay=3):
    """为所有商品获取分类信息"""
    # 读取商品数据
    df = read_xls(input_file)
    if df.empty:
        print("没有读取到商品数据")
        return
    
    # 限制处理的商品数量
    if max_items and max_items > 0:
        df = df.head(max_items)
        print(f"限制处理前 {max_items} 条商品")
    
    # 确保有商品链接列
    url_column = None
    for col in ['商品详情页链接', '链接', 'url', 'link']:
        if col in df.columns:
            url_column = col
            break
    
    if not url_column:
        print("数据中没有找到商品链接列")
        return
    
    # 确保有商品分类列
    if '商品分类' not in df.columns:
        df['商品分类'] = ''
    
    # 为每个商品获取分类
    count = 0
    updated = 0
    
    for index, row in df.iterrows():
        url = row[url_column]
        
        # 跳过没有链接的商品
        if not url or not isinstance(url, str) or not url.startswith('http'):
            continue
        
        count += 1
        
        # 如果已经有分类信息，则跳过
        if row['商品分类'] and row['商品分类'] != '':
            print(f"商品 {index+1} 已有分类: {row['商品分类']}")
            continue
        
        print(f"处理商品 {index+1}/{len(df)}: {url}")
        
        # 使用Selenium获取页面和API数据
        response_data = fetch_product_detail(url, use_selenium=True)
        
        # 提取分类信息
        if response_data:
            category = extract_category_from_html(response_data)
            if category:
                df.at[index, '商品分类'] = category
                print(f"找到分类: {category}")
                updated += 1
            else:
                print("未找到分类信息")
                
                # 尝试使用商品名称推断分类
                if '商品名称' in df.columns and row['商品名称']:
                    product_name = row['商品名称']
                    # 提取商品名称中的关键词作为分类
                    keywords = ['连衣裙', '外套', '裤子', '衬衫', '鞋', '包', '配饰', '首饰', '家居', '电子']
                    for keyword in keywords:
                        if keyword in product_name:
                            df.at[index, '商品分类'] = keyword
                            print(f"从商品名称中推断分类: {keyword}")
                            updated += 1
                            break
        
        # 每5个商品保存一次临时结果
        if count % 5 == 0:
            temp_output = output_file.replace('.xls', '_temp.xls')
            save_to_xls(df, temp_output)
            print(f"已保存临时结果，处理了 {count}/{len(df)} 个商品，更新了 {updated} 个分类")
        
        # 添加延迟，避免被封
        if delay > 0:
            time.sleep(delay)
    
    # 保存最终结果
    save_to_xls(df, output_file)
    print(f"完成! 处理了 {count}/{len(df)} 个商品，更新了 {updated} 个分类")

if __name__ == "__main__":
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    input_file = "data/items_all.xls"
    output_file = "data/items_all_with_categories.xls"
    
    # 执行爬取分类的操作
    fetch_categories_for_products(
        input_file=input_file,
        output_file=output_file,
        max_items=20,  # 设置为20表示只处理前20个商品进行测试
        delay=3  # 每个请求之间的延迟秒数
    ) 