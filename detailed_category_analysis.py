#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分类分析工具 - 提取更细致的子分类信息
根据用户需求，从商品名称中提取详细的子分类，如'高温白玉瓷餐具-釉中青花'等
"""

import xlrd
import xlwt
import re
import os
from collections import defaultdict

def extract_detailed_subcategory(product_name):
    """从商品名称中提取详细的子分类"""
    if not product_name:
        return "未分类"
    
    name = str(product_name).strip()
    
    # 1. 如果商品名称本身就很具体，直接作为子分类
    if len(name) <= 50:  # 名称不太长的情况
        return name
    
    # 2. 提取关键特征组合
    features = []
    
    # 材质特征
    materials = ['高温白玉瓷', '骨瓷', '陶瓷', '景德镇瓷', '白瓷', '青瓷', '玲珑瓷']
    for material in materials:
        if material in name:
            features.append(material)
            break
    
    # 工艺特征
    crafts = ['釉中青花', '釉下彩', '手绘', '描金', '金边', '银边', '镶金', '贴花']
    for craft in crafts:
        if craft in name:
            features.append(craft)
    
    # 图案特征
    patterns = ['青花', '牡丹', '荷花', '梅花', '竹子', '龙凤', '花鸟', '山水', '几何']
    for pattern in patterns:
        if pattern in name:
            features.append(pattern)
    
    # 套装规格
    head_match = re.search(r'(\d+)头', name)
    if head_match:
        features.append(f"{head_match.group(1)}头")
    
    # 产品类型
    types = ['餐具', '茶具', '碗', '盘', '杯', '壶', '碟', '勺', '筷']
    for ptype in types:
        if ptype in name:
            features.append(ptype)
            break
    
    # 组合特征生成子分类
    if features:
        subcategory = '-'.join(features)
        return subcategory
    
    # 如果没有提取到特征，返回原名称的前30个字符
    return name[:30] + ('...' if len(name) > 30 else '')

def analyze_and_group_products(input_file, output_file):
    """分析商品并按详细子分类分组"""
    try:
        # 读取数据
        workbook = xlrd.open_workbook(input_file)
        sheet = workbook.sheet_by_index(0)
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 找到关键列
        name_col = -1
        id_col = -1
        price_col = -1
        category_col = -1
        
        for i, header in enumerate(headers):
            if '商品名称' in str(header):
                name_col = i
            elif '商品ID' in str(header):
                id_col = i
            elif '价格' in str(header):
                price_col = i
            elif '商品分类' in str(header):
                category_col = i
        
        print(f"读取到 {sheet.nrows-1} 条商品数据")
        
        # 按子分类分组
        subcategory_groups = defaultdict(list)
        
        for row in range(1, sheet.nrows):
            product_name = sheet.cell_value(row, name_col) if name_col >= 0 else ""
            product_id = sheet.cell_value(row, id_col) if id_col >= 0 else ""
            price = sheet.cell_value(row, price_col) if price_col >= 0 else ""
            category = sheet.cell_value(row, category_col) if category_col >= 0 else ""
            
            # 提取详细子分类
            subcategory = extract_detailed_subcategory(product_name)
            
            # 添加到分组
            subcategory_groups[subcategory].append({
                'product_id': product_id,
                'product_name': product_name,
                'price': price,
                'category': category,
                'subcategory': subcategory
            })
        
        # 创建输出工作簿
        output_workbook = xlwt.Workbook()
        
        # 创建汇总表
        summary_sheet = output_workbook.add_sheet('分类汇总')
        summary_headers = ['子分类名称', '商品数量', '商品ID列表']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header)
        
        # 创建详细表
        detail_sheet = output_workbook.add_sheet('详细分类')
        detail_headers = ['商品ID', '商品名称', '价格', '原分类', '详细子分类']
        for col, header in enumerate(detail_headers):
            detail_sheet.write(0, col, header)
        
        # 填充数据
        summary_row = 1
        detail_row = 1
        
        # 按商品数量排序
        sorted_subcategories = sorted(subcategory_groups.items(), 
                                    key=lambda x: len(x[1]), reverse=True)
        
        print(f"\n找到 {len(sorted_subcategories)} 个详细子分类:")
        
        for subcategory, products in sorted_subcategories:
            # 汇总表
            product_ids = [str(p['product_id']) for p in products]
            summary_sheet.write(summary_row, 0, subcategory)
            summary_sheet.write(summary_row, 1, len(products))
            summary_sheet.write(summary_row, 2, ', '.join(product_ids[:10]) + 
                              ('...' if len(product_ids) > 10 else ''))
            summary_row += 1
            
            # 详细表
            for product in products:
                detail_sheet.write(detail_row, 0, str(product['product_id']))
                detail_sheet.write(detail_row, 1, str(product['product_name']))
                detail_sheet.write(detail_row, 2, str(product['price']))
                detail_sheet.write(detail_row, 3, str(product['category']))
                detail_sheet.write(detail_row, 4, str(product['subcategory']))
                detail_row += 1
            
            # 打印统计信息
            print(f"  {subcategory}: {len(products)} 个商品")
        
        # 保存文件
        output_workbook.save(output_file)
        print(f"\n✅ 详细分类分析完成！")
        print(f"结果已保存到: {output_file}")
        print(f"包含 {len(sorted_subcategories)} 个子分类，{detail_row-1} 个商品")
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    input_file = "data/items_all_new_with_categories.xls"
    output_file = "data/detailed_subcategory_analysis.xls"
    
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        print("请先运行商品爬取和分类脚本")
        return
    
    print("=== 详细子分类分析工具 ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    success = analyze_and_group_products(input_file, output_file)
    
    if success:
        print(f"\n📊 分析结果:")
        print(f"1. 汇总表: 显示每个子分类的商品数量")
        print(f"2. 详细表: 显示每个商品的详细分类信息")
        print(f"\n💡 提示: 可以根据子分类名称进一步筛选和分析商品")

if __name__ == "__main__":
    main()
