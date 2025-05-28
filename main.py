from crawler.fetcher import fetch_page
from crawler.parser import parse_items
from crawler.pipelines import save_to_xls
from crawler.api_analyzer import analyze_apis
import os
import json
import requests
import re
import argparse
import time

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
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="微店商品数据采集工具")
    parser.add_argument("-u", "--url", default="https://weidian.com/?userid=1286456178&spider_token=2ead&tabType=all",
                        help="微店店铺链接")
    parser.add_argument("-p", "--pages", type=int, default=5,
                        help="采集页数，默认为5页。设置为0表示采集全部商品直到没有新数据")
    parser.add_argument("-o", "--output", default="data/items_new.xls",
                        help="输出文件名，默认为 data/items_new.xls")
    parser.add_argument("-d", "--delay", type=float, default=1.0,
                        help="每页请求间隔时间(秒)，默认为1秒")
    parser.add_argument("-a", "--all", action="store_true",
                        help="采集全部商品，直到没有新商品")
    args = parser.parse_args()
    
    url = args.url
    max_pages = args.pages
    output_file = args.output
    delay_time = args.delay
    collect_all = args.all or max_pages == 0
    
    if collect_all:
        print("模式：采集全部商品，直到没有新数据")
        max_pages = float('inf')  # 设置为无限大
    else:
        print(f"模式：采集指定页数 {max_pages} 页")
        
    print(f"开始采集 {url}")
    print(f"输出文件: {output_file}")
    
    # 第一步：尝试从 HTML 解析商品数据
    print("尝试从 HTML 解析商品数据...")
    html = fetch_page(url)
    items = parse_items(html)
    
    # 如果 HTML 解析无结果，尝试分析接口
    all_items = []
    if not items:
        print("HTML 解析无结果，开始分析接口...")
        api_info = analyze_apis(url)
        
        product_api = None
        if api_info["product_api"]:
            product_api = api_info["product_api"]
            print(f"找到商品数据接口: {product_api}")
        elif api_info["json_responses"]:
            print("尝试解析找到的 JSON 响应...")
            for response in api_info["json_responses"]:
                try:
                    data = json.loads(response["content"])
                    items = parse_api_data(data)
                    if items:
                        product_api = response["url"]
                        print(f"成功从接口解析出商品数据: {product_api}")
                        all_items.extend(items)
                        break
                except Exception as e:
                    print(f"解析 JSON 响应出错: {e}")
                    continue
        
        # 如果找到了商品API，尝试分页获取更多数据
        if product_api:
            # 从URL中提取参数
            param_match = re.search(r'param=([^&]+)', product_api)
            if param_match:
                param_json = json.loads(requests.utils.unquote(param_match.group(1)))
                base_offset = param_json.get("offset", 0)
                limit = param_json.get("limit", 20)
                
                # 先获取第一页数据
                print(f"\n正在获取第 1 页数据，offset={base_offset}...")
                try:
                    api_data = fetch_api_data(product_api)
                    page_items = parse_api_data(api_data)
                    
                    if page_items:
                        all_items.extend(page_items)
                        print(f"第 1 页成功获取 {len(page_items)} 条数据")
                        
                        # 保存第一页数据，以防后续出错
                        temp_output_dir = os.path.dirname(output_file)
                        if temp_output_dir:
                            os.makedirs(temp_output_dir, exist_ok=True)
                        temp_output = output_file.replace(".xls", "_temp.xls")
                        save_to_xls(all_items, temp_output)
                        print(f"已保存临时数据到 {temp_output}")
                    else:
                        print(f"第 1 页没有数据，停止采集")
                except Exception as e:
                    print(f"获取第 1 页数据出错: {e}")
                
                # 然后从第二页开始循环
                page = 1
                empty_pages_count = 0  # 记录连续空页面的数量
                
                while page < max_pages:
                    # 更新offset参数
                    new_offset = base_offset + page * limit
                    param_json["offset"] = new_offset
                    
                    # 构建新的API URL
                    new_param = requests.utils.quote(json.dumps(param_json))
                    new_api_url = re.sub(r'param=([^&]+)', f'param={new_param}', product_api)
                    
                    print(f"\n正在获取第 {page+1} 页数据，offset={new_offset}...")
                    try:
                        # 添加延迟，避免请求过快
                        if delay_time > 0:
                            time.sleep(delay_time)
                            
                        api_data = fetch_api_data(new_api_url)
                        page_items = parse_api_data(api_data)
                        
                        if page_items and len(page_items) > 0:
                            empty_pages_count = 0  # 重置空页面计数
                            all_items.extend(page_items)
                            print(f"第 {page+1} 页成功获取 {len(page_items)} 条数据")
                            
                            # 每5页保存一次临时数据
                            if page % 5 == 0:
                                temp_output = output_file.replace(".xls", "_temp.xls")
                                save_to_xls(all_items, temp_output)
                                print(f"已保存临时数据到 {temp_output}，当前共 {len(all_items)} 条数据")
                        else:
                            empty_pages_count += 1
                            print(f"第 {page+1} 页没有数据")
                            
                            # 如果是全部采集模式，连续3个空页面则停止
                            if collect_all and empty_pages_count >= 3:
                                print("连续3页没有新数据，采集完成")
                                break
                            elif not collect_all:
                                # 非全部采集模式，遇到空页面直接停止
                                print("没有更多数据，停止采集")
                                break
                    except Exception as e:
                        print(f"获取第 {page+1} 页数据出错: {e}")
                        # 发生错误时保存已采集的数据
                        error_output = output_file.replace(".xls", "_error.xls")
                        save_to_xls(all_items, error_output)
                        print(f"发生错误，已保存已采集的 {len(all_items)} 条数据到 {error_output}")
                        break
                    
                    page += 1
                    
                    # 非全部采集模式，达到指定页数后停止
                    if not collect_all and page >= max_pages:
                        print(f"已达到指定页数 {max_pages}，停止采集")
                        break
    
    # 保存数据
    if all_items:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        save_to_xls(all_items, output_file)
        print(f"已采集 {len(all_items)} 条商品数据，保存在 {output_file}")
        
        # 删除临时文件
        temp_output = output_file.replace(".xls", "_temp.xls")
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
                print(f"已删除临时文件 {temp_output}")
            except:
                pass
    else:
        print("未能采集到商品数据！") 