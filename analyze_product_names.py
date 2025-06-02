#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析商品名称模式，寻找可能的分类规律
"""

import xlrd
import re
from collections import defaultdict

def analyze_product_names(filename):
    """分析商品名称，寻找模式"""
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        name_col = next((i for i, h in enumerate(headers) if '商品名称' in str(h)), -1)
        
        if name_col == -1:
            print("未找到商品名称列")
            return
        
        print(f"=== 商品名称分析 ===")
        print(f"总商品数: {sheet.nrows - 1}")
        print("\n=== 所有商品名称 ===")
        
        # 收集所有商品名称
        product_names = []
        for row in range(1, sheet.nrows):
            name = str(sheet.cell_value(row, name_col)).strip()
            if name:
                product_names.append(name)
                print(f"{row:3d}. {name}")
        
        print(f"\n=== 名称模式分析 ===")
        
        # 分析包含特定关键词的商品
        keywords = {
            "高温": [],
            "白玉": [],
            "青花": [],
            "釉中": [],
            "精品": [],
            "至尊": [],
            "玲珑": [],
            "餐具": []
        }
        
        for i, name in enumerate(product_names, 1):
            for keyword in keywords:
                if keyword in name:
                    keywords[keyword].append((i, name))
        
        for keyword, matches in keywords.items():
            print(f"\n包含'{keyword}'的商品 ({len(matches)}个):")
            for row, name in matches:
                print(f"  {row:3d}. {name}")
        
        # 寻找可能的系列产品
        print(f"\n=== 可能的系列产品 ===")
        
        # 按前缀分组
        prefixes = defaultdict(list)
        for i, name in enumerate(product_names, 1):
            # 提取可能的系列前缀
            if "头" in name:
                # 提取"XX头"后面的部分作为系列名
                match = re.search(r'\d+头\s*(.+)', name)
                if match:
                    series = match.group(1).strip()
                    prefixes[series].append((i, name))
            elif len(name) > 10:
                # 对于长名称，取前10个字符作为可能的系列
                prefix = name[:10]
                prefixes[prefix].append((i, name))
        
        # 显示有多个商品的系列
        for prefix, items in prefixes.items():
            if len(items) > 1:
                print(f"\n系列: {prefix} ({len(items)}个商品)")
                for row, name in items:
                    print(f"  {row:3d}. {name}")
        
        return product_names
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    filename = "data/items_all_new.xls"
    analyze_product_names(filename)

if __name__ == "__main__":
    main()
