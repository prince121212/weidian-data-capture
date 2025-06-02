#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确获取每个分类下的商品ID
基于all_categories.xls文件中的分类信息
"""

import requests
import json
import xlwt
import xlrd
import os
import time

def read_categories_from_excel(filename):
    """从Excel文件中读取分类信息"""
    categories = []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)  # 分类汇总表
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 找到关键列
        id_col = headers.index("分类ID") if "分类ID" in headers else -1
        name_col = headers.index("分类名称") if "分类名称" in headers else -1
        path_col = headers.index("完整分类路径") if "完整分类路径" in headers else -1
        count_col = headers.index("商品数量") if "商品数量" in headers else -1
        
        print(f"列索引: ID={id_col}, 名称={name_col}, 路径={path_col}, 数量={count_col}")
        
        # 读取数据
        for row in range(1, sheet.nrows):
            category = {
                "分类ID": str(sheet.cell_value(row, id_col)) if id_col >= 0 else "",
                "分类名称": str(sheet.cell_value(row, name_col)) if name_col >= 0 else "",
                "完整分类路径": str(sheet.cell_value(row, path_col)) if path_col >= 0 else "",
                "预期商品数量": int(sheet.cell_value(row, count_col)) if count_col >= 0 and sheet.cell_value(row, count_col) else 0
            }
            
            if category["分类ID"] and category["分类ID"] != "0":
                categories.append(category)
        
        print(f"从Excel中读取到 {len(categories)} 个分类")
        return categories
        
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return []

def test_different_api_params(shop_id, cate_id, cate_name, expected_count):
    """测试不同的API参数来获取正确的商品数量"""
    print(f"\n测试分类: {cate_name} (ID: {cate_id}, 预期: {expected_count}个商品)")
    
    # 测试不同的API接口和参数
    test_cases = [
        {
            "name": "使用tabId参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "tabId": cate_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        },
        {
            "name": "使用cateId参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0", 
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": cate_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        },
        {
            "name": "使用categoryId参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "categoryId": cate_id,
                    "sortOrder": "desc", 
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        }
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    for test_case in test_cases:
        try:
            print(f"  测试: {test_case['name']}")
            response = requests.get(test_case["url"], params=test_case["params"], headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status", {}).get("code") == 0 and "result" in data:
                    result = data["result"]
                    items = result.get("itemList", [])
                    actual_count = len(items)
                    
                    print(f"    ✅ 成功获取 {actual_count} 个商品")
                    
                    if actual_count == expected_count:
                        print(f"    🎯 数量匹配！找到正确的API参数")
                        
                        # 返回商品ID列表
                        product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                        return product_ids, test_case["name"]
                    else:
                        print(f"    ⚠️ 数量不匹配 (预期: {expected_count}, 实际: {actual_count})")
                        
                        # 如果数量接近，也返回结果
                        if abs(actual_count - expected_count) <= 2:
                            print(f"    📝 数量接近，可能是正确的")
                            product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                            return product_ids, test_case["name"]
                else:
                    print(f"    ❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
            else:
                print(f"    ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ 异常: {e}")
        
        time.sleep(0.5)
    
    print(f"  ❌ 所有测试都失败了")
    return [], "失败"

def get_correct_category_products(categories, shop_id):
    """获取每个分类的正确商品列表"""
    results = []
    
    # 只测试有商品的分类
    categories_with_products = [cat for cat in categories if cat["预期商品数量"] > 0]
    
    print(f"开始测试 {len(categories_with_products)} 个有商品的分类...")
    
    for i, category in enumerate(categories_with_products, 1):
        cate_id = category["分类ID"]
        cate_name = category["分类名称"]
        full_path = category["完整分类路径"]
        expected_count = category["预期商品数量"]
        
        print(f"\n[{i}/{len(categories_with_products)}] {full_path}")
        
        product_ids, method = test_different_api_params(shop_id, cate_id, cate_name, expected_count)
        
        result = {
            "分类ID": cate_id,
            "分类名称": cate_name,
            "完整分类路径": full_path,
            "预期商品数量": expected_count,
            "实际商品数量": len(product_ids),
            "商品ID列表": product_ids,
            "成功方法": method
        }
        
        results.append(result)
        
        # 显示结果
        if product_ids:
            print(f"  ✅ 成功获取 {len(product_ids)} 个商品ID")
            print(f"  📝 商品ID: {', '.join(product_ids[:5])}" + ("..." if len(product_ids) > 5 else ""))
            
            # 特别标注重要分类
            if any(keyword in full_path for keyword in ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]):
                print(f"  🎯 重要分类！{full_path}分类下有商品id：{' 和 '.join(product_ids)}")
        else:
            print(f"  ❌ 未能获取到商品")
    
    return results

def save_correct_results(results, filename):
    """保存正确的结果到Excel"""
    try:
        workbook = xlwt.Workbook()
        
        # 创建详细结果表
        sheet = workbook.add_sheet('正确的分类商品映射')
        headers = ["分类ID", "完整分类路径", "预期商品数量", "实际商品数量", "商品ID列表", "成功方法", "格式化输出"]
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        row = 1
        for result in results:
            sheet.write(row, 0, result["分类ID"])
            sheet.write(row, 1, result["完整分类路径"])
            sheet.write(row, 2, result["预期商品数量"])
            sheet.write(row, 3, result["实际商品数量"])
            sheet.write(row, 4, ', '.join(result["商品ID列表"]))
            sheet.write(row, 5, result["成功方法"])
            
            # 格式化输出
            if result["商品ID列表"]:
                formatted = f"{result['完整分类路径']}分类下有商品id：{' 和 '.join(result['商品ID列表'])}"
                sheet.write(row, 6, formatted)
            
            row += 1
        
        workbook.save(filename)
        print(f"\n✅ 正确结果已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    shop_id = "1286456178"
    input_file = "data/all_categories.xls"
    output_file = "data/correct_category_products.xls"
    
    print("=== 正确获取分类商品ID ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 读取分类信息
    categories = read_categories_from_excel(input_file)
    
    if not categories:
        print("❌ 未能读取到分类信息")
        return
    
    # 显示分类概况
    print(f"\n📊 分类概况:")
    for cat in categories:
        if cat["预期商品数量"] > 0:
            print(f"  {cat['完整分类路径']}: {cat['预期商品数量']}个商品")
    
    # 获取正确的商品列表
    results = get_correct_category_products(categories, shop_id)
    
    # 保存结果
    if results:
        save_correct_results(results, output_file)
        
        # 显示重要分类的结果
        print(f"\n🎯 重要分类结果汇总:")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for result in results:
            full_path = result["完整分类路径"]
            product_ids = result["商品ID列表"]
            
            for keyword in target_keywords:
                if keyword in full_path and product_ids:
                    print(f"  ✅ {full_path}分类下有商品id：{' 和 '.join(product_ids)}")
                    break
    else:
        print("❌ 未能获取到任何结果")

if __name__ == "__main__":
    main()
