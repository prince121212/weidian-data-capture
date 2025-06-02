#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试我的商品获取函数
"""

from get_all_category_products import get_category_products

def test_my_function():
    """测试获取单个分类的商品"""
    shop_id = "1286456178"
    category_id = "124372605"  # 釉中青花
    category_name = "釉中青花"
    expected_count = 13
    
    print("=== 测试我的商品获取函数 ===")
    print(f"分类: {category_name}")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: {expected_count}")
    print("=" * 40)
    
    products = get_category_products(shop_id, category_id, category_name, expected_count, max_pages=2)
    
    print(f"\n=== 测试结果 ===")
    print(f"获取到 {len(products)} 个商品")
    
    if products:
        print(f"\n前3个商品:")
        for i, product in enumerate(products[:3], 1):
            print(f"  {i}. {product['商品ID']}: {product['商品名称']}")
            print(f"     价格: {product['商品价格']}")
            print(f"     链接: {product['商品链接']}")
    else:
        print("未获取到任何商品")
    
    return len(products) > 0

if __name__ == "__main__":
    success = test_my_function()
    
    if success:
        print(f"\n🎉 测试成功!")
    else:
        print(f"\n❌ 测试失败")
