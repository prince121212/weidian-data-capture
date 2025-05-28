# 微店数据采集工具

这是一个用于采集微店商品数据的工具，可以自动分析页面结构或接口，提取商品信息并保存为 Excel 表格。

## 功能特点

- 支持从 HTML 页面直接解析商品数据
- 支持自动分析并调用接口获取商品数据
- 采集商品名称、价格、图片、链接等完整信息
- 支持分页采集，可获取大量商品数据
- **支持全量采集功能，自动获取所有商品直到没有新数据**
- **支持爬取商品详情页，获取更多详细信息**
- 数据保存为 Excel 格式，方便查看和处理

## 环境要求

- Python 3.6+
- Chrome 浏览器（用于页面分析）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python main.py
```

### 高级用法（命令行参数）

```bash
# 指定店铺链接
python main.py -u "https://weidian.com/?userid=1286456178"

# 指定采集页数（每页约20条数据）
python main.py -p 10

# 采集全部商品（直到没有新数据）
python main.py -a
# 或者
python main.py -p 0

# 指定输出文件
python main.py -o "data/my_items.xls"

# 指定请求间隔时间（秒）
python main.py -d 2.0

# 组合使用
python main.py -u "https://weidian.com/?userid=1286456178" -a -o "data/items_all.xls" -d 1.5
```

```bash
# 实际使用：
#请求20页
python main.py -p 10 -o "data/items_full.xls" -d 1.5

#全量采集模式获取所有商品数据：
python main.py -a -o data/items_all.xls -d 2.0
```

### 爬取商品详情

完成商品列表采集后，可以使用以下命令爬取每个商品的详情页，获取更详细的信息：

```bash
# 基本用法 - 使用默认参数
python detail_crawler_main.py

# 指定输入输出文件
python detail_crawler_main.py -i "data/items_all.xls" -o "data/items_all_detailed.xls"

# 指定批量大小和延迟时间
python detail_crawler_main.py -b 5 -d 3.0

# 指定处理范围（只处理前10个商品）
python detail_crawler_main.py -s 0 -e 10

# 从之前中断的位置继续处理
python detail_crawler_main.py -s 50
```

### 详情爬取参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --input | -i | 输入的商品列表Excel文件 | data/items_all.xls |
| --output | -o | 输出的带详情Excel文件 | data/items_all_with_details.xls |
| --column | -c | 包含商品链接的列名 | 商品详情页链接 |
| --start | -s | 开始处理的商品索引(从0开始) | 0 |
| --end | -e | 结束处理的商品索引 | None(处理到结束) |
| --batch | -b | 每批处理的商品数量 | 10 |
| --delay | -d | 每个请求之间的延迟时间(秒) | 2.0 |
| --save_interval | -si | 多少批保存一次临时结果 | 1 |

### 查看帮助

```bash
python main.py -h
python detail_crawler_main.py -h
```

## 项目结构

```
weidian-data-capture/
├── README.md
├── requirements.txt
├── main.py                # 主程序入口（商品列表采集）
├── detail_crawler_main.py # 商品详情采集入口
├── crawler/
│   ├── fetcher.py         # 网页请求
│   ├── parser.py          # 数据解析
│   ├── pipelines.py       # 数据存储
│   ├── api_analyzer.py    # 接口分析
│   └── detail_crawler.py  # 商品详情爬取
└── data/                  # 数据存储目录
```

## 注意事项

- 首次运行时会自动下载 ChromeDriver
- 采集时请遵守网站的使用条款和爬虫协议
- 建议控制请求频率，避免对目标网站造成压力
- 不同的店铺页面结构可能不同，可能需要调整解析逻辑
- 采集大量数据时，程序会定期保存临时文件，防止意外中断导致数据丢失
- 商品详情爬取时，每批次处理后会保存临时文件，支持断点续爬功能 



完成本次任务的命令：
```bash
python batch_products_crawler.py --input data/items_all.xls --output data/items_all_details.xls
```