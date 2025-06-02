#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过商品名称分析商品与分类的对应关系
基于现有的商品数据和分类信息
"""

import xlrd
import xlwt
import re
import os

def read_products_data(filename):
    """读取商品数据"""
    products = []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 找到关键列
        id_col = next((i for i, h in enumerate(headers) if '商品ID' in str(h)), -1)
        name_col = next((i for i, h in enumerate(headers) if '商品名称' in str(h)), -1)
        
        print(f"商品数据列索引: ID={id_col}, 名称={name_col}")
        
        # 读取数据
        for row in range(1, sheet.nrows):
            product_id = str(sheet.cell_value(row, id_col)) if id_col >= 0 else ""
            product_name = str(sheet.cell_value(row, name_col)) if name_col >= 0 else ""
            
            if product_id and product_name:
                products.append({
                    "商品ID": product_id,
                    "商品名称": product_name
                })
        
        print(f"读取到 {len(products)} 个商品")
        return products
        
    except Exception as e:
        print(f"读取商品数据失败: {e}")
        return []

def read_categories_data(filename):
    """读取分类数据"""
    categories = []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 找到关键列
        path_col = next((i for i, h in enumerate(headers) if '完整分类路径' in str(h)), -1)
        count_col = next((i for i, h in enumerate(headers) if '商品数量' in str(h)), -1)
        
        print(f"分类数据列索引: 路径={path_col}, 数量={count_col}")
        
        # 读取数据
        for row in range(1, sheet.nrows):
            path = str(sheet.cell_value(row, path_col)) if path_col >= 0 else ""
            count = int(sheet.cell_value(row, count_col)) if count_col >= 0 and sheet.cell_value(row, count_col) else 0
            
            if path and count > 0:
                categories.append({
                    "完整分类路径": path,
                    "预期商品数量": count
                })
        
        print(f"读取到 {len(categories)} 个有商品的分类")
        return categories
        
    except Exception as e:
        print(f"读取分类数据失败: {e}")
        return []

def classify_product_by_name(product_name, categories):
    """根据商品名称判断所属分类"""
    name = product_name.lower()
    
    # 定义分类关键词映射
    category_keywords = {
        "高温白玉瓷餐具-釉中青花": ["釉中青花", "釉中", "青花"],
        "高温白玉瓷餐具-精品青花": ["精品青花", "精品"],
        "高温白玉瓷餐具-至尊青花": ["至尊青花", "至尊"],
        "高温白玉瓷餐具-釉中青花玲珑": ["青花玲珑", "玲珑青花", "釉中青花玲珑"],
        "高温白玉瓷餐具-玲珑釉上": ["玲珑釉上", "玲珑"],
        "高温白玉瓷餐具-臻品珐琅彩": ["臻品珐琅彩", "珐琅彩", "臻品"],
        "高温白玉瓷餐具-颜色釉": ["颜色釉"],
        "高温白玉瓷餐具-手工镶金": ["手工镶金", "镶金"],
        "高温白玉瓷餐具-粉彩": ["粉彩"],
        "高温白玉瓷餐具-酒杯款": ["酒杯"],
        "高温白玉瓷餐具-22头礼品装": ["22头"],
        "高温白玉瓷餐具-纯色": ["纯色"],
        "骨瓷餐具-经典": ["骨瓷", "经典"],
        "骨瓷餐具-网红爆款": ["网红", "爆款"],
        "骨瓷餐具-手工镶金": ["骨瓷", "镶金"],
        "骨瓷餐具-釉中": ["骨瓷", "釉中"],
        "骨瓷餐具-至尊珐琅彩": ["骨瓷", "珐琅彩"],
        "骨瓷餐具-高档锦盒": ["骨瓷", "锦盒"],
        "骨瓷餐具-欧式": ["骨瓷", "欧式"],
        "骨瓷餐具-22头礼品装": ["骨瓷", "22头"],
        "手绘茶具-玲珑盖碗套装": ["手绘", "玲珑", "盖碗"],
        "手绘茶具-玲珑壶组套装": ["手绘", "玲珑", "壶组"],
        "手绘茶具-工笔写艺盖碗套装": ["工笔", "写艺", "盖碗"],
        "手绘茶具-工笔写意壶组套装": ["工笔", "写意", "壶组"],
        "茶具套装-大套豪华套装": ["茶具", "大套", "豪华"],
        "茶具套装-中套家庭装": ["茶具", "中套", "家庭"],
        "茶具套装-小套功夫装": ["茶具", "小套", "功夫"],
        "茶具套装-杯垫": ["茶具", "杯垫"],
        "办公系列-手绘": ["办公", "手绘"],
        "办公系列-套杯": ["办公", "套杯"],
        "办公系列-盖杯": ["办公", "盖杯"],
        "花瓶-小花瓶": ["花瓶", "小花瓶"],
        "订货参考-寿碗": ["寿碗"],
        "订货参考-酒店前台": ["酒店", "前台"]
    }
    
    # 按优先级匹配（更具体的分类优先）
    best_match = None
    max_score = 0
    
    for category_path in categories:
        category_name = category_path["完整分类路径"]
        keywords = category_keywords.get(category_name, [])
        
        if not keywords:
            # 如果没有预定义关键词，从分类名称中提取
            parts = category_name.split('-')
            if len(parts) > 1:
                keywords = [parts[-1]]  # 使用最后一部分作为关键词
        
        # 计算匹配分数
        score = 0
        for keyword in keywords:
            if keyword.lower() in name:
                score += len(keyword)  # 更长的关键词权重更高
        
        if score > max_score:
            max_score = score
            best_match = category_name
    
    return best_match if max_score > 0 else "高温白玉瓷餐具"  # 默认分类

def analyze_products_categories(products, categories):
    """分析商品与分类的对应关系"""
    print("开始分析商品与分类的对应关系...")
    
    # 创建分类到商品的映射
    category_products = {}
    
    for product in products:
        product_id = product["商品ID"]
        product_name = product["商品名称"]
        
        # 判断商品所属分类
        category = classify_product_by_name(product_name, categories)
        
        if category not in category_products:
            category_products[category] = []
        
        category_products[category].append({
            "商品ID": product_id,
            "商品名称": product_name
        })
    
    return category_products

def save_analysis_results(category_products, categories, filename):
    """保存分析结果"""
    try:
        workbook = xlwt.Workbook()
        
        # 创建汇总表
        summary_sheet = workbook.add_sheet('分类商品分析')
        headers = ["分类名称", "预期商品数量", "分析得到数量", "商品ID列表", "格式化输出"]
        
        for col, header in enumerate(headers):
            summary_sheet.write(0, col, header)
        
        # 创建分类预期数量映射
        expected_counts = {cat["完整分类路径"]: cat["预期商品数量"] for cat in categories}
        
        row = 1
        for category_name, products in category_products.items():
            expected_count = expected_counts.get(category_name, 0)
            actual_count = len(products)
            product_ids = [p["商品ID"] for p in products]
            
            summary_sheet.write(row, 0, category_name)
            summary_sheet.write(row, 1, expected_count)
            summary_sheet.write(row, 2, actual_count)
            summary_sheet.write(row, 3, ', '.join(product_ids))
            
            # 格式化输出
            if product_ids:
                formatted = f"{category_name}分类下有商品id：{' 和 '.join(product_ids)}"
                summary_sheet.write(row, 4, formatted)
            
            row += 1
        
        # 创建详细表
        detail_sheet = workbook.add_sheet('商品详细分析')
        detail_headers = ["商品ID", "商品名称", "分析得到的分类"]
        
        for col, header in enumerate(detail_headers):
            detail_sheet.write(0, col, header)
        
        detail_row = 1
        for category_name, products in category_products.items():
            for product in products:
                detail_sheet.write(detail_row, 0, product["商品ID"])
                detail_sheet.write(detail_row, 1, product["商品名称"])
                detail_sheet.write(detail_row, 2, category_name)
                detail_row += 1
        
        workbook.save(filename)
        print(f"✅ 分析结果已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    products_file = "data/items_all_new.xls"
    categories_file = "data/all_categories.xls"
    output_file = "data/products_categories_analysis.xls"
    
    print("=== 通过商品名称分析分类对应关系 ===")
    print(f"商品数据文件: {products_file}")
    print(f"分类数据文件: {categories_file}")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    
    # 读取数据
    products = read_products_data(products_file)
    categories = read_categories_data(categories_file)
    
    if not products or not categories:
        print("❌ 数据读取失败")
        return
    
    # 分析对应关系
    category_products = analyze_products_categories(products, categories)
    
    # 保存结果
    if save_analysis_results(category_products, categories, output_file):
        print(f"\n🎯 重点分类分析结果:")
        print("=" * 50)
        
        target_categories = [
            "高温白玉瓷餐具-釉中青花",
            "高温白玉瓷餐具-精品青花", 
            "高温白玉瓷餐具-至尊青花",
            "高温白玉瓷餐具-釉中青花玲珑"
        ]
        
        for category in target_categories:
            if category in category_products:
                products = category_products[category]
                product_ids = [p["商品ID"] for p in products]
                if product_ids:
                    print(f"✅ {category}分类下有商品id：{' 和 '.join(product_ids)}")
                else:
                    print(f"❌ {category}: 未找到商品")
            else:
                print(f"❌ {category}: 分类不存在")
    
    else:
        print("❌ 保存结果失败")

if __name__ == "__main__":
    main()
