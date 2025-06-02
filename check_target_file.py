#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
import time
import json
from single_product_crawler import extract_item_id, fetch_detail_page, parse_detail_page_html, extract_detail_api, extract_all_images, extract_with_selenium

def check_target_file():
    """检查最终目标.xlsx文件的内容"""
    file_path = 'data/最终目标.xlsx'

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return

    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print('文件读取成功!')
        print(f'总行数: {len(df)}')
        print(f'总列数: {len(df.columns)}')
        print(f'列名: {list(df.columns)}')

        print('\n前5行数据:')
        for i, row in df.head().iterrows():
            print(f"\n第{i+1}行:")
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    print(f"  {col}: [空值]")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  {col}: {value[:100]}...")
                else:
                    print(f"  {col}: {value}")

        # 检查是否有商品详情页链接列
        link_columns = [col for col in df.columns if '链接' in col or 'link' in col.lower() or 'url' in col.lower()]
        print(f'\n包含链接的列: {link_columns}')

        # 检查是否有配置相关的列
        config_columns = [col for col in df.columns if '配置' in col or 'config' in col.lower()]
        print(f'包含配置的列: {config_columns}')

        # 检查有多少行有链接数据
        if link_columns:
            for col in link_columns:
                non_empty = df[col].notna().sum()
                print(f'列 "{col}" 中有 {non_empty} 行有数据')

                # 显示前几个链接示例
                valid_links = df[col].dropna().head(3)
                print(f'前3个链接示例:')
                for idx, link in valid_links.items():
                    print(f"  行{idx+1}: {link}")

        return df

    except Exception as e:
        print(f'读取文件失败: {e}')
        import traceback
        traceback.print_exc()
        return None

def extract_product_config(url, use_selenium=True):
    """
    从商品详情页提取配置信息

    Args:
        url: 商品详情页链接
        use_selenium: 是否使用Selenium提取更多内容

    Returns:
        dict: 包含配置信息的字典
    """
    print(f"正在提取商品配置: {url}")

    try:
        # 提取商品ID
        item_id = extract_item_id(url)

        # 1. 常规方式提取
        html = fetch_detail_page(url)
        if not html:
            print(f"获取页面失败: {url}")
            return {}

        # 解析HTML
        html_details = parse_detail_page_html(html)

        # 2. 使用API提取
        api_details = extract_detail_api(url)

        # 3. 使用Selenium提取更多内容 (可选)
        selenium_details = {}
        if use_selenium:
            print("使用Selenium提取配置信息...")
            selenium_details, _ = extract_with_selenium(url)

        # 合并所有信息
        all_details = {**html_details, **api_details, **selenium_details}

        # 提取配置相关信息
        config_info = {}

        # 查找配置相关的字段
        config_keys = ['商品配置', '提取的配置信息', '完整内容', '商品标题', '价格', '销量', '详细描述']
        for key in config_keys:
            if key in all_details:
                config_info[key] = all_details[key]

        print(f"提取到配置字段: {list(config_info.keys())}")
        return config_info

    except Exception as e:
        print(f"提取配置信息失败: {url}, 错误: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    check_target_file()
