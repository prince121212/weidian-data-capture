# 手动API测试指南 - 获取分类商品ID

## 🎯 基于您发现的正确API格式

您已经找到了正确的API调用方式，现在我们可以手动测试和批量获取。

## 📋 API调用详情

### 基础信息：
- **URL**: `https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0`
- **方法**: GET
- **参数**: URL编码的JSON字符串

### 🔧 重点分类的完整API调用

#### 1. 高温白玉瓷餐具-釉中青花 (13个商品)

**参数JSON**:
```json
{
  "shopId": "1286456178",
  "tabId": 124372605,
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5",
  "showItemTag": true
}
```

**URL编码后**:
```
%7B%22shopId%22:%221286456178%22,%22tabId%22:124372605,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D
```

**完整URL**:
```
https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param=%7B%22shopId%22:%221286456178%22,%22tabId%22:124372605,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D
```

#### 2. 高温白玉瓷餐具-精品青花 (8个商品)

**完整URL**:
```
https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param=%7B%22shopId%22:%221286456178%22,%22tabId%22:124372612,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D
```

#### 3. 高温白玉瓷餐具-至尊青花 (3个商品)

**完整URL**:
```
https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param=%7B%22shopId%22:%221286456178%22,%22tabId%22:139661840,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D
```

#### 4. 高温白玉瓷餐具-釉中青花玲珑 (6个商品)

**完整URL**:
```
https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param=%7B%22shopId%22:%221286456178%22,%22tabId%22:124372546,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D
```

## 🔑 必需的请求头

```
accept: application/json, text/plain, */*
accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
origin: https://weidian.com
referer: https://weidian.com/
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-site
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0
cookie: [您的完整Cookie字符串]
```

## 🛠️ 手动测试方法

### 方法1: 使用Postman

1. **创建新请求**
   - 方法: GET
   - URL: 上面的完整URL

2. **设置Headers**
   - 添加上述所有请求头
   - 特别注意Cookie要完整

3. **发送请求**
   - 检查响应状态码
   - 查看返回的JSON数据

### 方法2: 使用浏览器开发者工具

1. **打开微店页面**
   ```
   https://weidian.com/?userid=1286456178&spider_token=9145&tabType=all
   ```

2. **打开开发者工具**
   - 按F12
   - 切换到Network标签

3. **点击分类**
   - 点击"高温白玉瓷餐具-釉中青花"
   - 在Network中找到API请求
   - 右键 -> Copy -> Copy as cURL

4. **修改cURL命令**
   - 替换tabId为其他分类ID
   - 重复执行获取其他分类

### 方法3: 使用curl命令

```bash
curl -X GET "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0?param=%7B%22shopId%22:%221286456178%22,%22tabId%22:124372605,%22sortOrder%22:%22desc%22,%22offset%22:0,%22limit%22:50,%22from%22:%22h5%22,%22showItemTag%22:true%7D" \
  -H "accept: application/json, text/plain, */*" \
  -H "accept-language: zh-CN,zh;q=0.9,en;q=0.8" \
  -H "origin: https://weidian.com" \
  -H "referer: https://weidian.com/" \
  -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "cookie: [您的Cookie]"
```

## 📊 预期响应格式

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

## 🎯 验证要点

### 成功标准：
1. **HTTP 200状态码**
2. **status.code = 0**
3. **itemList不为空**
4. **商品数量与预期匹配**

### 特别检查：
- **高温白玉瓷餐具-釉中青花**应该包含商品ID: `7257502545`, `7257580227`

## 🔄 批量获取流程

### 步骤1: 验证单个分类
- 先测试"高温白玉瓷餐具-釉中青花"
- 确认API调用成功
- 验证返回的商品数量和ID

### 步骤2: 批量获取所有分类
- 使用相同的方法获取其他3个分类
- 记录每个分类的商品ID

### 步骤3: 整理结果
- 按照您要求的格式整理
- 创建最终的Excel表格

## 📝 结果记录模板

```
分类名称: 高温白玉瓷餐具-釉中青花
商品数量: 13
主要商品ID: 7257502545, 7257580227, [其他ID...]

分类名称: 高温白玉瓷餐具-精品青花  
商品数量: 8
主要商品ID: [待获取]

分类名称: 高温白玉瓷餐具-至尊青花
商品数量: 3  
主要商品ID: [待获取]

分类名称: 高温白玉瓷餐具-釉中青花玲珑
商品数量: 6
主要商品ID: [待获取]
```

## 🚨 注意事项

### Cookie有效期
- Cookie可能会过期
- 如果返回认证错误，需要重新登录获取新Cookie

### 请求频率
- 不要请求过于频繁
- 建议每次请求间隔1-2秒

### 参数格式
- tabId必须是数字类型，不是字符串
- JSON参数必须正确URL编码

---

## 🎯 下一步行动

1. **选择测试方法** (推荐Postman或浏览器开发者工具)
2. **测试单个分类** (先测试釉中青花分类)
3. **验证结果** (检查商品数量和目标ID)
4. **批量获取** (获取所有4个重点分类)
5. **整理数据** (创建最终的Excel表格)

您希望使用哪种方法来测试API？我可以为您提供更详细的指导。
