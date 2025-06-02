#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于真实浏览器请求的正确API调用
"""

import requests
import json
import urllib.parse
import xlwt

def get_category_products_correct(shop_id, tab_id, category_name, expected_count):
    """使用正确的方式获取分类商品"""
    
    # 构建参数（与浏览器完全一致）
    params_dict = {
        "shopId": shop_id,
        "tabId": tab_id,
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,  # 增加limit以获取更多商品
        "from": "h5",
        "showItemTag": True
    }
    
    # 将参数转换为JSON字符串并URL编码
    param_json = json.dumps(params_dict, separators=(',', ':'))
    param_encoded = urllib.parse.quote(param_json)
    
    # 构建完整URL
    url = f"https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param={param_encoded}"
    
    # 设置正确的请求头（基于您提供的真实请求）
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://weidian.com",
        "referer": "https://weidian.com/",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        # 注意：这里需要您的真实Cookie
        "cookie": "__spider__visitorid=f8aafd4628d8df46; visitor_id=6139fb27-aa45-42e8-894b-624ceb14cd31; Hm_lvt_f3b91484e26c0d850ada494bff4b469b=1747038927; is_login=true; login_type=LOGIN_USER_TYPE_MASTER; login_source=LOGIN_USER_SOURCE_MASTER; uid=1782954047; duid=1782954047; sid=1771946129; smart_login_type=0; login_token=_EwWqqVIQUxZ57lKJ1fKfI-LbdpmbvUO9CuSjJOTD9eWJrnP_vA34zVkM4kqwmNeGlZS0C6LRbSxUb7Ew31z1KxLIQH8wHTGXBkk1PaerIGOX3doAYLrK83gjL-5dle7MrqUCtshRawBhxDuYj8zD3i7DJMGTzfvko5DBAVFVhx8khvhcNUogWWuTaTZqfX3A5NHN83WSXzH7vBXmEtpPYyrpn17g03WHQ9bx2pyFp10YyI_yPIPMGGebMlPrmGiynYeNxnTU; hi_dxh=; hold=; cn_merchant=; wdtoken=c3999548; __spider__sessionid=99f7889b2170aca2"
    }
    
    print(f"\n=== 获取分类: {category_name} ===")
    print(f"分类ID: {tab_id}")
    print(f"预期商品数: {expected_count}")
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API状态: {data.get('status', {})}")
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    actual_count = len(items)
                    
                    print(f"✅ 成功获取 {actual_count} 个商品")
                    
                    if actual_count > 0:
                        # 提取商品ID
                        product_ids = []
                        for item in items:
                            item_id = str(item.get("itemId", ""))
                            item_name = item.get("itemName", "")
                            if item_id:
                                product_ids.append(item_id)
                        
                        print(f"商品ID: {', '.join(product_ids[:10])}")
                        if len(product_ids) > 10:
                            print(f"... 还有{len(product_ids)-10}个商品")
                        
                        # 检查目标商品ID
                        target_ids = ["7257502545", "7257580227"]
                        found_targets = [pid for pid in product_ids if pid in target_ids]
                        if found_targets:
                            print(f"🎯 找到目标商品ID: {found_targets}")
                        
                        # 验证数量
                        if actual_count == expected_count:
                            print(f"🎉 商品数量完全匹配！")
                        elif abs(actual_count - expected_count) <= 2:
                            print(f"📝 商品数量接近 (差异: {abs(actual_count - expected_count)})")
                        else:
                            print(f"⚠️ 商品数量差异较大 (预期: {expected_count}, 实际: {actual_count})")
                        
                        return True, product_ids
                    else:
                        print(f"❌ 未获取到商品")
                else:
                    error_msg = data.get('status', {}).get('message', '未知错误')
                    print(f"❌ API错误: {error_msg}")
                    
            except json.JSONDecodeError:
                print(f"❌ 响应不是有效JSON")
                print(f"响应内容: {response.text[:200]}...")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return False, []

def get_all_category_products():
    """获取所有重点分类的商品"""
    shop_id = "1286456178"
    
    # 重点分类列表
    categories = [
        {"tab_id": "124372605", "name": "高温白玉瓷餐具-釉中青花", "expected": 13},
        {"tab_id": "124372612", "name": "高温白玉瓷餐具-精品青花", "expected": 8},
        {"tab_id": "139661840", "name": "高温白玉瓷餐具-至尊青花", "expected": 3},
        {"tab_id": "124372546", "name": "高温白玉瓷餐具-釉中青花玲珑", "expected": 6}
    ]
    
    results = []
    
    print("=== 开始获取分类商品ID ===")
    print("=" * 60)
    
    for i, category in enumerate(categories, 1):
        print(f"\n[{i}/{len(categories)}] 处理分类...")
        
        success, product_ids = get_category_products_correct(
            shop_id,
            category["tab_id"],
            category["name"],
            category["expected"]
        )
        
        if success:
            result = {
                "分类名称": category["name"],
                "商品数量": len(product_ids),
                "主要商品ID": ', '.join(product_ids)
            }
            results.append(result)
            
            # 特别输出格式
            print(f"📝 {category['name']}分类下有商品id：{' 和 '.join(product_ids)}")
        else:
            print(f"❌ 获取失败: {category['name']}")
        
        print("-" * 50)
        
        # 避免请求过快
        import time
        time.sleep(1)
    
    return results

def save_results_to_excel(results):
    """保存结果到Excel"""
    if not results:
        print("❌ 没有结果可保存")
        return False
    
    try:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('正确的分类商品对应表')
        
        # 写入表头
        headers = ["分类名称", "商品数量", "主要商品ID"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        # 写入数据
        for row, result in enumerate(results, 1):
            sheet.write(row, 0, result["分类名称"])
            sheet.write(row, 1, result["商品数量"])
            sheet.write(row, 2, result["主要商品ID"])
        
        # 保存文件
        filename = "data/correct_category_products_final.xls"
        workbook.save(filename)
        
        print(f"✅ 结果已保存到: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    print("=== 使用正确的API获取分类商品ID ===")
    print("基于真实浏览器请求的完整实现")
    print("=" * 60)
    
    # 获取所有分类的商品
    results = get_all_category_products()
    
    if results:
        print(f"\n🎉 成功获取 {len(results)} 个分类的商品ID")
        
        # 保存到Excel
        save_results_to_excel(results)
        
        # 显示汇总
        print(f"\n📊 结果汇总:")
        for result in results:
            print(f"  ✅ {result['分类名称']}: {result['商品数量']}个商品")
        
        print(f"\n🎯 重点分类格式化输出:")
        for result in results:
            print(f"  {result['分类名称']}分类下有商品id：{result['主要商品ID'].replace(', ', ' 和 ')}")
    else:
        print(f"\n❌ 未能获取到任何分类的商品ID")
        print("可能的原因:")
        print("1. Cookie已过期，需要重新登录获取")
        print("2. 分类ID不正确")
        print("3. API接口有其他限制")

if __name__ == "__main__":
    main()
