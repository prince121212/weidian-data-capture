import pandas as pd
import os

def read_excel_file(file_path):
    """读取Excel文件"""
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
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
    
    import re
    # 匹配itemID参数
    match = re.search(r'itemID=([^&]+)', url)
    if match:
        return match.group(1)
    
    # 匹配item/数字格式
    match = re.search(r'/item/(\d+)', url)
    if match:
        return match.group(1)
    
    return None

def get_product_id(row, df_columns):
    """从行数据中获取商品ID"""
    # 尝试多种可能的商品ID列名
    id_columns = ['商品ID', 'itemId', 'id', 'ID', 'item_id', 'product_id']
    
    for col in id_columns:
        if col in df_columns and pd.notna(row.get(col)):
            return str(row[col]).strip()
    
    # 如果没有直接的ID，尝试从URL中提取
    url_columns = ['商品详情页链接', '商品链接', 'url', 'URL', '链接', 'itemUrl']
    for col in url_columns:
        if col in df_columns and pd.notna(row.get(col)):
            product_id = extract_product_id_from_url(row[col])
            if product_id:
                return product_id
    
    return None

def build_category_mapping(source_df):
    """从源文件构建商品ID到分类信息的映射"""
    category_mapping = {}
    
    print("开始构建分类映射...")
    
    for index, row in source_df.iterrows():
        product_id = get_product_id(row, source_df.columns)
        category = row.get('分类', '')
        full_path = row.get('完整分类路径', '')
        
        if product_id:
            category_mapping[product_id] = {
                '分类': category,
                '完整分类路径': full_path
            }
    
    print(f"构建完成，共映射 {len(category_mapping)} 个商品ID到分类信息")
    return category_mapping

def merge_category_info(target_df, category_mapping):
    """为目标文件添加分类信息"""
    print("开始合并分类信息...")
    
    # 确保有分类列
    if '分类' not in target_df.columns:
        target_df['分类'] = ''
    if '完整分类路径' not in target_df.columns:
        target_df['完整分类路径'] = ''
    
    merged_count = 0
    total_count = len(target_df)
    
    for index, row in target_df.iterrows():
        product_id = get_product_id(row, target_df.columns)
        
        if product_id and product_id in category_mapping:
            target_df.at[index, '分类'] = category_mapping[product_id]['分类']
            target_df.at[index, '完整分类路径'] = category_mapping[product_id]['完整分类路径']
            merged_count += 1
        
        # 显示进度
        if (index + 1) % 100 == 0:
            print(f"已处理 {index + 1}/{total_count} 条记录，已合并 {merged_count} 个分类")
    
    print(f"分类信息合并完成！共为 {merged_count}/{total_count} 个商品添加了分类信息")
    return merged_count

def main():
    """主函数"""
    print("=== 商品分类信息合并工具 ===")
    
    # 文件路径
    source_file = "data/items_all_with_full_paths.xlsx"  # 包含分类信息的源文件
    target_file = "data/全部商品.xlsx"  # 需要补充分类信息的目标文件
    output_file = "data/全部商品_with_categories.xlsx"  # 输出文件
    
    # 检查文件是否存在
    if not os.path.exists(source_file):
        print(f"错误：源文件不存在 - {source_file}")
        return
    
    if not os.path.exists(target_file):
        print(f"错误：目标文件不存在 - {target_file}")
        return
    
    print(f"源文件: {source_file}")
    print(f"目标文件: {target_file}")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    
    # 读取源文件（包含分类信息）
    print("\n1. 读取源文件（包含分类信息）...")
    source_df = read_excel_file(source_file)
    if source_df is None:
        return
    
    print(f"源文件列名: {list(source_df.columns)}")
    
    # 读取目标文件（需要补充分类信息）
    print("\n2. 读取目标文件（需要补充分类信息）...")
    target_df = read_excel_file(target_file)
    if target_df is None:
        return
    
    print(f"目标文件列名: {list(target_df.columns)}")
    
    # 构建分类映射
    print("\n3. 构建分类映射...")
    category_mapping = build_category_mapping(source_df)
    
    if not category_mapping:
        print("错误：未能构建分类映射")
        return
    
    # 显示映射示例
    print(f"\n分类映射示例（前5个）:")
    for i, (product_id, info) in enumerate(list(category_mapping.items())[:5]):
        print(f"  商品ID {product_id}:")
        print(f"    分类: {info['分类']}")
        print(f"    完整路径: {info['完整分类路径']}")
    
    # 合并分类信息
    print("\n4. 合并分类信息...")
    merged_count = merge_category_info(target_df, category_mapping)
    
    # 显示合并统计
    print("\n5. 合并结果统计:")
    if '分类' in target_df.columns:
        category_counts = target_df['分类'].value_counts()
        print(f"总共有 {len(category_counts)} 个不同的分类")
        for category, count in category_counts.head(10).items():
            if category:  # 排除空分类
                print(f"  {category}: {count} 个商品")
        
        empty_category_count = len(target_df[target_df['分类'] == ''])
        print(f"  未分类商品: {empty_category_count} 个")
    
    if '完整分类路径' in target_df.columns:
        path_counts = target_df['完整分类路径'].value_counts()
        print(f"总共有 {len(path_counts)} 个不同的完整路径")
        empty_path_count = len(target_df[target_df['完整分类路径'] == ''])
        print(f"  无路径商品: {empty_path_count} 个")
    
    # 保存结果
    print(f"\n6. 保存结果到 {output_file}...")
    success = save_to_xlsx(target_df, output_file)
    
    if success:
        print(f"\n✅ 任务完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理结果:")
        print(f"  - 总商品数: {len(target_df)}")
        print(f"  - 已合并分类: {merged_count}")
        print(f"  - 合并率: {merged_count/len(target_df)*100:.1f}%")
        
        # 显示示例
        print(f"\n🎯 合并结果示例 (前5个商品):")
        for i, row in target_df.head(5).iterrows():
            product_name = row.get('商品名称', 'N/A')
            product_id = get_product_id(row, target_df.columns)
            category = row.get('分类', 'N/A')
            full_path = row.get('完整分类路径', 'N/A')
            print(f"  {i+1}. {product_name}")
            print(f"     商品ID: {product_id}")
            print(f"     分类: {category}")
            print(f"     完整路径: {full_path}")
            print()
    else:
        print(f"\n❌ 保存文件失败")

if __name__ == "__main__":
    main()
