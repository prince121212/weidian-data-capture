#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
import time
import json
import argparse
from check_target_file import extract_product_config

def batch_extract_configs(input_file, output_file, start_row=0, end_row=None, delay=2.0, use_selenium=True, save_interval=10):
    """
    批量提取商品配置信息并更新Excel文件
    
    Args:
        input_file: 输入的Excel文件路径
        output_file: 输出的Excel文件路径
        start_row: 开始处理的行索引（从0开始）
        end_row: 结束处理的行索引，None表示处理到最后
        delay: 每个请求之间的延迟时间(秒)
        use_selenium: 是否使用Selenium提取更多内容
        save_interval: 每处理多少个商品保存一次
    """
    
    # 读取输入文件
    print(f"正在读取输入文件: {input_file}")
    try:
        df = pd.read_excel(input_file)
        print(f"成功读取文件，共 {len(df)} 行数据")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
    # 检查必要的列
    if '商品详情页链接' not in df.columns:
        print("错误: 文件中没有找到'商品详情页链接'列")
        return False
    
    # 确定处理范围
    total_rows = len(df)
    if end_row is None or end_row > total_rows:
        end_row = total_rows
    
    if start_row < 0:
        start_row = 0
    
    print(f"将处理第 {start_row+1} 到第 {end_row} 行，共 {end_row - start_row} 个商品")
    
    # 添加新列（如果不存在）
    new_columns = ['商品配置', '提取的配置信息', '完整内容描述', '爬取状态', '爬取时间']
    for col in new_columns:
        if col not in df.columns:
            df[col] = ''
            print(f"添加新列: {col}")
    
    # 创建临时文件用于保存进度
    temp_file = output_file.replace('.xlsx', '_temp.xlsx')
    
    # 开始批量处理
    processed_count = 0
    success_count = 0
    
    for idx in range(start_row, end_row):
        row = df.iloc[idx]
        url = row['商品详情页链接']
        
        if pd.isna(url) or not isinstance(url, str) or not url.startswith('http'):
            print(f"跳过第 {idx+1} 行: 无效链接")
            df.at[idx, '爬取状态'] = '跳过-无效链接'
            continue
        
        print(f"\n[{idx+1}/{end_row}] 正在处理: {url}")
        
        try:
            # 提取配置信息
            config_info = extract_product_config(url, use_selenium=use_selenium)

            if config_info:
                # 更新DataFrame - 确保所有字段都被正确保存
                for key, value in config_info.items():
                    if key in df.columns:
                        df.at[idx, key] = value
                        print(f"保存字段 {key}: {str(value)[:50]}...")

                # 特别处理配置信息字段
                if '提取的配置信息' in config_info:
                    df.at[idx, '提取的配置信息'] = config_info['提取的配置信息']
                if '完整内容' in config_info:
                    df.at[idx, '完整内容描述'] = config_info['完整内容']
                if '商品配置' in config_info:
                    df.at[idx, '商品配置'] = config_info['商品配置']

                df.at[idx, '爬取状态'] = '成功'
                df.at[idx, '爬取时间'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                success_count += 1
                print(f"成功提取配置信息，包含字段: {list(config_info.keys())}")
            else:
                df.at[idx, '爬取状态'] = '失败-无配置信息'
                print("未提取到配置信息")
            
        except Exception as e:
            print(f"处理失败: {e}")
            df.at[idx, '爬取状态'] = f'失败-{str(e)[:50]}'
        
        processed_count += 1
        
        # 定期保存进度
        if processed_count % save_interval == 0:
            print(f"\n保存临时进度到: {temp_file}")
            df.to_excel(temp_file, index=False)
            print(f"已处理 {processed_count} 个商品，成功 {success_count} 个")
        
        # 延迟
        if delay > 0:
            print(f"等待 {delay} 秒...")
            time.sleep(delay)
    
    # 保存最终结果
    print(f"\n保存最终结果到: {output_file}")
    df.to_excel(output_file, index=False)
    
    # 删除临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"删除临时文件: {temp_file}")
    
    print(f"\n批量处理完成!")
    print(f"总共处理: {processed_count} 个商品")
    print(f"成功提取: {success_count} 个商品")
    print(f"成功率: {success_count/processed_count*100:.1f}%")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='批量提取商品配置信息')
    parser.add_argument('--input', default='data/最终目标.xlsx', help='输入Excel文件路径')
    parser.add_argument('--output', default='data/最终目标_with_config.xlsx', help='输出Excel文件路径')
    parser.add_argument('--start', type=int, default=0, help='开始处理的行索引（从0开始）')
    parser.add_argument('--end', type=int, default=None, help='结束处理的行索引')
    parser.add_argument('--delay', type=float, default=2.0, help='每个请求之间的延迟时间(秒)')
    parser.add_argument('--no-selenium', action='store_true', help='不使用Selenium（更快但信息可能不完整）')
    parser.add_argument('--save-interval', type=int, default=10, help='每处理多少个商品保存一次')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return
    
    # 创建输出目录
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("=== 批量商品配置信息提取工具 ===")
    print(f"输入文件: {args.input}")
    print(f"输出文件: {args.output}")
    print(f"处理范围: 第{args.start+1}行 到 第{args.end if args.end else '最后'}行")
    print(f"延迟时间: {args.delay}秒")
    print(f"使用Selenium: {not args.no_selenium}")
    print(f"保存间隔: 每{args.save_interval}个商品")
    
    # 开始处理
    success = batch_extract_configs(
        input_file=args.input,
        output_file=args.output,
        start_row=args.start,
        end_row=args.end,
        delay=args.delay,
        use_selenium=not args.no_selenium,
        save_interval=args.save_interval
    )
    
    if success:
        print(f"\n✅ 处理完成! 结果已保存到: {args.output}")
    else:
        print(f"\n❌ 处理失败!")

if __name__ == "__main__":
    main()
