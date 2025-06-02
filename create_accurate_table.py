#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于准确数据创建分类商品对应表
根据all_categories.xls中的准确商品数量
"""

import xlrd
import xlwt

def read_accurate_categories():
    """读取准确的分类数据"""
    try:
        workbook = xlrd.open_workbook('data/all_categories.xls')
        sheet = workbook.sheet_by_index(0)
        
        print("=== 读取准确的分类数据 ===")
        print(f"总行数: {sheet.nrows}")
        
        categories = []
        
        # 读取数据
        for row in range(1, sheet.nrows):
            try:
                category_id = str(sheet.cell_value(row, 0)) if sheet.cell_value(row, 0) else ""
                category_name = str(sheet.cell_value(row, 1)) if sheet.cell_value(row, 1) else ""
                full_path = str(sheet.cell_value(row, 2)) if sheet.cell_value(row, 2) else ""
                level = int(sheet.cell_value(row, 3)) if sheet.cell_value(row, 3) else 0
                parent = str(sheet.cell_value(row, 4)) if sheet.cell_value(row, 4) else ""
                count = int(sheet.cell_value(row, 5)) if sheet.cell_value(row, 5) else 0
                
                if count > 0:  # 只保留有商品的分类
                    categories.append({
                        "分类ID": category_id,
                        "分类名称": category_name,
                        "完整分类路径": full_path,
                        "层级": level,
                        "父分类": parent,
                        "商品数量": count
                    })
                    print(f"  {full_path}: {count}个商品")
            except:
                continue
        
        print(f"\n总共读取到 {len(categories)} 个有商品的分类")
        return categories
        
    except Exception as e:
        print(f"读取失败: {e}")
        return []

def create_accurate_table(categories):
    """创建准确的分类表格"""
    try:
        # 创建工作簿
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('准确的分类商品对应表')
        
        # 写入表头
        headers = ["分类名称", "商品数量", "主要商品ID"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 按商品数量排序
        sorted_categories = sorted(categories, key=lambda x: x["商品数量"], reverse=True)
        
        # 写入数据
        for row, category in enumerate(sorted_categories, 1):
            sheet.write(row, 0, category["完整分类路径"])
            sheet.write(row, 1, category["商品数量"])
            
            # 对于重点分类，添加说明
            full_path = category["完整分类路径"]
            count = category["商品数量"]
            category_id = category["分类ID"]
            
            if "釉中青花" in full_path and "玲珑" not in full_path:
                sheet.write(row, 2, f"需要API获取{count}个商品ID (包含7257502545和7257580227)")
            elif "精品青花" in full_path:
                sheet.write(row, 2, f"需要API获取{count}个商品ID")
            elif "至尊青花" in full_path:
                sheet.write(row, 2, f"需要API获取{count}个商品ID")
            elif "釉中青花玲珑" in full_path:
                sheet.write(row, 2, f"需要API获取{count}个商品ID")
            else:
                sheet.write(row, 2, f"需要API获取{count}个商品ID (分类ID: {category_id})")
        
        # 保存文件
        output_file = "data/accurate_category_table.xls"
        workbook.save(output_file)
        
        print(f"\n✅ 准确的分类表已保存到: {output_file}")
        
        # 显示重点分类
        print(f"\n🎯 重点分类 (基于all_categories.xls的准确数据):")
        target_keywords = ["釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        
        for category in sorted_categories:
            full_path = category["完整分类路径"]
            count = category["商品数量"]
            category_id = category["分类ID"]
            
            for keyword in target_keywords:
                if keyword in full_path:
                    print(f"  ✅ {full_path}: {count}个商品 (分类ID: {category_id})")
                    if "釉中青花" in full_path and "玲珑" not in full_path:
                        print(f"      📝 此分类应包含商品ID: 7257502545 和 7257580227")
                    break
        
        # 显示前10个分类
        print(f"\n📊 商品数量最多的前10个分类:")
        for i, category in enumerate(sorted_categories[:10], 1):
            print(f"  {i:2d}. {category['完整分类路径']}: {category['商品数量']}个商品")
        
        return True
        
    except Exception as e:
        print(f"创建表格失败: {e}")
        return False

def main():
    print("=== 基于准确数据创建分类商品对应表 ===")
    print("数据来源: all_categories.xls (准确的商品数量)")
    print("=" * 60)
    
    # 读取准确的分类数据
    categories = read_accurate_categories()
    
    if not categories:
        print("❌ 未能读取到分类数据")
        return
    
    # 创建准确的表格
    success = create_accurate_table(categories)
    
    if success:
        print(f"\n🎉 完成！")
        print(f"📁 文件位置: data/accurate_category_table.xls")
        print(f"📋 格式: 分类名称 | 商品数量 | 主要商品ID")
        print(f"📊 数据来源: all_categories.xls (100%准确)")
        print(f"⚠️ 商品ID列需要通过API获取 (网络问题暂时无法获取)")
        
        print(f"\n💡 下一步:")
        print("1. 当网络稳定后，可以运行API脚本获取具体的商品ID")
        print("2. 目前的表格包含了准确的分类名称和商品数量")
        print("3. 特别标注了您关注的重点分类")
    else:
        print(f"\n❌ 创建失败")

if __name__ == "__main__":
    main()
