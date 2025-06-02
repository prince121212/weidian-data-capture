import pandas as pd

def check_shop_categories():
    """检查shop_categories.xlsx文件的结构"""
    print("=== 检查shop_categories.xlsx文件结构 ===")
    
    try:
        # 读取文件
        df = pd.read_excel("data/shop_categories.xlsx", engine='openpyxl')
        print(f"✅ 成功读取文件，共 {len(df)} 行数据")
        
        # 显示列名
        print(f"\n📋 列名: {list(df.columns)}")
        
        # 显示前几行数据
        print(f"\n📊 前5行数据:")
        for i, row in df.head().iterrows():
            print(f"第{i+1}行: {dict(row)}")
        
        # 检查是否有分类路径相关的列
        path_columns = [col for col in df.columns if '路径' in col or 'path' in col.lower() or '分类' in col]
        if path_columns:
            print(f"\n🎯 找到可能的分类路径列: {path_columns}")
        
        # 检查是否有分类ID或名称列
        id_columns = [col for col in df.columns if 'id' in col.lower() or 'ID' in col or '编号' in col]
        name_columns = [col for col in df.columns if '名称' in col or 'name' in col.lower() or '标题' in col]
        
        if id_columns:
            print(f"🔢 找到可能的ID列: {id_columns}")
        if name_columns:
            print(f"📝 找到可能的名称列: {name_columns}")
        
        return df
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

if __name__ == "__main__":
    check_shop_categories()
