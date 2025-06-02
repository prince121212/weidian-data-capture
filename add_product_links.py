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

def build_product_link_mapping(reference_df):
    """从参考文件构建商品ID到商品详情页链接的映射"""
    product_link_mapping = {}
    
    print("开始构建商品链接映射...")
    
    for index, row in reference_df.iterrows():
        product_id = str(row.get('商品ID', '')).strip()
        
        # 尝试多个可能的链接列名
        product_link = None
        link_columns = ['商品详情页链接', '商品链接', 'itemUrl', 'url', 'URL', '链接']
        
        for col in link_columns:
            if col in reference_df.columns and pd.notna(row.get(col)):
                product_link = row.get(col)
                break
        
        if product_id and product_link:
            product_link_mapping[product_id] = product_link
    
    print(f"构建完成，共映射 {len(product_link_mapping)} 个商品ID到商品链接")
    return product_link_mapping

def add_product_links(target_df, product_link_mapping):
    """为目标文件添加商品详情页链接"""
    print("开始添加商品详情页链接...")
    
    # 确保有商品详情页链接列
    if '商品详情页链接' not in target_df.columns:
        target_df['商品详情页链接'] = ''
    
    added_count = 0
    total_count = len(target_df)
    
    for index, row in target_df.iterrows():
        product_id = str(row.get('商品ID', '')).strip()
        
        if product_id and product_id in product_link_mapping:
            target_df.at[index, '商品详情页链接'] = product_link_mapping[product_id]
            added_count += 1
        
        # 显示进度
        if (index + 1) % 100 == 0:
            print(f"已处理 {index + 1}/{total_count} 条记录，已添加 {added_count} 个链接")
    
    print(f"商品链接添加完成！共为 {added_count}/{total_count} 个商品添加了详情页链接")
    return added_count

def main():
    """主函数"""
    print("=== 商品详情页链接补充工具 ===")
    
    # 文件路径
    reference_file = "data/items_all.xlsx"  # 参考文件（包含商品详情页链接）
    target_file = "data/全部商品_with_categories_fixed.xlsx"  # 需要补充链接的目标文件
    output_file = "data/全部商品_complete.xlsx"  # 输出文件
    
    # 检查文件是否存在
    if not os.path.exists(reference_file):
        print(f"错误：参考文件不存在 - {reference_file}")
        return
    
    if not os.path.exists(target_file):
        print(f"错误：目标文件不存在 - {target_file}")
        return
    
    print(f"参考文件: {reference_file}")
    print(f"目标文件: {target_file}")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    
    # 读取参考文件（包含商品详情页链接）
    print("\n1. 读取参考文件（包含商品详情页链接）...")
    reference_df = read_excel_file(reference_file)
    if reference_df is None:
        return
    
    print(f"参考文件列名: {list(reference_df.columns)}")
    
    # 读取目标文件（需要补充链接的文件）
    print("\n2. 读取目标文件（需要补充链接的文件）...")
    target_df = read_excel_file(target_file)
    if target_df is None:
        return
    
    print(f"目标文件列名: {list(target_df.columns)}")
    
    # 构建商品链接映射
    print("\n3. 构建商品链接映射...")
    product_link_mapping = build_product_link_mapping(reference_df)
    
    if not product_link_mapping:
        print("错误：未能构建商品链接映射")
        return
    
    # 显示映射示例
    print(f"\n商品链接映射示例（前5个）:")
    for i, (product_id, link) in enumerate(list(product_link_mapping.items())[:5]):
        print(f"  商品ID {product_id}:")
        print(f"    链接: {link}")
    
    # 添加商品详情页链接
    print("\n4. 添加商品详情页链接...")
    added_count = add_product_links(target_df, product_link_mapping)
    
    # 显示添加结果统计
    print("\n5. 添加结果统计:")
    print(f"  总商品数: {len(target_df)}")
    print(f"  已添加链接: {added_count}")
    print(f"  添加率: {added_count/len(target_df)*100:.1f}%")
    
    # 检查链接完整性
    empty_links = target_df[target_df['商品详情页链接'].isna() | (target_df['商品详情页链接'] == '')]
    print(f"  无链接商品: {len(empty_links)} 个")
    
    if len(empty_links) == 0:
        print(f"  ✅ 所有商品都有详情页链接")
    
    # 保存结果
    print(f"\n6. 保存结果到 {output_file}...")
    success = save_to_xlsx(target_df, output_file)
    
    if success:
        print(f"\n✅ 任务完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理结果:")
        print(f"  - 总商品数: {len(target_df)}")
        print(f"  - 已添加链接: {added_count}")
        print(f"  - 添加率: {added_count/len(target_df)*100:.1f}%")
        
        # 显示最终文件结构
        print(f"\n📋 最终文件包含的列:")
        for i, col in enumerate(target_df.columns, 1):
            print(f"  {i}. {col}")
        
        # 显示示例
        print(f"\n🎯 完整信息示例 (前5个商品):")
        for i, row in target_df.head(5).iterrows():
            product_id = row.get('商品ID', 'N/A')
            product_title = row.get('商品标题', 'N/A')
            price = row.get('价格', 'N/A')
            category = row.get('分类', 'N/A')
            full_path = row.get('完整分类路径', 'N/A')
            product_link = row.get('商品详情页链接', 'N/A')
            
            print(f"  {i+1}. 商品ID: {product_id}")
            print(f"     商品标题: {product_title}")
            print(f"     价格: {price}")
            print(f"     分类: {category}")
            print(f"     完整路径: {full_path}")
            print(f"     详情页链接: {product_link}")
            print()
    else:
        print(f"\n❌ 保存文件失败")

if __name__ == "__main__":
    main()
