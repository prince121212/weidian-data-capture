# 微店API分析指南 - 寻找正确的分类商品API

## 🔍 分析方法

### 1. 浏览器开发者工具分析

#### 步骤1：打开微店页面
```
https://weidian.com/?userid=1286456178&spider_token=9145&tabType=all
```

#### 步骤2：打开开发者工具
- 按F12或右键"检查"
- 切换到"Network"(网络)标签
- 勾选"Preserve log"(保留日志)

#### 步骤3：点击分类
- 点击"高温白玉瓷餐具-釉中青花"分类
- 观察Network标签中的API请求

#### 步骤4：分析API请求
查找包含以下特征的请求：
- URL包含"getItemList"或"item"
- 请求参数包含分类ID
- 响应包含商品列表

## 🎯 可能的API接口

### 1. 主要候选接口

#### A. shopDetail.tab.getItemList
```
URL: https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0
参数: {
  "shopId": "1286456178",
  "tabId": "124372605",  // 分类ID
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50,
  "from": "h5"
}
```

#### B. shop.getItemList
```
URL: https://thor.weidian.com/shop/getItemList/1.0
参数: {
  "shopId": "1286456178",
  "cateId": "124372605",  // 分类ID
  "sortOrder": "desc",
  "offset": 0,
  "limit": 50
}
```

#### C. wfr.shop.getItemList
```
URL: https://thor.weidian.com/wfr/shop/getItemList/1.0
参数: {
  "shopId": "1286456178",
  "cateId": "124372605",
  "offset": 0,
  "limit": 50
}
```

### 2. 参数变体测试

#### 参数名称变体：
- `tabId` vs `cateId` vs `categoryId`
- `shopId` vs `userId`
- `offset` vs `page`
- `limit` vs `pageSize`

#### 请求方式变体：
- GET请求 + JSON参数
- GET请求 + URL参数
- POST请求 + JSON body

## 🔧 测试脚本正在运行

当前正在测试以下API接口：

1. ✅ shopDetail.tab.getItemList (原接口)
2. ✅ shopDetail.tab.getItemList (使用cateId)
3. ✅ shop.getItemList (商店商品列表)
4. ✅ item.getItemListByCategory (按分类获取商品)
5. ✅ wfr.shop.getItemList (WFR商店接口)
6. ✅ category.getItemList (分类商品接口)
7. ✅ v2版本接口
8. ✅ 使用GET参数而非JSON

## 📊 预期结果

### 成功标准：
1. **HTTP 200状态码**
2. **API返回code=0**
3. **商品数量=13** (对于釉中青花分类)
4. **包含目标商品ID**: 7257502545, 7257580227

### 响应格式示例：
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
        "price": "价格",
        ...
      }
    ],
    "totalCount": 13
  }
}
```

## 🚨 可能的问题和解决方案

### 问题1：网络连接问题
**症状**: 连接超时、代理错误
**解决**: 
- 检查网络连接
- 尝试不同的网络环境
- 禁用代理设置

### 问题2：API认证问题
**症状**: 返回401、403错误
**解决**:
- 添加必要的请求头
- 获取有效的token或cookie
- 模拟真实浏览器请求

### 问题3：参数格式问题
**症状**: 返回400错误或空结果
**解决**:
- 检查参数名称和格式
- 验证分类ID的正确性
- 尝试不同的参数组合

### 问题4：API版本问题
**症状**: 404错误或接口不存在
**解决**:
- 尝试不同版本的API
- 查找最新的API文档
- 分析网页实际使用的接口

## 🎯 手动验证方法

如果自动化测试失败，可以手动验证：

### 方法1：浏览器Network分析
1. 打开微店页面
2. 打开开发者工具
3. 点击分类
4. 查看Network请求
5. 复制API请求信息

### 方法2：Postman测试
1. 使用Postman工具
2. 导入API请求
3. 测试不同参数组合
4. 验证响应结果

### 方法3：curl命令测试
```bash
curl -X GET "https://thor.weidian.com/decorate/shopDetail.tab.getItemList/1.0" \
  -H "User-Agent: Mozilla/5.0..." \
  -H "Referer: https://weidian.com/..." \
  -G -d "param={\"shopId\":\"1286456178\",\"tabId\":\"124372605\",...}"
```

## 📝 下一步行动

1. **等待测试脚本完成** - 查看自动化测试结果
2. **手动验证** - 如果自动化失败，进行手动分析
3. **优化参数** - 根据结果调整API参数
4. **批量获取** - 确定正确API后，批量获取所有分类的商品ID

---

## 🔄 实时状态

**当前状态**: 测试脚本正在运行中...
**测试进度**: 正在测试8个不同的API接口
**预计完成时间**: 约2-3分钟

请稍等，脚本完成后我们将获得准确的API信息！
