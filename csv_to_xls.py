#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将CSV文件转换为XLS格式
"""

import csv
import xlwt

def csv_to_xls(csv_file, xls_file):
    """将CSV文件转换为XLS格式"""
    try:
        # 创建工作簿
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('分类商品对应表')
        
        # 读取CSV文件
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row_idx, row in enumerate(reader):
                for col_idx, cell in enumerate(row):
                    sheet.write(row_idx, col_idx, cell)
        
        # 保存XLS文件
        workbook.save(xls_file)
        print(f"✅ 成功转换: {csv_file} -> {xls_file}")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

if __name__ == "__main__":
    csv_file = "data/final_category_product_table.csv"
    xls_file = "data/final_category_product_table.xls"
    
    print("=== CSV转XLS ===")
    success = csv_to_xls(csv_file, xls_file)
    
    if success:
        print("🎉 转换完成！")
        print(f"📁 XLS文件位置: {xls_file}")
        print("📋 格式: 分类名称 | 商品数量 | 主要商品ID")
    else:
        print("❌ 转换失败")
