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

def build_category_path_mapping(shop_categories_df):
    """从shop_categories构建分类名称到完整路径的映射"""
    category_path_mapping = {}
    
    print("开始构建分类路径映射...")
    
    for index, row in shop_categories_df.iterrows():
        category_name = row.get('分类名称', '')
        category_path = row.get('完整分类路径', '')
        category_id = row.get('分类ID', '')
        
        if category_name and category_path:
            category_path_mapping[category_name] = category_path
            print(f"映射: {category_name} -> {category_path}")
    
    print(f"构建完成，共映射 {len(category_path_mapping)} 个分类到完整路径")
    return category_path_mapping

def add_category_paths(items_df, category_path_mapping):
    """为商品数据添加完整分类路径"""
    print("开始添加完整分类路径...")
    
    # 确保有完整分类路径列
    if '完整分类路径' not in items_df.columns:
        items_df['完整分类路径'] = ''
    
    added_count = 0
    total_count = len(items_df)
    
    for index, row in items_df.iterrows():
        category = row.get('分类', '')
        
        if category and category in category_path_mapping:
            items_df.at[index, '完整分类路径'] = category_path_mapping[category]
            added_count += 1
        elif category:
            # 如果没有找到映射，就使用分类名称本身作为路径
            items_df.at[index, '完整分类路径'] = category
            added_count += 1
        
        # 显示进度
        if (index + 1) % 100 == 0:
            print(f"已处理 {index + 1}/{total_count} 条记录，已添加 {added_count} 个路径")
    
    print(f"完整分类路径添加完成！共为 {added_count}/{total_count} 个商品添加了路径信息")
    return added_count

def main():
    """主函数"""
    print("=== 添加完整分类路径工具 ===")
    
    # 文件路径
    shop_categories_file = "data/shop_categories.xlsx"
    items_file = "data/items_all_with_categories.xlsx"
    output_file = "data/items_all_with_full_paths.xlsx"
    
    # 检查文件是否存在
    if not os.path.exists(shop_categories_file):
        print(f"错误：分类文件不存在 - {shop_categories_file}")
        return
    
    if not os.path.exists(items_file):
        print(f"错误：商品文件不存在 - {items_file}")
        return
    
    print(f"分类文件: {shop_categories_file}")
    print(f"商品文件: {items_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)
    
    # 读取分类文件
    print("\n1. 读取分类文件...")
    shop_categories_df = read_excel_file(shop_categories_file)
    if shop_categories_df is None:
        return
    
    print(f"分类文件列名: {list(shop_categories_df.columns)}")
    
    # 读取商品文件
    print("\n2. 读取商品文件...")
    items_df = read_excel_file(items_file)
    if items_df is None:
        return
    
    print(f"商品文件列名: {list(items_df.columns)}")
    
    # 构建分类路径映射
    print("\n3. 构建分类路径映射...")
    category_path_mapping = build_category_path_mapping(shop_categories_df)
    
    if not category_path_mapping:
        print("错误：未能构建分类路径映射")
        return
    
    # 显示映射示例
    print(f"\n分类路径映射示例（前5个）:")
    for i, (category, path) in enumerate(list(category_path_mapping.items())[:5]):
        print(f"  {category} -> {path}")
    
    # 添加完整分类路径
    print("\n4. 添加完整分类路径...")
    added_count = add_category_paths(items_df, category_path_mapping)
    
    # 显示路径统计
    print("\n5. 完整分类路径统计:")
    path_counts = items_df['完整分类路径'].value_counts()
    print(f"总共有 {len(path_counts)} 个不同的完整路径")
    for path, count in path_counts.head(10).items():
        if path:  # 排除空路径
            print(f"  {path}: {count} 个商品")
    
    empty_path_count = len(items_df[items_df['完整分类路径'] == ''])
    print(f"  无路径商品: {empty_path_count} 个")
    
    # 保存结果
    print(f"\n6. 保存结果到 {output_file}...")
    success = save_to_xlsx(items_df, output_file)
    
    if success:
        print(f"\n✅ 任务完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理结果:")
        print(f"  - 总商品数: {len(items_df)}")
        print(f"  - 已添加路径: {added_count}")
        print(f"  - 添加率: {added_count/len(items_df)*100:.1f}%")
        
        # 显示示例
        print(f"\n🎯 完整路径示例 (前5个商品):")
        for i, row in items_df.head(5).iterrows():
            product_name = row.get('商品名称', 'N/A')
            category = row.get('分类', 'N/A')
            full_path = row.get('完整分类路径', 'N/A')
            print(f"  {i+1}. {product_name}")
            print(f"     分类: {category}")
            print(f"     完整路径: {full_path}")
            print()
    else:
        print(f"\n❌ 保存文件失败")

if __name__ == "__main__":
    main()
