#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微店分类搜集工具
从指定的微店分类页面搜集所有分类信息并保存到xlsx文件
"""

import requests
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import openpyxl
from openpyxl.styles import Font, Alignment
import os
import urllib.parse
from urllib.parse import urlparse, parse_qs

class CategoryCollector:
    def __init__(self, delay=2.0):
        """初始化分类搜集器"""
        self.delay = delay
        self.categories = []
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        options = Options()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # 启用网络日志
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 启用性能日志以捕获网络请求
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 执行CDP命令启用网络域
        driver.execute_cdp_cmd('Network.enable', {})
        
        return driver
    
    def extract_shop_id_from_url(self, url):
        """从URL中提取店铺ID"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'userid' in query_params:
                return query_params['userid'][0]
            
            # 尝试从URL路径中提取
            match = re.search(r'userid[=:](\d+)', url)
            if match:
                return match.group(1)
                
            print("❌ 无法从URL中提取店铺ID")
            return None
            
        except Exception as e:
            print(f"❌ 解析URL失败: {e}")
            return None
    
    def get_categories_via_api(self, shop_id):
        """通过API获取分类信息"""
        print(f"🔍 尝试通过API获取店铺 {shop_id} 的分类信息...")
        
        url = "https://thor.weidian.com/decorate/shopDetail.tab.getCateTree/1.0"
        
        params = {
            "param": json.dumps({
                "shopId": shop_id,
                "from": "h5"
            })
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": f"https://h5.weidian.com/decoration/shop-category/?userid={shop_id}",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    cate_list = result.get("cateList", [])
                    
                    if cate_list:
                        print(f"✅ API成功获取到 {len(cate_list)} 个主分类")
                        return self.parse_category_tree(cate_list, "", 0, shop_id)
                    else:
                        print("⚠️ API返回的分类列表为空")
                        return []
                else:
                    print(f"❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
                    return []
            else:
                print(f"❌ API请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ API请求异常: {e}")
            return []
    
    def parse_category_tree(self, cate_list, parent_name="", level=0, shop_id=""):
        """解析分类树结构"""
        categories = []

        for cate in cate_list:
            cate_id = cate.get("cateId", "")
            cate_name = cate.get("cateName", "")
            item_count = cate.get("speCateItemNum", 0)

            if cate_name:
                # 构建完整分类路径
                if parent_name:
                    full_path = f"{parent_name} > {cate_name}"
                else:
                    full_path = cate_name

                # 生成分类链接
                category_links = self.generate_category_links(shop_id, cate_id, cate_name)

                category_info = {
                    "分类ID": cate_id,
                    "分类名称": cate_name,
                    "完整分类路径": full_path,
                    "层级": level + 1,
                    "父分类": parent_name if parent_name else "根分类",
                    "商品数量": item_count,
                    "分类类型": "API获取",
                    "H5分类链接": category_links["h5_link"],
                    "PC分类链接": category_links["pc_link"],
                    "API查询链接": category_links["api_link"]
                }

                categories.append(category_info)
                print(f"{'  ' * level}📁 {full_path} (ID: {cate_id}, 商品数: {item_count})")

                # 处理子分类
                child_categories = cate.get("childCateList", [])
                if child_categories:
                    child_cats = self.parse_category_tree(child_categories, full_path, level + 1, shop_id)
                    categories.extend(child_cats)

        return categories

    def generate_category_links(self, shop_id, cate_id, cate_name=""):
        """生成分类的各种链接"""
        # 默认spider_token，可以根据需要调整
        spider_token = "5b20"

        links = {
            "h5_link": "",
            "pc_link": "",
            "api_link": ""
        }

        if cate_id and cate_id != "0":
            # H5分类页面链接
            links["h5_link"] = f"https://h5.weidian.com/decoration/shop-category/?userid={shop_id}&spider_token={spider_token}&cateId={cate_id}"

            # PC分类页面链接
            links["pc_link"] = f"https://weidian.com/?userid={shop_id}&spider_token={spider_token}&tabType={cate_id}"

            # API查询链接（用于获取该分类下的商品）
            api_params = {
                "shopId": shop_id,
                "tabId": cate_id,
                "sortOrder": "desc",
                "offset": 0,
                "limit": 50,
                "from": "h5",
                "showItemTag": True
            }
            param_json = json.dumps(api_params, separators=(',', ':'))
            param_encoded = urllib.parse.quote(param_json)
            links["api_link"] = f"https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param={param_encoded}"
        else:
            # 未分类或根分类的链接
            links["h5_link"] = f"https://h5.weidian.com/decoration/shop-category/?userid={shop_id}&spider_token={spider_token}"
            links["pc_link"] = f"https://weidian.com/?userid={shop_id}&spider_token={spider_token}&tabType=all"
            links["api_link"] = f"https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param={urllib.parse.quote(json.dumps({'shopId': shop_id, 'sortOrder': 'desc', 'offset': 0, 'limit': 50, 'from': 'h5'}))}"

        return links

    def get_categories_via_selenium(self, url):
        """通过Selenium获取分类信息（备用方案）"""
        print(f"🔍 尝试通过Selenium获取分类信息...")

        # 从URL中提取shop_id
        shop_id = self.extract_shop_id_from_url(url)

        driver = self.setup_driver()
        categories = []

        try:
            # 访问页面
            driver.get(url)
            print("⏳ 页面加载中，等待5秒...")
            time.sleep(5)

            # 等待页面加载完成
            wait = WebDriverWait(driver, 10)

            # 尝试多种选择器来查找分类元素
            category_selectors = [
                "div.cate-list a",
                "ul.category-list li a",
                "div.tab-menu a",
                ".category-item",
                ".cate-item",
                "[class*='category']",
                "[class*='cate']"
            ]

            found_categories = False

            for selector in category_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ 使用选择器 '{selector}' 找到 {len(elements)} 个分类元素")

                        for i, elem in enumerate(elements):
                            try:
                                category_name = elem.text.strip()
                                category_url = elem.get_attribute("href")

                                if category_name and len(category_name) > 0:
                                    # 生成分类链接
                                    category_links = self.generate_category_links(shop_id, f"selenium_{i+1}", category_name)

                                    category_info = {
                                        "分类ID": f"selenium_{i+1}",
                                        "分类名称": category_name,
                                        "完整分类路径": category_name,
                                        "层级": 1,
                                        "父分类": "根分类",
                                        "商品数量": 0,
                                        "分类类型": "页面提取",
                                        "H5分类链接": category_url if category_url else category_links["h5_link"],
                                        "PC分类链接": category_links["pc_link"],
                                        "API查询链接": category_links["api_link"]
                                    }

                                    categories.append(category_info)
                                    print(f"  📁 {category_name}")

                            except Exception as e:
                                print(f"  ⚠️ 处理分类元素失败: {e}")
                                continue

                        found_categories = True
                        break

                except Exception as e:
                    print(f"  ⚠️ 选择器 '{selector}' 失败: {e}")
                    continue

            if not found_categories:
                print("⚠️ 未找到分类信息，尝试获取页面源码进行分析...")

                # 获取页面源码并尝试正则匹配
                page_source = driver.page_source

                # 尝试从页面源码中提取分类信息
                category_patterns = [
                    r'"cateName":\s*"([^"]+)"',
                    r'"name":\s*"([^"]+)"',
                    r'分类[：:]\s*([^<>\n]+)',
                    r'category[：:]\s*([^<>\n]+)'
                ]

                for pattern in category_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        print(f"✅ 通过正则表达式找到 {len(matches)} 个分类")

                        for i, match in enumerate(set(matches)):  # 去重
                            if len(match.strip()) > 0:
                                # 生成分类链接
                                category_links = self.generate_category_links(shop_id, f"regex_{i+1}", match.strip())

                                category_info = {
                                    "分类ID": f"regex_{i+1}",
                                    "分类名称": match.strip(),
                                    "完整分类路径": match.strip(),
                                    "层级": 1,
                                    "父分类": "根分类",
                                    "商品数量": 0,
                                    "分类类型": "正则提取",
                                    "H5分类链接": category_links["h5_link"],
                                    "PC分类链接": category_links["pc_link"],
                                    "API查询链接": category_links["api_link"]
                                }

                                categories.append(category_info)
                                print(f"  📁 {match.strip()}")

                        break

        except Exception as e:
            print(f"❌ Selenium获取分类失败: {e}")

        finally:
            driver.quit()

        return categories

    def save_categories_to_xlsx(self, categories, filename):
        """保存分类信息到xlsx文件"""
        try:
            print(f"💾 正在保存分类数据到 {filename}...")

            # 创建工作簿
            workbook = openpyxl.Workbook()

            # 删除默认工作表
            workbook.remove(workbook.active)

            # 创建分类汇总表
            summary_sheet = workbook.create_sheet('分类汇总')

            # 设置表头
            headers = ["分类ID", "分类名称", "完整分类路径", "层级", "父分类", "商品数量", "分类类型", "H5分类链接", "PC分类链接", "API查询链接"]

            # 写入表头并设置样式
            for col, header in enumerate(headers, 1):
                cell = summary_sheet.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # 写入分类数据
            for row, category in enumerate(categories, 2):
                for col, header in enumerate(headers, 1):
                    value = category.get(header, "")
                    summary_sheet.cell(row=row, column=col, value=str(value))

            # 自动调整列宽
            for column in summary_sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)  # 最大宽度50
                summary_sheet.column_dimensions[column_letter].width = adjusted_width

            # 创建统计表
            stats_sheet = workbook.create_sheet('分类统计')

            # 统计信息
            stats_data = [
                ["统计项目", "数值"],
                ["总分类数", len(categories)],
                ["", ""],
                ["按层级统计", ""],
            ]

            # 按层级统计
            level_count = {}
            for cat in categories:
                level = cat.get("层级", 1)
                level_count[level] = level_count.get(level, 0) + 1

            for level in sorted(level_count.keys()):
                stats_data.append([f"第{level}级分类", level_count[level]])

            stats_data.extend([
                ["", ""],
                ["按类型统计", ""],
            ])

            # 按类型统计
            type_count = {}
            for cat in categories:
                cat_type = cat.get("分类类型", "未知")
                type_count[cat_type] = type_count.get(cat_type, 0) + 1

            for cat_type, count in type_count.items():
                stats_data.append([cat_type, count])

            # 写入统计数据
            for row, (key, value) in enumerate(stats_data, 1):
                stats_sheet.cell(row=row, column=1, value=key)
                stats_sheet.cell(row=row, column=2, value=value)

                # 设置表头样式
                if row == 1 or key in ["按层级统计", "按类型统计"]:
                    stats_sheet.cell(row=row, column=1).font = Font(bold=True)
                    stats_sheet.cell(row=row, column=2).font = Font(bold=True)

            # 调整统计表列宽
            stats_sheet.column_dimensions['A'].width = 20
            stats_sheet.column_dimensions['B'].width = 15

            # 保存文件
            workbook.save(filename)
            print(f"✅ 分类数据已成功保存到: {filename}")

            return True

        except Exception as e:
            print(f"❌ 保存xlsx文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def collect_categories(self, url):
        """搜集分类信息的主方法"""
        print("=" * 60)
        print("🏪 微店分类搜集工具")
        print("=" * 60)
        print(f"🔗 目标链接: {url}")

        # 提取店铺ID
        shop_id = self.extract_shop_id_from_url(url)
        if not shop_id:
            print("❌ 无法提取店铺ID，程序退出")
            return []

        print(f"🏪 店铺ID: {shop_id}")

        # 首先尝试API方式获取分类
        categories = self.get_categories_via_api(shop_id)

        # 如果API方式失败，尝试Selenium方式
        if not categories:
            print("\n🔄 API方式未获取到分类，尝试页面解析方式...")
            categories = self.get_categories_via_selenium(url)

        # 如果还是没有分类，尝试其他API端点
        if not categories:
            print("\n🔄 尝试其他API端点...")
            categories = self.try_alternative_apis(shop_id)

        return categories

    def try_alternative_apis(self, shop_id):
        """尝试其他API端点获取分类信息"""
        alternative_apis = [
            {
                "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
                "params": {
                    "param": json.dumps({
                        "shopId": shop_id,
                        "sortOrder": "desc",
                        "offset": 0,
                        "limit": 50,
                        "from": "h5"
                    })
                }
            },
            {
                "url": "https://weidian.com/api/pc/shop/getShopInfo",
                "params": {
                    "shopId": shop_id
                }
            }
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

        for i, api_config in enumerate(alternative_apis):
            try:
                print(f"🔍 尝试备用API {i+1}...")

                response = requests.get(
                    api_config["url"],
                    params=api_config["params"],
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 备用API {i+1} 响应成功")

                    # 尝试从响应中提取分类信息
                    categories = self.extract_categories_from_response(data, f"备用API{i+1}", shop_id)
                    if categories:
                        return categories

            except Exception as e:
                print(f"❌ 备用API {i+1} 失败: {e}")
                continue

        return []

    def extract_categories_from_response(self, data, source="API", shop_id=""):
        """从API响应中提取分类信息"""
        categories = []

        try:
            # 递归搜索包含分类信息的字段
            def search_categories(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key in ["cateList", "categories", "categoryList", "cates"]:
                            if isinstance(value, list):
                                for i, item in enumerate(value):
                                    if isinstance(item, dict) and "cateName" in item:
                                        cate_id = item.get("cateId", f"{source}_{i+1}")
                                        cate_name = item.get("cateName", "")

                                        # 生成分类链接
                                        category_links = self.generate_category_links(shop_id, cate_id, cate_name)

                                        category_info = {
                                            "分类ID": cate_id,
                                            "分类名称": cate_name,
                                            "完整分类路径": cate_name,
                                            "层级": 1,
                                            "父分类": "根分类",
                                            "商品数量": item.get("speCateItemNum", 0),
                                            "分类类型": source,
                                            "H5分类链接": category_links["h5_link"],
                                            "PC分类链接": category_links["pc_link"],
                                            "API查询链接": category_links["api_link"]
                                        }
                                        categories.append(category_info)
                        else:
                            search_categories(value, f"{path}.{key}" if path else key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        search_categories(item, f"{path}[{i}]")

            search_categories(data)

        except Exception as e:
            print(f"❌ 从{source}响应中提取分类失败: {e}")

        return categories


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='微店分类搜集工具')
    parser.add_argument('--url', '-u',
                       default='https://h5.weidian.com/decoration/shop-category/?userid=1286456178&spider_token=5b20',
                       help='微店分类页面链接')
    parser.add_argument('--output', '-o',
                       default='data/shop_categories.xlsx',
                       help='输出xlsx文件路径')
    parser.add_argument('--delay', '-d',
                       type=float, default=2.0,
                       help='请求间隔时间(秒)')

    args = parser.parse_args()

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")

    # 创建分类搜集器
    collector = CategoryCollector(delay=args.delay)

    try:
        # 搜集分类信息
        categories = collector.collect_categories(args.url)

        if categories:
            print(f"\n📊 分类搜集完成!")
            print(f"✅ 共找到 {len(categories)} 个分类")

            # 显示分类统计
            level_count = {}
            type_count = {}

            for cat in categories:
                level = cat.get("层级", 1)
                cat_type = cat.get("分类类型", "未知")

                level_count[level] = level_count.get(level, 0) + 1
                type_count[cat_type] = type_count.get(cat_type, 0) + 1

            print(f"\n📈 分类统计:")
            print(f"  按层级:")
            for level in sorted(level_count.keys()):
                print(f"    第{level}级: {level_count[level]}个")

            print(f"  按来源:")
            for cat_type, count in type_count.items():
                print(f"    {cat_type}: {count}个")

            # 显示前10个分类示例
            print(f"\n🎯 分类示例 (前10个):")
            for i, cat in enumerate(categories[:10]):
                print(f"  {i+1}. {cat['完整分类路径']} (ID: {cat['分类ID']})")

            if len(categories) > 10:
                print(f"  ... 还有 {len(categories) - 10} 个分类")

            # 保存到xlsx文件
            success = collector.save_categories_to_xlsx(categories, args.output)

            if success:
                print(f"\n🎉 任务完成!")
                print(f"📁 文件已保存: {args.output}")
                print(f"📊 包含内容:")
                print(f"  - 分类汇总表: 所有分类的详细信息")
                print(f"  - 分类统计表: 分类数量统计")
            else:
                print(f"\n❌ 保存文件失败")
        else:
            print(f"\n❌ 未能获取到任何分类信息")
            print(f"💡 建议:")
            print(f"  1. 检查网络连接")
            print(f"  2. 确认链接是否正确")
            print(f"  3. 尝试手动访问链接查看是否需要登录")

    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
