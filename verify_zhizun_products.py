#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证至尊青花商品文件
"""

import pandas as pd

def verify_zhizun_products():
    """验证至尊青花商品文件"""
    try:
        df = pd.read_excel('data/至尊青花_商品列表_正确API.xlsx', sheet_name='至尊青花_商品列表')
        print(f'✅ 文件读取成功! 总行数: {len(df)}')
        print('\n📋 商品信息:')
        for i, row in df.iterrows():
            print(f'{i+1}. {row["商品名称"]} (ID: {row["商品ID"]}, 价格: ¥{row["价格"]})')
            print(f'   库存: {row["库存"]}')
            print(f'   链接: {row["商品链接"]}')
            print()
        
        # 检查统计表
        stats_df = pd.read_excel('data/至尊青花_商品列表_正确API.xlsx', sheet_name='商品统计')
        print('📊 统计信息:')
        print(stats_df.head(10))
        
    except Exception as e:
        print(f'❌ 读取文件失败: {e}')

if __name__ == "__main__":
    verify_zhizun_products()
