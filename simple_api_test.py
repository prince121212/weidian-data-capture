#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API测试 - 找到正确的分类商品API
"""

import requests
import json

def test_single_api():
    """测试单个API接口"""
    shop_id = "1286456178"
    category_id = "124372605"  # 高温白玉瓷餐具-釉中青花
    
    print("=== 简单API测试 ===")
    print(f"店铺ID: {shop_id}")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: 13")
    print("=" * 40)
    
    # 测试最常见的API
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "tabId": category_id,
            "sortOrder": "desc",
            "offset": 0,
            "limit": 50,
            "from": "h5"
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all"
    }
    
    try:
        print("发送API请求...")
        print(f"URL: {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("响应内容:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            
            try:
                data = response.json()
                print(f"\nJSON解析成功:")
                print(f"状态: {data.get('status', {})}")
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    print(f"✅ 获取到 {len(items)} 个商品")
                    
                    if items:
                        print("前5个商品ID:")
                        for i, item in enumerate(items[:5]):
                            item_id = item.get("itemId", "")
                            item_name = item.get("itemName", "")
                            print(f"  {i+1}. {item_id} - {item_name}")
                        
                        # 检查目标商品ID
                        all_ids = [str(item.get("itemId", "")) for item in items]
                        target_ids = ["7257502545", "7257580227"]
                        found = [tid for tid in target_ids if tid in all_ids]
                        if found:
                            print(f"🎯 找到目标商品ID: {found}")
                        else:
                            print("❌ 未找到目标商品ID")
                        
                        return True, all_ids
                else:
                    print(f"❌ API错误: {data.get('status', {}).get('message', '未知错误')}")
                    
            except json.JSONDecodeError:
                print("❌ 响应不是有效JSON")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return False, []

def main():
    success, product_ids = test_single_api()
    
    if success:
        print(f"\n🎉 API测试成功！")
        print(f"获取到 {len(product_ids)} 个商品ID")
        print(f"商品ID列表: {', '.join(product_ids)}")
        
        # 保存结果
        with open("api_test_result.txt", "w", encoding="utf-8") as f:
            f.write(f"API测试成功\n")
            f.write(f"商品数量: {len(product_ids)}\n")
            f.write(f"商品ID: {', '.join(product_ids)}\n")
        
        print("结果已保存到 api_test_result.txt")
    else:
        print(f"\n❌ API测试失败")

if __name__ == "__main__":
    main()
