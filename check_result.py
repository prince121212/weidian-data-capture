#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

def check_result():
    """检查处理结果"""
    file_path = 'data/最终目标_with_config.xlsx'
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        df = pd.read_excel(file_path)
        print('文件读取成功!')
        print(f'总行数: {len(df)}')
        print(f'总列数: {len(df.columns)}')
        print(f'列名: {list(df.columns)}')
        
        # 检查配置信息列
        config_columns = [col for col in df.columns if '配置' in col]
        print(f'\n配置相关列: {config_columns}')
        
        # 检查前3行的配置信息
        print('\n前3行的配置信息:')
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f'\n第{i+1}行商品: {row["商品标题"]}')
            
            if '提取的配置信息' in df.columns and pd.notna(row.get('提取的配置信息', '')):
                config = row['提取的配置信息']
                if len(str(config)) > 200:
                    print(f'配置信息: {str(config)[:200]}...')
                else:
                    print(f'配置信息: {config}')
            else:
                print('配置信息: [空]')
            
            if '爬取状态' in df.columns:
                print(f'爬取状态: {row.get("爬取状态", "未知")}')
        
        # 统计爬取状态
        if '爬取状态' in df.columns:
            status_counts = df['爬取状态'].value_counts()
            print(f'\n爬取状态统计:')
            for status, count in status_counts.items():
                print(f'  {status}: {count}')
        
        return df
        
    except Exception as e:
        print(f'读取文件失败: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    check_result()
