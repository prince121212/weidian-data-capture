#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取微店完整分类树的脚本
使用您发现的getCateTree接口
"""

import requests
import json
import xlwt
import os
from urllib.parse import unquote

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
        
        print(f"请求URL: {response.url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取分类数据")
            return data
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def parse_category_tree(data):
    """解析分类树数据"""
    categories = []
    
    if not data or "result" not in data:
        print("❌ 数据格式错误")
        return categories
    
    result = data["result"]
    print(f"原始数据结构: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}...")
    
    # 查找分类数据的可能位置
    category_data = None
    
    # 尝试不同的数据结构
    possible_keys = ["cateTree", "categories", "cateList", "tree", "data"]
    
    for key in possible_keys:
        if key in result:
            category_data = result[key]
            print(f"找到分类数据在: {key}")
            break
    
    if not category_data:
        # 如果没有找到，直接使用result
        category_data = result
        print("使用整个result作为分类数据")
    
    # 递归解析分类树
    def parse_categories(cate_list, parent_name="", level=0):
        if not isinstance(cate_list, list):
            return
        
        for cate in cate_list:
            if not isinstance(cate, dict):
                continue
            
            # 提取分类信息
            cate_id = cate.get("cateId", cate.get("id", ""))
            cate_name = cate.get("cateName", cate.get("name", ""))
            
            if cate_name:
                full_name = f"{parent_name}-{cate_name}" if parent_name else cate_name
                
                category_info = {
                    "分类ID": cate_id,
                    "分类名称": cate_name,
                    "完整分类路径": full_name,
                    "层级": level,
                    "父分类": parent_name
                }
                
                categories.append(category_info)
                print(f"{'  ' * level}📁 {full_name} (ID: {cate_id})")
                
                # 递归处理子分类
                sub_categories = cate.get("childCateList", cate.get("subCateList", cate.get("children", cate.get("subCategories", []))))
                if sub_categories:
                    parse_categories(sub_categories, full_name, level + 1)
    
    # 开始解析
    if isinstance(category_data, list):
        parse_categories(category_data)
    elif isinstance(category_data, dict):
        # 如果是字典，查找列表数据
        for key, value in category_data.items():
            if isinstance(value, list):
                print(f"解析字典中的列表: {key}")
                parse_categories(value)
                break
    
    return categories

def get_category_products(shop_id, cate_id, limit=100):
    """获取指定分类下的商品"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "cateId": cate_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": limit,
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
                return data["result"]["itemList"]
        return []
    except:
        return []

def save_categories_to_excel(categories, filename):
    """保存分类信息到Excel"""
    try:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('分类树')
        
        # 表头
        headers = ["分类ID", "分类名称", "完整分类路径", "层级", "父分类"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 数据
        for row, category in enumerate(categories, 1):
            for col, header in enumerate(headers):
                value = category.get(header, "")
                sheet.write(row, col, str(value))
        
        workbook.save(filename)
        print(f"✅ 分类数据已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    shop_id = "1286456178"
    output_file = "data/category_tree.xls"
    
    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)
    
    print("=== 微店分类树获取工具 ===")
    print(f"店铺ID: {shop_id}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 获取分类树
    data = get_category_tree(shop_id)
    
    if data:
        print("\n=== 解析分类树 ===")
        categories = parse_category_tree(data)
        
        if categories:
            print(f"\n📊 分类统计:")
            print(f"总分类数: {len(categories)}")
            
            # 按层级统计
            level_count = {}
            for cat in categories:
                level = cat["层级"]
                level_count[level] = level_count.get(level, 0) + 1
            
            for level in sorted(level_count.keys()):
                print(f"  第{level+1}级分类: {level_count[level]}个")
            
            # 保存到Excel
            save_categories_to_excel(categories, output_file)
            
            # 显示一些示例分类
            print(f"\n🎯 详细分类示例:")
            for i, cat in enumerate(categories[:10]):
                print(f"  {i+1}. {cat['完整分类路径']}")
            
            if len(categories) > 10:
                print(f"  ... 还有 {len(categories) - 10} 个分类")
            
            # 检查是否有您要找的分类
            target_keywords = ["高温白玉瓷", "釉中青花", "精品青花", "至尊青花", "青花玲珑"]
            found_targets = []
            
            for cat in categories:
                for keyword in target_keywords:
                    if keyword in cat["分类名称"] or keyword in cat["完整分类路径"]:
                        found_targets.append(cat)
                        break
            
            if found_targets:
                print(f"\n🎉 找到目标分类 ({len(found_targets)}个):")
                for cat in found_targets:
                    print(f"  ✅ {cat['完整分类路径']} (ID: {cat['分类ID']})")
            else:
                print(f"\n💡 未找到包含目标关键词的分类名称")
                print("但这可能是因为这些是商品名称而不是分类名称")
            
        else:
            print("❌ 未能解析出分类数据")
            print("原始数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("❌ 获取分类数据失败")

if __name__ == "__main__":
    main()
