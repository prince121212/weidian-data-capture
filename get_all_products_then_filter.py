#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取所有商品然后按分类过滤
"""

import requests
import json
import urllib.parse
import time

def get_all_products(shop_id, max_pages=50):
    """获取店铺的所有商品"""
    print("=== 获取店铺所有商品 ===")
    
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
    
    all_products = []
    
    for page in range(max_pages):
        offset = page * 20
        
        # 使用一个通用的tabId来获取所有商品
        params_dict = {
            "shopId": shop_id,
            "tabId": 0,  # 使用0或者不指定分类来获取所有商品
            "sortOrder": "desc",
            "offset": offset,
            "limit": 20,
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
                    
                    if not items:
                        print(f"第{page+1}页没有更多商品，停止获取")
                        break
                    
                    all_products.extend(items)
                    print(f"第{page+1}页获取到 {len(items)} 个商品，累计 {len(all_products)} 个")
                    
                else:
                    print(f"第{page+1}页API错误: {data.get('status', {})}")
                    break
            else:
                print(f"第{page+1}页HTTP错误: {response.status_code}")
                break
                
        except Exception as e:
            print(f"第{page+1}页请求异常: {e}")
            break
        
        # 添加延迟
        time.sleep(0.5)
    
    print(f"✅ 总共获取到 {len(all_products)} 个商品")
    return all_products

def get_product_detail(item_id):
    """获取商品详情，包括分类信息"""
    url = "https://thor.weidian.com/detail/getItemDetail/1.0"
    
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
    
    params_dict = {
        "itemId": item_id,
        "from": "h5"
    }
    
    param_json = json.dumps(params_dict, separators=(',', ':'))
    param_encoded = urllib.parse.quote(param_json)
    full_url = f"{url}?param={param_encoded}"
    
    try:
        response = requests.get(full_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status", {}).get("code") == 0:
                result = data.get("result", {})
                item_info = result.get("itemInfo", {})
                
                # 提取分类信息
                category_info = {
                    "cateId": item_info.get("cateId"),
                    "cateName": item_info.get("cateName"),
                    "parentCateId": item_info.get("parentCateId"),
                    "parentCateName": item_info.get("parentCateName")
                }
                
                return category_info
            else:
                print(f"商品 {item_id} 详情API错误: {data.get('status', {})}")
        else:
            print(f"商品 {item_id} HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"商品 {item_id} 请求异常: {e}")
    
    return None

def test_category_filtering():
    """测试分类过滤方法"""
    shop_id = "1286456178"
    
    # 测试用例
    target_categories = [
        {"cate_id": 115027143, "cate_name": "酒店前台", "expected": 2},
        {"cate_id": 124372605, "cate_name": "釉中青花", "expected": 13}
    ]
    
    print("=== 测试分类过滤方法 ===")
    
    # 获取所有商品（只获取前5页进行测试）
    all_products = get_all_products(shop_id, max_pages=5)
    
    if not all_products:
        print("❌ 未获取到任何商品")
        return
    
    print(f"\n=== 分析商品分类信息 ===")
    
    # 分析前10个商品的分类信息
    for i, product in enumerate(all_products[:10], 1):
        item_id = product.get("itemId")
        item_name = product.get("itemName", "")
        
        print(f"\n{i}. 商品ID: {item_id}, 名称: {item_name}")
        
        category_info = get_product_detail(item_id)
        
        if category_info:
            print(f"   分类ID: {category_info.get('cateId')}")
            print(f"   分类名称: {category_info.get('cateName')}")
            print(f"   父分类ID: {category_info.get('parentCateId')}")
            print(f"   父分类名称: {category_info.get('parentCateName')}")
            
            # 检查是否属于目标分类
            for target in target_categories:
                if category_info.get('cateId') == target['cate_id']:
                    print(f"   ✅ 属于目标分类: {target['cate_name']}")
        else:
            print(f"   ❌ 无法获取分类信息")
        
        # 添加延迟避免请求过快
        time.sleep(1)

if __name__ == "__main__":
    test_category_filtering()
