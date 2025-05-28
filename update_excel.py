import pandas as pd
import json
import os
import sys
import argparse
from xlutils.copy import copy
from xlrd import open_workbook

def load_product_details(json_file="product_details.json"):
    """加载爬取到的商品详情"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"读取商品详情失败: {e}")
        return None

def check_excel_structure(excel_file="data/items_all.xls"):
    """检查Excel文件结构"""
    try:
        df = pd.read_excel(excel_file)
        print("\n【Excel文件结构】")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        print("\n【第一行数据示例】")
        if len(df) > 0:
            first_row = df.iloc[0]
            for col, value in first_row.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"{col}: {value[:100]}...")
                else:
                    print(f"{col}: {value}")
        return df
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def update_excel_with_details(excel_file="data/items_all.xls", output_file=None, json_file="product_details.json", row_index=0, interactive=True):
    """更新Excel文件中的指定商品记录
    
    Args:
        excel_file: 要更新的Excel文件路径
        output_file: 输出Excel文件路径，如果为None则自动生成
        json_file: 包含商品详情的JSON文件路径
        row_index: 要更新的行索引（从0开始）
        interactive: 是否交互模式，如果为False则不需要用户确认
    """
    # 设置默认输出文件
    if output_file is None:
        output_file = excel_file.replace('.xls', '_updated.xls')
    
    # 加载商品详情
    product_data = load_product_details(json_file)
    if not product_data:
        return False
    
    details = product_data.get("details", {})
    images = product_data.get("images", [])
    
    # 使用xlrd和xlutils修改Excel文件
    try:
        print(f"正在更新 {excel_file} 的第 {row_index + 1} 行数据...")
        
        # 打开原始工作簿
        rb = open_workbook(excel_file)
        # 创建一个可写的工作簿
        wb = copy(rb)
        # 获取第一个工作表
        sheet = wb.get_sheet(0)
        
        # 读取原始工作簿的第一个工作表
        orig_sheet = rb.sheet_by_index(0)
        # 获取列名
        header_row = orig_sheet.row_values(0)
        
        # 准备新增的列
        new_columns = ["商品标题", "价格", "销量", "详细描述", "图片数量", "图片链接", "商品配置", "提取的配置信息"]
        for col in new_columns:
            if col not in header_row:
                # 新增列
                col_index = len(header_row)
                sheet.write(0, col_index, col)
                header_row.append(col)
                print(f"新增列: {col} (索引: {col_index})")
        
        # 确保有足够的行
        if orig_sheet.nrows <= row_index + 1:
            print(f"错误: Excel文件中没有第 {row_index + 1} 行数据")
            return False
        
        # 更新指定行数据
        # 添加商品详情
        for col_name, value in details.items():
            if col_name in header_row:
                col_index = header_row.index(col_name)
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: {col_name} = {value if not isinstance(value, str) or len(value) < 50 else value[:50] + '...'}")
            elif col_name == "商品标题" and "商品标题" in header_row:
                col_index = header_row.index("商品标题")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 商品标题 = {value}")
            elif col_name == "价格" and "价格" in header_row:
                col_index = header_row.index("价格")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 价格 = {value}")
            elif col_name == "销量" and "销量" in header_row:
                col_index = header_row.index("销量")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 销量 = {value}")
            elif col_name == "详细描述" and "详细描述" in header_row:
                col_index = header_row.index("详细描述")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 详细描述 = {value if len(value) < 50 else value[:50] + '...'}")
            elif col_name == "商品配置" and "商品配置" in header_row:
                col_index = header_row.index("商品配置")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 商品配置 = {value if len(value) < 50 else value[:50] + '...'}")
            elif col_name == "提取的配置信息" and "提取的配置信息" in header_row:
                col_index = header_row.index("提取的配置信息")
                sheet.write(row_index + 1, col_index, value)
                print(f"更新字段: 提取的配置信息 = {value if len(value) < 50 else value[:50] + '...'}")
        
        # 添加图片信息
        if "图片数量" in header_row:
            col_index = header_row.index("图片数量")
            sheet.write(row_index + 1, col_index, len(images))
            print(f"更新字段: 图片数量 = {len(images)}")
        
        if "图片链接" in header_row:
            col_index = header_row.index("图片链接")
            # 仅保存前5个图片链接，避免单元格内容过长
            image_links = ";".join(images[:5])
            sheet.write(row_index + 1, col_index, image_links)
            print(f"更新字段: 图片链接 = {image_links[:50]}...")
        
        # 保存更新后的工作簿
        wb.save(output_file)
        print(f"\n成功更新Excel文件，已保存到: {output_file}")
        
        # 显示文件大小
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"文件大小: {file_size:.2f} KB")
        
        return True
    
    except Exception as e:
        print(f"更新Excel文件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="将商品详情数据添加到Excel文件中的指定行")
    parser.add_argument("--excel", "-e", default="data/items_all.xls", help="要更新的Excel文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出Excel文件路径，默认在原文件名后添加_updated")
    parser.add_argument("--json", "-j", default="product_details.json", help="包含商品详情的JSON文件路径")
    parser.add_argument("--row", "-r", type=int, default=0, help="要更新的行索引（从0开始，0表示第一行数据）")
    parser.add_argument("--check", "-c", action="store_true", help="仅检查Excel文件结构，不进行更新")
    parser.add_argument("--non-interactive", "-n", action="store_true", help="非交互模式，不需要用户确认")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.excel):
        print(f"错误: Excel文件不存在: {args.excel}")
        return
    
    if not os.path.exists(args.json):
        print(f"错误: JSON文件不存在: {args.json}")
        return
    
    # 检查Excel文件结构
    df = check_excel_structure(args.excel)
    if df is None:
        return
    
    if args.check:
        print("仅进行结构检查，不更新数据。")
        return
    
    # 检查行索引是否有效
    if args.row < 0 or args.row >= len(df):
        print(f"错误: 行索引 {args.row} 超出范围 (0-{len(df)-1})")
        return
    
    # 确认更新（交互模式）
    if not args.non_interactive:
        print(f"\n准备更新 {args.excel} 的第 {args.row + 1} 行数据...")
        choice = input("是否继续? (y/n): ").strip().lower()
        if choice != 'y' and choice != 'yes':
            print("操作已取消")
            return
    
    # 更新Excel文件
    success = update_excel_with_details(args.excel, args.output, args.json, args.row, not args.non_interactive)
    
    if success:
        print("数据更新完成！")
        
        # 询问是否覆盖原文件（交互模式）
        if not args.non_interactive and args.output is not None and args.output != args.excel:
            choice = input(f"是否用更新后的文件 {args.output} 替换原始文件 {args.excel}? (y/n): ").strip().lower()
            if choice == 'y' or choice == 'yes':
                try:
                    import shutil
                    # 备份原文件
                    backup_file = args.excel + '.bak'
                    shutil.copy2(args.excel, backup_file)
                    print(f"已创建原文件备份: {backup_file}")
                    
                    # 替换原文件
                    shutil.copy2(args.output, args.excel)
                    print(f"已用更新后的文件替换原文件")
                except Exception as e:
                    print(f"替换文件失败: {e}")

if __name__ == "__main__":
    main() 