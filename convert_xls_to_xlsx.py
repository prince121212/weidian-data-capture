#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将data文件夹中的所有xls文件转换为xlsx格式
"""

import os
import glob
import pandas as pd
from pathlib import Path

def convert_xls_to_xlsx(data_folder="data"):
    """
    将指定文件夹中的所有xls文件转换为xlsx格式
    """
    print("=== XLS到XLSX格式转换工具 ===")
    print(f"目标文件夹: {data_folder}")
    print("=" * 50)
    
    # 确保data文件夹存在
    if not os.path.exists(data_folder):
        print(f"❌ 文件夹不存在: {data_folder}")
        return
    
    # 查找所有xls文件
    xls_pattern = os.path.join(data_folder, "*.xls")
    xls_files = glob.glob(xls_pattern)
    
    if not xls_files:
        print("❌ 未找到任何xls文件")
        return
    
    print(f"📁 找到 {len(xls_files)} 个xls文件:")
    for file in xls_files:
        print(f"  - {os.path.basename(file)}")
    
    print("\n🔄 开始转换...")
    
    converted_count = 0
    failed_count = 0
    
    for xls_file in xls_files:
        try:
            # 获取文件名（不含扩展名）
            file_path = Path(xls_file)
            xlsx_file = file_path.with_suffix('.xlsx')
            
            print(f"\n📝 转换: {file_path.name} -> {xlsx_file.name}")
            
            # 读取xls文件
            # 尝试读取所有工作表
            try:
                # 先尝试读取所有工作表
                excel_data = pd.read_excel(xls_file, sheet_name=None, engine='xlrd')
                
                # 创建ExcelWriter对象
                with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
                    # 写入所有工作表
                    for sheet_name, df in excel_data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                print(f"  ✅ 成功转换，包含 {len(excel_data)} 个工作表")
                converted_count += 1
                
            except Exception as e:
                # 如果读取多工作表失败，尝试读取默认工作表
                print(f"  ⚠️ 多工作表读取失败，尝试单工作表: {e}")
                try:
                    df = pd.read_excel(xls_file, engine='xlrd')
                    df.to_excel(xlsx_file, index=False, engine='openpyxl')
                    print(f"  ✅ 成功转换（单工作表）")
                    converted_count += 1
                except Exception as e2:
                    print(f"  ❌ 转换失败: {e2}")
                    failed_count += 1
                    
        except Exception as e:
            print(f"  ❌ 处理文件失败: {e}")
            failed_count += 1
    
    print(f"\n📊 转换完成统计:")
    print(f"  ✅ 成功转换: {converted_count} 个文件")
    print(f"  ❌ 转换失败: {failed_count} 个文件")
    print(f"  📁 总文件数: {len(xls_files)} 个文件")
    
    if converted_count > 0:
        print(f"\n🎉 转换成功！")
        print(f"所有xlsx文件已保存在 {data_folder} 文件夹中")
        
        # 询问是否删除原始xls文件
        print(f"\n❓ 是否删除原始的xls文件？")
        print(f"注意：删除后无法恢复！")
        
        # 这里我们不自动删除，让用户手动决定
        print(f"💡 如需删除原始xls文件，请手动删除或运行删除脚本")
    
    return converted_count, failed_count

def main():
    """主函数"""
    try:
        converted, failed = convert_xls_to_xlsx("data")
        
        if converted > 0:
            print(f"\n📋 转换后的文件列表:")
            xlsx_files = glob.glob("data/*.xlsx")
            for file in sorted(xlsx_files):
                print(f"  📄 {os.path.basename(file)}")
                
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
