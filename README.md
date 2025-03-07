# Social Media Data Processor

## 简介
`social-media-data-processor` 是一个基于 PyQt5 开发的桌面应用程序，用于处理社交媒体数据。它提供了一系列功能，包括文件导入、词条筛选、根据词条筛选数据集、数据溯源以及复现社交媒体发帖的层次结构。




## 功能特性
1. **文件导入**  
   - 支持选择多个文件（NDJSON 格式）
   - 实时显示文件路径和处理状态

2. **词条筛选**  
   - 统计 `hashtags` 字段出现次数并按降序排列
   - 自动生成 CSV 统计报告

3. **词条选择**  
   - 支持多选和分页浏览（每页 50 条）
   - 提供搜索功能快速定位词条

4. **数据集筛选**  
   - 根据选中词条过滤数据
   - 生成新的筛选后数据文件

5. **数据溯源**  
   - 查找数据项的完整父级链
   - 生成包含所有关联数据的溯源文件

6. **层次结构复现**  
   - 生成缩进式文本结构
   - 使用 Graphviz 生成可视化树状图
   
   

## 安装与使用

### 依赖环境

- Python 3.8+
- PyQt5 >= 5.15
- graphviz >= 0.20

```bash
pip install PyQt5 graphviz
```



## 代码结构

```plaintext
social-media-data-processor/
├── main.py          # 主窗口逻辑与界面布局
├── functions.py     # 核心业务逻辑实现
└── README.md        # 项目说明文档
```
