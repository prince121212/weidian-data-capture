#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建最终的分类商品对应表
按照用户要求的格式：分类名称 | 商品数量 | 主要商品ID
"""

import xlrd
import xlwt
import os

def read_analysis_results(filename):
    """读取分析结果数据"""
    categories_data = []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)  # 分类商品分析表
        
        print(f"读取文件: {filename}")
        print(f"工作表名称: {workbook.sheet_names()[0]}")
        print(f"总行数: {sheet.nrows}")
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        print(f"表头: {headers}")
        
        # 找到关键列
        name_col = -1
        count_col = -1
        ids_col = -1
        
        for i, header in enumerate(headers):
            if '分类名称' in str(header):
                name_col = i
            elif '分析得到数量' in str(header) or '实际商品数量' in str(header):
                count_col = i
            elif '商品ID列表' in str(header):
                ids_col = i
        
        print(f"列索引: 分类名称={name_col}, 商品数量={count_col}, 商品ID={ids_col}")
        
        # 读取数据
        for row in range(1, sheet.nrows):
            category_name = str(sheet.cell_value(row, name_col)) if name_col >= 0 else ""
            product_count = int(sheet.cell_value(row, count_col)) if count_col >= 0 and sheet.cell_value(row, count_col) else 0
            product_ids = str(sheet.cell_value(row, ids_col)) if ids_col >= 0 else ""
            
            if category_name and product_count > 0:
                categories_data.append({
                    "分类名称": category_name,
                    "商品数量": product_count,
                    "商品ID列表": product_ids,
                    "主要商品ID": product_ids  # 完整的ID列表作为主要商品ID
                })
        
        print(f"成功读取 {len(categories_data)} 个分类数据")
        return categories_data
        
    except Exception as e:
        print(f"读取分析结果失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_final_table(categories_data, output_file):
    """创建最终的分类商品对应表"""
    try:
        # 创建工作簿
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('分类商品对应表')
        
        # 设置表头
        headers = ["分类名称", "商品数量", "主要商品ID"]
        
        # 写入表头
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 按商品数量排序（从多到少）
        sorted_categories = sorted(categories_data, key=lambda x: x["商品数量"], reverse=True)
        
        # 写入数据
        for row, category in enumerate(sorted_categories, 1):
            sheet.write(row, 0, category["分类名称"])
            sheet.write(row, 1, category["商品数量"])
            sheet.write(row, 2, category["主要商品ID"])
        
        # 保存文件
        workbook.save(output_file)
        print(f"✅ 最终分类表已保存到: {output_file}")
        
        # 显示统计信息
        print(f"\n📊 数据统计:")
        print(f"  总分类数: {len(sorted_categories)}")
        print(f"  总商品数: {sum(cat['商品数量'] for cat in sorted_categories)}")
        
        # 显示前10个分类
        print(f"\n🏆 商品数量最多的前10个分类:")
        for i, category in enumerate(sorted_categories[:10], 1):
            ids_preview = category["主要商品ID"][:50] + "..." if len(category["主要商品ID"]) > 50 else category["主要商品ID"]
            print(f"  {i:2d}. {category['分类名称']}: {category['商品数量']}个商品")
            print(f"      商品ID: {ids_preview}")
        
        # 特别显示重点分类
        print(f"\n🎯 重点分类:")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for category in sorted_categories:
            for keyword in target_keywords:
                if keyword in category["分类名称"]:
                    print(f"  ✅ {category['分类名称']}: {category['商品数量']}个商品")
                    print(f"      商品ID: {category['主要商品ID']}")
                    break
        
        return True
        
    except Exception as e:
        print(f"❌ 创建最终表格失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    input_file = "data/products_categories_analysis.xls"
    output_file = "data/final_category_product_table.xls"
    
    print("=== 创建最终分类商品对应表 ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        print("请先运行商品分类分析脚本")
        return
    
    # 读取分析结果
    categories_data = read_analysis_results(input_file)
    
    if not categories_data:
        print("❌ 未能读取到分类数据")
        return
    
    # 创建最终表格
    success = create_final_table(categories_data, output_file)
    
    if success:
        print(f"\n🎉 完成！")
        print(f"📁 最终文件位置: {output_file}")
        print(f"📋 文件格式: 分类名称 | 商品数量 | 主要商品ID")
        print(f"📊 数据已按商品数量从多到少排序")
    else:
        print(f"\n❌ 创建失败")

if __name__ == "__main__":
    main()
