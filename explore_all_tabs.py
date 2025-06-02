#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索所有分类标签页的商品
"""

import requests
import json
import time
import xlwt
import os

def fetch_tab_data(shop_id, tab_id, offset=0, limit=20):
    """获取指定标签页的商品数据"""
    url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
    
    params = {
        "param": json.dumps({
            "shopId": shop_id,
            "tabId": tab_id,
            "sortOrder": "desc",
            "offset": offset,
            "limit": limit,
            "from": "h5",
            "showItemTag": True
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://weidian.com/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def parse_product_data(data):
    """解析商品数据"""
    products = []
    
    if not data or "result" not in data:
        return products
    
    result = data["result"]
    if "itemList" not in result:
        return products
    
    for item in result["itemList"]:
        product = {
            "商品ID": item.get("itemId", ""),
            "商品名称": item.get("itemName", ""),
            "价格": item.get("price", ""),
            "原价": item.get("originalPrice", ""),
            "销量": item.get("sold", ""),
            "库存": item.get("stock", ""),
            "图片链接": item.get("itemImg", ""),
            "商品详情页链接": f"https://weidian.com/item.html?itemID={item.get('itemId', '')}" if item.get('itemId') else ""
        }
        products.append(product)
    
    return products

def explore_all_tabs(shop_id):
    """探索所有可能的分类标签页"""
    print(f"=== 探索店铺 {shop_id} 的所有分类标签页 ===\n")
    
    all_products = {}
    tab_info = {}
    
    # 尝试不同的tabId (通常从0到10)
    for tab_id in range(0, 15):
        print(f"正在检查标签页 {tab_id}...")
        
        # 获取第一页数据
        data = fetch_tab_data(shop_id, tab_id, 0, 20)
        
        if data and "result" in data:
            result = data["result"]
            has_data = result.get("hasData", False)
            item_count = len(result.get("itemList", []))
            
            if has_data and item_count > 0:
                print(f"  ✅ 标签页 {tab_id}: 找到 {item_count} 个商品")
                
                # 解析商品数据
                products = parse_product_data(data)
                
                # 获取更多页面的数据
                all_tab_products = products.copy()
                offset = 20
                
                while True:
                    time.sleep(1)  # 添加延迟
                    more_data = fetch_tab_data(shop_id, tab_id, offset, 20)
                    
                    if not more_data or "result" not in more_data:
                        break
                    
                    more_result = more_data["result"]
                    if not more_result.get("hasData", False):
                        break
                    
                    more_products = parse_product_data(more_data)
                    if not more_products:
                        break
                    
                    all_tab_products.extend(more_products)
                    offset += 20
                    
                    print(f"    获取到第 {offset//20} 页，累计 {len(all_tab_products)} 个商品")
                    
                    if len(more_products) < 20:  # 最后一页
                        break
                
                all_products[tab_id] = all_tab_products
                tab_info[tab_id] = {
                    "count": len(all_tab_products),
                    "sample_names": [p["商品名称"] for p in all_tab_products[:5]]
                }
                
                print(f"  📊 标签页 {tab_id} 总计: {len(all_tab_products)} 个商品")
                
                # 显示前几个商品名称作为示例
                for i, product in enumerate(all_tab_products[:3]):
                    print(f"    {i+1}. {product['商品名称']}")
                
            else:
                print(f"  ❌ 标签页 {tab_id}: 无数据")
        else:
            print(f"  ❌ 标签页 {tab_id}: 请求失败")
        
        time.sleep(0.5)  # 避免请求过快
    
    return all_products, tab_info

def save_all_tabs_data(all_products, output_file):
    """保存所有标签页的数据到Excel"""
    try:
        workbook = xlwt.Workbook()
        
        # 创建汇总表
        summary_sheet = workbook.add_sheet('标签页汇总')
        summary_headers = ['标签页ID', '商品数量', '示例商品名称']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(0, col, header)
        
        summary_row = 1
        for tab_id, products in all_products.items():
            summary_sheet.write(summary_row, 0, f"标签页{tab_id}")
            summary_sheet.write(summary_row, 1, len(products))
            sample_names = [p["商品名称"] for p in products[:3]]
            summary_sheet.write(summary_row, 2, " | ".join(sample_names))
            summary_row += 1
        
        # 为每个标签页创建单独的工作表
        for tab_id, products in all_products.items():
            if not products:
                continue
                
            sheet_name = f"标签页{tab_id}"
            sheet = workbook.add_sheet(sheet_name)
            
            # 写入表头
            headers = ["商品ID", "商品名称", "价格", "原价", "销量", "库存", "图片链接", "商品详情页链接"]
            for col, header in enumerate(headers):
                sheet.write(0, col, header)
            
            # 写入数据
            for row, product in enumerate(products, 1):
                for col, header in enumerate(headers):
                    value = product.get(header, "")
                    sheet.write(row, col, str(value))
        
        # 保存文件
        workbook.save(output_file)
        print(f"\n✅ 所有标签页数据已保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def search_specific_products(all_products, keywords):
    """在所有标签页中搜索特定商品"""
    print(f"\n=== 搜索包含关键词的商品 ===")
    
    found_products = []
    
    for keyword in keywords:
        print(f"\n搜索关键词: '{keyword}'")
        keyword_found = []
        
        for tab_id, products in all_products.items():
            for product in products:
                if keyword.lower() in product["商品名称"].lower():
                    keyword_found.append({
                        "tab_id": tab_id,
                        "product": product
                    })
        
        if keyword_found:
            print(f"  找到 {len(keyword_found)} 个相关商品:")
            for item in keyword_found:
                print(f"    标签页{item['tab_id']}: {item['product']['商品名称']}")
            found_products.extend(keyword_found)
        else:
            print(f"  未找到包含 '{keyword}' 的商品")
    
    return found_products

def main():
    shop_id = "1286456178"
    output_file = "data/all_tabs_products.xls"

    # 确保输出目录存在
    os.makedirs("data", exist_ok=True)

    print("开始探索所有分类标签页...")
    print(f"店铺ID: {shop_id}")
    print("=" * 50)
    
    # 探索所有标签页
    all_products, tab_info = explore_all_tabs(shop_id)
    
    # 显示汇总信息
    print(f"\n=== 探索结果汇总 ===")
    total_products = sum(len(products) for products in all_products.values())
    print(f"找到 {len(all_products)} 个有效标签页")
    print(f"总商品数: {total_products}")
    
    for tab_id, info in tab_info.items():
        print(f"  标签页{tab_id}: {info['count']} 个商品")
    
    # 保存数据
    if all_products:
        save_all_tabs_data(all_products, output_file)
        
        # 搜索特定商品
        keywords = ["高温白玉瓷", "釉中青花", "精品青花", "至尊青花", "青花玲珑"]
        found = search_specific_products(all_products, keywords)
        
        if found:
            print(f"\n🎯 找到了您要找的商品类型！")
        else:
            print(f"\n❌ 未找到您提到的具体商品名称")
            print("可能的原因:")
            print("1. 这些商品可能已经下架")
            print("2. 可能需要特定的搜索条件")
            print("3. 可能在其他店铺或页面中")
    
    else:
        print("未找到任何商品数据")

if __name__ == "__main__":
    main()
