import pandas as pd

def verify_categories():
    """验证分类填充结果"""
    print("=== 分类填充结果验证 ===")
    
    # 读取结果文件
    try:
        df = pd.read_excel("data/items_all_with_categories.xlsx", engine='openpyxl')
        print(f"✅ 成功读取结果文件，共 {len(df)} 条记录")
    except Exception as e:
        print(f"❌ 读取结果文件失败: {e}")
        return
    
    # 检查分类列
    if '分类' not in df.columns:
        print("❌ 结果文件中没有找到'分类'列")
        return
    
    print(f"✅ 找到分类列")
    
    # 统计分类信息
    print(f"\n📊 分类统计:")
    category_counts = df['分类'].value_counts()
    print(f"总共有 {len(category_counts)} 个不同的分类")
    
    # 显示所有分类及其商品数量
    for category, count in category_counts.items():
        print(f"  {category}: {count} 个商品")
    
    # 检查是否有未分类的商品
    empty_categories = df[df['分类'].isna() | (df['分类'] == '')]
    if len(empty_categories) > 0:
        print(f"\n⚠️  有 {len(empty_categories)} 个商品未分类")
    else:
        print(f"\n✅ 所有商品都已分类")
    
    # 显示一些示例
    print(f"\n🎯 分类示例 (前10个商品):")
    for i, row in df.head(10).iterrows():
        product_name = row.get('商品名称', 'N/A')
        category = row.get('分类', 'N/A')
        product_id = row.get('商品ID', 'N/A')
        print(f"  {i+1}. {product_name} -> {category} (ID: {product_id})")
    
    print(f"\n✅ 验证完成！")

if __name__ == "__main__":
    verify_categories()
