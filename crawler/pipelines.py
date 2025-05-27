import xlwt

def save_to_xls(items, filename):
    if not items:
        print("没有商品数据可保存！")
        return
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Items')
    # 写表头
    headers = list(items[0].keys())
    for col, h in enumerate(headers):
        sheet.write(0, col, h)
    # 写数据
    for row, item in enumerate(items, 1):
        for col, h in enumerate(headers):
            sheet.write(row, col, item.get(h, ''))
    workbook.save(filename) 