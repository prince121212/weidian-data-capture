import pandas as pd
import xlrd
import xlwt
import os
import re
from collections import defaultdict

def read_excel_file(file_path):
    """读取Excel文件，支持xls和xlsx格式"""
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, engine='xlrd')
        print(f"成功读取文件 {file_path}，共 {len(df)} 行数据")
        return df
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
        return None

def save_to_xlsx(df, output_file):
    """保存DataFrame到xlsx文件"""
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"成功保存 {len(df)} 条数据到 {output_file}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False

def extract_product_id_from_url(url):
    """从商品URL中提取商品ID"""
    if not url or not isinstance(url, str):
        return None
    
    # 匹配itemID参数
    match = re.search(r'itemID=([^&]+)', url)
    if match:
        return match.group(1)
    
    # 匹配item/数字格式
    match = re.search(r'/item/(\d+)', url)
    if match:
        return match.group(1)
    
    return None

def build_category_mapping(category_df):
    """从分类汇总文件构建商品ID到分类的映射"""
    category_mapping = {}

    print("开始构建分类映射...")
    print(f"分类汇总文件的列名: {list(category_df.columns)}")

    # 显示前几行数据以便调试
    print("\n前3行数据:")
    for i in range(min(3, len(category_df))):
        print(f"第{i+1}行: {dict(category_df.iloc[i])}")

    for index, row in category_df.iterrows():
        category_name = row.get('分类名称', '')

        # 尝试多个可能的商品ID列名
        product_ids_str = None
        for col_name in ['商品ID[]', '商品ID列表', '商品ID', 'itemIds', 'product_ids']:
            if col_name in category_df.columns:
                product_ids_str = row.get(col_name, '')
                if product_ids_str:
                    print(f"使用列 '{col_name}' 获取商品ID")
                    break

        if not category_name or not product_ids_str:
            print(f"第{index+1}行跳过: 分类名称='{category_name}', 商品ID='{product_ids_str}'")
            continue

        # 解析商品ID列表
        try:
            # 移除方括号并分割
            if isinstance(product_ids_str, str):
                # 处理不同格式的商品ID列表
                product_ids_str = product_ids_str.strip()

                # 如果是列表格式 [id1, id2, id3]
                if product_ids_str.startswith('[') and product_ids_str.endswith(']'):
                    product_ids_str = product_ids_str.strip('[]')

                if product_ids_str:
                    # 按逗号分割，并清理每个ID
                    product_ids = [pid.strip().strip("'\"") for pid in product_ids_str.split(',')]

                    for product_id in product_ids:
                        if product_id and product_id != 'nan':
                            category_mapping[product_id] = category_name

                    print(f"第{index+1}行: 分类'{category_name}' 添加了 {len([p for p in product_ids if p and p != 'nan'])} 个商品ID")
        except Exception as e:
            print(f"解析第 {index+1} 行的商品ID列表时出错: {e}")
            continue

    print(f"构建完成，共映射 {len(category_mapping)} 个商品ID到分类")
    return category_mapping

def fill_categories_in_items(items_df, category_mapping):
    """为商品数据填充分类信息"""
    print("开始填充分类信息...")
    
    # 确保有分类列
    if '分类' not in items_df.columns:
        items_df['分类'] = ''
    
    filled_count = 0
    total_count = len(items_df)
    
    for index, row in items_df.iterrows():
        # 尝试从多个可能的列获取商品ID
        product_id = None
        
        # 首先尝试直接的商品ID列
        for id_col in ['商品ID', 'itemId', 'id', 'ID']:
            if id_col in items_df.columns and pd.notna(row.get(id_col)):
                product_id = str(row[id_col]).strip()
                break
        
        # 如果没有直接的ID，尝试从URL中提取
        if not product_id:
            for url_col in ['商品详情页链接', '商品链接', 'url', 'URL', '链接']:
                if url_col in items_df.columns and pd.notna(row.get(url_col)):
                    product_id = extract_product_id_from_url(row[url_col])
                    if product_id:
                        break
        
        # 如果找到了商品ID且在分类映射中存在
        if product_id and product_id in category_mapping:
            items_df.at[index, '分类'] = category_mapping[product_id]
            filled_count += 1
        
        # 显示进度
        if (index + 1) % 100 == 0:
            print(f"已处理 {index + 1}/{total_count} 条记录，已填充 {filled_count} 个分类")
    
    print(f"分类填充完成！共填充 {filled_count}/{total_count} 个商品的分类信息")
    return filled_count

def main():
    """主函数"""
    print("=== 商品分类信息填充工具 ===")
    
    # 文件路径
    category_file = "data/所有分类商品汇总.xlsx"
    items_file = "data/items_all.xlsx"
    output_file = "data/items_all_with_categories.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(category_file):
        print(f"错误：分类汇总文件不存在 - {category_file}")
        return
    
    if not os.path.exists(items_file):
        print(f"错误：商品文件不存在 - {items_file}")
        return
    
    print(f"分类汇总文件: {category_file}")
    print(f"商品文件: {items_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 读取分类汇总文件
    print("\n1. 读取分类汇总文件...")
    category_df = read_excel_file(category_file)
    if category_df is None:
        return
    
    print(f"分类汇总文件列名: {list(category_df.columns)}")
    
    # 读取商品文件
    print("\n2. 读取商品文件...")
    items_df = read_excel_file(items_file)
    if items_df is None:
        return
    
    print(f"商品文件列名: {list(items_df.columns)}")
    
    # 构建分类映射
    print("\n3. 构建分类映射...")
    category_mapping = build_category_mapping(category_df)
    
    if not category_mapping:
        print("错误：未能构建分类映射，请检查分类汇总文件格式")
        return
    
    # 显示分类映射示例
    print(f"\n分类映射示例（前5个）:")
    for i, (product_id, category) in enumerate(list(category_mapping.items())[:5]):
        print(f"  商品ID {product_id} -> 分类 {category}")
    
    # 填充分类信息
    print("\n4. 填充分类信息...")
    filled_count = fill_categories_in_items(items_df, category_mapping)
    
    # 显示分类统计
    print("\n5. 分类统计:")
    category_counts = items_df['分类'].value_counts()
    print(f"总共有 {len(category_counts)} 个不同的分类")
    for category, count in category_counts.head(10).items():
        if category:  # 排除空分类
            print(f"  {category}: {count} 个商品")
    
    empty_category_count = len(items_df[items_df['分类'] == ''])
    print(f"  未分类商品: {empty_category_count} 个")
    
    # 保存结果
    print(f"\n6. 保存结果到 {output_file}...")
    success = save_to_xlsx(items_df, output_file)
    
    if success:
        print(f"\n✅ 任务完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理结果:")
        print(f"  - 总商品数: {len(items_df)}")
        print(f"  - 已填充分类: {filled_count}")
        print(f"  - 填充率: {filled_count/len(items_df)*100:.1f}%")
    else:
        print(f"\n❌ 保存文件失败")

if __name__ == "__main__":
    main()
