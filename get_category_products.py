#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取每个细分分类下的具体商品ID
"""

import requests
import json
import xlwt
import xlrd
import os
import time

def get_category_tree(shop_id):
    """获取店铺的完整分类树"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getCateTree/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "from": "h5"
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"获取分类树失败: {e}")
        return None

def get_category_products(shop_id, cate_id, cate_name, max_pages=20):
    """获取指定分类下的所有商品"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    all_products = []
    
    for page in range(max_pages):
        offset = page * 20
        
        params = {
            "param": json.dumps({
                "shopId": shop_id,
                "tabId": cate_id,
                "sortOrder": "desc",
                "offset": offset,
                "limit": 20,
                "from": "h5",
                "showItemTag": True
            })
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "result" in data and "itemList" in data["result"]:
                    items = data["result"]["itemList"]
                    
                    if not items:  # 没有更多商品了
                        break
                    
                    for item in items:
                        product_info = {
                            "商品ID": str(item.get("itemId", "")),
                            "商品名称": item.get("itemName", ""),
                            "价格": item.get("price", ""),
                            "原价": item.get("originalPrice", ""),
                            "销量": item.get("sold", ""),
                            "库存": item.get("stock", ""),
                            "图片链接": item.get("itemImg", ""),
                            "商品详情页链接": f"https://weidian.com/item.html?itemID={item.get('itemId', '')}" if item.get('itemId') else ""
                        }
                        all_products.append(product_info)
                    
                    print(f"  第{page+1}页: 获取到 {len(items)} 个商品")
                    
                    if len(items) < 20:  # 最后一页
                        break
                else:
                    break
            else:
                print(f"  请求失败，状态码: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  获取第{page+1}页失败: {e}")
            break
        
        time.sleep(0.5)  # 避免请求过快
    
    print(f"分类 '{cate_name}' 总共获取到 {len(all_products)} 个商品")
    return all_products

def parse_categories(data):
    """解析分类数据，返回所有分类信息"""
    all_categories = []
    
    if not data or "result" not in data:
        return all_categories
    
    result = data["result"]
    cate_list = result.get("cateList", [])
    
    def extract_categories(categories, parent_name="", level=0):
        for cate in categories:
            cate_id = cate.get("cateId", "")
            cate_name = cate.get("cateName", "")
            item_count = cate.get("speCateItemNum", 0)
            
            if cate_name:
                # 构建完整分类路径
                if parent_name:
                    full_path = f"{parent_name}-{cate_name}"
                else:
                    full_path = cate_name
                
                category_info = {
                    "分类ID": cate_id,
                    "分类名称": cate_name,
                    "完整分类路径": full_path,
                    "层级": level + 1,
                    "父分类": parent_name,
                    "商品数量": item_count
                }
                
                all_categories.append(category_info)
                
                # 处理子分类
                child_categories = cate.get("childCateList", [])
                if child_categories:
                    extract_categories(child_categories, full_path, level + 1)
    
    extract_categories(cate_list)
    return all_categories

def save_category_products_to_excel(categories_with_products, filename):
    """保存分类商品数据到Excel"""
    try:
        workbook = xlwt.Workbook()
        
        # 创建汇总表
        summary_sheet = workbook.add_sheet('分类商品汇总')
        summary_headers = ["分类ID", "完整分类路径", "商品数量", "商品ID列表(前10个)", "所有商品ID"]
        
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header)
        
        summary_row = 1
        
        # 创建详细表
        detail_sheet = workbook.add_sheet('商品详细信息')
        detail_headers = ["分类ID", "完整分类路径", "商品ID", "商品名称", "价格", "原价", "销量", "库存", "图片链接", "商品详情页链接"]
        
        for col, header in enumerate(detail_headers):
            detail_sheet.write(0, col, header)
        
        detail_row = 1
        
        # 处理每个分类的数据
        for category_info in categories_with_products:
            cate_id = category_info["分类ID"]
            full_path = category_info["完整分类路径"]
            products = category_info.get("商品列表", [])
            
            if products:
                # 汇总表数据
                product_ids = [p["商品ID"] for p in products]
                summary_sheet.write(summary_row, 0, str(cate_id))
                summary_sheet.write(summary_row, 1, full_path)
                summary_sheet.write(summary_row, 2, len(products))
                summary_sheet.write(summary_row, 3, ", ".join(product_ids[:10]) + ("..." if len(product_ids) > 10 else ""))
                summary_sheet.write(summary_row, 4, ", ".join(product_ids))
                summary_row += 1
                
                # 详细表数据
                for product in products:
                    detail_sheet.write(detail_row, 0, str(cate_id))
                    detail_sheet.write(detail_row, 1, full_path)
                    detail_sheet.write(detail_row, 2, product["商品ID"])
                    detail_sheet.write(detail_row, 3, product["商品名称"])
                    detail_sheet.write(detail_row, 4, str(product["价格"]))
                    detail_sheet.write(detail_row, 5, str(product["原价"]))
                    detail_sheet.write(detail_row, 6, str(product["销量"]))
                    detail_sheet.write(detail_row, 7, str(product["库存"]))
                    detail_sheet.write(detail_row, 8, product["图片链接"])
                    detail_sheet.write(detail_row, 9, product["商品详情页链接"])
                    detail_row += 1
        
        workbook.save(filename)
        print(f"✅ 数据已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    shop_id = "1286456178"
    output_file = "data/category_products_detail.xls"
    
    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)
    
    print("=== 获取每个分类下的商品ID ===")
    print(f"店铺ID: {shop_id}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 获取分类树
    print("1. 获取分类树...")
    data = get_category_tree(shop_id)
    
    if not data:
        print("❌ 获取分类树失败")
        return
    
    # 解析分类
    print("2. 解析分类...")
    categories = parse_categories(data)
    print(f"找到 {len(categories)} 个分类")
    
    # 获取每个分类的商品
    print("3. 获取每个分类的商品...")
    categories_with_products = []
    
    for i, category in enumerate(categories, 1):
        cate_id = category["分类ID"]
        cate_name = category["分类名称"]
        full_path = category["完整分类路径"]
        
        print(f"\n[{i}/{len(categories)}] 处理分类: {full_path}")
        
        if cate_id and cate_id != "0":  # 跳过"未分类"
            products = get_category_products(shop_id, cate_id, cate_name)
            
            category_with_products = category.copy()
            category_with_products["商品列表"] = products
            category_with_products["实际商品数量"] = len(products)
            
            categories_with_products.append(category_with_products)
            
            # 显示商品ID
            if products:
                product_ids = [p["商品ID"] for p in products]
                print(f"  商品ID: {', '.join(product_ids[:5])}" + ("..." if len(product_ids) > 5 else ""))
                
                # 特别标注目标分类
                if "釉中青花" in full_path:
                    print(f"  🎯 目标分类找到！商品ID: {', '.join(product_ids)}")
            else:
                print(f"  该分类下没有商品")
        else:
            print(f"  跳过分类: {full_path}")
    
    # 保存数据
    print(f"\n4. 保存数据...")
    success = save_category_products_to_excel(categories_with_products, output_file)
    
    if success:
        print(f"\n🎉 完成！")
        print(f"📁 文件位置: {output_file}")
        
        # 统计信息
        total_products = sum(len(cat.get("商品列表", [])) for cat in categories_with_products)
        categories_with_items = sum(1 for cat in categories_with_products if cat.get("商品列表"))
        
        print(f"📊 统计信息:")
        print(f"  - 处理分类数: {len(categories_with_products)}")
        print(f"  - 有商品的分类: {categories_with_items}")
        print(f"  - 总商品数: {total_products}")
        
        # 显示重点分类的结果
        print(f"\n🎯 重点分类结果:")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for cat in categories_with_products:
            full_path = cat["完整分类路径"]
            products = cat.get("商品列表", [])
            
            for keyword in target_keywords:
                if keyword in full_path and products:
                    product_ids = [p["商品ID"] for p in products]
                    print(f"  ✅ {full_path}: {', '.join(product_ids)}")
                    break
    else:
        print(f"\n❌ 保存失败")

if __name__ == "__main__":
    main()
