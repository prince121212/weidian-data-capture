#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
寻找正确的API来获取分类商品ID
分析微店的API结构
"""

import requests
import json
import time

def test_different_apis():
    """测试不同的API接口"""
    shop_id = "1286456178"
    test_category_id = "124372605"  # 高温白玉瓷餐具-釉中青花
    test_category_name = "高温白玉瓷餐具-釉中青花"
    expected_count = 13
    
    print("=== 寻找正确的API接口 ===")
    print(f"测试店铺ID: {shop_id}")
    print(f"测试分类ID: {test_category_id}")
    print(f"测试分类: {test_category_name}")
    print(f"预期商品数: {expected_count}")
    print("=" * 60)
    
    # 设置通用请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all",
        "Origin": "https://weidian.com"
    }
    
    # 测试不同的API接口
    api_tests = [
        {
            "name": "shopDetail.tab.getItemList (原接口)",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "tabId": test_category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        },
        {
            "name": "shopDetail.tab.getItemList (使用cateId)",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": test_category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        },
        {
            "name": "shop.getItemList (商店商品列表)",
            "url": "https://thor.weidian.com/shop/getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": test_category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50
                })
            }
        },
        {
            "name": "item.getItemListByCategory (按分类获取商品)",
            "url": "https://thor.weidian.com/item/getItemListByCategory/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "categoryId": test_category_id,
                    "offset": 0,
                    "limit": 50
                })
            }
        },
        {
            "name": "wfr.shop.getItemList (WFR商店接口)",
            "url": "https://thor.weidian.com/wfr/shop/getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "cateId": test_category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50
                })
            }
        },
        {
            "name": "category.getItemList (分类商品接口)",
            "url": "https://thor.weidian.com/category/getItemList/1.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "categoryId": test_category_id,
                    "offset": 0,
                    "limit": 50
                })
            }
        },
        {
            "name": "v2版本接口",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/2.0",
            "params": {
                "param": json.dumps({
                    "shopId": shop_id,
                    "tabId": test_category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
        },
        {
            "name": "使用GET参数而非JSON",
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "params": {
                "shopId": shop_id,
                "tabId": test_category_id,
                "sortOrder": "desc",
                "offset": 0,
                "limit": 50,
                "from": "h5"
            }
        }
    ]
    
    successful_apis = []
    
    for i, api_test in enumerate(api_tests, 1):
        print(f"\n[{i}/{len(api_tests)}] 测试: {api_test['name']}")
        print(f"URL: {api_test['url']}")
        
        try:
            # 发送请求
            response = requests.get(
                api_test["url"], 
                params=api_test["params"], 
                headers=headers, 
                timeout=15,
                verify=False  # 忽略SSL证书验证
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"API响应状态: {data.get('status', {})}")
                    
                    if data.get("status", {}).get("code") == 0:
                        result = data.get("result", {})
                        items = result.get("itemList", [])
                        actual_count = len(items)
                        
                        print(f"✅ 成功获取 {actual_count} 个商品")
                        
                        if actual_count > 0:
                            # 显示前几个商品ID
                            product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                            print(f"商品ID示例: {', '.join(product_ids[:5])}")
                            
                            # 检查是否包含预期的商品ID
                            target_ids = ["7257502545", "7257580227"]
                            found_targets = [pid for pid in product_ids if pid in target_ids]
                            if found_targets:
                                print(f"🎯 找到目标商品ID: {found_targets}")
                            
                            # 验证数量
                            if actual_count == expected_count:
                                print(f"🎉 数量完全匹配！这可能是正确的API")
                                successful_apis.append({
                                    "api": api_test,
                                    "count": actual_count,
                                    "product_ids": product_ids,
                                    "match_level": "完全匹配"
                                })
                            elif abs(actual_count - expected_count) <= 2:
                                print(f"📝 数量接近 (差异: {abs(actual_count - expected_count)})")
                                successful_apis.append({
                                    "api": api_test,
                                    "count": actual_count,
                                    "product_ids": product_ids,
                                    "match_level": "接近匹配"
                                })
                            else:
                                print(f"⚠️ 数量差异较大 (预期: {expected_count}, 实际: {actual_count})")
                                successful_apis.append({
                                    "api": api_test,
                                    "count": actual_count,
                                    "product_ids": product_ids,
                                    "match_level": "数量不匹配"
                                })
                        else:
                            print(f"❌ 未获取到商品")
                    else:
                        error_msg = data.get('status', {}).get('message', '未知错误')
                        print(f"❌ API返回错误: {error_msg}")
                        
                except json.JSONDecodeError:
                    print(f"❌ 响应不是有效的JSON格式")
                    print(f"响应内容: {response.text[:200]}...")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
        
        print("-" * 50)
        time.sleep(1)  # 避免请求过快
    
    # 总结结果
    print(f"\n🎯 测试结果总结:")
    print("=" * 60)
    
    if successful_apis:
        print(f"成功的API接口数量: {len(successful_apis)}")
        
        # 按匹配程度排序
        successful_apis.sort(key=lambda x: {"完全匹配": 0, "接近匹配": 1, "数量不匹配": 2}[x["match_level"]])
        
        for i, success in enumerate(successful_apis, 1):
            api_info = success["api"]
            print(f"\n{i}. {api_info['name']} - {success['match_level']}")
            print(f"   URL: {api_info['url']}")
            print(f"   获取商品数: {success['count']}")
            print(f"   商品ID: {', '.join(success['product_ids'][:10])}")
            
            if success["match_level"] == "完全匹配":
                print(f"   🎉 推荐使用此API！")
    else:
        print("❌ 没有找到成功的API接口")
        print("可能的原因:")
        print("1. 网络连接问题")
        print("2. API接口已更改")
        print("3. 需要特殊的认证或token")
        print("4. 分类ID格式不正确")

def main():
    print("开始寻找正确的API接口...")
    test_different_apis()

if __name__ == "__main__":
    main()
