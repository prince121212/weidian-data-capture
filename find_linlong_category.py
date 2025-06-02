#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找釉中青花玲珑分类信息
"""

import pandas as pd

def find_linlong_category():
    """查找釉中青花玲珑分类"""
    try:
        df = pd.read_excel('data/shop_categories_with_links.xlsx', sheet_name='分类汇总')
        
        # 查找包含'釉中青花玲珑'的分类
        target_categories = df[df['分类名称'].str.contains('釉中青花玲珑', na=False)]
        
        if len(target_categories) > 0:
            print("找到釉中青花玲珑分类:")
            for i, row in target_categories.iterrows():
                print(f'分类名称: {row["分类名称"]}')
                print(f'分类ID: {row["分类ID"]}')
                print(f'完整路径: {row["完整分类路径"]}')
                print(f'商品数量: {row["商品数量"]}')
                return row["分类ID"], row["分类名称"]
        else:
            print('未找到"釉中青花玲珑"分类，显示所有包含"玲珑"的分类:')
            linlong_categories = df[df['分类名称'].str.contains('玲珑', na=False)]
            
            if len(linlong_categories) > 0:
                for i, row in linlong_categories.iterrows():
                    print(f'{i+1}. {row["分类名称"]} (ID: {row["分类ID"]}, 商品数: {row["商品数量"]})')
                    print(f'   完整路径: {row["完整分类路径"]}')
                    print()
                
                # 返回第一个玲珑相关分类
                first_row = linlong_categories.iloc[0]
                return first_row["分类ID"], first_row["分类名称"]
            else:
                print('未找到任何包含"玲珑"的分类')
                return None, None
                
    except Exception as e:
        print(f'读取文件失败: {e}')
        return None, None

if __name__ == "__main__":
    cate_id, cate_name = find_linlong_category()
    if cate_id:
        print(f"\n将使用分类: {cate_name} (ID: {cate_id})")
    else:
        print("未找到目标分类")
