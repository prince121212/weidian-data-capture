import os
import requests
import json
import re
import time
import pandas as pd
import xlrd
import xlwt
from xlutils.copy import copy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse

def read_xls_to_pandas(xls_file):
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

def save_df_to_xls(df, output_file):
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
        workbook.save(output_file)
        print(f"成功保存 {len(df)} 条数据到 {output_file}")
        return True
    
    except Exception as e:
        print(f"保存XLS文件失败: {e}")
        return False

def extract_shop_categories(shop_url):
    """使用Selenium提取店铺分类和商品信息"""
    print(f"正在提取店铺分类信息: {shop_url}")
    
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
    categories = {}  # 存储分类信息
    category_products = {}  # 存储每个分类下的商品
    
    try:
        # 初始化WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 访问页面
        driver.get(shop_url)
        print("页面加载中，等待5秒...")
        time.sleep(5)  # 等待页面加载
        
        # 提取分类信息
        try:
            category_elements = driver.find_elements(By.CSS_SELECTOR, "div.cate-list a, ul.category-list li a, div.tab-menu a")
            for elem in category_elements:
                category_name = elem.text.strip()
                category_url = elem.get_attribute("href")
                if category_name and category_url:
                    categories[category_name] = category_url
                    print(f"找到分类: {category_name}")
        except Exception as e:
            print(f"提取分类信息失败: {e}")
        
        # 如果找不到分类元素，尝试其他可能的选择器
        if not categories:
            try:
                category_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'cate') or contains(@class, 'category')]")
                for elem in category_elements:
                    category_name = elem.text.strip()
                    category_url = elem.get_attribute("href")
                    if category_name and category_url:
                        categories[category_name] = category_url
                        print(f"找到分类: {category_name}")
            except Exception as e:
                print(f"第二次提取分类信息失败: {e}")
        
        # 提取API数据
        logs = driver.get_log("performance")
        api_responses = []
        
        # 从日志中提取商品列表API响应
        for log in logs:
            try:
                log_entry = json.loads(log["message"])["message"]
                
                if "Network.responseReceived" in log_entry["method"]:
                    if "response" in log_entry["params"]:
                        response = log_entry["params"]["response"]
                        response_url = response["url"]
                        
                        # 寻找可能的商品列表API
                        if ("item" in response_url or "goods" in response_url or "list" in response_url) and (
                            "api" in response_url or "json" in response_url):
                            if "mimeType" in response and "json" in response["mimeType"].lower():
                                # 尝试获取响应内容
                                request_id = log_entry["params"]["requestId"]
                                try:
                                    response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                                    if "body" in response_body:
                                        api_responses.append({
                                            "url": response_url,
                                            "content": response_body["body"]
                                        })
                                except:
                                    pass
            except:
                continue
        
        # 解析API响应，提取商品和分类信息
        products_with_category = {}  # 存储商品ID与分类的映射
        
        for response in api_responses:
            try:
                data = json.loads(response["content"])
                
                # 检查是否包含分类信息
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]
                    
                    # 尝试提取分类列表
                    categories_data = None
                    for key in ["categories", "cateList", "categoryList", "cates"]:
                        if key in result and isinstance(result[key], list):
                            categories_data = result[key]
                            print(f"在API中找到分类列表: {key}")
                            break
                    
                    if categories_data:
                        for category in categories_data:
                            if isinstance(category, dict):
                                cat_id = category.get("id") or category.get("cateId") or ""
                                cat_name = category.get("name") or category.get("cateName") or ""
                                if cat_id and cat_name:
                                    categories[cat_name] = cat_id
                                    print(f"从API中提取分类: {cat_name}")
                    
                    # 尝试提取商品列表
                    product_list = None
                    for key in ["itemList", "items", "goods", "products", "list"]:
                        if key in result and isinstance(result[key], list):
                            product_list = result[key]
                            print(f"找到商品列表字段: {key}, 包含 {len(product_list)} 个商品")
                            break
                    
                    if product_list:
                        for product in product_list:
                            if isinstance(product, dict):
                                item_id = product.get("itemId") or product.get("id") or ""
                                category_id = product.get("cateId") or product.get("categoryId") or ""
                                category_name = product.get("cateName") or product.get("categoryName") or ""
                                
                                if item_id:
                                    # 优先使用商品自带的分类名称
                                    if category_name:
                                        products_with_category[item_id] = category_name
                                    # 其次使用分类ID匹配分类名称
                                    elif category_id:
                                        for name, id_or_url in categories.items():
                                            if str(id_or_url) == str(category_id):
                                                products_with_category[item_id] = name
                                                break
            except Exception as e:
                print(f"解析API响应失败: {e}")
        
        # 如果从API未能提取足够的分类信息，则尝试访问每个分类页面爬取商品
        if categories and (len(products_with_category) < 20):
            print("从API提取的商品与分类关联不足，尝试访问分类页面...")
            
            for category_name, category_url in categories.items():
                if isinstance(category_url, str) and category_url.startswith("http"):
                    try:
                        print(f"访问分类页面: {category_name} - {category_url}")
                        driver.get(category_url)
                        time.sleep(3)  # 等待页面加载
                        
                        # 提取商品元素
                        product_elements = driver.find_elements(By.CSS_SELECTOR, "div.item, div.product, a.item-wrap")
                        
                        for product_elem in product_elements:
                            try:
                                # 尝试提取商品链接和ID
                                product_link = product_elem.get_attribute("href")
                                if not product_link:
                                    link_elem = product_elem.find_element(By.TAG_NAME, "a")
                                    product_link = link_elem.get_attribute("href")
                                
                                if product_link:
                                    # 从链接中提取商品ID
                                    item_id_match = re.search(r'itemID=([^&]+)', product_link)
                                    if item_id_match:
                                        item_id = item_id_match.group(1)
                                        products_with_category[item_id] = category_name
                                        print(f"分类页面找到商品: {item_id} - {category_name}")
                            except:
                                continue
                    except Exception as e:
                        print(f"处理分类页面出错: {e}")
                        continue
        
        return products_with_category
    
    except Exception as e:
        print(f"提取店铺分类信息失败: {e}")
        return {}
    
    finally:
        if driver:
            driver.quit()

def update_excel_with_categories(input_file, output_file, shop_url):
    """更新Excel文件，添加分类信息"""
    # 读取原始数据
    df = read_xls_to_pandas(input_file)
    if df.empty:
        print("输入文件为空或无法读取")
        return
    
    # 提取店铺分类和商品信息
    products_with_category = extract_shop_categories(shop_url)
    
    if not products_with_category:
        print("未能提取到分类信息，不更新文件")
        return
    
    print(f"成功提取 {len(products_with_category)} 个商品的分类信息")
    
    # 确保DataFrame中有商品ID列
    id_column = None
    for col in ['商品ID', 'itemId', 'id']:
        if col in df.columns:
            id_column = col
            break
    
    if not id_column:
        print("Excel文件中没有找到商品ID列，尝试从URL中提取")
        # 尝试从URL中提取商品ID
        if '商品详情页链接' in df.columns:
            df['商品ID'] = df['商品详情页链接'].apply(lambda url: re.search(r'itemID=([^&]+)', url).group(1) if url and isinstance(url, str) and re.search(r'itemID=([^&]+)', url) else '')
            id_column = '商品ID'
    
    if not id_column:
        print("无法在Excel中找到或创建商品ID列，无法更新分类信息")
        return
    
    # 添加商品分类列
    if '商品分类' not in df.columns:
        df['商品分类'] = ''
    
    # 更新分类信息
    updated_count = 0
    for index, row in df.iterrows():
        item_id = str(row[id_column])
        if item_id in products_with_category:
            df.at[index, '商品分类'] = products_with_category[item_id]
            updated_count += 1
    
    print(f"成功更新 {updated_count} 个商品的分类信息")
    
    # 保存更新后的文件
    save_df_to_xls(df, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微店商品分类信息爬取工具")
    parser.add_argument("-i", "--input", default="data/items_all.xls",
                       help="输入的商品列表Excel文件")
    parser.add_argument("-o", "--output", default="data/items_all_with_categories.xls",
                       help="输出的带分类信息Excel文件")
    parser.add_argument("-u", "--url", default="https://weidian.com/?userid=1286456178&spider_token=8555&tabType=all",
                       help="微店店铺链接")
    
    args = parser.parse_args()
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    # 使用命令行参数或默认值
    input_file = args.input
    output_file = args.output
    shop_url = args.url
    
    # 执行更新
    update_excel_with_categories(
        input_file=input_file,
        output_file=output_file,
        shop_url=shop_url
    ) 