#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索特定商品的脚本
"""

import xlrd
import os

def search_products(filename, keywords):
    """搜索包含特定关键词的商品"""
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 找到商品名称列
        name_col = -1
        id_col = -1
        for i, header in enumerate(headers):
            if '商品名称' in str(header):
                name_col = i
            elif '商品ID' in str(header):
                id_col = i
        
        if name_col == -1:
            print("未找到商品名称列")
            return []
        
        print(f"搜索关键词: {keywords}")
        print("=" * 60)
        
        found_products = []
        
        for row in range(1, sheet.nrows):
            product_name = str(sheet.cell_value(row, name_col))
            product_id = str(sheet.cell_value(row, id_col)) if id_col >= 0 else f"行{row}"
            
            # 检查是否包含任何关键词
            for keyword in keywords:
                if keyword.lower() in product_name.lower():
                    found_products.append({
                        'id': product_id,
                        'name': product_name,
                        'row': row
                    })
                    print(f"ID: {product_id} | {product_name}")
                    break
        
        print(f"\n找到 {len(found_products)} 个相关商品")
        return found_products
        
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def main():
    filename = "data/items_all_new.xls"
    
    print("=== 搜索特定商品 ===\n")
    
    # 搜索关键词列表
    search_terms = [
        ["高温白玉瓷"],
        ["釉中青花"],
        ["精品青花"],
        ["至尊青花"],
        ["青花玲珑"],
        ["白玉瓷"],
        ["青花"]
    ]
    
    for terms in search_terms:
        search_products(filename, terms)
        print("\n" + "-" * 60 + "\n")
    
    # 显示所有商品名称（前50个）
    print("=== 前50个商品名称示例 ===")
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        name_col = next((i for i, h in enumerate(headers) if '商品名称' in str(h)), -1)
        
        if name_col >= 0:
            for row in range(1, min(51, sheet.nrows)):
                product_name = str(sheet.cell_value(row, name_col))
                print(f"{row:2d}. {product_name}")
    except Exception as e:
        print(f"显示商品列表失败: {e}")

if __name__ == "__main__":
    main()
