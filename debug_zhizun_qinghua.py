#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试至尊青花分类API，检查为什么返回的商品数量不匹配
"""

import requests
import json
import pandas as pd

def test_zhizun_qinghua_api():
    """测试至尊青花分类的API"""
    
    # 获取分类信息
    df = pd.read_excel('data/shop_categories_with_links.xlsx', sheet_name='分类汇总')
    target_category = df.iloc[4]  # 第5个分类（至尊青花）
    
    print("=== 至尊青花分类API调试 ===")
    print(f"分类名称: {target_category['分类名称']}")
    print(f"分类ID: {target_category['分类ID']}")
    print(f"预期商品数量: {target_category['商品数量']}")
    print(f"完整路径: {target_category['完整分类路径']}")
    
    shop_id = "1286456178"
    category_id = target_category['分类ID']
    
    # 测试不同的API参数组合
    test_cases = [
        {
            "name": "使用tabId参数",
            "params": {
                "shopId": shop_id,
                "tabId": int(category_id),
                "sortOrder": "desc",
                "offset": 0,
                "limit": 20,
                "from": "h5",
                "showItemTag": True
            }
        },
        {
            "name": "使用cateId参数",
            "params": {
                "shopId": shop_id,
                "cateId": int(category_id),
                "sortOrder": "desc",
                "offset": 0,
                "limit": 20,
                "from": "h5",
                "showItemTag": True
            }
        }
    ]
    
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://h5.weidian.com/decoration/shop-category/?userid={shop_id}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- 测试 {i+1}: {test_case['name']} ---")
        
        params = {
            "param": json.dumps(test_case['params'])
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    item_list = result.get("itemList", [])
                    
                    print(f"✅ API响应成功")
                    print(f"返回商品数量: {len(item_list)}")
                    
                    if item_list:
                        print("前5个商品:")
                        for j, item in enumerate(item_list[:5]):
                            item_name = item.get("itemName", "无名称")
                            item_id = item.get("itemId", "无ID")
                            print(f"  {j+1}. {item_name} (ID: {item_id})")
                    
                    # 检查是否有分页信息
                    total_count = result.get("totalCount", 0)
                    has_more = result.get("hasMore", False)
                    print(f"总数量: {total_count}")
                    print(f"是否有更多: {has_more}")
                    
                    # 检查商品名称中是否包含"至尊青花"
                    zhizun_count = 0
                    for item in item_list:
                        item_name = item.get("itemName", "")
                        if "至尊青花" in item_name or "至尊" in item_name:
                            zhizun_count += 1
                            print(f"  🎯 找到相关商品: {item_name}")
                    
                    print(f"包含'至尊'相关的商品: {zhizun_count}个")
                    
                else:
                    print(f"❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    # 测试获取所有商品（不指定分类）
    print(f"\n--- 测试: 获取所有商品（不指定分类） ---")
    all_params = {
        "param": json.dumps({
            "shopId": shop_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 50,  # 增加限制数量
            "from": "h5",
            "showItemTag": True
        })
    }
    
    try:
        response = requests.get(url, params=all_params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status", {}).get("code") == 0:
                result = data.get("result", {})
                item_list = result.get("itemList", [])
                
                print(f"✅ 获取所有商品成功")
                print(f"返回商品数量: {len(item_list)}")
                
                # 检查商品中是否包含"至尊青花"相关的
                zhizun_products = []
                for item in item_list:
                    item_name = item.get("itemName", "")
                    if "至尊青花" in item_name or "至尊" in item_name:
                        zhizun_products.append(item)
                
                print(f"包含'至尊'相关的商品: {len(zhizun_products)}个")
                for item in zhizun_products:
                    print(f"  🎯 {item.get('itemName', '无名称')} (ID: {item.get('itemId', '无ID')})")
                    
            else:
                print(f"❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_zhizun_qinghua_api()
