#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关键分类的商品ID
"""

import requests
import json
import time

def test_category_api(shop_id, cate_id, cate_name, expected_count):
    """测试单个分类的API"""
    print(f"\n测试分类: {cate_name} (ID: {cate_id}, 预期: {expected_count}个商品)")
    
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "tabId": cate_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 50,
            "from": "h5"
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status", {}).get("code") == 0 and "result" in data:
                result = data["result"]
                items = result.get("itemList", [])
                actual_count = len(items)
                
                print(f"  ✅ 成功获取 {actual_count} 个商品")
                
                if actual_count == expected_count or abs(actual_count - expected_count) <= 2:
                    product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                    print(f"  🎯 {cate_name}分类下有商品id：{' 和 '.join(product_ids)}")
                    return product_ids
                else:
                    print(f"  ⚠️ 数量不匹配 (预期: {expected_count}, 实际: {actual_count})")
            else:
                print(f"  ❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    return []

def main():
    shop_id = "1286456178"
    
    # 重点测试的分类
    key_categories = [
        {"id": "124372605", "name": "釉中青花", "full_name": "高温白玉瓷餐具-釉中青花", "count": 13},
        {"id": "124372612", "name": "精品青花", "full_name": "高温白玉瓷餐具-精品青花", "count": 8},
        {"id": "139661840", "name": "至尊青花", "full_name": "高温白玉瓷餐具-至尊青花", "count": 3},
        {"id": "124372546", "name": "釉中青花玲珑", "full_name": "高温白玉瓷餐具-釉中青花玲珑", "count": 6}
    ]
    
    print("=== 测试关键分类商品ID ===")
    print("=" * 50)
    
    results = []
    
    for category in key_categories:
        product_ids = test_category_api(
            shop_id, 
            category["id"], 
            category["full_name"], 
            category["count"]
        )
        
        if product_ids:
            results.append({
                "分类": category["full_name"],
                "商品ID": product_ids
            })
        
        time.sleep(1)  # 避免请求过快
    
    print(f"\n🎯 最终结果汇总:")
    print("=" * 50)
    
    for result in results:
        print(f"✅ {result['分类']}分类下有商品id：{' 和 '.join(result['商品ID'])}")
    
    if not results:
        print("❌ 未能获取到任何分类的商品ID")

if __name__ == "__main__":
    main()
