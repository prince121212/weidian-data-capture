#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析商品数据结构
"""

import requests
import json
import urllib.parse

def analyze_product_data():
    """分析商品数据结构"""
    shop_id = "1286456178"
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://weidian.com",
        "referer": "https://weidian.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "cookie": "__spider__visitorid=f8aafd4628d8df46; visitor_id=6139fb27-aa45-42e8-894b-624ceb14cd31; Hm_lvt_f3b91484e26c0d850ada494bff4b469b=1747038927; is_login=true; login_type=LOGIN_USER_TYPE_MASTER; login_source=LOGIN_USER_SOURCE_MASTER; uid=1782954047; duid=1782954047; sid=1771946129; smart_login_type=0; login_token=_EwWqqVIQUxZ57lKJ1fKfI-LbdpmbvUO9CuSjJOTD9eWJrnP_vA34zVkM4kqwmNeGlZS0C6LRbSxUb7Ew31z1KxLIQH8wHTGXBkk1PaerIGOX3doAYLrK83gjL-5dle7MrqUCtshRawBhxDuYj8zD3i7DJMGTzfvko5DBAVFVhx8khvhcNUogWWuTaTZqfX3A5NHN83WSXzH7vBXmEtpPYyrpn17g03WHQ9bx2pyFp10YyI_yPIPMGGebMlPrmGiynYeNxnTU; hi_dxh=; hold=; cn_merchant=; wdtoken=c3999548; __spider__sessionid=99f7889b2170aca2"
    }
    
    # 获取一页商品数据进行分析
    params_dict = {
        "shopId": shop_id,
        "tabId": 0,
        "sortOrder": "desc",
        "offset": 0,
        "limit": 5,  # 只获取5个商品进行详细分析
        "from": "h5"
    }
    
    param_json = json.dumps(params_dict, separators=(',', ':'))
    param_encoded = urllib.parse.quote(param_json)
    full_url = f"{url}?param={param_encoded}"
    
    try:
        response = requests.get(full_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status", {}).get("code") == 0:
                result = data.get("result", {})
                items = result.get("itemList", [])
                
                print("=== 商品数据结构分析 ===")
                print(f"获取到 {len(items)} 个商品")
                
                for i, item in enumerate(items, 1):
                    print(f"\n商品 {i}:")
                    print(f"完整数据结构:")
                    print(json.dumps(item, ensure_ascii=False, indent=2))
                    print("-" * 80)
                
                # 分析是否有分类相关字段
                print(f"\n=== 分类相关字段分析 ===")
                if items:
                    sample_item = items[0]
                    all_keys = list(sample_item.keys())
                    
                    category_related_keys = [key for key in all_keys if 'cate' in key.lower() or 'category' in key.lower() or 'tab' in key.lower()]
                    
                    print(f"所有字段: {all_keys}")
                    print(f"可能的分类相关字段: {category_related_keys}")
                    
                    for key in category_related_keys:
                        print(f"  {key}: {sample_item.get(key)}")
                
            else:
                print(f"API错误: {data.get('status', {})}")
        else:
            print(f"HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def test_different_tabids():
    """测试不同的tabId值"""
    shop_id = "1286456178"
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://weidian.com",
        "referer": "https://weidian.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "cookie": "__spider__visitorid=f8aafd4628d8df46; visitor_id=6139fb27-aa45-42e8-894b-624ceb14cd31; Hm_lvt_f3b91484e26c0d850ada494bff4b469b=1747038927; is_login=true; login_type=LOGIN_USER_TYPE_MASTER; login_source=LOGIN_USER_SOURCE_MASTER; uid=1782954047; duid=1782954047; sid=1771946129; smart_login_type=0; login_token=_EwWqqVIQUxZ57lKJ1fKfI-LbdpmbvUO9CuSjJOTD9eWJrnP_vA34zVkM4kqwmNeGlZS0C6LRbSxUb7Ew31z1KxLIQH8wHTGXBkk1PaerIGOX3doAYLrK83gjL-5dle7MrqUCtshRawBhxDuYj8zD3i7DJMGTzfvko5DBAVFVhx8khvhcNUogWWuTaTZqfX3A5NHN83WSXzH7vBXmEtpPYyrpn17g03WHQ9bx2pyFp10YyI_yPIPMGGebMlPrmGiynYeNxnTU; hi_dxh=; hold=; cn_merchant=; wdtoken=c3999548; __spider__sessionid=99f7889b2170aca2"
    }
    
    # 测试不同的tabId值，看看是否对应分类ID
    test_tab_ids = [
        0,  # 所有商品
        115027143,  # 酒店前台的cateId
        124372605,  # 釉中青花的cateId
        124372612,  # 精品青花的cateId
    ]
    
    print(f"\n=== 测试不同tabId值 ===")
    
    for tab_id in test_tab_ids:
        print(f"\n测试 tabId = {tab_id}:")
        
        params_dict = {
            "shopId": shop_id,
            "tabId": tab_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 10,
            "from": "h5"
        }
        
        param_json = json.dumps(params_dict, separators=(',', ':'))
        param_encoded = urllib.parse.quote(param_json)
        full_url = f"{url}?param={param_encoded}"
        
        try:
            response = requests.get(full_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    
                    print(f"  获取到 {len(items)} 个商品")
                    
                    if items:
                        print(f"  前3个商品:")
                        for i, item in enumerate(items[:3], 1):
                            print(f"    {i}. {item.get('itemId')}: {item.get('itemName')}")
                else:
                    print(f"  API错误: {data.get('status', {})}")
            else:
                print(f"  HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"  请求异常: {e}")

if __name__ == "__main__":
    analyze_product_data()
    test_different_tabids()
