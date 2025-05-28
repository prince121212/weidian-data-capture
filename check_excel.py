import pandas as pd
import sys

def check_updated_excel(excel_file="data/items_all_updated.xls"):
    """检查更新后的Excel文件"""
    try:
        df = pd.read_excel(excel_file)
        print("\n【更新后的Excel文件结构】")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        print("\n【第一行数据（更新后）】")
        if len(df) > 0:
            first_row = df.iloc[0]
            for col, value in first_row.items():
                if isinstance(value, str) and len(value) > 100:
                    # 截断过长的字符串以便于显示
                    print(f"{col}: {value[:100]}...")
                else:
                    print(f"{col}: {value}")
        
        # 检查新增的列
        new_columns = ["商品标题", "价格", "销量", "详细描述", "图片数量", "图片链接"]
        print("\n【新增列检查】")
        for col in new_columns:
            if col in df.columns:
                print(f"{col}: 已添加")
            else:
                print(f"{col}: 未添加")
        
        return df
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

if __name__ == "__main__":
    # 默认文件路径
    excel_file = "data/items_all_updated.xls"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    
    check_updated_excel(excel_file) 