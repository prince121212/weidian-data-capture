#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有分类商品汇总文件
"""

import pandas as pd

def verify_all_products():
    """验证所有分类商品汇总文件"""
    try:
        # 读取主数据表
        df = pd.read_excel('data/所有分类商品汇总.xlsx', sheet_name='所有分类商品汇总')
        print(f'✅ 文件读取成功! 总行数: {len(df)}')
        
        # 显示表头
        print(f'\n📋 表头信息:')
        for i, col in enumerate(df.columns):
            print(f'  {i+1}. {col}')
        
        # 显示前5个分类的详细信息
        print(f'\n🎯 前5个分类的详细信息:')
        for i, row in df.head(5).iterrows():
            print(f'\n{i+1}. 【{row["分类名称"]}】')
            print(f'   分类ID: {row["分类ID"]}')
            print(f'   预期商品数量: {row["预期商品数量"]}')
            print(f'   实际商品数量: {row["实际商品数量"]}')
            
            # 解析商品名称列表并显示前3个
            try:
                product_names = eval(row["商品名称列表"])
                if product_names:
                    print(f'   商品示例: {", ".join(product_names[:3])}')
                    if len(product_names) > 3:
                        print(f'   ... 还有 {len(product_names) - 3} 个商品')
                else:
                    print(f'   商品示例: 无商品')
            except:
                print(f'   商品示例: 解析失败')
        
        # 读取统计表
        try:
            stats_df = pd.read_excel('data/所有分类商品汇总.xlsx', sheet_name='统计信息')
            print(f'\n📊 统计信息:')
            for i, row in stats_df.head(10).iterrows():
                if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                    print(f'  {row.iloc[0]}: {row.iloc[1]}')
        except Exception as e:
            print(f'统计表读取失败: {e}')
        
        # 计算一些额外统计
        total_expected = df['预期商品数量'].sum()
        total_actual = df['实际商品数量'].sum()
        success_rate = (total_actual / total_expected * 100) if total_expected > 0 else 0
        
        print(f'\n📈 汇总统计:')
        print(f'  总分类数: {len(df)}')
        print(f'  预期商品总数: {total_expected}')
        print(f'  实际商品总数: {total_actual}')
        print(f'  获取成功率: {success_rate:.1f}%')
        
        # 找出商品数量最多的分类
        max_products_row = df.loc[df['实际商品数量'].idxmax()]
        print(f'  商品最多的分类: {max_products_row["分类名称"]} ({max_products_row["实际商品数量"]}个商品)')
        
        # 找出无商品的分类
        no_products = df[df['实际商品数量'] == 0]
        if len(no_products) > 0:
            print(f'  无商品的分类: {len(no_products)}个')
            for _, row in no_products.iterrows():
                print(f'    - {row["分类名称"]} (ID: {row["分类ID"]})')
        else:
            print(f'  无商品的分类: 0个 (所有分类都有商品)')
        
    except Exception as e:
        print(f'❌ 读取文件失败: {e}')

if __name__ == "__main__":
    verify_all_products()
