from crawler.fetcher import fetch_page
from crawler.parser import parse_items
from crawler.pipelines import save_to_xls
from crawler.api_analyzer import analyze_apis
import os
import json
import requests

def fetch_api_data(api_url):
    """从 API 获取商品数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://h5.weidian.com/"
    }
    resp = requests.get(api_url, headers=headers)
    return resp.json()

def parse_api_data(data):
    """解析微店 API 返回的商品数据"""
    items = []
    try:
        # 打印原始数据结构，帮助调试
        print("API 返回数据结构:", json.dumps(data, ensure_ascii=False)[:200] + "...")
        
        # 微店 API 返回结构分析
        if isinstance(data, dict) and "result" in data:
            result = data["result"]
            product_list = None
            
            # 微店接口常用字段名
            for key in ["itemList", "items", "goods", "products", "list"]:
                if key in result and isinstance(result[key], list):
                    product_list = result[key]
                    print(f"找到商品列表字段: {key}, 包含 {len(product_list)} 个商品")
                    break
            
            # 如果找不到标准字段，尝试遍历 result 中的所有列表
            if not product_list:
                for key, value in result.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        if any(k in value[0] for k in ["itemId", "itemName", "price", "title"]):
                            product_list = value
                            print(f"找到可能的商品列表字段: {key}, 包含 {len(product_list)} 个商品")
                            break

            if product_list:
                for product in product_list:
                    item = {}
                    # 商品 ID
                    item["商品ID"] = product.get("itemId") or product.get("id") or ""
                    
                    # 商品名称
                    item["商品名称"] = (
                        product.get("itemName") or 
                        product.get("title") or 
                        product.get("name") or 
                        ""
                    )
                    
                    # 价格处理
                    price = None
                    if "price" in product:
                        price = product["price"]
                    elif "priceInfo" in product and isinstance(product["priceInfo"], dict):
                        price = product["priceInfo"].get("price")
                    
                    item["价格"] = price or ""
                    
                    # 原价处理
                    original_price = None
                    if "originalPrice" in product:
                        original_price = product["originalPrice"]
                    elif "priceInfo" in product and isinstance(product["priceInfo"], dict):
                        original_price = product["priceInfo"].get("originalPrice")
                    
                    item["原价"] = original_price or ""
                    
                    # 销量
                    item["销量"] = (
                        product.get("sold") or 
                        product.get("sales") or 
                        product.get("saleNum") or 
                        ""
                    )
                    
                    # 库存
                    item["库存"] = product.get("stock") or ""
                    
                    # 图片处理
                    img_url = ""
                    if "img" in product:
                        img_url = product["img"]
                    elif "image" in product:
                        img_url = product["image"]
                    elif "imgHead" in product:
                        img_url = product["imgHead"]
                    elif "images" in product and isinstance(product["images"], list) and len(product["images"]) > 0:
                        img_url = product["images"][0]
                    elif "itemImg" in product:
                        img_url = product["itemImg"]
                    
                    item["图片链接"] = img_url
                    
                    # 商品链接
                    item["商品详情页链接"] = (
                        product.get("url") or 
                        product.get("link") or 
                        f"https://weidian.com/item.html?itemID={item['商品ID']}" if item["商品ID"] else ""
                    )
                    
                    # 分类
                    item["商品分类"] = product.get("category") or product.get("cate") or ""
                    
                    # 其他可能有用的字段
                    for key, value in product.items():
                        if key not in item and isinstance(value, (str, int, float)):
                            item[key] = value
                    
                    items.append(item)
                
                print(f"成功解析 {len(items)} 个商品数据")
            else:
                print("未找到商品列表字段，API 结构:", json.dumps(result.keys(), ensure_ascii=False))
    except Exception as e:
        print(f"解析 API 数据时出错: {e}")
    
    return items

if __name__ == "__main__":
    url = "https://h5.weidian.com/decoration/shop-category/category.html?userid=1286456178&c=124372511"
    
    # 第一步：尝试从 HTML 解析商品数据
    print("尝试从 HTML 解析商品数据...")
    html = fetch_page(url)
    items = parse_items(html)
    
    # 如果 HTML 解析无结果，尝试分析接口
    if not items:
        print("HTML 解析无结果，开始分析接口...")
        api_info = analyze_apis(url)
        
        if api_info["product_api"]:
            print(f"找到商品数据接口: {api_info['product_api']}")
            api_data = fetch_api_data(api_info["product_api"])
            items = parse_api_data(api_data)
        elif api_info["json_responses"]:
            print("尝试解析找到的 JSON 响应...")
            for response in api_info["json_responses"]:
                try:
                    data = json.loads(response["content"])
                    items = parse_api_data(data)
                    if items:
                        print(f"成功从接口解析出商品数据: {response['url']}")
                        break
                except Exception as e:
                    print(f"解析 JSON 响应出错: {e}")
                    continue
    
    # 保存数据
    if items:
        os.makedirs("data", exist_ok=True)
        save_to_xls(items, "data/items.xls")
        print(f"已采集 {len(items)} 条商品数据，保存在 data/items.xls")
    else:
        print("未能采集到商品数据！") 