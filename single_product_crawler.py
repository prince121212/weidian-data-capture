from crawler.detail_crawler import fetch_detail_page, parse_detail_page_html, extract_detail_api
import sys
import re
import json
import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import xlwt

def extract_images_from_json(html):
    """从页面中嵌入的JSON数据提取图片"""
    img_urls = set()
    # 查找常见的商品图片JSON模式
    patterns = [
        r'var\s+itemData\s*=\s*({.*?});',
        r'var\s+itemInfo\s*=\s*({.*?});',
        r'var\s+goods\s*=\s*({.*?});',
        r'"images"\s*:\s*(\[.*?\])',
        r'"pics"\s*:\s*(\[.*?\])',
        r'"pictures"\s*:\s*(\[.*?\])',
        r'"gallery"\s*:\s*(\[.*?\])',
        r'"detailImages"\s*:\s*(\[.*?\])'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            try:
                # 尝试解析为JSON
                if match.startswith('['):
                    # 直接是数组
                    data = json.loads(match)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, str) and item.startswith('http'):
                                img_urls.add(item)
                            elif isinstance(item, dict) and 'url' in item:
                                url = item['url']
                                if isinstance(url, str) and url.startswith('http'):
                                    img_urls.add(url)
                else:
                    # 是对象
                    data = json.loads(match)
                    # 寻找可能包含图片的字段
                    for key in ['images', 'pics', 'pictures', 'gallery', 'detailImages', 'imgs', 'photos']:
                        if key in data and isinstance(data[key], list):
                            for img in data[key]:
                                if isinstance(img, str) and img.startswith('http'):
                                    img_urls.add(img)
                                elif isinstance(img, dict) and 'url' in img:
                                    url = img['url']
                                    if isinstance(url, str) and url.startswith('http'):
                                        img_urls.add(url)
            except:
                # JSON解析失败，继续尝试下一个
                pass
    
    return img_urls

def extract_all_images(html):
    """从HTML中提取所有图片链接"""
    soup = BeautifulSoup(html, 'html.parser')
    img_urls = set()
    
    # 提取img标签
    for img in soup.find_all('img'):
        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src']:
            src = img.get(attr)
            if src and src.startswith('http'):
                img_urls.add(src)
    
    # 提取style中的背景图
    for tag in soup.find_all(lambda tag: tag.has_attr('style')):
        style = tag['style']
        urls = re.findall(r'url\([\'"]?(https?://[^\)\'"\s]+)[\'"]?\)', style)
        for url in urls:
            img_urls.add(url)
    
    # 从JSON数据中提取
    json_images = extract_images_from_json(html)
    img_urls.update(json_images)
    
    return list(img_urls)

def extract_with_selenium(url):
    """使用Selenium进行完整页面爬取"""
    print("使用Selenium进行完整页面爬取...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    full_details = {}
    all_images = set()
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 滚动页面以加载更多内容
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(1)
        
        # 尝试点击"查看详情"按钮或类似元素
        try:
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '详情') or contains(text(), '详细') or contains(text(), '规格')]")
            for button in buttons:
                button.click()
                time.sleep(2)
        except:
            pass
        
        # 提取页面源码
        page_source = driver.page_source
        
        # 提取图片
        images_from_src = extract_all_images(page_source)
        all_images.update(images_from_src)
        
        # 提取标题和价格
        try:
            title_element = driver.find_element(By.XPATH, "//h1 | //div[contains(@class, 'title') or contains(@class, 'name')]")
            if title_element:
                full_details["商品标题"] = title_element.text.strip()
        except:
            pass
            
        try:
            price_element = driver.find_element(By.XPATH, "//div[contains(@class, 'price') or contains(@class, 'amount')]")
            if price_element:
                full_details["价格"] = price_element.text.strip()
        except:
            pass
            
        # 尝试提取销量
        try:
            sales_element = driver.find_element(By.XPATH, "//div[contains(text(), '销量') or contains(text(), '已售')]")
            if sales_element:
                full_details["销量"] = sales_element.text.strip()
        except:
            pass
            
        # 尝试提取详细描述
        try:
            desc_element = driver.find_element(By.XPATH, "//div[contains(@class, 'desc') or contains(@class, 'detail') or contains(@class, 'description')]")
            if desc_element:
                full_details["详细描述"] = desc_element.text.strip()
        except:
            pass
            
        # 尝试提取规格参数
        try:
            specs_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'specs') or contains(@class, 'params')]//li")
            if specs_elements:
                specs = []
                for elem in specs_elements:
                    specs.append(elem.text.strip())
                full_details["规格参数"] = ", ".join(specs)
        except:
            pass
            
        # 尝试提取商品配置信息
        try:
            config_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '配置') or contains(text(), '套装') or contains(text(), '规格')]//following-sibling::div | //div[contains(text(), '配置') or contains(text(), '套装') or contains(text(), '规格')]/parent::div//div")
            if config_elements:
                configs = []
                for elem in config_elements:
                    text = elem.text.strip()
                    if text and text not in configs and not text.startswith("配置") and len(text) < 100:
                        configs.append(text)
                if configs:
                    full_details["商品配置"] = "\n".join(configs)
        except:
            pass
        
        # 尝试从页面文本中提取配置信息
        try:
            content_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'content') or contains(@class, 'detail-content') or contains(@class, 'description')]")
            full_content = ""
            for elem in content_elements:
                content_text = elem.text.strip()
                if content_text and len(content_text) > 10:  # 避免太短的内容
                    full_content += content_text + "\n"
            
            if full_content and "配置" not in full_details:
                # 尝试从内容中提取配置信息
                config_lines = []
                lines = full_content.split("\n")
                for line in lines:
                    line = line.strip()
                    if "配置" in line or "套装" in line or "规格" in line or "包含" in line or "包括" in line or "清单" in line:
                        config_lines.append(line)
                        # 获取后续几行
                        idx = lines.index(line)
                        for i in range(idx + 1, min(idx + 6, len(lines))):
                            if lines[i].strip() and len(lines[i].strip()) < 100:  # 避免太长的行
                                config_lines.append(lines[i].strip())
                
                if config_lines:
                    full_details["提取的配置信息"] = "\n".join(config_lines)
                    
            # 保存完整内容以备参考
            if full_content and len(full_content) > 20:
                full_details["完整内容"] = full_content
        except:
            pass
        
        # 从JavaScript变量中提取数据
        js_vars = [
            "itemInfo", "itemData", "goodsInfo", "detailInfo", 
            "skuInfo", "productData", "shopInfo"
        ]
        
        for var_name in js_vars:
            try:
                script = f"return typeof {var_name} !== 'undefined' ? {var_name} : null;"
                data = driver.execute_script(script)
                if data and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (str, int, float, bool)) and key not in ['id', 'itemId']:
                            full_details[key] = value
                    
                    # 查找可能的图片数组
                    for img_key in ['images', 'pics', 'gallery', 'detailImages']:
                        if img_key in data and isinstance(data[img_key], list):
                            for img in data[img_key]:
                                if isinstance(img, str) and img.startswith('http'):
                                    all_images.add(img)
                                elif isinstance(img, dict) and 'url' in img:
                                    url = img['url']
                                    if isinstance(url, str) and url.startswith('http'):
                                        all_images.add(url)
            except:
                pass
    
    except Exception as e:
        print(f"Selenium提取失败: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return full_details, list(all_images)

def download_images(images, output_dir="product_images"):
    """下载图片到指定目录"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\n开始下载 {len(images)} 张图片到 {output_dir} 目录")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    downloaded = 0
    for i, img_url in enumerate(images):
        try:
            filename = os.path.join(output_dir, f"image_{i+1}.jpg")
            response = requests.get(img_url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            downloaded += 1
            print(f"已下载: {img_url} -> {filename}")
        except Exception as e:
            print(f"下载失败: {img_url}, 错误: {e}")
    
    print(f"成功下载 {downloaded}/{len(images)} 张图片")
    return downloaded

def save_details_to_json(details, images, output_file="product_details.json"):
    """保存商品详情和图片链接到JSON文件"""
    # 尝试清理描述中的异常编码
    cleaned_details = {}
    for key, value in details.items():
        if isinstance(value, str):
            # 尝试修复编码问题
            try:
                # 如果字符串中有乱码，可能需要更复杂的转换方式
                cleaned_value = value
                # 检测是否有乱码字符
                if any(ord(c) > 127 for c in value):
                    # 将常见的乱码模式替换成易读的格式
                    if '鈥?' in value:
                        cleaned_value = value.replace('鈥?', '"')
                    if '鏀惧叆璐墿杞' in value:
                        cleaned_value = value.replace('鏀惧叆璐墿杞', '放入购物车')
                cleaned_details[key] = cleaned_value
            except:
                cleaned_details[key] = value
        else:
            cleaned_details[key] = value
    
    data = {
        "details": cleaned_details,
        "images": images
    }
    
    # 使用UTF-8编码保存，确保中文正确显示
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存商品详情和图片链接到 {output_file}")

    # 为了方便查看，也保存一个纯文本版本
    with open(output_file.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
        f.write("【商品详情】\n")
        for k, v in cleaned_details.items():
            f.write(f"{k}: {v}\n")
        f.write("\n【商品图片】\n")
        for i, img in enumerate(images, 1):
            f.write(f"{i}. {img}\n")
    
    print(f"同时保存了纯文本版本到 {output_file.replace('.json', '.txt')}")
    
    # 为Windows命令行特别保存一份GBK编码的文本文件
    try:
        with open(output_file.replace('.json', '_gbk.txt'), 'w', encoding='gbk', errors='ignore') as f:
            f.write("【商品详情】\n")
            for k, v in cleaned_details.items():
                f.write(f"{k}: {v}\n")
            f.write("\n【商品图片】\n")
            for i, img in enumerate(images[:10], 1):
                f.write(f"{i}. {img}\n")
            if len(images) > 10:
                f.write(f"... 还有 {len(images) - 10} 张图片未显示\n")
        print(f"为Windows命令行保存了GBK编码的文本文件: {output_file.replace('.json', '_gbk.txt')}")
    except Exception as e:
        print(f"保存GBK编码文件失败: {e}")
    
    # 将主要信息输出到HTML文件中，以便在浏览器中查看
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>商品详情 - {cleaned_details.get('商品标题', '未知商品')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1 {{ color: #333; }}
                .info-box {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .price {{ color: #e4393c; font-size: 24px; font-weight: bold; }}
                .image-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }}
                .image-item {{ overflow: hidden; border-radius: 5px; }}
                .image-item img {{ width: 100%; height: auto; transition: transform 0.3s; }}
                .image-item img:hover {{ transform: scale(1.05); }}
                table {{ border-collapse: collapse; width: 100%; }}
                table, th, td {{ border: 1px solid #ddd; }}
                th, td {{ padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{cleaned_details.get('商品标题', '未知商品')}</h1>
            <div class="info-box">
                <p class="price">¥ {cleaned_details.get('价格', '价格未知')}</p>
                <p>销量: {cleaned_details.get('销量', '未知')}</p>
                <p>描述: {cleaned_details.get('详细描述', '无描述')}</p>
            </div>
            
            <h2>商品详情</h2>
            <table>
                <tr>
                    <th>属性</th>
                    <th>值</th>
                </tr>
        """
        
        for k, v in cleaned_details.items():
            if k not in ['商品标题', '价格', '销量', '详细描述']:
                html_content += f"""
                <tr>
                    <td>{k}</td>
                    <td>{v}</td>
                </tr>
                """
        
        html_content += """
            </table>
            
            <h2>商品图片</h2>
            <div class="image-grid">
        """
        
        for img in images:
            html_content += f"""
                <div class="image-item">
                    <a href="{img}" target="_blank">
                        <img src="{img}" alt="商品图片">
                    </a>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_file.replace('.json', '.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已生成HTML网页版本，方便在浏览器查看: {output_file.replace('.json', '.html')}")
    except Exception as e:
        print(f"生成HTML文件失败: {e}")

def extract_item_id(url):
    import re
    match = re.search(r'itemID=(\d+)', url)
    if match:
        return match.group(1)
    return ''

def save_to_new_xls(details, images, output_file, url):
    """将商品ID、商品详情和图片链接保存到新的Excel文件"""
    item_id = extract_item_id(url)
    wb = xlwt.Workbook()
    ws = wb.add_sheet('商品信息')
    # 写表头
    headers = ['商品ID'] + list(details.keys()) + ['图片链接']
    for col, h in enumerate(headers):
        ws.write(0, col, h)
    # 写内容
    ws.write(1, 0, item_id)
    for col, h in enumerate(details.keys()):
        ws.write(1, col + 1, details[h])
    ws.write(1, len(details) + 1, '\n'.join(images))
    wb.save(output_file)
    print(f"已保存到新的Excel文件: {output_file}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="爬取单个商品详情并更新到Excel文件")
    parser.add_argument("url", help="商品详情页URL")
    parser.add_argument("--download", "-d", choices=["yes", "no"], default="no", help="是否下载图片 (默认: no)")
    parser.add_argument("--excel", "-e", default="data/items_all.xls", help="要更新的Excel文件路径")
    parser.add_argument("--output", "-o", default="data/items_all_with_details.xls", help="输出Excel文件路径")
    parser.add_argument("--row", "-r", type=int, default=0, help="要更新的Excel行索引(从0开始)")
    parser.add_argument("--skip-excel", "-s", action="store_true", help="跳过更新Excel文件")
    parser.add_argument("--new-xls", help="将结果保存到新的Excel文件（不依赖原有Excel）")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    url = args.url
    download_imgs = args.download.lower() == "yes"
    
    # 输出系统编码信息
    import locale
    print(f"系统默认编码: {locale.getpreferredencoding()}")
    print(f"控制台编码: {sys.stdout.encoding}")
    print(f"Python默认编码: {sys.getdefaultencoding()}")
    
    print(f"开始爬取商品详情页: {url}")
    
    # 1. 常规方式提取
    html = fetch_detail_page(url)
    if not html:
        print("获取页面失败")
        return
    
    # 解析HTML
    html_details = parse_detail_page_html(html)
    images_from_html = extract_all_images(html)
    
    # 2. 使用API提取
    api_details = extract_detail_api(url)
    
    # 3. 使用Selenium提取更多内容
    selenium_details, selenium_images = extract_with_selenium(url)
    
    # 合并所有信息
    all_details = {**html_details, **api_details, **selenium_details}
    all_images = list(set(images_from_html + selenium_images))
    
    # 输出结果
    print("\n【商品详情主要字段】:")
    for k, v in all_details.items():
        if isinstance(v, str) and len(v) > 100:
            print(f"{k}: {v[:100]}...")
        else:
            print(f"{k}: {v}")
    
    print(f"\n【共提取到图片 {len(all_images)} 张】:")
    for img in all_images[:5]:  # 只显示前5张
        print(img)
    
    if len(all_images) > 5:
        print(f"... 还有 {len(all_images) - 5} 张图片未显示")
    
    # 保存到JSON文件
    save_details_to_json(all_details, all_images)
    
    if args.new_xls:
        save_to_new_xls(all_details, all_images, args.new_xls, url)
        return
    
    # 下载图片
    if download_imgs:
        download_images(all_images)
    else:
        print("\n未下载图片，仅保存了图片链接")
    
    # 更新Excel文件
    if not args.skip_excel:
        try:
            # 先检查update_excel.py是否存在
            if os.path.exists("update_excel.py"):
                print("\n正在将抓取的数据更新到Excel文件...")
                # 导入update_excel模块
                import update_excel
                # 使用非交互模式更新Excel
                success = update_excel.update_excel_with_details(
                    excel_file=args.excel,
                    output_file=args.output,
                    json_file="product_details.json",
                    row_index=args.row,
                    interactive=False
                )
                if success:
                    print(f"Excel文件更新完成! 数据已保存到: {args.output}")
                else:
                    print("Excel文件更新失败!")
            else:
                print("未找到update_excel.py文件，无法更新Excel")
        except Exception as e:
            print(f"更新Excel文件失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n您可以手动运行: python update_excel.py --excel {args.excel} --output {args.output} --row {args.row} --non-interactive")

if __name__ == "__main__":
    main() 