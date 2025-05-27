# 微店数据采集工具

这是一个用于采集微店商品数据的工具，可以自动分析页面结构或接口，提取商品信息并保存为 Excel 表格。

## 功能特点

- 支持从 HTML 页面直接解析商品数据
- 支持自动分析并调用接口获取商品数据
- 采集商品名称、价格、图片、链接等完整信息
- 数据保存为 Excel 格式，方便查看和处理

## 环境要求

- Python 3.6+
- Chrome 浏览器（用于页面分析）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 安装依赖
2. 运行主程序

```bash
python main.py
```

3. 查看结果：数据将保存在 `data/items.xls`

## 项目结构

```
weidian-data-capture/
├── README.md
├── requirements.txt
├── main.py                # 主程序入口
├── crawler/
│   ├── fetcher.py         # 网页请求
│   ├── parser.py          # 数据解析
│   ├── pipelines.py       # 数据存储
│   └── api_analyzer.py    # 接口分析
└── data/                  # 数据存储目录
```

## 注意事项

- 首次运行时会自动下载 ChromeDriver
- 采集时请遵守网站的使用条款和爬虫协议
- 建议控制请求频率，避免对目标网站造成压力 