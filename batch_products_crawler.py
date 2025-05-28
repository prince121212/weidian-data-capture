import xlrd
import xlwt
import time
import os
from single_product_crawler import extract_item_id, fetch_detail_page, parse_detail_page_html, extract_detail_api, extract_all_images, extract_with_selenium

def batch_crawl(input_xls, url_column, output_xls, delay=2.0, use_selenium=True):
    """
    批量爬取商品详情
    
    参数:
    - input_xls: 输入的商品列表Excel文件
    - url_column: 包含商品链接的列名
    - output_xls: 输出的Excel文件
    - delay: 每个请求之间的延迟时间(秒)
    - use_selenium: 是否使用Selenium提取更多内容(速度较慢但信息更完整)
    """
    # 创建输出目录
    os.makedirs(os.path.dirname(output_xls), exist_ok=True)
    
    # 读取商品链接
    print(f"正在读取输入文件: {input_xls}")
    wb = xlrd.open_workbook(input_xls)
    sheet = wb.sheet_by_index(0)
    headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
    
    if url_column not in headers:
        print(f"错误: 未找到列 '{url_column}'")
        return
    
    url_idx = headers.index(url_column)
    all_rows = []
    all_keys = set()
    
    total_items = sheet.nrows - 1  # 排除表头
    print(f"共找到 {total_items} 个商品链接")
    
    # 临时文件，用于保存中间结果
    temp_output = output_xls.replace(".xls", "_temp.xls")
    
    for row in range(1, sheet.nrows):
        url = sheet.cell_value(row, url_idx)
        if not url or not isinstance(url, str) or not url.startswith('http'):
            print(f"跳过无效链接: 第 {row} 行")
            continue
        
        print(f"[{row}/{sheet.nrows-1}] 正在爬取: {url}")
        
        try:
            # 提取商品ID
            item_id = extract_item_id(url)
            
            # 1. 常规方式提取
            html = fetch_detail_page(url)
            if not html:
                print(f"获取页面失败: {url}")
                continue
            
            # 解析HTML
            html_details = parse_detail_page_html(html)
            images_from_html = extract_all_images(html)
            
            # 2. 使用API提取
            api_details = extract_detail_api(url)
            
            # 3. 使用Selenium提取更多内容 (可选)
            selenium_details = {}
            selenium_images = []
            if use_selenium:
                print("使用Selenium提取更多内容...")
                selenium_details, selenium_images = extract_with_selenium(url)
            
            # 合并所有信息
            all_details = {**html_details, **api_details, **selenium_details}
            all_images = list(set(images_from_html + selenium_images))
            
            # 输出结果摘要
            print(f"  - 提取到 {len(all_details)} 个详情字段")
            print(f"  - 提取到 {len(all_images)} 张图片链接")
            
            # 创建行数据
            row_dict = {'商品ID': item_id}
            row_dict.update(all_details)
            row_dict['图片链接'] = '\n'.join(all_images)
            
            # 添加到结果集
            all_rows.append(row_dict)
            all_keys.update(all_details.keys())
            
            # 每爬取5个商品保存一次临时结果
            if len(all_rows) % 5 == 0:
                save_to_xls(all_rows, all_keys, temp_output)
                print(f"已保存临时结果: {temp_output}")
            
            # 等待一段时间，避免请求过于频繁
            print(f"等待 {delay} 秒...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"处理商品失败: {url}, 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 写入最终结果
    if all_rows:
        save_to_xls(all_rows, all_keys, output_xls)
        print(f"已保存所有商品详情到: {output_xls}")
        
        # 删除临时文件
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except:
                pass
    else:
        print("未爬取到任何数据")

def save_to_xls(all_rows, all_keys, output_file):
    """保存结果到Excel文件"""
    wb_out = xlwt.Workbook()
    ws = wb_out.add_sheet('商品详情')
    
    # 固定字段顺序：首列是商品ID，最后一列是图片链接
    fixed_keys = ['商品ID', '商品标题', '价格', '销量', '详细描述']
    other_keys = sorted([k for k in all_keys if k not in fixed_keys])
    out_headers = fixed_keys + other_keys + ['图片链接']
    
    # 写入表头
    for col, h in enumerate(out_headers):
        ws.write(0, col, h)
    
    # 写入数据
    for row, row_dict in enumerate(all_rows, 1):
        for col, h in enumerate(out_headers):
            value = row_dict.get(h, '')
            if isinstance(value, (str, int, float, bool)):
                ws.write(row, col, value)
            else:
                ws.write(row, col, str(value))
    
    # 保存文件
    wb_out.save(output_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='批量爬取商品详情')
    parser.add_argument('--input', default='data/items_all.xls', help='输入商品列表xls')
    parser.add_argument('--column', default='商品详情页链接', help='商品详情页链接列名')
    parser.add_argument('--output', default='data/items_all_details.xls', help='输出xls文件名')
    parser.add_argument('--delay', type=float, default=2.0, help='每个商品间隔秒数')
    parser.add_argument('--no-selenium', action='store_true', help='不使用Selenium（更快但信息可能不完整）')
    args = parser.parse_args()
    batch_crawl(args.input, args.column, args.output, args.delay, use_selenium=not args.no_selenium) 