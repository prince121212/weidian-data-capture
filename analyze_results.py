#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析获取的分类商品结果
"""

import xlrd

def analyze_results():
    """分析结果文件"""
    filename = "data/all_category_products.xls"
    
    try:
        workbook = xlrd.open_workbook(filename)
        
        # 分析商品详情表
        detail_sheet = workbook.sheet_by_name('商品详情')
        print("=== 商品详情表分析 ===")
        print(f"总行数: {detail_sheet.nrows}")
        print(f"总列数: {detail_sheet.ncols}")
        
        # 获取表头
        headers = [detail_sheet.cell_value(0, col) for col in range(detail_sheet.ncols)]
        print(f"表头: {headers}")
        
        # 显示前5个商品
        print(f"\n前5个商品:")
        for row in range(1, min(6, detail_sheet.nrows)):
            product_id = detail_sheet.cell_value(row, 0)
            product_name = detail_sheet.cell_value(row, 1)
            product_price = detail_sheet.cell_value(row, 2)
            category_name = detail_sheet.cell_value(row, 6)
            print(f"  {row}. ID: {product_id}, 名称: {product_name}, 价格: {product_price}, 分类: {category_name}")
        
        # 分析分类汇总表
        summary_sheet = workbook.sheet_by_name('分类汇总')
        print(f"\n=== 分类汇总表分析 ===")
        print(f"总行数: {summary_sheet.nrows}")
        print(f"总列数: {summary_sheet.ncols}")
        
        # 获取表头
        summary_headers = [summary_sheet.cell_value(0, col) for col in range(summary_sheet.ncols)]
        print(f"表头: {summary_headers}")
        
        # 统计匹配状态
        status_count = {}
        total_expected = 0
        total_actual = 0
        
        print(f"\n分类详情:")
        for row in range(1, summary_sheet.nrows):
            category_id = summary_sheet.cell_value(row, 0)
            category_name = summary_sheet.cell_value(row, 1)
            full_path = summary_sheet.cell_value(row, 2)
            expected = int(summary_sheet.cell_value(row, 3))
            actual = int(summary_sheet.cell_value(row, 4))
            status = summary_sheet.cell_value(row, 5)
            
            total_expected += expected
            total_actual += actual
            status_count[status] = status_count.get(status, 0) + 1
            
            print(f"  {category_name}: {actual}/{expected} ({status})")
        
        print(f"\n=== 总体统计 ===")
        print(f"总分类数: {summary_sheet.nrows - 1}")
        print(f"预期商品总数: {total_expected}")
        print(f"实际商品总数: {total_actual}")
        print(f"差异: {total_actual - total_expected}")
        
        print(f"\n匹配状态统计:")
        for status, count in status_count.items():
            print(f"  {status}: {count}个分类")
        
        # 查找重点分类
        print(f"\n=== 重点分类分析 ===")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "高温白玉瓷餐具"]
        
        for row in range(1, summary_sheet.nrows):
            category_name = summary_sheet.cell_value(row, 1)
            full_path = summary_sheet.cell_value(row, 2)
            expected = int(summary_sheet.cell_value(row, 3))
            actual = int(summary_sheet.cell_value(row, 4))
            
            for keyword in target_keywords:
                if keyword in category_name or keyword in full_path:
                    print(f"  ✅ {full_path}: {actual}/{expected}")
                    break
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 分类商品结果分析 ===")
    success = analyze_results()
    
    if success:
        print(f"\n🎉 分析完成！")
    else:
        print(f"\n❌ 分析失败")
