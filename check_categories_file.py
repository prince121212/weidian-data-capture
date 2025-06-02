#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查生成的分类文件
"""

import xlrd
import os

def check_categories_file(filename):
    """检查分类文件内容"""
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return
    
    try:
        workbook = xlrd.open_workbook(filename)
        
        print(f"=== 文件: {filename} ===")
        print(f"工作表数量: {workbook.nsheets}")
        
        for sheet_idx in range(workbook.nsheets):
            sheet = workbook.sheet_by_index(sheet_idx)
            sheet_name = workbook.sheet_names()[sheet_idx]
            
            print(f"\n--- 工作表: {sheet_name} ---")
            print(f"行数: {sheet.nrows}")
            print(f"列数: {sheet.ncols}")
            
            if sheet.nrows > 0:
                # 显示表头
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                print(f"列名: {headers}")
                
                # 显示前10行数据
                print(f"\n前10行数据:")
                for row in range(1, min(11, sheet.nrows)):
                    row_data = []
                    for col in range(sheet.ncols):
                        value = sheet.cell_value(row, col)
                        if isinstance(value, str) and len(value) > 30:
                            value = value[:30] + "..."
                        row_data.append(value)
                    print(f"  {row:2d}. {row_data}")
                
                # 查找目标分类
                if "分类名称" in headers:
                    name_col = headers.index("分类名称")
                    target_keywords = ["高温白玉瓷", "精品青花", "至尊青花", "釉中青花"]
                    
                    print(f"\n🎯 目标分类:")
                    found_count = 0
                    for row in range(1, sheet.nrows):
                        category_name = str(sheet.cell_value(row, name_col))
                        for keyword in target_keywords:
                            if keyword in category_name:
                                row_data = [sheet.cell_value(row, col) for col in range(sheet.ncols)]
                                print(f"  ✅ {row_data}")
                                found_count += 1
                                break
                    
                    if found_count == 0:
                        print("  未找到目标分类")
                    else:
                        print(f"  找到 {found_count} 个目标分类")
        
        return True
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False

def main():
    filename = "data/all_categories.xls"
    print("=== 检查分类文件 ===")
    check_categories_file(filename)

if __name__ == "__main__":
    main()
