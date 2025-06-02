#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确读取all_categories.xls文件的数据
"""

import xlrd
import xlwt

def read_correct_categories():
    """正确读取分类数据"""
    try:
        print("正在读取 all_categories.xls 文件...")
        workbook = xlrd.open_workbook('data/all_categories.xls')
        sheet = workbook.sheet_by_index(0)
        
        print(f"工作表名称: {workbook.sheet_names()[0]}")
        print(f"总行数: {sheet.nrows}")
        print(f"总列数: {sheet.ncols}")
        
        # 读取表头
        headers = []
        for col in range(sheet.ncols):
            header = sheet.cell_value(0, col)
            headers.append(str(header))
        
        print(f"表头: {headers}")
        
        # 读取所有数据
        categories = []
        for row in range(1, sheet.nrows):
            row_data = []
            for col in range(sheet.ncols):
                value = sheet.cell_value(row, col)
                row_data.append(value)
            categories.append(row_data)
        
        print(f"\n=== 所有分类数据 ===")
        print("格式: 分类ID | 分类名称 | 完整分类路径 | 层级 | 父分类 | 商品数量")
        
        # 只显示有商品的分类
        categories_with_products = []
        for i, row_data in enumerate(categories):
            if len(row_data) >= 6:  # 确保有足够的列
                category_id = str(row_data[0]) if row_data[0] else ""
                category_name = str(row_data[1]) if row_data[1] else ""
                full_path = str(row_data[2]) if row_data[2] else ""
                level = int(row_data[3]) if row_data[3] else 0
                parent = str(row_data[4]) if row_data[4] else ""
                count = int(row_data[5]) if row_data[5] else 0
                
                if count > 0:  # 只保留有商品的分类
                    category_info = {
                        "分类ID": category_id,
                        "分类名称": category_name,
                        "完整分类路径": full_path,
                        "层级": level,
                        "父分类": parent,
                        "商品数量": count
                    }
                    categories_with_products.append(category_info)
                    print(f"{category_id} | {category_name} | {full_path} | {level} | {parent} | {count}")
        
        print(f"\n总共有 {len(categories_with_products)} 个分类有商品")
        
        return categories_with_products
        
    except Exception as e:
        print(f"读取失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_correct_table(categories_data):
    """基于正确的分类数据创建表格"""
    if not categories_data:
        print("没有分类数据")
        return False
    
    try:
        # 创建工作簿
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('正确的分类商品对应表')
        
        # 写入表头
        headers = ["分类名称", "商品数量", "主要商品ID"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 按商品数量排序
        sorted_categories = sorted(categories_data, key=lambda x: x["商品数量"], reverse=True)
        
        # 写入数据
        for row, category in enumerate(sorted_categories, 1):
            sheet.write(row, 0, category["完整分类路径"])
            sheet.write(row, 1, category["商品数量"])
            # 商品ID列暂时留空，因为我们没有准确的商品ID数据
            sheet.write(row, 2, f"需要通过API获取{category['商品数量']}个商品ID")
        
        # 保存文件
        output_file = "data/correct_category_table.xls"
        workbook.save(output_file)
        
        print(f"\n✅ 正确的分类表已保存到: {output_file}")
        
        # 显示重点分类
        print(f"\n🎯 重点分类:")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for category in sorted_categories:
            full_path = category["完整分类路径"]
            count = category["商品数量"]
            
            for keyword in target_keywords:
                if keyword in full_path:
                    print(f"  ✅ {full_path}: {count}个商品 (分类ID: {category['分类ID']})")
                    break
        
        return True
        
    except Exception as e:
        print(f"创建表格失败: {e}")
        return False

def main():
    print("=== 读取正确的分类数据 ===")
    
    # 读取正确的分类数据
    categories_data = read_correct_categories()
    
    if categories_data:
        # 创建正确的表格
        create_correct_table(categories_data)
        
        print(f"\n📊 数据摘要:")
        print(f"  - 总分类数: {len(categories_data)}")
        print(f"  - 总商品数: {sum(cat['商品数量'] for cat in categories_data)}")
        
        print(f"\n⚠️ 重要说明:")
        print("由于API网络问题，商品ID列暂时无法填充准确数据")
        print("分类名称和商品数量是准确的，来自all_categories.xls文件")
        print("如需准确的商品ID，需要解决API连接问题")
    else:
        print("❌ 未能读取到分类数据")

if __name__ == "__main__":
    main()
