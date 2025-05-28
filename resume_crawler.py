import xlrd
import xlwt
import time
import os
import argparse
from single_product_crawler import extract_item_id, fetch_detail_page, parse_detail_page_html, extract_detail_api, extract_all_images, extract_with_selenium
from xlutils.copy import copy as xl_copy # To avoid confusion with os.copy

def normalize_id(val):
    val = str(val).strip()
    if '.' in val:
        val = val.split('.')[0]
    return val

def read_existing_details(details_xls_path):
    """Reads existing crawled details from an XLS file."""
    if not os.path.exists(details_xls_path):
        return [], [], set() # headers, rows, existing_ids

    wb = xlrd.open_workbook(details_xls_path, formatting_info=True)
    sheet = wb.sheet_by_index(0)
    
    headers = []
    if sheet.nrows > 0:
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
    
    rows = []
    existing_ids = set()
    
    id_column_index = -1
    if '商品ID' in headers:
        id_column_index = headers.index('商品ID')

    for row_idx in range(1, sheet.nrows):
        row_dict = {}
        for col_idx, header in enumerate(headers):
            row_dict[header] = sheet.cell_value(row_idx, col_idx)
        rows.append(row_dict)
        if id_column_index != -1 and '商品ID' in row_dict:
            item_id_val = row_dict.get('商品ID')
            if item_id_val is not None:
                existing_ids.add(normalize_id(item_id_val))
                
    print(f"读取到 {len(rows)} 条已存在的详情数据， {len(existing_ids)} 个已处理的商品ID。")
    return headers, rows, existing_ids

def resume_crawl(input_xls, url_column, output_xls, start_index, delay=2.0, use_selenium=True):
    """
    Resumes crawling product details from a specific start index.
    """
    print(f"开始从索引 {start_index} 继续爬取...")
    os.makedirs(os.path.dirname(output_xls), exist_ok=True)

    # 1. Read existing details from the output file if it exists
    # This helps in merging new data with previously crawled data.
    # If output_xls is the same as the interrupted details_xls, this will load its content.
    existing_headers, existing_rows, crawled_item_ids = read_existing_details(output_xls)
    
    # If existing_headers is empty and output_xls existed, it might mean it was an empty/header-only file.
    # For a fresh run where output_xls might not exist or is new, existing_headers will be empty.
    
    all_processed_rows = list(existing_rows) # Start with existing data
    all_keys = set(existing_headers) if existing_headers else set(['商品ID', '图片链接'])


    # 2. Read the main product list
    print(f"正在读取原始商品列表: {input_xls}")
    try:
        wb_input = xlrd.open_workbook(input_xls)
        sheet_input = wb_input.sheet_by_index(0)
        input_headers = [sheet_input.cell_value(0, col) for col in range(sheet_input.ncols)]
    except FileNotFoundError:
        print(f"错误: 输入文件 {input_xls} 未找到。")
        return
    except xlrd.XLRDError as e:
        print(f"错误: 读取输入文件 {input_xls} 失败: {e}")
        return

    if url_column not in input_headers:
        print(f"错误: 在 {input_xls} 中未找到列 '{url_column}'。 可用列: {input_headers}")
        return
    url_idx = input_headers.index(url_column)

    total_items_in_input = sheet_input.nrows - 1 # Exclude header
    print(f"原始商品列表中共有 {total_items_in_input} 个商品。")

    items_to_crawl_this_session = []

    # 3. Determine items to crawl
    # We start from row 1 (after header) in the input XLS.
    # The start_index is 0-based for items, so it corresponds to row start_index + 1 in XLS.
    for row_num in range(1, sheet_input.nrows): # Iterate through all items in input_xls
        current_item_index = row_num - 1 # 0-based index
        
        if current_item_index < start_index:
            continue # Skip items before the start_index

        url = sheet_input.cell_value(row_num, url_idx)
        if not url or not isinstance(url, str) or not url.startswith('http'):
            print(f"第 {row_num} 行 (索引 {current_item_index}) 的链接无效，跳过: {url}")
            continue
        
        item_id = extract_item_id(url) # Assumes extract_item_id is robust
        if not item_id:
            print(f"警告: 无法从URL {url} (第 {row_num} 行) 提取商品ID。跳过此商品。")
            continue
        
        normalized_item_id = normalize_id(item_id)

        # Check if this item_id was already crawled (e.g., if output_xls had some data)
        if normalized_item_id in crawled_item_ids:
            print(f"商品ID {normalized_item_id} (来自 {url}) 已存在于输出文件中，跳过爬取。")
            continue
            
        items_to_crawl_this_session.append({'url': url, 'id': normalized_item_id, 'original_row': row_num})

    if not items_to_crawl_this_session:
        print("没有需要爬取的新商品。")
        if all_processed_rows: # If there was existing data, resave it.
             print(f"将已有的 {len(all_processed_rows)} 条数据保存到 {output_xls}")
             save_data_to_xls(all_processed_rows, all_keys, output_xls)
        return

    print(f"找到 {len(items_to_crawl_this_session)} 个商品需要从此会话开始爬取 (从索引 {start_index} 开始)。")
    
    temp_output_xls = output_xls.replace(".xls", "_temp_resume.xls")

    # 4. Crawl new data
    newly_crawled_rows_this_session = []
    for i, item_info in enumerate(items_to_crawl_this_session):
        url = item_info['url']
        item_id = item_info['id']
        original_row_num = item_info['original_row']
        
        print(f"[{i+1}/{len(items_to_crawl_this_session)}] (原始文件行号 {original_row_num}) 正在爬取: {url}")
        
        try:
            html_content = fetch_detail_page(url)
            if not html_content:
                print(f"  获取页面内容失败: {url}")
                continue

            html_details = parse_detail_page_html(html_content)
            images_from_html = extract_all_images(html_content)
            api_details = extract_detail_api(url) # Assuming this function handles potential failures

            selenium_details = {}
            selenium_images = []
            if use_selenium:
                print("  使用Selenium提取更多内容...")
                # Ensure extract_with_selenium can handle problematic URLs gracefully
                s_details, s_images = extract_with_selenium(url)
                if s_details: selenium_details.update(s_details)
                if s_images: selenium_images.extend(s_images)

            combined_details = {**html_details, **api_details, **selenium_details}
            all_images_list = list(set(images_from_html + selenium_images))

            row_data = {'商品ID': item_id} # Ensure '商品ID' is the normalized one
            row_data.update(combined_details)
            row_data['图片链接'] = '\n'.join(all_images_list)
            
            # Add all original columns from input_xls for this item, if not already present from crawling
            # This ensures that if crawling doesn't pick up some fields present in input_xls, they are not lost.
            # However, typical detail crawlers focus on *new* details, not copying old ones.
            # For now, we mainly focus on crawled details.

            newly_crawled_rows_this_session.append(row_data)
            all_keys.update(row_data.keys()) # Update global keys set

            print(f"  - 提取到 {len(combined_details)} 个详情字段, {len(all_images_list)} 张图片链接。")

            # Save intermediate results periodically
            if (i + 1) % 5 == 0 or (i + 1) == len(items_to_crawl_this_session) :
                current_snapshot_data = list(all_processed_rows) + newly_crawled_rows_this_session
                save_data_to_xls(current_snapshot_data, all_keys, temp_output_xls)
                print(f"  已保存临时结果 ({len(current_snapshot_data)} 条) 到: {temp_output_xls}")

            if delay > 0:
                print(f"  等待 {delay} 秒...")
                time.sleep(delay)

        except Exception as e:
            print(f"  处理商品 {url} (ID: {item_id}) 时发生错误: {e}")
            import traceback
            traceback.print_exc()
            # Optionally, add a placeholder for this failed item or skip
            # For now, it's skipped, and it won't be in newly_crawled_rows_this_session

    # 5. Combine existing and newly crawled data
    all_processed_rows.extend(newly_crawled_rows_this_session)

    # 6. Save final results
    if all_processed_rows: # Check if there's any data to save
        save_data_to_xls(all_processed_rows, all_keys, output_xls)
        print(f"完成! 总共 {len(all_processed_rows)} 条商品详情已保存到: {output_xls}")
        if os.path.exists(temp_output_xls):
            try:
                os.remove(temp_output_xls)
                print(f"已删除临时文件: {temp_output_xls}")
            except OSError as e:
                print(f"删除临时文件 {temp_output_xls} 失败: {e}")
    else:
        print("没有爬取到任何新的数据，也无旧数据可保存。")


def save_data_to_xls(data_rows, all_header_keys, output_file_path):
    """
    Saves a list of dictionaries (data_rows) to an XLS file.
    all_header_keys is a set of all possible keys encountered.
    """
    wb_out = xlwt.Workbook(encoding='utf-8')
    ws = wb_out.add_sheet('商品详情')

    # Define a preferred order for headers, putting known important ones first
    # '商品ID' must be present.
    preferred_order = ['商品ID', '商品标题', '价格', '销量', 'SKU信息', '库存', '运费', '商品链接', '商品描述', '评价数量', '店铺名称', '图片链接']
    
    # Start with preferred headers that are actually in all_header_keys
    headers = [h for h in preferred_order if h in all_header_keys]
    # Add any other keys not in preferred_order, sorted for consistency
    remaining_keys = sorted(list(all_header_keys - set(headers)))
    final_headers = headers + remaining_keys

    # Ensure '商品ID' is the very first column if it exists
    if '商品ID' in final_headers:
        final_headers.insert(0, final_headers.pop(final_headers.index('商品ID')))
        # Remove duplicates if '商品ID' was already in preferred_order at the start
        final_headers = sorted(set(final_headers), key=final_headers.index)


    for col_idx, header_name in enumerate(final_headers):
        ws.write(0, col_idx, header_name)

    for row_idx, data_item in enumerate(data_rows, 1):
        for col_idx, header_name in enumerate(final_headers):
            value = data_item.get(header_name, '') # Get value or empty string if key missing
            if isinstance(value, list) or isinstance(value, set): # e.g. image links
                value = '\n'.join(map(str,value))
            elif not isinstance(value, (str, int, float, bool)):
                value = str(value) # Convert other types to string
            
            # XLS cell character limit (xlwt specific)
            if len(value) > 32767:
                value = value[:32767] # Truncate if too long
            ws.write(row_idx, col_idx, value)
    
    try:
        wb_out.save(output_file_path)
    except Exception as e:
        print(f"保存Excel文件 {output_file_path} 失败: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='从指定索引开始断点续爬商品详情')
    parser.add_argument('--input', default='data/items_all.xls', 
                        help='包含商品链接的原始Excel文件路径 (例如 data/items_all.xls)')
    parser.add_argument('--url_column', default='商品详情页链接', 
                        help='在输入Excel中包含商品URL的列名')
    parser.add_argument('--output', default='data/items_all_details_resumed.xls',
                        help='输出Excel文件路径 (例如 data/items_all_details.xls or a new file)')
    parser.add_argument('--start_index', type=int, required=True,
                        help='要开始爬取的商品在输入文件中的0基索引 (例如 159 表示从第160条商品开始)')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='每个商品爬取之间的延迟时间（秒）')
    parser.add_argument('--use_selenium', action='store_true', default=False,
                        help='是否使用Selenium进行补充爬取 (可能更慢但信息更全, 默认不使用)')
    parser.add_argument('--no_selenium', action='store_false', dest='use_selenium',
                        help='明确不使用Selenium')


    args = parser.parse_args()

    if args.start_index < 0:
        parser.error("--start_index 不能为负数。")

    resume_crawl(
        input_xls=args.input,
        url_column=args.url_column,
        output_xls=args.output,
        start_index=args.start_index,
        delay=args.delay,
        use_selenium=args.use_selenium
    ) 