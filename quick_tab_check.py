#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查不同标签页的商品
"""

import requests
import json
import time

def fetch_tab_data(shop_id, tab_id, offset=0, limit=20):
    """获取指定标签页的商品数据"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "tabId": tab_id,
            "sortOrder": "desc",
            "offset": offset,
            "limit": limit,
            "from": "h5",
            "showItemTag": True
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://weidian.com/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def quick_check_tabs(shop_id):
    """快速检查前几个标签页"""
    print(f"=== 快速检查店铺 {shop_id} 的标签页 ===\n")
    
    # 检查前10个标签页的第一页数据
    for tab_id in range(0, 10):
        print(f"检查标签页 {tab_id}...")
        
        data = fetch_tab_data(shop_id, tab_id, 0, 20)
        
        if data and "result" in data:
            result = data["result"]
            has_data = result.get("hasData", False)
            item_list = result.get("itemList", [])
            
            if has_data and item_list:
                print(f"  ✅ 标签页 {tab_id}: 找到 {len(item_list)} 个商品")
                
                # 显示前3个商品名称
                for i, item in enumerate(item_list[:3]):
                    name = item.get("itemName", "")
                    print(f"    {i+1}. {name}")
                
                # 检查是否有包含"高温白玉瓷"的商品
                found_target = False
                for item in item_list:
                    name = item.get("itemName", "")
                    if any(keyword in name for keyword in ["高温白玉瓷", "釉中青花", "精品青花", "至尊青花"]):
                        print(f"    🎯 找到目标商品: {name}")
                        found_target = True
                
                if not found_target:
                    # 检查是否有青花相关商品
                    qinghua_products = []
                    for item in item_list:
                        name = item.get("itemName", "")
                        if "青花" in name:
                            qinghua_products.append(name)
                    
                    if qinghua_products:
                        print(f"    💙 青花相关商品 ({len(qinghua_products)}个):")
                        for name in qinghua_products[:2]:
                            print(f"      - {name}")
                
            else:
                print(f"  ❌ 标签页 {tab_id}: 无数据")
        else:
            print(f"  ❌ 标签页 {tab_id}: 请求失败")
        
        time.sleep(0.5)  # 避免请求过快
        print()

def search_in_tab(shop_id, tab_id, keywords, max_pages=5):
    """在指定标签页中搜索关键词"""
    print(f"=== 在标签页 {tab_id} 中搜索关键词 ===")
    
    found_products = []
    
    for page in range(max_pages):
        offset = page * 20
        data = fetch_tab_data(shop_id, tab_id, offset, 20)
        
        if not data or "result" not in data:
            break
        
        result = data["result"]
        if not result.get("hasData", False):
            break
        
        item_list = result.get("itemList", [])
        if not item_list:
            break
        
        print(f"  检查第 {page+1} 页 ({len(item_list)} 个商品)...")
        
        for item in item_list:
            name = item.get("itemName", "")
            for keyword in keywords:
                if keyword in name:
                    found_products.append({
                        "name": name,
                        "id": item.get("itemId", ""),
                        "page": page + 1
                    })
                    print(f"    🎯 找到: {name}")
        
        time.sleep(0.5)
    
    return found_products

def main():
    shop_id = "1286456178"
    
    print("开始快速检查标签页...")
    print("=" * 50)
    
    # 快速检查所有标签页
    quick_check_tabs(shop_id)
    
    # 在最有希望的标签页中深度搜索
    print("=" * 50)
    print("开始深度搜索...")
    
    keywords = ["高温白玉瓷", "釉中青花", "精品青花", "至尊青花", "青花玲珑"]
    
    # 在标签页0中搜索（通常是主要商品页）
    found = search_in_tab(shop_id, 0, keywords, 20)
    
    if found:
        print(f"\n🎉 找到 {len(found)} 个匹配的商品!")
        for product in found:
            print(f"  - {product['name']} (ID: {product['id']}, 第{product['page']}页)")
    else:
        print(f"\n❌ 未找到包含指定关键词的商品")
        print("可能的原因:")
        print("1. 这些商品可能已经下架")
        print("2. 商品名称可能与预期不同")
        print("3. 可能需要在其他店铺或页面中查找")

if __name__ == "__main__":
    main()
