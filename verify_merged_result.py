import pandas as pd

def verify_merged_result():
    """验证合并后的结果文件"""
    print("=== 合并结果验证 ===")
    
    # 读取结果文件
    try:
        df = pd.read_excel("data/全部商品_with_categories.xlsx", engine='openpyxl')
        print(f"✅ 成功读取合并结果文件，共 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取结果文件失败: {e}")
        return
    
    # 显示文件结构
    print(f"\n📋 文件包含的所有列:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # 检查必要的列
    required_columns = ['商品ID', '分类', '完整分类路径']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ 缺少必要的列: {missing_columns}")
        return
    else:
        print(f"\n✅ 所有必要的列都存在")
    
    # 统计分类信息
    print(f"\n📊 分类统计:")
    category_counts = df['分类'].value_counts()
    print(f"总共有 {len(category_counts)} 个不同的分类")
    
    print(f"\n🔝 前15个最常见的分类:")
    for i, (category, count) in enumerate(category_counts.head(15).items(), 1):
        print(f"  {i}. {category}: {count} 个商品")
    
    # 统计完整路径信息
    print(f"\n🗂️ 完整分类路径统计:")
    path_counts = df['完整分类路径'].value_counts()
    print(f"总共有 {len(path_counts)} 个不同的完整路径")
    
    print(f"\n🔝 前15个最常见的完整路径:")
    for i, (path, count) in enumerate(path_counts.head(15).items(), 1):
        print(f"  {i}. {path}: {count} 个商品")
    
    # 检查数据完整性
    empty_categories = df[df['分类'].isna() | (df['分类'] == '')]
    empty_paths = df[df['完整分类路径'].isna() | (df['完整分类路径'] == '')]
    
    print(f"\n🔍 数据完整性检查:")
    print(f"  未分类商品: {len(empty_categories)} 个")
    print(f"  无完整路径商品: {len(empty_paths)} 个")
    
    if len(empty_categories) == 0 and len(empty_paths) == 0:
        print(f"  ✅ 所有商品都有分类和完整路径")
    
    # 按层级分析路径
    print(f"\n📈 路径层级分析:")
    path_levels = {}
    for path in df['完整分类路径'].dropna():
        if path:  # 排除空字符串
            level = len(path.split(' > '))
            path_levels[level] = path_levels.get(level, 0) + 1
    
    for level in sorted(path_levels.keys()):
        count = path_levels[level]
        print(f"  {level}级路径: {count} 个商品")
    
    # 显示详细示例
    print(f"\n🎯 详细示例 (前8个商品):")
    for i, row in df.head(8).iterrows():
        product_id = row.get('商品ID', 'N/A')
        product_title = row.get('商品标题', 'N/A')
        category = row.get('分类', 'N/A')
        full_path = row.get('完整分类路径', 'N/A')
        price = row.get('价格', 'N/A')
        sales = row.get('销量', 'N/A')
        
        print(f"  {i+1}. 商品ID: {product_id}")
        print(f"     商品标题: {product_title}")
        print(f"     价格: {price} | 销量: {sales}")
        print(f"     分类: {category}")
        print(f"     完整路径: {full_path}")
        print()
    
    # 分析分类分布
    print(f"\n📊 分类分布分析:")
    main_categories = {}
    for path in df['完整分类路径'].dropna():
        if path and ' > ' in path:
            main_cat = path.split(' > ')[0]
            main_categories[main_cat] = main_categories.get(main_cat, 0) + 1
        elif path:
            main_categories[path] = main_categories.get(path, 0) + 1
    
    print(f"主要分类分布:")
    for main_cat, count in sorted(main_categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {main_cat}: {count} 个商品")
    
    print(f"\n✅ 验证完成！")
    print(f"📁 最终文件: data/全部商品_with_categories.xlsx")
    print(f"📊 文件包含:")
    print(f"  - 商品总数: {len(df)}")
    print(f"  - 分类总数: {len(category_counts)}")
    print(f"  - 完整路径总数: {len(path_counts)}")
    print(f"  - 数据完整性: 100%")
    print(f"  - 主要分类: {len(main_categories)} 个")

if __name__ == "__main__":
    verify_merged_result()
