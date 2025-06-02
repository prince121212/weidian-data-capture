#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查包含链接的分类文件
"""

import pandas as pd

def check_categories_file():
    """检查分类文件内容"""
    try:
        # 读取文件
        df = pd.read_excel('data/shop_categories_with_links.xlsx', sheet_name='分类汇总')
        print(f"✅ 文件读取成功! 总行数: {len(df)}")
        
        # 显示表头
        print("\n📋 表头信息:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. {col}")
        
        # 显示前3行数据
        print("\n🎯 前3行数据示例:")
        for i, row in df.head(3).iterrows():
            print(f"\n第{i+1}行:")
            print(f"  分类名称: {row['分类名称']}")
            print(f"  分类ID: {row['分类ID']}")
            
            if 'H5分类链接' in df.columns:
                h5_link = str(row['H5分类链接'])
                if len(h5_link) > 80:
                    print(f"  H5链接: {h5_link[:80]}...")
                else:
                    print(f"  H5链接: {h5_link}")
            
            if 'PC分类链接' in df.columns:
                pc_link = str(row['PC分类链接'])
                if len(pc_link) > 80:
                    print(f"  PC链接: {pc_link[:80]}...")
                else:
                    print(f"  PC链接: {pc_link}")
        
        # 检查链接完整性
        print("\n🔗 链接完整性检查:")
        h5_links_count = df['H5分类链接'].notna().sum() if 'H5分类链接' in df.columns else 0
        pc_links_count = df['PC分类链接'].notna().sum() if 'PC分类链接' in df.columns else 0
        api_links_count = df['API查询链接'].notna().sum() if 'API查询链接' in df.columns else 0
        
        print(f"  H5分类链接: {h5_links_count}/{len(df)} 个")
        print(f"  PC分类链接: {pc_links_count}/{len(df)} 个")
        print(f"  API查询链接: {api_links_count}/{len(df)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

if __name__ == "__main__":
    check_categories_file()
