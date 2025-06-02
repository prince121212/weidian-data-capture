#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正确的参数使用方式
"""

import requests
import json
import urllib.parse

def test_both_params():
    """测试tabId和cateId两种参数"""
    shop_id = "1286456178"
    category_id = "115027143"  # 酒店前台，应该只有2个商品
    category_name = "酒店前台"
    expected_count = 2
    
    print("=== 测试不同参数方式 ===")
    print(f"分类: {category_name}")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: {expected_count}")
    print("=" * 50)
    
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
    
    # 测试1: 使用tabId
    print("\n1. 测试使用 tabId 参数:")
    params_dict1 = {
        "shopId": shop_id,
        "tabId": int(category_id),
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,
        "from": "h5",
        "showItemTag": True
    }
    
    param_json1 = json.dumps(params_dict1, separators=(',', ':'))
    param_encoded1 = urllib.parse.quote(param_json1)
    full_url1 = f"{url}?param={param_encoded1}"
    
    try:
        response1 = requests.get(full_url1, headers=headers, timeout=15)
        if response1.status_code == 200:
            data1 = response1.json()
            if data1.get("status", {}).get("code") == 0:
                items1 = data1.get("result", {}).get("itemList", [])
                print(f"   使用tabId获取到 {len(items1)} 个商品")
                if items1:
                    for i, item in enumerate(items1[:3], 1):
                        print(f"     {i}. {item.get('itemId')}: {item.get('itemName')}")
            else:
                print(f"   API错误: {data1.get('status', {})}")
        else:
            print(f"   HTTP错误: {response1.status_code}")
    except Exception as e:
        print(f"   请求异常: {e}")
    
    # 测试2: 使用cateId
    print("\n2. 测试使用 cateId 参数:")
    params_dict2 = {
        "shopId": shop_id,
        "cateId": int(category_id),
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,
        "from": "h5",
        "showItemTag": True
    }
    
    param_json2 = json.dumps(params_dict2, separators=(',', ':'))
    param_encoded2 = urllib.parse.quote(param_json2)
    full_url2 = f"{url}?param={param_encoded2}"
    
    try:
        response2 = requests.get(full_url2, headers=headers, timeout=15)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("status", {}).get("code") == 0:
                items2 = data2.get("result", {}).get("itemList", [])
                print(f"   使用cateId获取到 {len(items2)} 个商品")
                if items2:
                    for i, item in enumerate(items2[:3], 1):
                        print(f"     {i}. {item.get('itemId')}: {item.get('itemName')}")
            else:
                print(f"   API错误: {data2.get('status', {})}")
        else:
            print(f"   HTTP错误: {response2.status_code}")
    except Exception as e:
        print(f"   请求异常: {e}")
    
    print(f"\n=== 结论 ===")
    print(f"预期商品数: {expected_count}")
    print(f"使用tabId获取数量: {len(items1) if 'items1' in locals() else '未知'}")
    print(f"使用cateId获取数量: {len(items2) if 'items2' in locals() else '未知'}")

if __name__ == "__main__":
    test_both_params()
