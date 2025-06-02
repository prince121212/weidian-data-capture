#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查第五个分类信息
"""

import pandas as pd

def check_fifth_category():
    """检查第五个分类信息"""
    try:
        df = pd.read_excel('data/shop_categories_with_links.xlsx', sheet_name='分类汇总')
        
        print("前10个分类信息:")
        for i in range(min(10, len(df))):
            category = df.iloc[i]
            print(f"{i+1}. {category['分类名称']} (ID: {category['分类ID']}, 商品数: {category['商品数量']})")
        
        if len(df) >= 5:
            fifth_category = df.iloc[4]  # 第5个分类（索引为4）
            print(f"\n第五个分类详细信息:")
            print(f"分类名称: {fifth_category['分类名称']}")
            print(f"分类ID: {fifth_category['分类ID']}")
            print(f"商品数量: {fifth_category['商品数量']}")
            print(f"完整路径: {fifth_category['完整分类路径']}")
            return fifth_category
        else:
            print("分类数量不足5个")
            return None
            
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

if __name__ == "__main__":
    check_fifth_category()
