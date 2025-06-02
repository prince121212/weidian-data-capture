#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API连接 - 不使用代理
"""

import requests
import json
import time

def test_api_connection():
    """测试API连接"""
    shop_id = "1286456178"
    
    # 测试重点分类
    test_categories = [
        {"id": "124372605", "name": "高温白玉瓷餐具-釉中青花", "expected": 13},
        {"id": "124372612", "name": "高温白玉瓷餐具-精品青花", "expected": 8},
        {"id": "139661840", "name": "高温白玉瓷餐具-至尊青花", "expected": 3},
        {"id": "124372546", "name": "高温白玉瓷餐具-釉中青花玲珑", "expected": 6}
    ]
    
    # 设置请求参数 - 不使用代理
    session = requests.Session()
    session.trust_env = False  # 不使用环境变量中的代理设置
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    print("=== 测试API连接 (无代理) ===")
    print("=" * 50)
    
    for category in test_categories:
        print(f"\n测试分类: {category['name']}")
        print(f"分类ID: {category['id']}")
        print(f"预期商品数: {category['expected']}")
        
        # 构建API请求
        url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
        
        params = {
            "param": json.dumps({
                "shopId": shop_id,
                "tabId": category["id"],
                "sortOrder": "desc",
                "offset": 0,
                "limit": 50,
                "from": "h5"
            })
        }
        
        try:
            print("  发送请求...")
            response = session.get(url, params=params, headers=headers, timeout=15)
            
            print(f"  HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  API响应状态: {data.get('status', {})}")
                    
                    if data.get("status", {}).get("code") == 0 and "result" in data:
                        result = data["result"]
                        items = result.get("itemList", [])
                        actual_count = len(items)
                        
                        print(f"  ✅ 成功获取 {actual_count} 个商品")
                        
                        if actual_count > 0:
                            product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                            print(f"  🎯 {category['name']}分类下有商品id：{' 和 '.join(product_ids[:10])}")
                            
                            if len(product_ids) > 10:
                                print(f"      (还有{len(product_ids)-10}个商品ID...)")
                            
                            # 验证数量
                            if actual_count == category['expected']:
                                print(f"  ✅ 数量完全匹配！")
                            elif abs(actual_count - category['expected']) <= 2:
                                print(f"  📝 数量接近 (差异: {abs(actual_count - category['expected'])})")
                            else:
                                print(f"  ⚠️ 数量差异较大 (预期: {category['expected']}, 实际: {actual_count})")
                        else:
                            print(f"  ❌ 未获取到商品")
                    else:
                        print(f"  ❌ API返回错误: {data.get('status', {}).get('message', '未知错误')}")
                        
                except json.JSONDecodeError:
                    print(f"  ❌ 响应不是有效的JSON格式")
                    print(f"  响应内容: {response.text[:200]}...")
            else:
                print(f"  ❌ HTTP请求失败")
                
        except requests.exceptions.ProxyError as e:
            print(f"  ❌ 代理错误: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ 连接错误: {e}")
        except requests.exceptions.Timeout as e:
            print(f"  ❌ 超时错误: {e}")
        except Exception as e:
            print(f"  ❌ 其他错误: {e}")
        
        print("  " + "-" * 40)
        time.sleep(2)  # 避免请求过快

def main():
    test_api_connection()

if __name__ == "__main__":
    main()
