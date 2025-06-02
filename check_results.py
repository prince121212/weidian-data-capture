#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查爬取结果的脚本
"""

import xlrd
import os

def check_excel_file(filename):
    """检查Excel文件内容"""
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return
    
    try:
        # 打开工作簿
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        print(f"=== 文件: {filename} ===")
        print(f"总行数: {sheet.nrows}")
        print(f"总列数: {sheet.ncols}")
        
        # 读取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        print(f"列名: {headers}")
        
        # 找到关键列的索引
        name_col = -1
        category_col = -1
        price_col = -1
        
        for i, header in enumerate(headers):
            if '商品名称' in str(header):
                name_col = i
            elif '商品分类' in str(header):
                category_col = i
            elif '价格' in str(header):
                price_col = i
        
        print(f"\n关键列索引:")
        print(f"  商品名称: {name_col}")
        print(f"  商品分类: {category_col}")
        print(f"  价格: {price_col}")
        
        # 统计分类
        if category_col >= 0:
            categories = {}
            for row in range(1, sheet.nrows):
                category = sheet.cell_value(row, category_col)
                if category:
                    categories[category] = categories.get(category, 0) + 1
            
            print(f"\n分类统计:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count} 个商品")
        
        # 显示前10行数据示例
        print(f"\n前10行数据示例:")
        for row in range(1, min(11, sheet.nrows)):
            name = sheet.cell_value(row, name_col) if name_col >= 0 else "N/A"
            category = sheet.cell_value(row, category_col) if category_col >= 0 else "N/A"
            price = sheet.cell_value(row, price_col) if price_col >= 0 else "N/A"
            print(f"  {row}. {name[:30]}... | {category} | {price}")
        
        return True
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False

def main():
    print("=== 微店数据爬取结果检查 ===\n")
    
    # 检查各个文件
    files_to_check = [
        "data/items_all_new.xls",
        "data/items_all_new_with_categories.xls"
    ]
    
    for filename in files_to_check:
        check_excel_file(filename)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
