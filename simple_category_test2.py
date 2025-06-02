#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试分类商品获取
"""

import requests
import json

def test_simple_api():
    """测试简单的API调用"""
    shop_id = "1286456178"
    
    # 测试1: 获取分类树
    print("=== 测试1: 获取分类树 ===")
    url1 = "https://thor.weidian.com/decorate/shopDetail.tab.getCateTree/1.0"
    params1 = {
        "param": json.dumps({
            "shopId": shop_id,
            "from": "h5"
        })
    }
    
    try:
        response1 = requests.get(url1, params=params1, timeout=10)
        print(f"分类树状态码: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print("分类树获取成功")
            
            # 找一个有商品的分类
            if "result" in data1 and "cateList" in data1["result"]:
                for cate in data1["result"]["cateList"]:
                    if cate.get("speCateItemNum", 0) > 0:
                        cate_id = cate.get("cateId")
                        cate_name = cate.get("cateName")
                        item_count = cate.get("speCateItemNum")
                        
                        print(f"找到分类: {cate_name} (ID: {cate_id}, 商品数: {item_count})")
                        
                        # 测试2: 获取这个分类的商品
                        print(f"\n=== 测试2: 获取分类 {cate_name} 的商品 ===")
                        url2 = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
                        params2 = {
                            "param": json.dumps({
                                "shopId": shop_id,
                                "cateId": cate_id,
                                "sortOrder": "desc",
                                "offset": 0,
                                "limit": 5,
                                "from": "h5",
                                "showItemTag": True
                            })
                        }
                        
                        response2 = requests.get(url2, params=params2, timeout=10)
                        print(f"商品列表状态码: {response2.status_code}")
                        print(f"响应内容: {response2.text[:500]}")
                        
                        if response2.status_code == 200:
                            data2 = response2.json()
                            print("商品数据:")
                            print(json.dumps(data2, ensure_ascii=False, indent=2)[:1000])
                        
                        break
        else:
            print(f"分类树获取失败: {response1.text}")
            
    except Exception as e:
        print(f"异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_api()
