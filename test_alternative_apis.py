#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试其他可能的API接口
"""

import requests
import json
import urllib.parse

def test_alternative_apis():
    """测试其他API接口"""
    shop_id = "1286456178"
    category_id = "115027143"  # 酒店前台，应该只有2个商品
    category_name = "酒店前台"
    expected_count = 2
    
    print("=== 测试其他API接口 ===")
    print(f"分类: {category_name}")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: {expected_count}")
    print("=" * 50)
    
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
    
    # 测试不同的API接口
    apis = [
        {
            "name": "shop.getItemList",
            "url": "https://thor.weidian.com/shop/getItemList/1.0",
            "param_key": "cateId"
        },
        {
            "name": "wfr.shop.getItemList",
            "url": "https://thor.weidian.com/wfr/shop/getItemList/1.0",
            "param_key": "cateId"
        },
        {
            "name": "category.getItemList",
            "url": "https://thor.weidian.com/category/getItemList/1.0",
            "param_key": "categoryId"
        },
        {
            "name": "item.getItemListByCategory",
            "url": "https://thor.weidian.com/item/getItemListByCategory/1.0",
            "param_key": "categoryId"
        }
    ]
    
    for i, api in enumerate(apis, 1):
        print(f"\n{i}. 测试 {api['name']}:")
        
        params_dict = {
            "shopId": shop_id,
            api["param_key"]: int(category_id),
            "sortOrder": "desc",
            "offset": 0,
            "limit": 50,
            "from": "h5"
        }
        
        param_json = json.dumps(params_dict, separators=(',', ':'))
        param_encoded = urllib.parse.quote(param_json)
        full_url = f"{api['url']}?param={param_encoded}"
        
        try:
            response = requests.get(full_url, headers=headers, timeout=15)
            print(f"   HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   API状态: {data.get('status', {})}")
                    
                    if data.get("status", {}).get("code") == 0:
                        result = data.get("result", {})
                        items = result.get("itemList", [])
                        print(f"   ✅ 获取到 {len(items)} 个商品")
                        
                        if items:
                            print(f"   前3个商品:")
                            for j, item in enumerate(items[:3], 1):
                                print(f"     {j}. {item.get('itemId')}: {item.get('itemName')}")
                        
                        # 检查数量匹配
                        if len(items) == expected_count:
                            print(f"   🎉 数量完全匹配！")
                        elif abs(len(items) - expected_count) <= 2:
                            print(f"   📝 数量接近 (差异: {abs(len(items) - expected_count)})")
                        else:
                            print(f"   ⚠️ 数量差异较大 (预期: {expected_count}, 实际: {len(items)})")
                    else:
                        print(f"   ❌ API错误: {data.get('status', {})}")
                except json.JSONDecodeError:
                    print(f"   ❌ 响应不是有效JSON")
                    print(f"   响应内容: {response.text[:200]}...")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应内容: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

def test_different_category():
    """测试一个商品数量更多的分类"""
    shop_id = "1286456178"
    category_id = "124372605"  # 釉中青花，应该有13个商品
    category_name = "釉中青花"
    expected_count = 13
    
    print(f"\n\n=== 测试另一个分类: {category_name} ===")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: {expected_count}")
    print("=" * 50)
    
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
    
    # 只测试shop.getItemList，因为它最有可能工作
    url = "https://thor.weidian.com/shop/getItemList/1.0"
    
    params_dict = {
        "shopId": shop_id,
        "cateId": int(category_id),
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,
        "from": "h5"
    }
    
    param_json = json.dumps(params_dict, separators=(',', ':'))
    param_encoded = urllib.parse.quote(param_json)
    full_url = f"{url}?param={param_encoded}"
    
    try:
        response = requests.get(full_url, headers=headers, timeout=15)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API状态: {data.get('status', {})}")
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    print(f"✅ 获取到 {len(items)} 个商品")
                    
                    if items:
                        print(f"前5个商品:")
                        for j, item in enumerate(items[:5], 1):
                            print(f"  {j}. {item.get('itemId')}: {item.get('itemName')}")
                    
                    # 检查数量匹配
                    if len(items) == expected_count:
                        print(f"🎉 数量完全匹配！")
                    elif abs(len(items) - expected_count) <= 2:
                        print(f"📝 数量接近 (差异: {abs(len(items) - expected_count)})")
                    else:
                        print(f"⚠️ 数量差异较大 (预期: {expected_count}, 实际: {len(items)})")
                else:
                    print(f"❌ API错误: {data.get('status', {})}")
            except json.JSONDecodeError:
                print(f"❌ 响应不是有效JSON")
                print(f"响应内容: {response.text[:200]}...")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_alternative_apis()
    test_different_category()
