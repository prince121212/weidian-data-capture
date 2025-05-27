from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def analyze_apis(url):
    """
    使用 Selenium 分析页面加载的 API 请求
    """
    print("正在启动浏览器分析接口...")
    
    # 设置 Chrome 选项
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 启用性能日志记录
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    # 初始化 WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 访问页面
        driver.get(url)
        print("页面加载中，等待 5 秒...")
        time.sleep(5)  # 等待页面加载完成
        
        # 获取性能日志
        logs = driver.get_log("performance")
        
        # 分析日志中的 XHR 请求
        api_endpoints = []
        json_responses = []
        
        for log in logs:
            try:
                log_entry = json.loads(log["message"])["message"]
                
                # 查找网络请求
                if "Network.responseReceived" in log_entry["method"]:
                    if "response" in log_entry["params"]:
                        response = log_entry["params"]["response"]
                        url = response["url"]
                        
                        # 过滤可能包含商品数据的 API
                        if "api" in url and ("item" in url or "goods" in url or "product" in url or "shop" in url):
                            api_endpoints.append(url)
                            
                        # 检查 JSON 响应
                        if "mimeType" in response and "json" in response["mimeType"].lower():
                            api_endpoints.append(url)
                            
                            # 尝试获取响应内容
                            request_id = log_entry["params"]["requestId"]
                            try:
                                response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                                if "body" in response_body:
                                    body_content = response_body["body"]
                                    if "item" in body_content or "goods" in body_content or "product" in body_content:
                                        json_responses.append({
                                            "url": url,
                                            "content": body_content
                                        })
                            except Exception as e:
                                pass
            except Exception as e:
                continue
        
        # 输出找到的 API 端点
        print(f"\n找到 {len(api_endpoints)} 个可能的 API 端点:")
        for i, endpoint in enumerate(api_endpoints, 1):
            print(f"{i}. {endpoint}")
        
        # 输出找到的 JSON 响应
        print(f"\n找到 {len(json_responses)} 个包含商品数据的响应:")
        for i, response in enumerate(json_responses, 1):
            print(f"{i}. {response['url']}")
            
        # 分析 JSON 响应，找到商品数据
        product_api = None
        for response in json_responses:
            try:
                data = json.loads(response["content"])
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]
                    if isinstance(result, dict) and ("items" in result or "goods" in result or "products" in result):
                        product_api = response["url"]
                        print(f"\n找到商品数据 API: {product_api}")
                        break
            except:
                continue
                
        return {
            "api_endpoints": api_endpoints,
            "product_api": product_api,
            "json_responses": json_responses
        }
        
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://h5.weidian.com/decoration/shop-category/category.html?userid=1286456178&c=124372511"
    analyze_apis(url) 