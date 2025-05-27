from bs4 import BeautifulSoup
import re

def parse_items(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    # 尝试查找商品卡片（常见 class 名有 item、goods、product 等）
    for div in soup.find_all(['div', 'li'], class_=re.compile(r'(item|goods|product)', re.I)):
        item = {}
        # 商品名称
        name = div.find(['span', 'div'], class_=re.compile(r'(name|title)', re.I))
        item['商品名称'] = name.get_text(strip=True) if name else ''
        # 价格
        price = div.find(['span', 'div'], class_=re.compile(r'(price|current)', re.I))
        item['价格'] = price.get_text(strip=True) if price else ''
        # 原价
        old_price = div.find(['span', 'div'], class_=re.compile(r'(old|origin|original)', re.I))
        item['原价'] = old_price.get_text(strip=True) if old_price else ''
        # 图片
        img = div.find('img')
        item['图片链接'] = img['src'] if img and img.has_attr('src') else ''
        # 商品详情页链接
        a = div.find('a', href=True)
        item['商品详情页链接'] = a['href'] if a else ''
        # 分类（如有）
        item['商品分类'] = ''
        # 其他字段可根据页面结构补充
        if item['商品名称']:
            items.append(item)
    return items 