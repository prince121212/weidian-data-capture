#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
from single_product_crawler import extract_item_id, fetch_detail_page, parse_detail_page_html, extract_detail_api, extract_all_images, extract_with_selenium

def test_single_product():
    """测试单个商品的配置提取"""
    
    # 读取目标文件获取第一个商品链接
    try:
        df = pd.read_excel('data/最终目标.xlsx')
        first_url = df.iloc[0]['商品详情页链接']
        print(f"测试商品链接: {first_url}")
        
        # 提取商品ID
        item_id = extract_item_id(first_url)
        print(f"商品ID: {item_id}")
        
        # 1. 常规方式提取
        print("\n=== 使用常规方式提取 ===")
        html = fetch_detail_page(first_url)
        if html:
            print(f"获取到HTML内容，长度: {len(html)}")
            html_details = parse_detail_page_html(html)
            print(f"HTML解析结果: {html_details}")
        else:
            print("获取HTML失败")
            html_details = {}
        
        # 2. 使用API提取
        print("\n=== 使用API提取 ===")
        api_details = extract_detail_api(first_url)
        print(f"API提取结果: {api_details}")
        
        # 3. 使用Selenium提取更多内容
        print("\n=== 使用Selenium提取 ===")
        try:
            selenium_details, selenium_images = extract_with_selenium(first_url)
            print(f"Selenium提取结果: {selenium_details}")
            print(f"Selenium图片数量: {len(selenium_images)}")
        except Exception as e:
            print(f"Selenium提取失败: {e}")
            selenium_details = {}
        
        # 合并所有信息
        all_details = {**html_details, **api_details, **selenium_details}
        
        print(f"\n=== 合并后的所有信息 ===")
        for key, value in all_details.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"{key}: {value[:100]}...")
            else:
                print(f"{key}: {value}")
        
        # 查找配置相关信息
        config_info = {}
        config_keys = ['商品配置', '提取的配置信息', '完整内容', '商品标题', '价格', '销量', '详细描述']
        for key in config_keys:
            if key in all_details:
                config_info[key] = all_details[key]
        
        print(f"\n=== 提取到的配置信息 ===")
        for key, value in config_info.items():
            if isinstance(value, str) and len(value) > 200:
                print(f"{key}: {value[:200]}...")
            else:
                print(f"{key}: {value}")
        
        return config_info
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    test_single_product()
