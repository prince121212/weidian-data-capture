#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确的cateId参数测试
"""

import requests
import json
import urllib.parse

def test_with_correct_cateid():
    """使用正确的cateId参数测试"""
    shop_id = "1286456178"
    
    # 测试用例
    test_cases = [
        {
            "cate_id": 115027143,
            "cate_name": "酒店前台", 
            "expected": 2
        },
        {
            "cate_id": 124372605,
            "cate_name": "釉中青花",
            "expected": 13
        },
        {
            "cate_id": 124372612,
            "cate_name": "精品青花",
            "expected": 8
        }
    ]
    
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
    
    # 尝试不同的API接口和参数组合
    api_variants = [
        {
            "name": "使用cateId参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "param_key": "cateId"
        },
        {
            "name": "使用categoryId参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "param_key": "categoryId"
        },
        {
            "name": "使用cate_id参数",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "param_key": "cate_id"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试分类: {test_case['cate_name']}")
        print(f"分类ID: {test_case['cate_id']}")
        print(f"预期商品数: {test_case['expected']}")
        print(f"{'='*60}")
        
        for variant in api_variants:
            print(f"\n🔍 {variant['name']}:")
            
            params_dict = {
                "shopId": shop_id,
                variant["param_key"]: test_case["cate_id"],
                "sortOrder": "desc",
                "offset": 0,
                "limit": 50,
                "from": "h5"
            }
            
            param_json = json.dumps(params_dict, separators=(',', ':'))
            param_encoded = urllib.parse.quote(param_json)
            full_url = f"{variant['url']}?param={param_encoded}"
            
            try:
                response = requests.get(full_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        status = data.get("status", {})
                        
                        if status.get("code") == 0:
                            result = data.get("result", {})
                            items = result.get("itemList", [])
                            actual_count = len(items)
                            
                            print(f"   ✅ 获取到 {actual_count} 个商品")
                            
                            if actual_count == test_case["expected"]:
                                print(f"   🎉 数量完全匹配！")
                                
                                if items:
                                    print(f"   前3个商品:")
                                    for i, item in enumerate(items[:3], 1):
                                        print(f"     {i}. {item.get('itemId')}: {item.get('itemName')}")
                                
                                # 如果找到了正确的API，记录下来
                                print(f"   ✨ 找到正确的API组合！")
                                return variant, test_case
                                
                            elif abs(actual_count - test_case["expected"]) <= 2:
                                print(f"   📝 数量接近 (差异: {abs(actual_count - test_case['expected'])})")
                            else:
                                print(f"   ⚠️ 数量差异较大 (预期: {test_case['expected']}, 实际: {actual_count})")
                        else:
                            print(f"   ❌ API错误: {status}")
                    except json.JSONDecodeError:
                        print(f"   ❌ 响应不是有效JSON")
                else:
                    print(f"   ❌ HTTP错误: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 请求异常: {e}")
    
    print(f"\n❌ 未找到完全匹配的API组合")
    return None, None

if __name__ == "__main__":
    print("=== 测试正确的cateId参数 ===")
    correct_api, test_case = test_with_correct_cateid()
    
    if correct_api:
        print(f"\n🎉 找到正确的API！")
        print(f"API: {correct_api['name']}")
        print(f"URL: {correct_api['url']}")
        print(f"参数: {correct_api['param_key']}")
        print(f"测试分类: {test_case['cate_name']}")
    else:
        print(f"\n❌ 未找到正确的API组合")
        print("可能需要尝试其他方法或API接口")
