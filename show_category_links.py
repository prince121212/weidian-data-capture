#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示分类链接详细信息
"""

import pandas as pd

def show_category_links():
    """显示分类链接详细信息"""
    try:
        # 读取文件
        df = pd.read_excel('data/shop_categories_with_links.xlsx', sheet_name='分类汇总')
        print(f"📊 分类链接详细信息 (共{len(df)}个分类)")
        print("=" * 80)
        
        # 显示前10个分类的完整链接信息
        for i, row in df.head(10).iterrows():
            print(f"\n{i+1}. 【{row['分类名称']}】(ID: {row['分类ID']})")
            print(f"   完整路径: {row['完整分类路径']}")
            print(f"   商品数量: {row['商品数量']}")
            print(f"   H5链接: {row['H5分类链接']}")
            print(f"   PC链接: {row['PC分类链接']}")
            print(f"   API链接: {row['API查询链接']}")
        
        if len(df) > 10:
            print(f"\n... 还有 {len(df) - 10} 个分类")
        
        # 统计信息
        print(f"\n📈 统计信息:")
        print(f"  总分类数: {len(df)}")
        
        # 按层级统计
        level_count = df['层级'].value_counts().sort_index()
        print(f"  按层级:")
        for level, count in level_count.items():
            print(f"    第{level}级: {count}个")
        
        # 按类型统计
        type_count = df['分类类型'].value_counts()
        print(f"  按来源:")
        for cat_type, count in type_count.items():
            print(f"    {cat_type}: {count}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

if __name__ == "__main__":
    show_category_links()
