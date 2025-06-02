#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取并保存所有商品分类到XLS文件
"""

import requests
import json
import xlwt
import os

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
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    try:
        print(f"正在获取店铺 {shop_id} 的分类树...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取分类数据")
            return data
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def parse_categories(data):
    """解析分类数据"""
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
                print(f"{'  ' * level}📁 {full_path} (ID: {cate_id}, 商品数: {item_count})")
                
                # 处理子分类
                child_categories = cate.get("childCateList", [])
                if child_categories:
                    extract_categories(child_categories, full_path, level + 1)
    
    extract_categories(cate_list)
    return all_categories

def get_category_products(shop_id, cate_id, cate_name):
    """获取指定分类下的商品ID列表"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "cateId": cate_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 100,
            "from": "h5",
            "showItemTag": True
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "itemList" in data["result"]:
                items = data["result"]["itemList"]
                product_ids = [str(item.get("itemId", "")) for item in items]
                print(f"  获取到分类 '{cate_name}' 下的 {len(product_ids)} 个商品")
                return product_ids
        return []
    except Exception as e:
        print(f"  获取分类 '{cate_name}' 商品失败: {e}")
        return []

def save_categories_to_xls(categories, filename):
    """保存分类信息到XLS文件"""
    try:
        # 创建工作簿
        workbook = xlwt.Workbook()
        
        # 创建分类汇总表
        summary_sheet = workbook.add_sheet('分类汇总')
        summary_headers = ["分类ID", "分类名称", "完整分类路径", "层级", "父分类", "商品数量"]
        
        # 写入表头
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header)
        
        # 写入分类数据
        for row, category in enumerate(categories, 1):
            for col, header in enumerate(summary_headers):
                value = category.get(header, "")
                summary_sheet.write(row, col, str(value))
        
        # 创建详细分类表（包含商品ID）
        detail_sheet = workbook.add_sheet('分类商品详情')
        detail_headers = ["分类ID", "分类名称", "完整分类路径", "商品ID列表", "商品数量"]
        
        # 写入表头
        for col, header in enumerate(detail_headers):
            detail_sheet.write(0, col, header)
        
        # 获取每个分类的商品并写入
        shop_id = "1286456178"
        detail_row = 1
        
        for category in categories:
            cate_id = category["分类ID"]
            cate_name = category["分类名称"]
            full_path = category["完整分类路径"]
            
            if cate_id and cate_id != "0":  # 跳过"未分类"
                product_ids = get_category_products(shop_id, cate_id, cate_name)
                
                detail_sheet.write(detail_row, 0, str(cate_id))
                detail_sheet.write(detail_row, 1, cate_name)
                detail_sheet.write(detail_row, 2, full_path)
                detail_sheet.write(detail_row, 3, ", ".join(product_ids))
                detail_sheet.write(detail_row, 4, len(product_ids))
                
                detail_row += 1
        
        # 保存文件
        workbook.save(filename)
        print(f"\n✅ 分类数据已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    shop_id = "1286456178"
    output_file = "data/all_categories.xls"
    
    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)
    
    print("=== 微店所有分类保存工具 ===")
    print(f"店铺ID: {shop_id}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 获取分类树
    data = get_category_tree(shop_id)
    
    if data:
        print("\n=== 解析分类树 ===")
        categories = parse_categories(data)
        
        if categories:
            print(f"\n📊 分类统计:")
            print(f"总分类数: {len(categories)}")
            
            # 按层级统计
            level_count = {}
            for cat in categories:
                level = cat["层级"]
                level_count[level] = level_count.get(level, 0) + 1
            
            for level in sorted(level_count.keys()):
                print(f"  第{level}级分类: {level_count[level]}个")
            
            # 显示所有分类
            print(f"\n🎯 所有分类列表:")
            for i, cat in enumerate(categories, 1):
                indent = "  " * (cat["层级"] - 1)
                print(f"  {i:2d}. {indent}{cat['分类名称']} (商品数: {cat['商品数量']})")
            
            # 重点显示您关注的分类
            target_categories = []
            for cat in categories:
                if any(keyword in cat["分类名称"] for keyword in ["高温白玉瓷", "精品青花", "至尊青花", "釉中青花"]):
                    target_categories.append(cat)
            
            if target_categories:
                print(f"\n🎉 找到目标分类 ({len(target_categories)}个):")
                for cat in target_categories:
                    print(f"  ✅ {cat['完整分类路径']} (ID: {cat['分类ID']}, 商品数: {cat['商品数量']})")
            
            # 保存到Excel
            print(f"\n=== 保存分类数据 ===")
            success = save_categories_to_xls(categories, output_file)
            
            if success:
                print(f"\n🎉 完成！")
                print(f"📁 文件位置: {output_file}")
                print(f"📊 包含内容:")
                print(f"  - 分类汇总表: {len(categories)}个分类的基本信息")
                print(f"  - 分类商品详情表: 每个分类下的商品ID列表")
            else:
                print(f"\n❌ 保存失败")
                
        else:
            print("❌ 未能解析出分类数据")
    else:
        print("❌ 获取分类数据失败")

if __name__ == "__main__":
    main()
