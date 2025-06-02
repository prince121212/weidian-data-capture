#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于商品名称推断分类的工具
"""

import pandas as pd
import re
import os
import xlrd
import xlwt

def save_to_xls(df, filename):
    """将DataFrame保存为XLS文件"""
    try:
        # 创建工作簿和工作表
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('商品数据')

        # 写入表头
        headers = df.columns.tolist()
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        # 写入数据
        for row, item in enumerate(df.to_dict('records'), 1):
            for col, header in enumerate(headers):
                value = item.get(header, '')
                if pd.isna(value):
                    value = ''
                elif isinstance(value, (str, int, float, bool)):
                    sheet.write(row, col, value)
                else:
                    sheet.write(row, col, str(value))

        # 保存文件
        workbook.save(filename)
        return True

    except Exception as e:
        print(f"保存XLS文件失败: {e}")
        return False

def categorize_by_name(product_name):
    """根据商品名称推断分类"""
    if not product_name or pd.isna(product_name):
        return "未分类"
    
    name = str(product_name).lower()
    
    # 定义分类关键词
    categories = {
        "餐具套装": ["头", "餐具", "套装", "碗", "盘", "碟", "勺", "筷"],
        "茶具": ["茶具", "茶杯", "茶壶", "盖碗", "茶盘", "茶叶", "功夫茶"],
        "瓷器工艺品": ["瓷", "陶", "花瓶", "摆件", "工艺品", "装饰"],
        "餐具单品": ["碗", "盘", "碟", "杯", "勺", "筷子"],
        "厨房用品": ["厨房", "锅", "炒锅", "平底锅", "蒸锅"],
        "家居装饰": ["装饰", "摆设", "家居", "饰品"],
        "礼品套装": ["礼品", "礼盒", "套装", "组合"],
        "青花瓷": ["青花", "青花瓷"],
        "骨瓷": ["骨瓷", "骨质瓷"],
        "景德镇瓷器": ["景德镇", "景瓷"],
        "玲珑瓷": ["玲珑"],
        "手绘瓷器": ["手绘"],
        "金边瓷器": ["金边", "金镶", "金装"],
        "花卉图案": ["花园", "花卉", "牡丹", "荷花", "梅花"],
        "动物图案": ["鱼", "龙", "凤", "鸟"],
        "几何图案": ["格子", "条纹", "几何"]
    }
    
    # 按优先级匹配分类
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in name:
                return category
    
    # 特殊规则：包含"头"的通常是餐具套装
    if re.search(r'\d+头', name):
        return "餐具套装"
    
    # 如果包含"瓷"字，归为瓷器
    if "瓷" in name:
        return "瓷器"
    
    return "其他"

def add_categories_to_excel(input_file, output_file):
    """为Excel文件中的商品添加分类"""
    try:
        # 读取数据
        df = pd.read_excel(input_file)
        print(f"读取到 {len(df)} 条商品数据")
        
        # 确保有商品分类列
        if '商品分类' not in df.columns:
            df['商品分类'] = ''
        
        # 为每个商品推断分类
        updated_count = 0
        for index, row in df.iterrows():
            # 如果已经有分类且不为空，则跳过
            if pd.notna(row['商品分类']) and row['商品分类'] != '':
                continue
                
            product_name = row.get('商品名称', '')
            category = categorize_by_name(product_name)
            df.at[index, '商品分类'] = category
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"已处理 {updated_count} 个商品...")
        
        # 保存结果为xls格式
        save_to_xls(df, output_file)
        print(f"成功为 {updated_count} 个商品添加分类，保存到 {output_file}")
        
        # 打印分类统计
        category_counts = df['商品分类'].value_counts()
        print("\n分类统计:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} 个商品")
        
        return True
        
    except Exception as e:
        print(f"处理失败: {e}")
        return False

def main():
    input_file = "data/items_all_new.xls"
    output_file = "data/items_all_new_with_categories.xls"
    
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        return
    
    print("=== 基于商品名称添加分类信息 ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("=" * 40)
    
    success = add_categories_to_excel(input_file, output_file)
    
    if success:
        print("\n✅ 分类添加完成！")
    else:
        print("\n❌ 分类添加失败！")

if __name__ == "__main__":
    main()
