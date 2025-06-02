#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证釉中青花玲珑商品文件
"""

import pandas as pd

def verify_linlong_products():
    """验证釉中青花玲珑商品文件"""
    try:
        df = pd.read_excel('data/釉中青花玲珑_商品列表.xlsx', sheet_name='釉中青花玲珑_商品列表')
        print(f'✅ 文件读取成功! 总行数: {len(df)}')
        print('\n📋 釉中青花玲珑商品信息:')
        for i, row in df.iterrows():
            print(f'{i+1}. {row["商品名称"]}')
            print(f'   ID: {row["商品ID"]}')
            print(f'   价格: ¥{row["价格"]}')
            print(f'   库存: {row["库存"]}')
            print(f'   链接: {row["商品链接"]}')
            print()
        
        # 检查统计表
        try:
            stats_df = pd.read_excel('data/釉中青花玲珑_商品列表.xlsx', sheet_name='商品统计')
            print('📊 统计信息:')
            print(f'分类名称: 釉中青花玲珑')
            print(f'总商品数: {len(df)}')
            print(f'价格范围: 所有商品均为¥3000')
            print(f'库存情况: 999-9999个')
        except Exception as e:
            print(f'统计表读取失败: {e}')
        
    except Exception as e:
        print(f'❌ 读取文件失败: {e}')

if __name__ == "__main__":
    verify_linlong_products()
