#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
import time
import argparse
from batch_config_crawler import batch_extract_configs

def main():
    """完整的配置信息提取工具"""
    
    parser = argparse.ArgumentParser(description='完整提取所有商品配置信息')
    parser.add_argument('--input', default='data/最终目标.xlsx', help='输入Excel文件路径')
    parser.add_argument('--output', default='data/最终目标_完整配置.xlsx', help='输出Excel文件路径')
    parser.add_argument('--batch-size', type=int, default=50, help='每批处理的商品数量')
    parser.add_argument('--delay', type=float, default=2.0, help='每个请求之间的延迟时间(秒)')
    parser.add_argument('--start-batch', type=int, default=0, help='从第几批开始处理')
    parser.add_argument('--max-batches', type=int, default=None, help='最多处理多少批')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        return
    
    # 读取文件获取总行数
    df = pd.read_excel(args.input)
    total_items = len(df)
    total_batches = (total_items + args.batch_size - 1) // args.batch_size
    
    print("=== 完整商品配置信息提取工具 ===")
    print(f"输入文件: {args.input}")
    print(f"输出文件: {args.output}")
    print(f"总商品数: {total_items}")
    print(f"批次大小: {args.batch_size}")
    print(f"总批次数: {total_batches}")
    print(f"延迟时间: {args.delay}秒")
    
    if args.max_batches:
        total_batches = min(total_batches, args.max_batches)
        print(f"限制处理批次: {total_batches}")
    
    # 分批处理
    for batch_num in range(args.start_batch, total_batches):
        start_row = batch_num * args.batch_size
        end_row = min((batch_num + 1) * args.batch_size, total_items)
        
        print(f"\n{'='*50}")
        print(f"处理第 {batch_num + 1}/{total_batches} 批")
        print(f"商品范围: 第{start_row + 1}行 到 第{end_row}行")
        print(f"{'='*50}")
        
        # 处理当前批次
        success = batch_extract_configs(
            input_file=args.input,
            output_file=args.output,
            start_row=start_row,
            end_row=end_row,
            delay=args.delay,
            use_selenium=True,  # 使用Selenium获取完整配置信息
            save_interval=10
        )
        
        if not success:
            print(f"批次 {batch_num + 1} 处理失败，停止处理")
            break
        
        print(f"批次 {batch_num + 1} 处理完成")
        
        # 批次间休息
        if batch_num < total_batches - 1:
            print(f"批次间休息 10 秒...")
            time.sleep(10)
    
    print(f"\n🎉 所有批次处理完成!")
    print(f"最终结果保存在: {args.output}")
    
    # 显示最终统计
    try:
        final_df = pd.read_excel(args.output)
        if '爬取状态' in final_df.columns:
            status_counts = final_df['爬取状态'].value_counts()
            print(f"\n最终统计:")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            # 计算成功率
            success_count = status_counts.get('成功', 0)
            total_processed = status_counts.sum()
            if total_processed > 0:
                success_rate = success_count / total_processed * 100
                print(f"\n总成功率: {success_rate:.1f}% ({success_count}/{total_processed})")
    except Exception as e:
        print(f"读取最终结果失败: {e}")

if __name__ == "__main__":
    main()
