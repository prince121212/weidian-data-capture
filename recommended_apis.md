# 微店分类商品API推荐方案

## 🎯 最可能的正确API

基于微店的API结构分析，以下是最有可能获取分类商品ID的API接口：

### 1. 主推荐API：shopDetail.tab.getItemList

```javascript
URL: https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0
方法: GET
参数格式: JSON字符串

参数示例:
{
  "param": "{
    \"shopId\": \"1286456178\",
    \"tabId\": \"124372605\",
    \"sortOrder\": \"desc\",
    \"offset\": 0,
    \"limit\": 50,
    \"from\": \"h5\"
  }"
}
```

**使用方法**:
```python
import requests
import json

url = "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0"
params = {
    "param": json.dumps({
        "shopId": "1286456178",
        "tabId": "124372605",  # 分类ID
        "sortOrder": "desc",
        "offset": 0,
        "limit": 50,
        "from": "h5"
    })
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://weidian.com/?userid=1286456178&spider_token=9145&tabType=all"
}

response = requests.get(url, params=params, headers=headers)
```

### 2. 备选API：shop.getItemList

```javascript
URL: https://thor.weidian.com/shop/getItemList/1.0
方法: GET

参数示例:
{
  "param": "{
    \"shopId\": \"1286456178\",
    \"cateId\": \"124372605\",
    \"sortOrder\": \"desc\",
    \"offset\": 0,
    \"limit\": 50
  }"
}
```

### 3. 备选API：wfr.shop.getItemList

```javascript
URL: https://thor.weidian.com/wfr/shop/getItemList/1.0
方法: GET

参数示例:
{
  "param": "{
    \"shopId\": \"1286456178\",
    \"cateId\": \"124372605\",
    \"offset\": 0,
    \"limit\": 50
  }"
}
```

## 📋 重点分类的API调用参数

### 您关注的分类API参数：

#### 1. 高温白玉瓷餐具-釉中青花 (13个商品)
```json
{
  "shopId": "1286456178",
  "tabId": "124372605",
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5"
}
```

#### 2. 高温白玉瓷餐具-精品青花 (8个商品)
```json
{
  "shopId": "1286456178",
  "tabId": "124372612",
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5"
}
```

#### 3. 高温白玉瓷餐具-至尊青花 (3个商品)
```json
{
  "shopId": "1286456178",
  "tabId": "139661840",
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5"
}
```

#### 4. 高温白玉瓷餐具-釉中青花玲珑 (6个商品)
```json
{
  "shopId": "1286456178",
  "tabId": "124372546",
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5"
}
```

## 🔧 完整的Python实现

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取微店分类商品ID的完整实现
"""

import requests
import json
import time
import xlwt

def get_category_products(shop_id, category_id, category_name, expected_count):
    """获取指定分类的商品ID"""
    
    # API接口列表（按优先级排序）
    apis = [
        {
            "url": "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0",
            "param_key": "tabId"
        },
        {
            "url": "https://thor.weidian.com/shop/getItemList/1.0", 
            "param_key": "cateId"
        },
        {
            "url": "https://thor.weidian.com/wfr/shop/getItemList/1.0",
            "param_key": "cateId"
        }
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://weidian.com/?userid={shop_id}&spider_token=9145&tabType=all",
        "Accept": "application/json, text/plain, */*"
    }
    
    for api in apis:
        try:
            params = {
                "param": json.dumps({
                    "shopId": shop_id,
                    api["param_key"]: category_id,
                    "sortOrder": "desc",
                    "offset": 0,
                    "limit": 50,
                    "from": "h5"
                })
            }
            
            response = requests.get(api["url"], params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status", {}).get("code") == 0:
                    result = data.get("result", {})
                    items = result.get("itemList", [])
                    
                    if len(items) == expected_count or abs(len(items) - expected_count) <= 2:
                        product_ids = [str(item.get("itemId", "")) for item in items if item.get("itemId")]
                        return product_ids, api["url"]
                        
        except Exception as e:
            continue
    
    return [], "未找到有效API"

def main():
    """主函数"""
    shop_id = "1286456178"
    
    # 重点分类
    categories = [
        {"id": "124372605", "name": "高温白玉瓷餐具-釉中青花", "count": 13},
        {"id": "124372612", "name": "高温白玉瓷餐具-精品青花", "count": 8},
        {"id": "139661840", "name": "高温白玉瓷餐具-至尊青花", "count": 3},
        {"id": "124372546", "name": "高温白玉瓷餐具-釉中青花玲珑", "count": 6}
    ]
    
    results = []
    
    for category in categories:
        print(f"获取分类: {category['name']}")
        
        product_ids, api_used = get_category_products(
            shop_id, 
            category["id"], 
            category["name"], 
            category["count"]
        )
        
        if product_ids:
            print(f"✅ 成功获取 {len(product_ids)} 个商品ID")
            print(f"使用API: {api_used}")
            print(f"商品ID: {', '.join(product_ids)}")
            
            results.append({
                "分类名称": category["name"],
                "商品数量": len(product_ids),
                "商品ID": ', '.join(product_ids),
                "API": api_used
            })
        else:
            print(f"❌ 获取失败")
        
        time.sleep(1)  # 避免请求过快
    
    # 保存结果
    if results:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('分类商品ID')
        
        headers = ["分类名称", "商品数量", "主要商品ID", "使用的API"]
        for col, header in enumerate(headers):
            sheet.write(0, col, header)
        
        for row, result in enumerate(results, 1):
            sheet.write(row, 0, result["分类名称"])
            sheet.write(row, 1, result["商品数量"])
            sheet.write(row, 2, result["商品ID"])
            sheet.write(row, 3, result["API"])
        
        workbook.save("category_products_final.xls")
        print("结果已保存到 category_products_final.xls")

if __name__ == "__main__":
    main()
```

## 🚨 重要注意事项

### 1. 网络环境
- 确保网络连接稳定
- 可能需要特定的网络环境（如国内网络）
- 避免使用代理或VPN

### 2. 请求频率
- 不要请求过于频繁
- 建议每次请求间隔1-2秒
- 避免被反爬虫机制拦截

### 3. 请求头设置
- 必须设置正确的User-Agent
- 必须设置正确的Referer
- 可能需要设置Cookie（如果有登录状态）

### 4. 参数格式
- 参数必须是JSON字符串格式
- 分类ID必须是字符串类型
- 注意参数名称的差异（tabId vs cateId）

## 🎯 验证方法

### 成功标准：
1. HTTP状态码 = 200
2. 响应JSON中 status.code = 0
3. 商品数量与预期匹配
4. 包含目标商品ID（如7257502545, 7257580227）

### 响应格式：
```json
{
  "status": {
    "code": 0,
    "message": "success"
  },
  "result": {
    "itemList": [
      {
        "itemId": "7257502545",
        "itemName": "商品名称",
        "price": 价格,
        "imgUrl": "图片URL",
        ...
      }
    ],
    "totalCount": 13
  }
}
```

## 📞 下一步建议

1. **手动测试**: 使用浏览器开发者工具验证API
2. **逐步调试**: 先测试单个分类，确认API正确性
3. **批量处理**: 确认API后，批量获取所有分类的商品ID
4. **数据验证**: 对比获取的商品数量与预期数量

当网络环境稳定后，建议按照上述方案进行测试！
