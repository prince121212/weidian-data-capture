#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取所有分类下的商品，按指定格式保存
格式：分类id|分类名|商品数量|商品名称[]|商品ID[]
"""

import pandas as pd
import requests
import json
import openpyxl
from openpyxl.styles import Font, Alignment
import time

class AllCategoriesProductsCollector:
    def __init__(self):
        """初始化商品搜集器"""
        self.shop_id = "1286456178"
        self.all_results = []
        
    def get_category_products_api(self, cate_id, category_name):
        """使用API获取单个分类的商品"""
        print(f"🔍 获取分类 '{category_name}' (ID: {cate_id}) 的商品...")
        
        # 正确的API端点
        url = "https://thor.weidian.com/decorate/itemCate.getCateItemList/1.0"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
            "Accept": "application/json, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://h5.weidian.com/",
            "Origin": "https://h5.weidian.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        
        all_products = []
        page = 0
        max_pages = 20  # 最大页数限制
        
        while page < max_pages:
            offset = page * 20
            
            # 构建API参数
            api_params = {
                "cateId": str(cate_id),
                "shopId": str(self.shop_id),
                "offset": offset,
                "limit": 20,
                "sortField": "all",
                "sortType": "desc",
                "isQdFx": False,
                "isHideSold": False,
                "hideItemRealAmount": False,
                "from": "h5",
                "fanSpreadMode": -1,
                "isShopItemListConfOpen": False,
                "attrQuery": [],
                "isStockDown": 0,
                "isConsumerProtect": False,
                "hideItemComment": False
            }
            
            params = {
                "param": json.dumps(api_params, separators=(',', ':'))
            }
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status", {}).get("code") == 0:
                        result = data.get("result", {})
                        item_list = result.get("itemList", [])
                        has_data = result.get("hasData", False)
                        
                        if not item_list or not has_data:
                            break
                        
                        # 解析商品信息
                        for item in item_list:
                            product_info = {
                                "商品ID": item.get("itemId", ""),
                                "商品名称": item.get("itemName", "")
                            }
                            all_products.append(product_info)
                        
                        # 如果返回的商品数量少于20，说明已经是最后一页
                        if len(item_list) < 20:
                            break
                            
                    else:
                        # API错误，跳出循环
                        break
                else:
                    # HTTP错误，跳出循环
                    break
                    
            except Exception as e:
                # 请求异常，跳出循环
                break
            
            page += 1
            time.sleep(0.5)  # 避免请求过快
        
        print(f"  ✅ 获取到 {len(all_products)} 个商品")
        return all_products
    
    def process_all_categories(self):
        """处理所有分类"""
        print("🚀 开始获取所有分类的商品信息...")
        print("=" * 60)
        
        try:
            # 读取过滤后的分类文件
            df = pd.read_excel('data/shop_categories_with_links_filtered.xlsx', sheet_name='分类汇总')
            print(f"📊 总共需要处理 {len(df)} 个分类")
            
            for index, row in df.iterrows():
                cate_id = str(row['分类ID'])
                cate_name = row['分类名称']
                expected_count = row['商品数量']
                
                print(f"\n[{index+1}/{len(df)}] 处理分类: {cate_name}")
                
                # 获取商品
                products = self.get_category_products_api(cate_id, cate_name)
                
                # 提取商品名称和ID列表
                product_names = [p['商品名称'] for p in products]
                product_ids = [p['商品ID'] for p in products]
                
                # 构建结果记录
                result_record = {
                    "分类ID": cate_id,
                    "分类名称": cate_name,
                    "预期商品数量": expected_count,
                    "实际商品数量": len(products),
                    "商品名称列表": str(product_names),  # 转换为字符串格式
                    "商品ID列表": str(product_ids)      # 转换为字符串格式
                }
                
                self.all_results.append(result_record)
                
                print(f"  📊 预期: {expected_count}个, 实际: {len(products)}个")
                
                # 每处理10个分类暂停一下
                if (index + 1) % 10 == 0:
                    print(f"\n⏸️ 已处理 {index + 1} 个分类，暂停2秒...")
                    time.sleep(2)
            
            print(f"\n🎉 所有分类处理完成！共处理 {len(self.all_results)} 个分类")
            return True
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_results_to_xlsx(self, filename):
        """保存结果到xlsx文件"""
        try:
            print(f"\n💾 正在保存结果到 {filename}...")
            
            # 创建工作簿
            workbook = openpyxl.Workbook()
            workbook.remove(workbook.active)
            
            # 创建主数据表
            main_sheet = workbook.create_sheet('所有分类商品汇总')
            
            # 设置表头
            headers = ["分类ID", "分类名称", "预期商品数量", "实际商品数量", "商品名称列表", "商品ID列表"]
            
            # 写入表头并设置样式
            for col, header in enumerate(headers, 1):
                cell = main_sheet.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')
            
            # 写入数据
            for row_idx, result in enumerate(self.all_results, 2):
                for col_idx, header in enumerate(headers, 1):
                    value = result.get(header, "")
                    main_sheet.cell(row=row_idx, column=col_idx, value=str(value))
            
            # 自动调整列宽
            column_widths = [15, 25, 15, 15, 80, 80]  # 预设列宽
            for i, width in enumerate(column_widths, 1):
                column_letter = main_sheet.cell(row=1, column=i).column_letter
                main_sheet.column_dimensions[column_letter].width = width
            
            # 创建统计表
            stats_sheet = workbook.create_sheet('统计信息')
            
            # 计算统计信息
            total_categories = len(self.all_results)
            total_expected = sum(r['预期商品数量'] for r in self.all_results)
            total_actual = sum(r['实际商品数量'] for r in self.all_results)
            categories_with_products = len([r for r in self.all_results if r['实际商品数量'] > 0])
            categories_without_products = total_categories - categories_with_products
            
            stats_data = [
                ["统计项目", "数值"],
                ["总分类数", total_categories],
                ["有商品的分类数", categories_with_products],
                ["无商品的分类数", categories_without_products],
                ["预期商品总数", total_expected],
                ["实际商品总数", total_actual],
                ["获取成功率", f"{(total_actual/total_expected*100):.1f}%" if total_expected > 0 else "N/A"],
                ["", ""],
                ["商品数量分布", ""],
            ]
            
            # 商品数量分布统计
            product_count_distribution = {}
            for result in self.all_results:
                count = result['实际商品数量']
                if count == 0:
                    key = "0个商品"
                elif count <= 5:
                    key = "1-5个商品"
                elif count <= 10:
                    key = "6-10个商品"
                elif count <= 20:
                    key = "11-20个商品"
                else:
                    key = "20个以上商品"
                
                product_count_distribution[key] = product_count_distribution.get(key, 0) + 1
            
            for range_key, count in product_count_distribution.items():
                stats_data.append([range_key, count])
            
            # 写入统计数据
            for row, (key, value) in enumerate(stats_data, 1):
                stats_sheet.cell(row=row, column=1, value=key)
                stats_sheet.cell(row=row, column=2, value=value)
                
                # 设置表头样式
                if row == 1 or key in ["商品数量分布"]:
                    stats_sheet.cell(row=row, column=1).font = Font(bold=True)
                    stats_sheet.cell(row=row, column=2).font = Font(bold=True)
            
            # 调整统计表列宽
            stats_sheet.column_dimensions['A'].width = 25
            stats_sheet.column_dimensions['B'].width = 20
            
            # 保存文件
            workbook.save(filename)
            print(f"✅ 结果已成功保存到: {filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("🛍️ 所有分类商品搜集工具")
    print("=" * 60)
    
    collector = AllCategoriesProductsCollector()
    
    # 处理所有分类
    if collector.process_all_categories():
        # 保存结果
        filename = "data/所有分类商品汇总.xlsx"
        if collector.save_results_to_xlsx(filename):
            print(f"\n🎉 任务完成!")
            print(f"📁 文件已保存: {filename}")
            print(f"📊 包含内容:")
            print(f"  - 所有分类商品汇总: {len(collector.all_results)}个分类的商品信息")
            print(f"  - 统计信息: 详细的统计数据")
            
            # 显示前5个分类的结果示例
            print(f"\n🎯 结果示例 (前5个分类):")
            for i, result in enumerate(collector.all_results[:5]):
                print(f"  {i+1}. {result['分类名称']} (ID: {result['分类ID']})")
                print(f"     商品数量: {result['实际商品数量']}个")
                if result['实际商品数量'] > 0:
                    # 显示前3个商品名称
                    names = eval(result['商品名称列表'])[:3] if result['商品名称列表'] != '[]' else []
                    if names:
                        print(f"     商品示例: {', '.join(names)}")
                print()
        else:
            print(f"\n❌ 保存文件失败")
    else:
        print(f"\n❌ 处理分类失败")


if __name__ == "__main__":
    main()
