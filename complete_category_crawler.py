#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的微店分类信息爬取工具
支持爬取店铺的所有分类以及每个分类下的所有商品
"""

import os
import time
import json
import re
import requests
import pandas as pd
import xlrd
import xlwt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import argparse

class WeidianCategoryCrawler:
    def __init__(self, shop_url, delay=2):
        self.shop_url = shop_url
        self.delay = delay
        self.categories = {}  # 存储分类信息 {分类名: 分类URL}
        self.category_products = {}  # 存储每个分类下的商品 {分类名: [商品列表]}
        self.all_products = []  # 存储所有商品
        
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 启用性能日志记录
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def extract_categories_from_page(self, driver):
        """从店铺主页提取分类信息"""
        print("正在提取店铺分类信息...")
        
        try:
            # 等待页面加载
            time.sleep(5)
            
            # 尝试多种可能的分类选择器
            category_selectors = [
                "div.cate-list a",
                "ul.category-list li a", 
                "div.tab-menu a",
                "div.category a",
                "div.cate a",
                "a[href*='cate']",
                "a[href*='category']",
                "div.nav-item a",
                "div.menu-item a"
            ]
            
            categories_found = {}
            
            for selector in category_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        category_name = elem.text.strip()
                        category_url = elem.get_attribute("href")
                        
                        if category_name and category_url and "weidian.com" in category_url:
                            # 过滤掉一些无关的链接
                            if category_name not in ["首页", "全部", "店铺", "客服", "收藏"]:
                                categories_found[category_name] = category_url
                                print(f"找到分类: {category_name} -> {category_url}")
                    
                    if categories_found:
                        break
                        
                except Exception as e:
                    print(f"使用选择器 {selector} 提取分类失败: {e}")
                    continue
            
            # 如果还是没找到，尝试从页面源码中提取
            if not categories_found:
                print("尝试从页面源码中提取分类信息...")
                page_source = driver.page_source
                
                # 查找可能的分类链接模式
                category_patterns = [
                    r'href="([^"]*cate[^"]*)"[^>]*>([^<]+)</a>',
                    r'href="([^"]*category[^"]*)"[^>]*>([^<]+)</a>',
                    r'href="([^"]*tabType=([^&"]+)[^"]*)"[^>]*>([^<]+)</a>'
                ]
                
                for pattern in category_patterns:
                    matches = re.findall(pattern, page_source)
                    for match in matches:
                        if len(match) >= 2:
                            url = match[0] if match[0].startswith('http') else f"https://weidian.com{match[0]}"
                            name = match[-1].strip()
                            if name and name not in ["首页", "全部", "店铺", "客服", "收藏"]:
                                categories_found[name] = url
                                print(f"从源码中找到分类: {name} -> {url}")
            
            self.categories = categories_found
            print(f"总共找到 {len(self.categories)} 个分类")
            return categories_found
            
        except Exception as e:
            print(f"提取分类信息失败: {e}")
            return {}
    
    def extract_api_data(self, driver):
        """从浏览器日志中提取API数据"""
        api_responses = []
        try:
            logs = driver.get_log("performance")
            for log in logs:
                try:
                    log_entry = json.loads(log["message"])["message"]
                    
                    if "Network.responseReceived" in log_entry["method"]:
                        if "response" in log_entry["params"]:
                            response = log_entry["params"]["response"]
                            response_url = response["url"]
                            
                            # 寻找商品列表API
                            if ("item" in response_url or "goods" in response_url or "list" in response_url) and (
                                "api" in response_url or "json" in response_url):
                                if "mimeType" in response and "json" in response["mimeType"].lower():
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
        except Exception as e:
            print(f"提取API数据失败: {e}")
        
        return api_responses
    
    def parse_products_from_api(self, api_responses, category_name=""):
        """从API响应中解析商品数据"""
        products = []
        
        for response in api_responses:
            try:
                data = json.loads(response["content"])
                
                if isinstance(data, dict) and "result" in data:
                    result = data["result"]
                    
                    # 寻找商品列表
                    product_list = None
                    for key in ["itemList", "items", "goods", "products", "list"]:
                        if key in result and isinstance(result[key], list):
                            product_list = result[key]
                            break
                    
                    if product_list:
                        for product in product_list:
                            if isinstance(product, dict):
                                item = self.parse_single_product(product, category_name)
                                if item:
                                    products.append(item)
                        
                        print(f"从API中解析出 {len(products)} 个商品")
                        break
                        
            except Exception as e:
                print(f"解析API数据失败: {e}")
                continue
        
        return products
    
    def parse_single_product(self, product, category_name=""):
        """解析单个商品数据"""
        try:
            item = {}
            
            # 商品ID
            item["商品ID"] = product.get("itemId") or product.get("id") or ""
            
            # 商品名称
            item["商品名称"] = (
                product.get("itemName") or 
                product.get("title") or 
                product.get("name") or 
                ""
            )
            
            # 价格
            price = product.get("price") or ""
            if "priceInfo" in product and isinstance(product["priceInfo"], dict):
                price = product["priceInfo"].get("price") or price
            item["价格"] = price
            
            # 原价
            original_price = product.get("originalPrice") or ""
            if "priceInfo" in product and isinstance(product["priceInfo"], dict):
                original_price = product["priceInfo"].get("originalPrice") or original_price
            item["原价"] = original_price
            
            # 销量
            item["销量"] = (
                product.get("sold") or 
                product.get("sales") or 
                product.get("saleNum") or 
                ""
            )
            
            # 库存
            item["库存"] = product.get("stock") or ""
            
            # 图片
            img_url = ""
            for img_key in ["img", "image", "imgHead", "itemImg"]:
                if img_key in product:
                    img_url = product[img_key]
                    break
            if not img_url and "images" in product and isinstance(product["images"], list) and len(product["images"]) > 0:
                img_url = product["images"][0]
            item["图片链接"] = img_url
            
            # 商品链接
            item["商品详情页链接"] = (
                product.get("url") or 
                product.get("link") or 
                f"https://weidian.com/item.html?itemID={item['商品ID']}" if item["商品ID"] else ""
            )
            
            # 分类
            item["商品分类"] = (
                product.get("cateName") or 
                product.get("categoryName") or 
                product.get("category") or 
                category_name or 
                ""
            )
            
            return item
            
        except Exception as e:
            print(f"解析商品数据失败: {e}")
            return None
    
    def crawl_category_products(self, category_name, category_url):
        """爬取指定分类下的所有商品"""
        print(f"\n开始爬取分类: {category_name}")
        print(f"分类URL: {category_url}")
        
        driver = self.setup_driver()
        products = []
        
        try:
            # 访问分类页面
            driver.get(category_url)
            time.sleep(self.delay)
            
            # 提取API数据
            api_responses = self.extract_api_data(driver)
            
            # 解析商品数据
            if api_responses:
                products = self.parse_products_from_api(api_responses, category_name)
            
            # 如果API没有数据，尝试从页面直接提取
            if not products:
                print("API中没有找到商品数据，尝试从页面提取...")
                products = self.extract_products_from_page(driver, category_name)
            
            print(f"分类 {category_name} 共找到 {len(products)} 个商品")
            
        except Exception as e:
            print(f"爬取分类 {category_name} 失败: {e}")
        
        finally:
            driver.quit()
        
        return products
    
    def extract_products_from_page(self, driver, category_name):
        """从页面直接提取商品信息"""
        products = []
        try:
            # 尝试多种商品元素选择器
            product_selectors = [
                "div.item",
                "div.product", 
                "a.item-wrap",
                "div.goods-item",
                "div.product-item"
            ]
            
            for selector in product_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 {selector} 找到 {len(elements)} 个商品元素")
                    
                    for elem in elements:
                        try:
                            # 提取商品信息
                            product = self.extract_product_from_element(elem, category_name)
                            if product:
                                products.append(product)
                        except:
                            continue
                    break
                    
        except Exception as e:
            print(f"从页面提取商品失败: {e}")
        
        return products
    
    def extract_product_from_element(self, element, category_name):
        """从页面元素中提取商品信息"""
        try:
            product = {}
            
            # 商品链接和ID
            link_elem = element.find_element(By.TAG_NAME, "a") if element.tag_name != "a" else element
            product_url = link_elem.get_attribute("href")
            
            if product_url:
                # 从URL中提取商品ID
                item_id_match = re.search(r'itemID=([^&]+)', product_url)
                product["商品ID"] = item_id_match.group(1) if item_id_match else ""
                product["商品详情页链接"] = product_url
            
            # 商品名称
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, "div.title, div.name, span.title, span.name")
                product["商品名称"] = name_elem.text.strip()
            except:
                product["商品名称"] = ""
            
            # 价格
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, "div.price, span.price, div.cost, span.cost")
                price_text = price_elem.text.strip()
                price_match = re.search(r'[\d.]+', price_text)
                product["价格"] = price_match.group() if price_match else ""
            except:
                product["价格"] = ""
            
            # 图片
            try:
                img_elem = element.find_element(By.TAG_NAME, "img")
                product["图片链接"] = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")
            except:
                product["图片链接"] = ""
            
            # 分类
            product["商品分类"] = category_name
            
            # 其他字段设置默认值
            product["原价"] = ""
            product["销量"] = ""
            product["库存"] = ""
            
            return product if product.get("商品ID") else None

        except Exception as e:
            print(f"提取商品元素信息失败: {e}")
            return None

    def crawl_all_categories(self):
        """爬取所有分类的商品"""
        print("开始爬取店铺所有分类的商品...")

        # 首先获取分类列表
        driver = self.setup_driver()
        try:
            driver.get(self.shop_url)
            categories = self.extract_categories_from_page(driver)
        finally:
            driver.quit()

        if not categories:
            print("未找到任何分类，尝试爬取主页商品...")
            # 如果没有找到分类，直接爬取主页的商品
            return self.crawl_main_page_products()

        # 爬取每个分类的商品
        all_products = []
        for category_name, category_url in categories.items():
            try:
                products = self.crawl_category_products(category_name, category_url)
                if products:
                    all_products.extend(products)
                    self.category_products[category_name] = products

                # 添加延迟，避免请求过快
                if self.delay > 0:
                    time.sleep(self.delay)

            except Exception as e:
                print(f"爬取分类 {category_name} 失败: {e}")
                continue

        self.all_products = all_products
        return all_products

    def crawl_main_page_products(self):
        """爬取主页商品（当没有找到分类时）"""
        print("爬取主页商品...")

        driver = self.setup_driver()
        products = []

        try:
            driver.get(self.shop_url)
            time.sleep(self.delay)

            # 提取API数据
            api_responses = self.extract_api_data(driver)

            # 解析商品数据
            if api_responses:
                products = self.parse_products_from_api(api_responses, "全部商品")

            # 如果API没有数据，尝试从页面直接提取
            if not products:
                products = self.extract_products_from_page(driver, "全部商品")

            print(f"主页共找到 {len(products)} 个商品")

        except Exception as e:
            print(f"爬取主页商品失败: {e}")

        finally:
            driver.quit()

        self.all_products = products
        return products

    def save_to_excel(self, filename):
        """保存数据到Excel文件"""
        if not self.all_products:
            print("没有商品数据可保存")
            return False

        try:
            # 创建DataFrame
            df = pd.DataFrame(self.all_products)

            # 确保输出目录存在
            output_dir = os.path.dirname(filename)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 保存为Excel文件
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('商品数据')

            # 写入表头
            headers = df.columns.tolist()
            for col, header in enumerate(headers):
                sheet.write(0, col, header)

            # 写入数据
            for row, item in enumerate(df.to_dict('records'), 1):
                for col, header in enumerate(headers):
                    value = item.get(header, '')
                    if isinstance(value, (str, int, float, bool)):
                        sheet.write(row, col, value)
                    else:
                        sheet.write(row, col, str(value))

            # 保存文件
            workbook.save(filename)
            print(f"成功保存 {len(self.all_products)} 条商品数据到 {filename}")

            # 打印分类统计
            if self.category_products:
                print("\n分类统计:")
                for category, products in self.category_products.items():
                    print(f"  {category}: {len(products)} 个商品")

            return True

        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            return False

    def print_summary(self):
        """打印爬取结果摘要"""
        print(f"\n=== 爬取结果摘要 ===")
        print(f"店铺URL: {self.shop_url}")
        print(f"找到分类数: {len(self.categories)}")
        print(f"总商品数: {len(self.all_products)}")

        if self.categories:
            print(f"\n分类列表:")
            for name, url in self.categories.items():
                count = len(self.category_products.get(name, []))
                print(f"  {name}: {count} 个商品")

        if self.all_products:
            print(f"\n商品示例 (前3个):")
            for i, product in enumerate(self.all_products[:3]):
                print(f"  {i+1}. {product.get('商品名称', 'N/A')} - {product.get('商品分类', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="微店完整分类信息爬取工具")
    parser.add_argument("-u", "--url",
                       default="https://weidian.com/?userid=1286456178&spider_token=8555&tabType=all",
                       help="微店店铺链接")
    parser.add_argument("-o", "--output",
                       default="data/complete_categories_products.xls",
                       help="输出Excel文件路径")
    parser.add_argument("-d", "--delay", type=float, default=2.0,
                       help="请求间隔时间(秒)")

    args = parser.parse_args()

    # 确保data目录存在
    os.makedirs("data", exist_ok=True)

    print("=== 微店完整分类信息爬取工具 ===")
    print(f"目标店铺: {args.url}")
    print(f"输出文件: {args.output}")
    print(f"请求延迟: {args.delay}秒")
    print("=" * 50)

    # 创建爬虫实例
    crawler = WeidianCategoryCrawler(args.url, args.delay)

    try:
        # 开始爬取
        products = crawler.crawl_all_categories()

        if products:
            # 保存数据
            success = crawler.save_to_excel(args.output)

            # 打印摘要
            crawler.print_summary()

            if success:
                print(f"\n✅ 爬取完成！数据已保存到: {args.output}")
            else:
                print(f"\n❌ 保存失败！")
        else:
            print("\n❌ 未能获取到任何商品数据！")

    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"\n爬取过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
