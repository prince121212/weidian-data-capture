#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证分类删除结果
"""

import pandas as pd

def verify_deletion():
    """验证分类删除结果"""
    
    # 要删除的分类ID列表
    delete_ids = [
        "124372511", "113657275", "135496663", "135496594", 
        "113791987", "113703833", "125170448", "115710964", "115026831"
    ]
    
    print("🔍 验证分类删除结果")
    print("=" * 50)
    
    try:
        # 读取原文件和过滤后文件
        df_original = pd.read_excel('data/shop_categories_with_links_backup.xlsx', sheet_name='分类汇总')
        df_filtered = pd.read_excel('data/shop_categories_with_links_filtered.xlsx', sheet_name='分类汇总')
        
        print(f"📊 原文件行数: {len(df_original)}")
        print(f"📊 过滤后行数: {len(df_filtered)}")
        print(f"📊 删除行数: {len(df_original) - len(df_filtered)}")
        
        # 检查删除的分类ID是否还存在
        print(f"\n🎯 检查删除的分类ID是否还存在:")
        remaining_delete_ids = []
        
        for delete_id in delete_ids:
            exists_in_filtered = delete_id in df_filtered['分类ID'].astype(str).values
            if exists_in_filtered:
                remaining_delete_ids.append(delete_id)
                print(f"  ❌ {delete_id} 仍然存在")
            else:
                print(f"  ✅ {delete_id} 已删除")
        
        if remaining_delete_ids:
            print(f"\n⚠️ 警告: 以下分类ID未被删除: {remaining_delete_ids}")
        else:
            print(f"\n✅ 所有指定的分类ID都已成功删除")
        
        # 显示剩余的主要分类
        print(f"\n📋 剩余的主要分类 (层级=1):")
        main_categories = df_filtered[df_filtered['层级'] == 1]
        
        for i, row in main_categories.iterrows():
            print(f"  - {row['分类名称']} (ID: {row['分类ID']}, 商品数: {row['商品数量']})")
        
        print(f"\n📊 剩余分类统计:")
        print(f"  一级分类: {len(main_categories)}个")
        print(f"  二级分类: {len(df_filtered[df_filtered['层级'] == 2])}个")
        print(f"  总分类: {len(df_filtered)}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    verify_deletion()
