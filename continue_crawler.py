import xlrd
import xlwt
import time
import os
from single_product_crawler import extract_item_id, fetch_detail_page, parse_detail_page_html, extract_detail_api, extract_all_images, extract_with_selenium

def normalize_id(val):
    val = str(val).strip()
    if '.' in val:
        val = val.split('.')[0]
    return val

def get_last_crawled_id(details_xls):
    wb = xlrd.open_workbook(details_xls)
    sheet = wb.sheet_by_index(0)
    headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
    if '商品ID' not in headers:
        return None
    id_idx = headers.index('商品ID')
    last_id = None
    for row in range(1, sheet.nrows):
        val = normalize_id(sheet.cell_value(row, id_idx))
        if val:
            last_id = val
    return last_id

def read_existing_rows(details_xls):
    wb = xlrd.open_workbook(details_xls)
    sheet = wb.sheet_by_index(0)
    headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
    rows = []
    for row in range(1, sheet.nrows):
        row_dict = {h: sheet.cell_value(row, idx) for idx, h in enumerate(headers)}
        rows.append(row_dict)
    return headers, rows

def continue_crawl(input_xls, url_column, details_xls, output_xls, delay=2.0, use_selenium=True):
    # 读取已爬取的最后一个商品ID
    last_id = get_last_crawled_id(details_xls)
    print(f"已爬取到的最后商品ID: {last_id}")
    
    # 读取已存在的详情数据
    exist_headers, exist_rows = read_existing_rows(details_xls)
    exist_ids = set(normalize_id(row['商品ID']) for row in exist_rows)
    
    # 读取原始商品链接
    wb = xlrd.open_workbook(input_xls)
    sheet = wb.sheet_by_index(0)
    headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
    url_idx = headers.index(url_column)
    
    # 找到断点位置
    start = False if last_id else True
    to_crawl = []
    for row in range(1, sheet.nrows):
        url = sheet.cell_value(row, url_idx)
        item_id = normalize_id(extract_item_id(url))
        print(f"调试: 当前item_id={item_id}, last_id={last_id}")
        if not url or not isinstance(url, str) or not url.startswith('http'):
            continue
        if not start:
            if item_id == last_id:
                start = True
            continue
        if item_id in exist_ids:
            continue
        to_crawl.append((item_id, url))
    print(f"本次需要继续爬取 {len(to_crawl)} 个商品")
    
    # 爬取新数据
    new_rows = []
    all_keys = set()
    for idx, (item_id, url) in enumerate(to_crawl, 1):
        print(f"[{idx}/{len(to_crawl)}] 正在爬取: {url}")
        try:
            html = fetch_detail_page(url)
            if not html:
                print(f"获取页面失败: {url}")
                continue
            html_details = parse_detail_page_html(html)
            images_from_html = extract_all_images(html)
            api_details = extract_detail_api(url)
            selenium_details = {}
            selenium_images = []
            if use_selenium:
                print("使用Selenium提取更多内容...")
                selenium_details, selenium_images = extract_with_selenium(url)
            all_details = {**html_details, **api_details, **selenium_details}
            all_images = list(set(images_from_html + selenium_images))
            row_dict = {'商品ID': item_id}
            row_dict.update(all_details)
            row_dict['图片链接'] = '\n'.join(all_images)
            new_rows.append(row_dict)
            all_keys.update(all_details.keys())
            print(f"  - 提取到 {len(all_details)} 个详情字段, {len(all_images)} 张图片链接")
            print(f"等待 {delay} 秒...")
            time.sleep(delay)
        except Exception as e:
            print(f"处理商品失败: {url}, 错误: {e}")
            import traceback
            traceback.print_exc()
    # 合并所有字段
    all_keys.update(h for h in exist_headers if h not in ['商品ID', '图片链接'])
    # 写入新Excel
    save_to_xls(exist_rows, new_rows, all_keys, output_xls)
    print(f"已合并并保存所有商品详情到: {output_xls}")

def save_to_xls(exist_rows, new_rows, all_keys, output_file):
    wb_out = xlwt.Workbook()
    ws = wb_out.add_sheet('商品详情')
    fixed_keys = ['商品ID', '商品标题', '价格', '销量', '详细描述']
    other_keys = sorted([k for k in all_keys if k not in fixed_keys])
    out_headers = fixed_keys + other_keys + ['图片链接']
    for col, h in enumerate(out_headers):
        ws.write(0, col, h)
    all_rows = exist_rows + new_rows
    for row, row_dict in enumerate(all_rows, 1):
        for col, h in enumerate(out_headers):
            value = row_dict.get(h, '')
            if isinstance(value, (str, int, float, bool)):
                ws.write(row, col, value)
            else:
                ws.write(row, col, str(value))
    wb_out.save(output_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='断点续爬商品详情')
    parser.add_argument('--input', default='data/items_all.xls', help='原始商品列表xls')
    parser.add_argument('--column', default='商品详情页链接', help='商品详情页链接列名')
    parser.add_argument('--details', default='data/items_all_details.xls', help='已爬取详情xls')
    parser.add_argument('--output', default='data/items_all_details_new.xls', help='合并输出xls')
    parser.add_argument('--delay', type=float, default=2.0, help='每个商品间隔秒数')
    parser.add_argument('--no-selenium', action='store_true', help='不使用Selenium（更快但信息可能不完整）')
    args = parser.parse_args()
    continue_crawl(args.input, args.column, args.details, args.output, args.delay, use_selenium=not args.no_selenium) 