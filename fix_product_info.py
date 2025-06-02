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

def build_product_info_mapping(reference_df):
    """从参考文件构建商品ID到商品信息的映射"""
    product_info_mapping = {}
    
    print("开始构建商品信息映射...")
    
    for index, row in reference_df.iterrows():
        product_id = str(row.get('商品ID', '')).strip()
        product_name = row.get('商品名称', '')
        price = row.get('价格', '')
        
        if product_id:
            product_info_mapping[product_id] = {
                '商品名称': product_name,
                '价格': price
            }
    
    print(f"构建完成，共映射 {len(product_info_mapping)} 个商品ID到商品信息")
    return product_info_mapping

def fix_product_info(target_df, product_info_mapping):
    """修正目标文件中的商品标题和价格"""
    print("开始修正商品标题和价格...")
    
    fixed_count = 0
    total_count = len(target_df)
    
    # 记录修正前后的对比
    changes_log = []
    
    for index, row in target_df.iterrows():
        product_id = str(row.get('商品ID', '')).strip()
        
        if product_id and product_id in product_info_mapping:
            # 获取正确的商品信息
            correct_info = product_info_mapping[product_id]
            
            # 记录修正前的信息
            old_title = row.get('商品标题', '')
            old_price = row.get('价格', '')
            
            # 修正商品标题
            if '商品标题' in target_df.columns:
                target_df.at[index, '商品标题'] = correct_info['商品名称']
            
            # 修正价格
            if '价格' in target_df.columns:
                target_df.at[index, '价格'] = correct_info['价格']
            
            # 记录变更
            if old_title != correct_info['商品名称'] or old_price != correct_info['价格']:
                changes_log.append({
                    '商品ID': product_id,
                    '原标题': old_title,
                    '新标题': correct_info['商品名称'],
                    '原价格': old_price,
                    '新价格': correct_info['价格']
                })
            
            fixed_count += 1
        
        # 显示进度
        if (index + 1) % 100 == 0:
            print(f"已处理 {index + 1}/{total_count} 条记录，已修正 {fixed_count} 个商品")
    
    print(f"商品信息修正完成！共修正 {fixed_count}/{total_count} 个商品的信息")
    
    # 显示部分变更记录
    if changes_log:
        print(f"\n📝 修正记录示例（前5个变更）:")
        for i, change in enumerate(changes_log[:5], 1):
            print(f"  {i}. 商品ID: {change['商品ID']}")
            if change['原标题'] != change['新标题']:
                print(f"     标题: {change['原标题']} -> {change['新标题']}")
            if change['原价格'] != change['新价格']:
                print(f"     价格: {change['原价格']} -> {change['新价格']}")
            print()
    
    return fixed_count, len(changes_log)

def main():
    """主函数"""
    print("=== 商品信息修正工具 ===")
    
    # 文件路径
    reference_file = "data/items_all_with_full_paths.xlsx"  # 参考文件（正确的商品名称和价格）
    target_file = "data/全部商品_with_categories.xlsx"  # 需要修正的目标文件
    output_file = "data/全部商品_with_categories_fixed.xlsx"  # 输出文件
    
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
    
    # 读取参考文件（包含正确的商品信息）
    print("\n1. 读取参考文件（包含正确的商品信息）...")
    reference_df = read_excel_file(reference_file)
    if reference_df is None:
        return
    
    print(f"参考文件列名: {list(reference_df.columns)}")
    
    # 读取目标文件（需要修正的文件）
    print("\n2. 读取目标文件（需要修正的文件）...")
    target_df = read_excel_file(target_file)
    if target_df is None:
        return
    
    print(f"目标文件列名: {list(target_df.columns)}")
    
    # 构建商品信息映射
    print("\n3. 构建商品信息映射...")
    product_info_mapping = build_product_info_mapping(reference_df)
    
    if not product_info_mapping:
        print("错误：未能构建商品信息映射")
        return
    
    # 显示映射示例
    print(f"\n商品信息映射示例（前5个）:")
    for i, (product_id, info) in enumerate(list(product_info_mapping.items())[:5]):
        print(f"  商品ID {product_id}:")
        print(f"    商品名称: {info['商品名称']}")
        print(f"    价格: {info['价格']}")
    
    # 修正商品信息
    print("\n4. 修正商品信息...")
    fixed_count, changes_count = fix_product_info(target_df, product_info_mapping)
    
    # 显示修正后的统计
    print("\n5. 修正结果统计:")
    print(f"  总商品数: {len(target_df)}")
    print(f"  已修正商品: {fixed_count}")
    print(f"  实际变更: {changes_count}")
    print(f"  修正率: {fixed_count/len(target_df)*100:.1f}%")
    
    # 保存结果
    print(f"\n6. 保存结果到 {output_file}...")
    success = save_to_xlsx(target_df, output_file)
    
    if success:
        print(f"\n✅ 任务完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理结果:")
        print(f"  - 总商品数: {len(target_df)}")
        print(f"  - 已修正商品: {fixed_count}")
        print(f"  - 实际变更数: {changes_count}")
        
        # 显示修正后的示例
        print(f"\n🎯 修正后示例 (前5个商品):")
        for i, row in target_df.head(5).iterrows():
            product_id = row.get('商品ID', 'N/A')
            product_title = row.get('商品标题', 'N/A')
            price = row.get('价格', 'N/A')
            category = row.get('分类', 'N/A')
            full_path = row.get('完整分类路径', 'N/A')
            
            print(f"  {i+1}. 商品ID: {product_id}")
            print(f"     商品标题: {product_title}")
            print(f"     价格: {price}")
            print(f"     分类: {category}")
            print(f"     完整路径: {full_path}")
            print()
    else:
        print(f"\n❌ 保存文件失败")

if __name__ == "__main__":
    main()
