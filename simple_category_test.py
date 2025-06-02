#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试分类接口
"""

import requests
import json

def test_category_api():
    """测试分类接口"""
    shop_id = "1286456178"
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
        print("正在测试分类接口...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 接口调用成功")
            
            # 打印原始数据结构
            print("\n原始数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            return data
        else:
            print(f"❌ 接口调用失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

if __name__ == "__main__":
    test_category_api()
