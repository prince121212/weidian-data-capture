#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同的参数格式
"""

import requests
import json

def test_different_params():
    """测试不同的参数格式"""
    shop_id = "1286456178"
    cate_id = "124372605"  # 釉中青花的分类ID
    
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "使用cateId",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": cate_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 5,
                    "from": "h5"
                })
            }
        },
        {
            "name": "使用tabId",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "tabId": cate_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 5,
                    "from": "h5"
                })
            }
        },
        {
            "name": "使用categoryId",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "categoryId": cate_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 5,
                    "from": "h5"
                })
            }
        },
        {
            "name": "简化参数",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": cate_id,
                    "offset": 0,
                    "limit": 5
                })
            }
        },
        {
            "name": "使用数字类型的cateId",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": int(cate_id),
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 5,
                    "from": "h5"
                })
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {test_case['name']} ===")
        print(f"参数: {test_case['params']}")
        
        try:
            response = requests.get(url, params=test_case['params'], headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:300]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status", {}).get("code") == 0:  # 成功
                    print("✅ 成功!")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
                    break
                else:
                    print(f"❌ 失败: {data.get('status', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print("-" * 50)

def test_main_product_list():
    """测试获取主商品列表（不指定分类）"""
    print("\n=== 测试主商品列表 ===")
    
    shop_id = "1286456178"
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 10,
            "from": "h5"
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status", {}).get("code") == 0:
                print("✅ 主商品列表获取成功!")
                items = data.get("result", {}).get("itemList", [])
                print(f"获取到 {len(items)} 个商品")
                for item in items[:3]:
                    print(f"  - {item.get('itemName', 'N/A')} (ID: {item.get('itemId', 'N/A')})")
            else:
                print(f"❌ 失败: {data.get('status', {}).get('message', '未知错误')}")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_different_params()
    test_main_product_list()
