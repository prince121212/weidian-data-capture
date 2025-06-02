#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除data文件夹中的原始xls文件（在确认xlsx文件已成功创建后）
"""

import os
import glob
from pathlib import Path

def remove_xls_files(data_folder="data"):
    """
    删除指定文件夹中的所有xls文件
    """
    print("=== 删除原始XLS文件工具 ===")
    print(f"目标文件夹: {data_folder}")
    print("⚠️  警告：此操作将永久删除所有xls文件！")
    print("=" * 50)
    
    # 确保data文件夹存在
    if not os.path.exists(data_folder):
        print(f"❌ 文件夹不存在: {data_folder}")
        return
    
    # 查找所有xls文件
    xls_pattern = os.path.join(data_folder, "*.xls")
    xls_files = glob.glob(xls_pattern)
    
    if not xls_files:
        print("✅ 未找到任何xls文件，可能已经全部删除")
        return
    
    print(f"📁 找到 {len(xls_files)} 个xls文件:")
    for file in xls_files:
        print(f"  - {os.path.basename(file)}")
    
    # 检查对应的xlsx文件是否存在
    print(f"\n🔍 检查对应的xlsx文件...")
    missing_xlsx = []
    
    for xls_file in xls_files:
        file_path = Path(xls_file)
        xlsx_file = file_path.with_suffix('.xlsx')
        
        if not xlsx_file.exists():
            missing_xlsx.append(os.path.basename(xls_file))
            print(f"  ❌ 缺少对应的xlsx文件: {xlsx_file.name}")
        else:
            print(f"  ✅ 找到对应的xlsx文件: {xlsx_file.name}")
    
    if missing_xlsx:
        print(f"\n⚠️  警告：以下xls文件没有对应的xlsx文件:")
        for file in missing_xlsx:
            print(f"  - {file}")
        print(f"建议先转换这些文件再删除！")
        return
    
    # 确认删除
    print(f"\n❓ 确认要删除所有 {len(xls_files)} 个xls文件吗？")
    print(f"输入 'YES' 确认删除，输入其他任何内容取消：")
    
    # 在脚本中我们不做交互式确认，而是提供一个安全的删除函数
    print(f"💡 如需删除，请手动调用 delete_confirmed() 函数")
    
    return xls_files

def delete_confirmed(data_folder="data"):
    """
    确认删除所有xls文件
    """
    xls_pattern = os.path.join(data_folder, "*.xls")
    xls_files = glob.glob(xls_pattern)
    
    deleted_count = 0
    failed_count = 0
    
    print(f"🗑️  开始删除 {len(xls_files)} 个xls文件...")
    
    for xls_file in xls_files:
        try:
            os.remove(xls_file)
            print(f"  ✅ 已删除: {os.path.basename(xls_file)}")
            deleted_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {os.path.basename(xls_file)} - {e}")
            failed_count += 1
    
    print(f"\n📊 删除完成统计:")
    print(f"  ✅ 成功删除: {deleted_count} 个文件")
    print(f"  ❌ 删除失败: {failed_count} 个文件")
    
    if deleted_count > 0:
        print(f"\n🎉 删除完成！")
        print(f"现在data文件夹中只保留xlsx格式的文件")

def main():
    """主函数"""
    try:
        xls_files = remove_xls_files("data")
        
        if xls_files:
            print(f"\n💡 使用说明:")
            print(f"如果您确认要删除这些xls文件，请运行:")
            print(f"python -c \"from remove_xls_files import delete_confirmed; delete_confirmed()\"")
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
