#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个分类的API调用
"""

import requests
import json
import urllib.parse

def test_single_category():
    """测试单个分类"""
    print("=== 测试单个分类API ===")
    
    # 测试参数
    shop_id = "1286456178"
    tab_id = "124372605"  # 高温白玉瓷餐具-釉中青花
    category_name = "高温白玉瓷餐具-釉中青花"
    
    print(f"店铺ID: {shop_id}")
    print(f"分类ID: {tab_id}")
    print(f"分类名称: {category_name}")
    print(f"预期商品数: 13")
    
    # 构建参数
    params_dict = {
        "shopId": shop_id,
        "tabId": int(tab_id),  # 转换为整数
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,
        "from": "h5",
        "showItemTag": True
    }
    
    # 转换为JSON并URL编码
    param_json = json.dumps(params_dict, separators=(',', ':'))
    param_encoded = urllib.parse.quote(param_json)
    
    # 构建URL
    url = f"https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param={param_encoded}"
    
    print(f"\n参数字典: {params_dict}")
    print(f"JSON参数: {param_json}")
    print(f"编码参数: {param_encoded}")
    print(f"完整URL: {url}")
    
    # 设置请求头
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
    
    print(f"\n发送请求...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"响应内容长度: {len(response.text)}")
            print(f"响应内容前500字符: {response.text[:500]}")
            
            try:
                data = response.json()
                print(f"\nJSON解析成功!")
                print(f"状态: {data.get('status', {})}")
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    
                    print(f"✅ 成功获取 {len(items)} 个商品")
                    
                    if items:
                        print(f"\n前5个商品:")
                        for i, item in enumerate(items[:5]):
                            item_id = item.get("itemId", "")
                            item_name = item.get("itemName", "")
                            print(f"  {i+1}. ID: {item_id}, 名称: {item_name}")
                        
                        # 检查目标商品ID
                        all_ids = [str(item.get("itemId", "")) for item in items]
                        target_ids = ["7257502545", "7257580227"]
                        found = [tid for tid in target_ids if tid in all_ids]
                        
                        if found:
                            print(f"\n🎯 找到目标商品ID: {found}")
                        else:
                            print(f"\n❌ 未找到目标商品ID")
                            print(f"所有商品ID: {', '.join(all_ids)}")
                        
                        print(f"\n📝 {category_name}分类下有商品id：{' 和 '.join(all_ids)}")
                        
                        return True, all_ids
                    else:
                        print(f"❌ 商品列表为空")
                else:
                    error_msg = data.get('status', {}).get('message', '未知错误')
                    print(f"❌ API错误: {error_msg}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
    
    return False, []

if __name__ == "__main__":
    success, product_ids = test_single_category()
    
    if success:
        print(f"\n🎉 测试成功!")
        print(f"获取到 {len(product_ids)} 个商品ID")
    else:
        print(f"\n❌ 测试失败")
