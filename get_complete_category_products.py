#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取每个分类的完整商品列表
"""

import requests
import json
import urllib.parse
import time

def get_complete_category_products(shop_id, tab_id, category_name, expected_count):
    """获取指定分类的完整商品列表"""
    print(f"\n=== 获取分类完整商品: {category_name} ===")
    print(f"tabId: {tab_id}")
    print(f"预期商品数: {expected_count}")
    
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
    page = 0
    max_pages = 10  # 最多获取10页
    
    while page < max_pages:
        offset = page * 20
        
        params_dict = {
            "shopId": shop_id,
            "tabId": tab_id,
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
                    
                    # 提取商品信息
                    for item in items:
                        product_info = {
                            "商品ID": str(item.get("itemId", "")),
                            "商品名称": item.get("itemName", ""),
                            "商品价格": item.get("price", ""),
                            "商品图片": item.get("itemImg", ""),
                            "商品链接": item.get("itemUrl", ""),
                            "销量": item.get("sold", ""),
                            "库存": item.get("stock", ""),
                            "添加时间": item.get("addTime", "")
                        }
                        all_products.append(product_info)
                    
                    print(f"第{page+1}页获取到 {len(items)} 个商品，累计 {len(all_products)} 个")
                    
                    # 如果获取的商品数量已经达到或超过预期，检查是否应该停止
                    if len(all_products) >= expected_count:
                        # 再获取一页确认是否还有更多商品
                        if len(items) < 20:  # 如果这一页不满20个，说明已经到最后了
                            print(f"已获取完所有商品")
                            break
                        elif len(all_products) >= expected_count + 20:  # 如果超出预期太多，停止
                            print(f"商品数量超出预期较多，停止获取")
                            break
                    
                    page += 1
                    
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
    
    actual_count = len(all_products)
    print(f"✅ 分类 {category_name} 共获取到 {actual_count} 个商品")
    
    # 验证数量
    if actual_count == expected_count:
        print(f"🎉 商品数量完全匹配！")
    elif abs(actual_count - expected_count) <= 2:
        print(f"📝 商品数量接近 (差异: {abs(actual_count - expected_count)})")
    else:
        print(f"⚠️ 商品数量差异较大 (预期: {expected_count}, 实际: {actual_count})")
    
    return all_products

def test_specific_categories():
    """测试特定分类"""
    shop_id = "1286456178"
    
    # 测试用例
    test_cases = [
        {
            "tab_id": 115027143,
            "category_name": "酒店前台",
            "expected_count": 2
        },
        {
            "tab_id": 124372605,
            "category_name": "釉中青花",
            "expected_count": 13
        },
        {
            "tab_id": 124372612,
            "category_name": "精品青花",
            "expected_count": 8
        }
    ]
    
    print("=== 测试特定分类的完整商品列表 ===")
    
    all_results = {}
    
    for test_case in test_cases:
        products = get_complete_category_products(
            shop_id,
            test_case["tab_id"],
            test_case["category_name"],
            test_case["expected_count"]
        )
        
        all_results[test_case["category_name"]] = {
            "products": products,
            "expected": test_case["expected_count"],
            "actual": len(products)
        }
        
        # 显示前几个商品
        if products:
            print(f"\n前5个商品:")
            for i, product in enumerate(products[:5], 1):
                print(f"  {i}. {product['商品ID']}: {product['商品名称']} (价格: {product['商品价格']})")
    
    # 分析结果
    print(f"\n=== 结果分析 ===")
    for category_name, result in all_results.items():
        expected = result["expected"]
        actual = result["actual"]
        print(f"{category_name}: {actual}/{expected} 个商品")
        
        if actual == expected:
            print(f"  ✅ 数量完全匹配")
        elif abs(actual - expected) <= 2:
            print(f"  📝 数量接近")
        else:
            print(f"  ⚠️ 数量差异较大")
    
    # 检查商品重叠
    print(f"\n=== 商品重叠分析 ===")
    category_names = list(all_results.keys())
    
    for i in range(len(category_names)):
        for j in range(i + 1, len(category_names)):
            cat1 = category_names[i]
            cat2 = category_names[j]
            
            products1 = {p['商品ID'] for p in all_results[cat1]['products']}
            products2 = {p['商品ID'] for p in all_results[cat2]['products']}
            
            overlap = products1.intersection(products2)
            
            if overlap:
                print(f"{cat1} 和 {cat2} 有 {len(overlap)} 个重叠商品:")
                for product_id in list(overlap)[:3]:  # 只显示前3个
                    print(f"  - {product_id}")
            else:
                print(f"{cat1} 和 {cat2} 没有重叠商品")

if __name__ == "__main__":
    test_specific_categories()
