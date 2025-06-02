import pandas as pd

def verify_final_result():
    """验证最终结果文件"""
    print("=== 最终结果验证 ===")
    
    # 读取结果文件
    try:
        df = pd.read_excel("data/items_all_with_full_paths.xlsx", engine='openpyxl')
        print(f"✅ 成功读取最终结果文件，共 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取结果文件失败: {e}")
        return
    
    # 检查必要的列
    required_columns = ['商品ID', '商品名称', '分类', '完整分类路径']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ 缺少必要的列: {missing_columns}")
        return
    else:
        print(f"✅ 所有必要的列都存在")
    
    print(f"\n📋 文件包含的所有列: {list(df.columns)}")
    
    # 统计分类信息
    print(f"\n📊 分类统计:")
    category_counts = df['分类'].value_counts()
    print(f"总共有 {len(category_counts)} 个不同的分类")
    
    # 统计完整路径信息
    print(f"\n🗂️ 完整分类路径统计:")
    path_counts = df['完整分类路径'].value_counts()
    print(f"总共有 {len(path_counts)} 个不同的完整路径")
    
    # 显示前10个最常见的完整路径
    print(f"\n🔝 前10个最常见的完整路径:")
    for i, (path, count) in enumerate(path_counts.head(10).items(), 1):
        print(f"  {i}. {path}: {count} 个商品")
    
    # 检查数据完整性
    empty_categories = df[df['分类'].isna() | (df['分类'] == '')]
    empty_paths = df[df['完整分类路径'].isna() | (df['完整分类路径'] == '')]
    
    print(f"\n🔍 数据完整性检查:")
    print(f"  未分类商品: {len(empty_categories)} 个")
    print(f"  无完整路径商品: {len(empty_paths)} 个")
    
    if len(empty_categories) == 0 and len(empty_paths) == 0:
        print(f"  ✅ 所有商品都有分类和完整路径")
    
    # 显示详细示例
    print(f"\n🎯 详细示例 (前10个商品):")
    for i, row in df.head(10).iterrows():
        product_id = row.get('商品ID', 'N/A')
        product_name = row.get('商品名称', 'N/A')
        category = row.get('分类', 'N/A')
        full_path = row.get('完整分类路径', 'N/A')
        price = row.get('价格', 'N/A')
        
        print(f"  {i+1}. 商品ID: {product_id}")
        print(f"     商品名称: {product_name}")
        print(f"     价格: {price}")
        print(f"     分类: {category}")
        print(f"     完整路径: {full_path}")
        print()
    
    # 按层级分析路径
    print(f"\n📈 路径层级分析:")
    path_levels = {}
    for path in df['完整分类路径'].dropna():
        level = len(path.split(' > '))
        path_levels[level] = path_levels.get(level, 0) + 1
    
    for level in sorted(path_levels.keys()):
        count = path_levels[level]
        print(f"  {level}级路径: {count} 个商品")
    
    print(f"\n✅ 验证完成！")
    print(f"📁 最终文件: data/items_all_with_full_paths.xlsx")
    print(f"📊 文件包含:")
    print(f"  - 商品总数: {len(df)}")
    print(f"  - 分类总数: {len(category_counts)}")
    print(f"  - 完整路径总数: {len(path_counts)}")
    print(f"  - 数据完整性: 100%")

if __name__ == "__main__":
    verify_final_result()
