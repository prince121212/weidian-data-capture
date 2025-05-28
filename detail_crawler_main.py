import os
import pandas as pd
import xlrd
import xlwt
from xlutils.copy import copy
import argparse
import time
from crawler.detail_crawler import crawl_item_detail

def read_xls_to_pandas(xls_file):
    """读取XLS文件为Pandas DataFrame"""
    try:
        # 使用xlrd直接读取xls
        workbook = xlrd.open_workbook(xls_file)
        sheet = workbook.sheet_by_index(0)
        
        # 读取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        
        # 读取数据
        data = []
        for row in range(1, sheet.nrows):
            row_data = {}
            for col in range(sheet.ncols):
                row_data[headers[col]] = sheet.cell_value(row, col)
            data.append(row_data)
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        print(f"成功读取 {len(df)} 条商品数据")
        return df
    
    except Exception as e:
        print(f"读取XLS文件失败: {e}")
        return pd.DataFrame()

def save_df_to_xls(df, output_file):
    """将DataFrame保存为XLS文件"""
    try:
        # 创建工作簿和工作表
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Items')
        
        # 写入表头
        headers = df.columns.tolist()
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 写入数据
        for row, item in enumerate(df.to_dict('records'), 1):
            for col, header in enumerate(headers):
                value = item.get(header, '')
                # 确保值是字符串、数字或布尔值
                if isinstance(value, (str, int, float, bool)):
                    sheet.write(row, col, value)
                else:
                    sheet.write(row, col, str(value))
        
        # 保存文件
        workbook.save(output_file)
        print(f"成功保存 {len(df)} 条数据到 {output_file}")
        return True
    
    except Exception as e:
        print(f"保存XLS文件失败: {e}")
        return False

def update_xls_with_details(input_file, output_file, url_column, start_index=0, end_index=None, 
                           batch_size=10, delay=2.0, save_interval=5):
    """
    爬取商品详情并更新Excel文件
    
    参数:
    - input_file: 输入的Excel文件
    - output_file: 输出的Excel文件
    - url_column: 包含商品链接的列名
    - start_index: 开始处理的行索引
    - end_index: 结束处理的行索引，None表示处理到最后
    - batch_size: 每批处理的商品数量
    - delay: 每个请求之间的延迟时间(秒)
    - save_interval: 多少批保存一次
    """
    # 读取原始数据
    df = read_xls_to_pandas(input_file)
    if df.empty:
        print("输入文件为空或无法读取")
        return
    
    # 确保URL列存在
    if url_column not in df.columns:
        print(f"错误: 输入文件中没有找到列 '{url_column}'")
        return
    
    # 确定处理范围
    total_items = len(df)
    if end_index is None or end_index > total_items:
        end_index = total_items
    
    if start_index < 0:
        start_index = 0
    
    # 创建临时文件名
    temp_output = output_file.replace(".xls", "_temp.xls")
    
    # 如果是继续处理，尝试加载之前的结果
    if start_index > 0 and os.path.exists(temp_output):
        try:
            temp_df = read_xls_to_pandas(temp_output)
            if not temp_df.empty and len(temp_df) >= start_index:
                df.iloc[:start_index] = temp_df.iloc[:start_index]
                print(f"已加载前 {start_index} 条处理过的数据")
        except:
            print("无法加载临时文件，将从头开始处理")
    
    # 分批处理
    total_batches = (end_index - start_index + batch_size - 1) // batch_size
    processed_count = 0
    
    print(f"开始处理 {input_file} 中的商品详情")
    print(f"处理范围: 第 {start_index+1} 到 {end_index} 条，共 {end_index-start_index} 条")
    print(f"分为 {total_batches} 批处理，每批 {batch_size} 条")
    
    for batch in range(total_batches):
        batch_start = start_index + batch * batch_size
        batch_end = min(batch_start + batch_size, end_index)
        
        print(f"\n处理第 {batch+1}/{total_batches} 批，项目 {batch_start+1}-{batch_end}/{total_items}")
        
        for i in range(batch_start, batch_end):
            try:
                # 获取商品URL
                item_url = df.iloc[i][url_column]
                if not isinstance(item_url, str) or not item_url.startswith("http"):
                    print(f"跳过无效URL: {item_url}")
                    continue
                
                print(f"[{i+1}/{total_items}] 处理商品: {item_url}")
                
                # 爬取详情
                details = crawl_item_detail(item_url, delay=delay)
                
                if details:
                    # 更新DataFrame
                    for key, value in details.items():
                        # 如果是新列，添加到DataFrame
                        if key not in df.columns:
                            df[key] = None
                        # 更新值
                        df.at[i, key] = value
                    
                    processed_count += 1
                    print(f"成功更新商品 {i+1}/{total_items}，已添加 {len(details)} 个详情字段")
                else:
                    print(f"未获取到商品 {i+1}/{total_items} 的详情")
                
            except Exception as e:
                print(f"处理商品 {i+1} 时出错: {e}")
        
        # 每处理完一个批次保存一次临时文件
        if (batch + 1) % save_interval == 0 or batch == total_batches - 1:
            print(f"\n保存临时结果到 {temp_output}")
            save_df_to_xls(df, temp_output)
    
    # 全部处理完成后，保存最终结果
    if processed_count > 0:
        print(f"\n全部处理完成，保存结果到 {output_file}")
        save_df_to_xls(df, output_file)
        
        # 如果成功保存，删除临时文件
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
                print(f"已删除临时文件 {temp_output}")
            except:
                pass
    else:
        print("未处理任何商品，不保存结果")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微店商品详情爬取工具")
    parser.add_argument("-i", "--input", default="data/items_all.xls",
                       help="输入的商品列表Excel文件")
    parser.add_argument("-o", "--output", default="data/items_all_with_details.xls",
                       help="输出的带详情Excel文件")
    parser.add_argument("-c", "--column", default="商品详情页链接",
                       help="包含商品链接的列名")
    parser.add_argument("-s", "--start", type=int, default=0,
                       help="开始处理的商品索引(从0开始)")
    parser.add_argument("-e", "--end", type=int, default=None,
                       help="结束处理的商品索引")
    parser.add_argument("-b", "--batch", type=int, default=10,
                       help="每批处理的商品数量")
    parser.add_argument("-d", "--delay", type=float, default=2.0,
                       help="每个请求之间的延迟时间(秒)")
    parser.add_argument("-si", "--save_interval", type=int, default=1,
                       help="多少批保存一次临时结果")
    
    args = parser.parse_args()
    
    # 执行详情爬取和更新
    update_xls_with_details(
        input_file=args.input,
        output_file=args.output,
        url_column=args.column,
        start_index=args.start,
        end_index=args.end,
        batch_size=args.batch,
        delay=args.delay,
        save_interval=args.save_interval
    ) 