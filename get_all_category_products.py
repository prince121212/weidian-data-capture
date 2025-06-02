#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取所有分类下的商品信息
基于all_categories.xls文件中的分类数据
"""

import requests
import json
import xlrd
import xlwt
import time
import os
from urllib.parse import quote

def read_categories_from_excel(filename):
    """从Excel文件中读取分类信息"""
    categories = []
    
    try:
        workbook = xlrd.open_workbook(filename)
        sheet = workbook.sheet_by_index(0)  # 分类汇总表
        
        # 获取表头
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        print(f"表头: {headers}")
        
        # 找到关键列
        id_col = headers.index("分类ID") if "分类ID" in headers else -1
        name_col = headers.index("分类名称") if "分类名称" in headers else -1
        path_col = headers.index("完整分类路径") if "完整分类路径" in headers else -1
        count_col = headers.index("商品数量") if "商品数量" in headers else -1
        
        print(f"列索引: ID={id_col}, 名称={name_col}, 路径={path_col}, 数量={count_col}")
        
        # 读取数据
        for row in range(1, sheet.nrows):
            category_id = str(sheet.cell_value(row, id_col)) if id_col >= 0 else ""
            category_name = str(sheet.cell_value(row, name_col)) if name_col >= 0 else ""
            full_path = str(sheet.cell_value(row, path_col)) if path_col >= 0 else ""
            product_count = int(sheet.cell_value(row, count_col)) if count_col >= 0 and sheet.cell_value(row, count_col) else 0
            
            if category_id and category_name and product_count > 0:
                categories.append({
                    "分类ID": category_id,
                    "分类名称": category_name,
                    "完整分类路径": full_path,
                    "预期商品数量": product_count
                })
        
        print(f"成功读取 {len(categories)} 个有商品的分类")
        return categories
        
    except Exception as e:
        print(f"读取分类文件失败: {e}")
        return []

def get_category_products(shop_id, category_id, category_name, expected_count, max_pages=10):
    """获取指定分类下的所有商品"""
    print(f"\n=== 获取分类商品: {category_name} ===")
    print(f"分类ID: {category_id}")
    print(f"预期商品数: {expected_count}")
    
    # 使用正确的API接口
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://weidian.com",
        "referer": "https://weidian.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "cookie": "__spider__visitorid=f8aafd4628d8df46; visitor_id=6139fb27-aa45-42e8-894b-624ceb14cd31; Hm_lvt_f3b91484e26c0d850ada494bff4b469b=1747038927; is_login=true; login_type=LOGIN_USER_TYPE_MASTER; login_source=LOGIN_USER_SOURCE_MASTER; uid=1782954047; duid=1782954047; sid=1771946129; smart_login_type=0; login_token=_EwWqqVIQUxZ57lKJ1fKfI-LbdpmbvUO9CuSjJOTD9eWJrnP_vA34zVkM4kqwmNeGlZS0C6LRbSxUb7Ew31z1KxLIQH8wHTGXBkk1PaerIGOX3doAYLrK83gjL-5dle7MrqUCtshRawBhxDuYj8zD3i7DJMGTzfvko5DBAVFVhx8khvhcNUogWWuTaTZqfX3A5NHN83WSXzH7vBXmEtpPYyrpn17g03WHQ9bx2pyFp10YyI_yPIPMGGebMlPrmGiynYeNxnTU; hi_dxh=; hold=; cn_merchant=; wdtoken=c3999548; __spider__sessionid=99f7889b2170aca2"
    }
    
    all_products = []
    
    # 分页获取商品
    for page in range(max_pages):
        offset = page * 20
        
        # 构建参数 - 使用tabId而不是cateId
        params_dict = {
            "shopId": shop_id,
            "tabId": int(category_id),  # 关键：使用tabId，转换为整数
            "sortOrder": "desc",
            "offset": offset,
            "limit": 20,
            "from": "h5",
            "showItemTag": True
        }

        # 将参数转换为JSON字符串并URL编码
        param_json = json.dumps(params_dict, separators=(',', ':'))
        param_encoded = quote(param_json)

        # 构建完整URL
        full_url = f"{url}?param={param_encoded}"
        
        try:
            response = requests.get(full_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get("status", {}).get("code") == 0:
                        result = data.get("result", {})
                        items = result.get("itemList", [])
                        
                        if not items:
                            print(f"第{page+1}页没有更多商品，停止获取")
                            break
                        
                        # 提取商品信息
                        for item in items:
                            product_info = {
                                "商品ID": str(item.get("itemId", "")),
                                "商品名称": item.get("itemName", ""),
                                "商品价格": item.get("price", ""),
                                "商品图片": item.get("thumbs", [""])[0] if item.get("thumbs") else "",
                                "商品链接": f"https://weidian.com/item.html?itemID={item.get('itemId', '')}",
                                "分类ID": category_id,
                                "分类名称": category_name
                            }
                            all_products.append(product_info)
                        
                        print(f"第{page+1}页获取到 {len(items)} 个商品")
                        
                        # 如果获取的商品数量已经达到预期，可以停止
                        if len(all_products) >= expected_count:
                            print(f"已获取足够商品数量，停止获取")
                            break
                            
                    else:
                        print(f"API返回错误: {data.get('status', {})}")
                        break
                        
                except json.JSONDecodeError:
                    print(f"第{page+1}页响应不是有效的JSON格式")
                    break
            else:
                print(f"第{page+1}页HTTP请求失败: {response.status_code}")
                break
                
        except Exception as e:
            print(f"第{page+1}页请求异常: {e}")
            break
        
        # 添加延迟避免请求过快
        time.sleep(1)
    
    actual_count = len(all_products)
    print(f"✅ 分类 {category_name} 共获取到 {actual_count} 个商品")
    
    # 验证数量
    if actual_count == expected_count:
        print(f"🎉 商品数量完全匹配！")
    elif abs(actual_count - expected_count) <= 2:
        print(f"📝 商品数量接近 (差异: {abs(actual_count - expected_count)})")
    else:
        print(f"⚠️ 商品数量差异较大 (预期: {expected_count}, 实际: {actual_count})")
    
    return all_products

def save_products_to_excel(all_products, categories, filename):
    """保存所有商品信息到Excel文件"""
    try:
        workbook = xlwt.Workbook(encoding='utf-8')

        # 创建商品详情表
        detail_sheet = workbook.add_sheet('商品详情')

        # 写入表头
        headers = ['商品ID', '商品名称', '商品价格', '商品图片', '商品链接', '分类ID', '分类名称', '完整分类路径']
        for col, header in enumerate(headers):
            detail_sheet.write(0, col, header)

        # 写入商品数据
        row = 1
        for product in all_products:
            detail_sheet.write(row, 0, product.get('商品ID', ''))
            detail_sheet.write(row, 1, product.get('商品名称', ''))
            detail_sheet.write(row, 2, product.get('商品价格', ''))
            detail_sheet.write(row, 3, product.get('商品图片', ''))
            detail_sheet.write(row, 4, product.get('商品链接', ''))
            detail_sheet.write(row, 5, product.get('分类ID', ''))
            detail_sheet.write(row, 6, product.get('分类名称', ''))

            # 查找完整分类路径
            full_path = ""
            for cat in categories:
                if cat['分类ID'] == product.get('分类ID', ''):
                    full_path = cat['完整分类路径']
                    break
            detail_sheet.write(row, 7, full_path)

            row += 1

        # 创建分类汇总表
        summary_sheet = workbook.add_sheet('分类汇总')

        # 写入汇总表头
        summary_headers = ['分类ID', '分类名称', '完整分类路径', '预期商品数', '实际商品数', '匹配状态']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header)

        # 统计每个分类的实际商品数
        category_counts = {}
        for product in all_products:
            cat_id = product.get('分类ID', '')
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1

        # 写入汇总数据
        row = 1
        for category in categories:
            cat_id = category['分类ID']
            expected = category['预期商品数量']
            actual = category_counts.get(cat_id, 0)

            # 判断匹配状态
            if actual == expected:
                status = "完全匹配"
            elif abs(actual - expected) <= 2:
                status = "接近匹配"
            else:
                status = "差异较大"

            summary_sheet.write(row, 0, cat_id)
            summary_sheet.write(row, 1, category['分类名称'])
            summary_sheet.write(row, 2, category['完整分类路径'])
            summary_sheet.write(row, 3, expected)
            summary_sheet.write(row, 4, actual)
            summary_sheet.write(row, 5, status)

            row += 1

        # 保存文件
        workbook.save(filename)
        print(f"\n✅ 商品数据已保存到: {filename}")
        return True

    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    """主函数"""
    shop_id = "1286456178"
    input_file = "data/all_categories.xls"
    output_file = "data/all_category_products.xls"

    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)

    print("=== 微店所有分类商品获取工具 ===")
    print(f"店铺ID: {shop_id}")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("=" * 50)

    # 读取分类信息
    categories = read_categories_from_excel(input_file)

    if not categories:
        print("❌ 未能读取到分类信息")
        return

    print(f"\n📊 将要处理 {len(categories)} 个分类")

    # 显示分类概况
    total_expected = sum(cat['预期商品数量'] for cat in categories)
    print(f"预期总商品数: {total_expected}")

    # 获取所有分类的商品
    all_products = []
    processed_count = 0

    for i, category in enumerate(categories, 1):
        print(f"\n[{i}/{len(categories)}] 处理分类: {category['分类名称']}")

        products = get_category_products(
            shop_id,
            category['分类ID'],
            category['分类名称'],
            category['预期商品数量']
        )

        all_products.extend(products)
        processed_count += 1

        print(f"已处理 {processed_count}/{len(categories)} 个分类，累计获取 {len(all_products)} 个商品")

        # 每处理5个分类休息一下
        if i % 5 == 0:
            print("⏸️ 休息5秒...")
            time.sleep(5)

    # 保存结果
    print(f"\n=== 保存结果 ===")
    print(f"总共获取到 {len(all_products)} 个商品")

    success = save_products_to_excel(all_products, categories, output_file)

    if success:
        print(f"\n🎉 完成！")
        print(f"📁 文件位置: {output_file}")
        print(f"📊 包含内容:")
        print(f"  - 商品详情表: {len(all_products)} 个商品的详细信息")
        print(f"  - 分类汇总表: {len(categories)} 个分类的统计信息")

        # 显示统计信息
        category_counts = {}
        for product in all_products:
            cat_id = product.get('分类ID', '')
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1

        print(f"\n📈 分类统计:")
        for category in categories:
            cat_id = category['分类ID']
            expected = category['预期商品数量']
            actual = category_counts.get(cat_id, 0)
            print(f"  {category['分类名称']}: {actual}/{expected}")
    else:
        print(f"\n❌ 保存失败")

if __name__ == "__main__":
    main()
