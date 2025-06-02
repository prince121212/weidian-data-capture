#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试
"""

import requests
import json

def quick_test():
    print("开始测试...")
    
    shop_id = "1286456178"
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    # 测试不带分类ID的请求
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 5,
            "from": "h5"
        })
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("解析JSON成功")
            print(f"状态: {data.get('status', {})}")
            
            if data.get("status", {}).get("code") == 0:
                print("API调用成功!")
                result = data.get("result", {})
                items = result.get("itemList", [])
                print(f"获取到 {len(items)} 个商品")
                
                for item in items:
                    print(f"商品: {item.get('itemName', 'N/A')} (ID: {item.get('itemId', 'N/A')})")
            else:
                print(f"API返回错误: {data.get('status', {}).get('message', '未知')}")
        
    except Exception as e:
        print(f"异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
