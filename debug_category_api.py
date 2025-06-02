#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试分类商品API
"""

import requests
import json

def test_category_product_api(shop_id, cate_id, cate_name):
    """测试获取分类商品的API"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "cateId": cate_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 20,
            "from": "h5",
            "showItemTag": True
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        print(f"测试分类: {cate_name} (ID: {cate_id})")
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:1000]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JSON数据结构:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
            
            return data
        else:
            print(f"请求失败")
            return None
            
    except Exception as e:
        print(f"异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_category_tree(shop_id):
    """获取分类树，找一个有商品的分类来测试"""
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

def main():
    shop_id = "1286456178"
    
    print("=== 调试分类商品API ===")
    
    # 获取分类树
    print("1. 获取分类树...")
    data = get_category_tree(shop_id)
    
    if data and "result" in data:
        cate_list = data["result"].get("cateList", [])
        
        # 找几个有商品数量的分类来测试
        test_categories = []
        
        def find_categories_with_items(categories, parent_name=""):
            for cate in categories:
                cate_id = cate.get("cateId", "")
                cate_name = cate.get("cateName", "")
                item_count = cate.get("speCateItemNum", 0)
                
                full_name = f"{parent_name}-{cate_name}" if parent_name else cate_name
                
                if item_count > 0:
                    test_categories.append({
                        "id": cate_id,
                        "name": cate_name,
                        "full_name": full_name,
                        "count": item_count
                    })
                
                # 检查子分类
                child_categories = cate.get("childCateList", [])
                if child_categories:
                    find_categories_with_items(child_categories, full_name)
        
        find_categories_with_items(cate_list)
        
        print(f"找到 {len(test_categories)} 个有商品的分类:")
        for cat in test_categories[:5]:  # 只显示前5个
            print(f"  - {cat['full_name']}: {cat['count']}个商品 (ID: {cat['id']})")
        
        # 测试前3个分类
        print(f"\n2. 测试API调用...")
        for i, cat in enumerate(test_categories[:3]):
            print(f"\n--- 测试 {i+1}: {cat['full_name']} ---")
            result = test_category_product_api(shop_id, cat['id'], cat['name'])
            print("=" * 60)
    
    else:
        print("获取分类树失败")

if __name__ == "__main__":
    main()
