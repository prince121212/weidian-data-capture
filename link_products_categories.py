#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立商品与分类的对应关系
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
    """获取指定分类下的所有商品ID"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    all_product_ids = []
    
    for page in range(max_pages):
        offset = page * 20
        
        params = {
            "param": json.dumps({
                "shopId": shop_id,
                "tabId": cate_id,  # 使用tabId而不是cateId
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
                
                if data.get("status", {}).get("code") == 0 and "result" in data:
                    result = data["result"]
                    items = result.get("itemList", [])
                    
                    if not items:  # 没有更多商品了
                        break
                    
                    for item in items:
                        product_id = str(item.get("itemId", ""))
                        if product_id:
                            all_product_ids.append(product_id)
                    
                    print(f"  第{page+1}页: 获取到 {len(items)} 个商品")
                    
                    if len(items) < 20:  # 最后一页
                        break
                else:
                    print(f"  API返回错误: {data.get('status', {}).get('message', '未知错误')}")
                    break
            else:
                print(f"  请求失败，状态码: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  获取第{page+1}页失败: {e}")
            break
        
        time.sleep(0.5)  # 避免请求过快
    
    print(f"分类 '{cate_name}' 总共获取到 {len(all_product_ids)} 个商品ID")
    return all_product_ids

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

def create_product_category_mapping(shop_id, categories):
    """创建商品与分类的映射关系"""
    print("开始建立商品与分类的对应关系...")
    
    # 存储商品ID到分类的映射
    product_to_categories = {}  # {product_id: [category_info, ...]}
    category_to_products = {}   # {category_path: [product_ids]}
    
    for i, category in enumerate(categories, 1):
        cate_id = category["分类ID"]
        cate_name = category["分类名称"]
        full_path = category["完整分类路径"]
        
        print(f"\n[{i}/{len(categories)}] 处理分类: {full_path}")
        
        if cate_id and cate_id != "0":  # 跳过"未分类"
            product_ids = get_category_products(shop_id, cate_id, cate_name)
            
            if product_ids:
                # 记录分类到商品的映射
                category_to_products[full_path] = product_ids
                
                # 记录商品到分类的映射
                for product_id in product_ids:
                    if product_id not in product_to_categories:
                        product_to_categories[product_id] = []
                    product_to_categories[product_id].append(category)
                
                print(f"  商品ID: {', '.join(product_ids[:5])}" + ("..." if len(product_ids) > 5 else ""))
                
                # 特别标注重要分类
                if any(keyword in full_path for keyword in ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]):
                    print(f"  🎯 重要分类！{full_path}分类下有商品id：{' 和 '.join(product_ids)}")
            else:
                print(f"  该分类下没有商品")
        else:
            print(f"  跳过分类: {full_path}")
    
    return product_to_categories, category_to_products

def save_mapping_to_excel(product_to_categories, category_to_products, filename):
    """保存映射关系到Excel"""
    try:
        workbook = xlwt.Workbook()
        
        # 工作表1: 分类到商品的映射
        sheet1 = workbook.add_sheet('分类商品映射')
        headers1 = ["分类路径", "商品数量", "商品ID列表", "商品ID详细"]
        
        for col, header in enumerate(headers1):
            sheet1.write(0, col, header)
        
        row = 1
        for category_path, product_ids in category_to_products.items():
            sheet1.write(row, 0, category_path)
            sheet1.write(row, 1, len(product_ids))
            sheet1.write(row, 2, ', '.join(product_ids[:10]) + ("..." if len(product_ids) > 10 else ""))
            sheet1.write(row, 3, ', '.join(product_ids))
            row += 1
        
        # 工作表2: 商品到分类的映射
        sheet2 = workbook.add_sheet('商品分类映射')
        headers2 = ["商品ID", "所属分类数量", "分类列表", "主要分类"]
        
        for col, header in enumerate(headers2):
            sheet2.write(0, col, header)
        
        row = 1
        for product_id, categories in product_to_categories.items():
            category_paths = [cat["完整分类路径"] for cat in categories]
            main_category = category_paths[0] if category_paths else ""
            
            sheet2.write(row, 0, product_id)
            sheet2.write(row, 1, len(categories))
            sheet2.write(row, 2, ' | '.join(category_paths))
            sheet2.write(row, 3, main_category)
            row += 1
        
        # 工作表3: 重点分类汇总
        sheet3 = workbook.add_sheet('重点分类汇总')
        headers3 = ["分类名称", "商品ID", "格式化输出"]
        
        for col, header in enumerate(headers3):
            sheet3.write(0, col, header)
        
        row = 1
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for category_path, product_ids in category_to_products.items():
            for keyword in target_keywords:
                if keyword in category_path and product_ids:
                    sheet3.write(row, 0, category_path)
                    sheet3.write(row, 1, ', '.join(product_ids))
                    sheet3.write(row, 2, f"{category_path}分类下有商品id：{' 和 '.join(product_ids)}")
                    row += 1
                    break
        
        workbook.save(filename)
        print(f"\n✅ 映射关系已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    shop_id = "1286456178"
    output_file = "data/product_category_mapping.xls"
    
    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)
    
    print("=== 建立商品与分类的对应关系 ===")
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
    
    # 建立映射关系
    print("3. 建立商品与分类的映射关系...")
    product_to_categories, category_to_products = create_product_category_mapping(shop_id, categories)
    
    # 保存数据
    print(f"\n4. 保存映射关系...")
    success = save_mapping_to_excel(product_to_categories, category_to_products, output_file)
    
    if success:
        print(f"\n🎉 完成！")
        print(f"📁 文件位置: {output_file}")
        
        # 统计信息
        total_products = len(product_to_categories)
        total_categories_with_products = len(category_to_products)
        
        print(f"📊 统计信息:")
        print(f"  - 有分类的商品数: {total_products}")
        print(f"  - 有商品的分类数: {total_categories_with_products}")
        
        # 显示重点分类的结果
        print(f"\n🎯 重点分类结果:")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for category_path, product_ids in category_to_products.items():
            for keyword in target_keywords:
                if keyword in category_path and product_ids:
                    print(f"  ✅ {category_path}分类下有商品id：{' 和 '.join(product_ids)}")
                    break
    else:
        print(f"\n❌ 保存失败")

if __name__ == "__main__":
    main()
