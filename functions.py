# -*- coding: UTF-8 -*-
"""
@Project ：Pyqt
@File    ：functions.py
@IDE     ：PyCharm 
@Author  ：xiaomu-258
@Date    ：2025/1/27 21:09 
"""

import csv
import json
import os
from collections import defaultdict
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem,QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLineEdit, QHBoxLayout, QPushButton
from collections import OrderedDict
from graphviz import Digraph
import random

def import_file(main_window):
    """
    处理导入文件逻辑（支持多文件选择）
    :param main_window: 主窗口对象，传入以操作界面元素
    """
    file_dialog = QFileDialog()
    # 允许选择多个文件
    file_paths, _ = file_dialog.getOpenFileNames(main_window, "选择文件", "", "所有文件 (*.*)")
    if file_paths:
        # 将文件路径存储到 main_window 中，方便后续使用
        main_window.imported_files = file_paths  # 新增保存文件路径的属性
        # 遍历每个选中的文件
        for file_path in file_paths:
            main_window.log_text.append(f"导入文件: {file_path}")
            add_file_to_table(main_window, file_path)


def filter_words(main_window):
    """
    处理筛选词条逻辑（统计hashtag并按出现次数降序排列）
    """
    # 获取之前通过导入文件选择的文件列表
    if not hasattr(main_window, 'imported_files') or not main_window.imported_files:
        main_window.log_text.append("没有导入文件，请先选择文件。")
        return

    main_window.log_text.append("正在统计 hashtags 字段出现次数...")

    hashtag_counts = defaultdict(int)

    total_files = len(main_window.imported_files)

    # 遍历导入的所有文件进行统计
    for idx, file_path in enumerate(main_window.imported_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():  # 检查是否为空行
                        entry = json.loads(line.strip())

                        # 获取 hashtags 字段
                        hashtags = entry.get('hashtags', [])

                        # 统计每个 tag 的出现次数
                        for tag in hashtags:
                            hashtag_counts[tag] += 1
        except Exception as e:
            main_window.log_text.append(f"文件 {file_path} 读取出错: {str(e)}")
            continue

        # 更新进度条：已处理文件数 / 总文件数
        progress = int(((idx + 1) / total_files) * 100)
        main_window.progress_bar.setValue(progress)

    # 将结果排序并保存
    sorted_hashtag_counts = sorted(hashtag_counts.items(), key=lambda item: item[1], reverse=True)

    # 设置表格列数为2，只保留 "词条名称" 和 "出现次数" 两列
    main_window.file_table.setColumnCount(2)

    # 修改表格列名为 "词条名称" 和 "出现次数"
    main_window.file_table.setHorizontalHeaderLabels(["词条名称", "出现次数"])

    # 显示结果
    main_window.log_text.append(f"已找到 {len(sorted_hashtag_counts)} 个不同的 hashtags，并按出现次数排序")
    display_sorted_hashtags(main_window, sorted_hashtag_counts)

    # 将排序结果保存为 CSV 文件
    save_hashtags_to_csv(main_window, sorted_hashtag_counts)


def save_hashtags_to_csv(main_window, sorted_hashtag_counts):
    """
    保存 hashtags 统计结果到 CSV 文件
    :param main_window: 主窗口对象
    :param sorted_hashtag_counts: 排序后的 hashtag 列表（元组）
    """
    if not main_window.imported_files:
        main_window.log_text.append("没有导入文件，无法保存 CSV。")
        return

    # 使用导入的第一个文件路径作为保存 CSV 文件的路径
    output_file = main_window.imported_files[0]
    output_file = output_file.rsplit('.', 1)[0] + "_hashtag_counts.csv"  # 修改文件名

    # 将结果写入 CSV 文件
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Hashtag', 'Count'])  # 写入表头
        for hashtag, count in sorted_hashtag_counts:
            writer.writerow([hashtag, count])  # 写入数据

    main_window.log_text.append(f"Hashtag 统计结果已保存到 {output_file}")


def selecttag_data(self):
    """
    选择词条的逻辑：弹出窗口供用户选择一个或多个筛选后的词条，带有搜索和分页功能
    """
    if not hasattr(self, 'imported_files') or not self.imported_files:
        self.log_text.append("没有导入文件，请先选择文件。")
        return

    # 获取词条筛选后的结果
    sorted_hashtag_counts = []  # 这里应该是从筛选结果中获取的词条和计数
    for row in range(self.file_table.rowCount()):
        hashtag = self.file_table.item(row, 0).text()  # 获取词条名称
        sorted_hashtag_counts.append(hashtag)

    # 限制每页显示词条的数量
    items_per_page = 50  # 每页显示50个词条
    total_items = len(sorted_hashtag_counts)
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page != 0 else 0)

    # 当前页码
    current_page = 1

    # 弹出窗口显示所有词条并让用户选择
    dialog = QDialog(self)
    dialog.setWindowTitle("选择词条")

    layout = QVBoxLayout(dialog)

    # 搜索框
    search_layout = QHBoxLayout()
    search_label = QLineEdit(dialog)
    search_label.setPlaceholderText("搜索词条...")
    search_layout.addWidget(search_label)

    # 创建一个列表框显示所有筛选的词条
    list_widget = QListWidget(dialog)
    list_widget.addItems(sorted_hashtag_counts[:items_per_page])
    list_widget.setSelectionMode(QListWidget.MultiSelection)  # 支持多选

    # 页码标签
    page_label = QPushButton(f"Page {current_page} / {total_pages}", dialog)

    # 翻页按钮
    prev_button = QPushButton("上一页", dialog)
    next_button = QPushButton("下一页", dialog)

    def update_page():
        # 更新当前页显示的内容
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        list_widget.clear()
        list_widget.addItems(sorted_hashtag_counts[start_idx:end_idx])
        page_label.setText(f"Page {current_page} / {total_pages}")

    def prev_page():
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            update_page()

    def next_page():
        nonlocal current_page
        if current_page < total_pages:
            current_page += 1
            update_page()

    prev_button.clicked.connect(prev_page)
    next_button.clicked.connect(next_page)

    # 绑定搜索功能
    def search_text():
        search_term = search_label.text().lower()
        filtered_items = [item for item in sorted_hashtag_counts if search_term in item.lower()]
        list_widget.clear()
        list_widget.addItems(filtered_items)

    search_label.textChanged.connect(search_text)

    # 创建按钮：确认和取消
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
    layout.addLayout(search_layout)
    layout.addWidget(list_widget)
    layout.addWidget(page_label)
    layout.addWidget(prev_button)
    layout.addWidget(next_button)
    layout.addWidget(button_box)

    # 绑定按钮事件
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    # 显示对话框
    if dialog.exec_() == QDialog.Accepted:
        self.selected_tags = [item.text() for item in list_widget.selectedItems()]
        self.log_text.append(f"选中的词条: {', '.join(self.selected_tags)}")

def add_file_to_table(main_window, file_name):
    """
    向表格中添加文件信息
    :param main_window: 主窗口对象
    :param file_name: 文件路径
    """
    row = main_window.file_table.rowCount()
    main_window.file_table.insertRow(row)
    main_window.file_table.setItem(row, 0, QTableWidgetItem(file_name))
    main_window.file_table.setItem(row, 1, QTableWidgetItem("未筛选"))
    main_window.file_table.setItem(row, 2, QTableWidgetItem("未还原"))


def display_sorted_hashtags(main_window, sorted_hashtag_counts):
    """
    将排序后的 hashtags 显示在表格中
    :param main_window: 主窗口对象
    :param sorted_hashtag_counts: 排序后的 hashtag 列表（元组）
    """
    # 清空已有内容
    main_window.file_table.setRowCount(0)

    # 添加排序后的 hashtags 到表格
    for idx, (hashtag, count) in enumerate(sorted_hashtag_counts):
        row = main_window.file_table.rowCount()
        main_window.file_table.insertRow(row)
        main_window.file_table.setItem(row, 0, QTableWidgetItem(hashtag))  # 词条名称
        main_window.file_table.setItem(row, 1, QTableWidgetItem(str(count)))  # 出现次数


def filter_hashtags_data(self):
    """
    根据用户挑选的tag词条来筛选数据集文件中“hashtags”字段中符合条件的数据
    并将所有符合条件的数据保存到新文件中
    """
    # 获取用户选择的词条
    if not hasattr(self, 'imported_files') or not self.imported_files:
        self.log_text.append("没有导入文件，请先选择文件。")
        return

    # 确保 selected_tags 已经正确赋值
    if not hasattr(self, 'selected_tags') or not self.selected_tags:
        self.log_text.append("没有选择词条进行筛选。")
        return

    selected_tags = self.selected_tags  # 使用 self.selected_tags 作为筛选依据
    data_files = self.imported_files  # 获取导入的文件路径

    filtered_data = []

    # 遍历数据集文件进行筛选
    try:
        for file_path in data_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        hashtags = entry.get('hashtags', [])
                        if any(tag in selected_tags for tag in hashtags):
                            filtered_data.append(entry)
    except Exception as e:
        self.log_text.append(f"读取文件时发生错误: {str(e)}")

    if not filtered_data:
        self.log_text.append("没有符合条件的数据。")
        return

    # 根据用户上传的文件路径生成新的文件名
    original_file_path = data_files[0]  # 使用第一个文件的路径作为参考
    file_dir = os.path.dirname(original_file_path)  # 获取文件所在目录
    base_name = os.path.basename(original_file_path)  # 获取文件名
    output_file = os.path.join(file_dir, f"{os.path.splitext(base_name)[0]}_filtered_data.json")

    # 保存筛选后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=4)

    self.filtered_file = output_file  # 将保存的文件路径存储为实例属性
    self.log_text.append(f"符合条件的数据已保存到 {output_file}")

def trace_data(self):
    """
    溯源数据：对新保存的文件在上传的数据集中进行溯源，寻找所有的 parent 数据
    """
    # 获取用户上传的数据集路径和新保存的文件路径
    if not hasattr(self, 'imported_files') or not self.imported_files:
        self.log_text.append("没有导入文件，请先选择文件。")
        return

    if not hasattr(self, 'filtered_file') or not self.filtered_file:
        self.log_text.append("没有保存的筛选文件，请先进行筛选。")
        return

    # 访问保存的筛选文件路径
    filtered_file_path = self.filtered_file
    # filtered_file_path = "filtered.json"
    self.log_text.append(f"读取筛选后的文件: {filtered_file_path}")

    # 读取筛选后的数据
    try:
        with open(filtered_file_path, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        self.log_text.append(f"成功读取 {len(filtered_data)} 条筛选数据")
    except Exception as e:
        self.log_text.append(f"读取筛选文件时发生错误: {str(e)}")
        return

    # 获取原始数据集文件路径
    data_file_path = self.imported_files
    # data_file_path = "test.json"

    # 确保只有一个文件路径，或者选取列表中的第一个文件路径
    if isinstance(data_file_path, list) and data_file_path:
        data_file_path = data_file_path[0]  # 取列表中的第一个文件路径
    else:
        self.log_text.append("没有有效的原始数据文件路径")
        return

    self.log_text.append(f"读取原始数据文件: {data_file_path}")

    # 读取原始数据（逐行处理 NDJSON 格式）
    original_data = []
    try:
        with open(data_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # 跳过空行
                    original_data.append(json.loads(line.strip()))  # 逐行解析 JSON
        self.log_text.append(f"成功读取 {len(original_data)} 条原始数据")
    except Exception as e:
        self.log_text.append(f"读取原始数据文件时发生错误: {str(e)}")
        return

    # 构建ID到数据项的映射
    id_map = {item['id']: item for item in original_data}

    # 定义查找根帖子的函数
    def find_root_post(item, id_map):
        visited = set()
        current_item = item
        while True:
            # 检查循环引用
            if current_item['id'] in visited:
                return None
            visited.add(current_item['id'])

            if current_item['datatype'] == 'posts':
                # 处理帖子类型
                if 'parent' not in current_item:
                    return current_item  # 原始帖子
                else:
                    parent_id = current_item['parent']
                    if parent_id not in id_map:
                        return None
                    current_item = id_map[parent_id]
            elif current_item['datatype'] == 'comments':
                # 处理评论类型
                post_id = current_item.get('post')
                if post_id not in id_map:
                    return None
                current_item = id_map[post_id]
            else:
                return None  # 未知数据类型

    # 处理筛选文件中的每条数据
    filtered_roots = set()
    for item in filtered_data:
        root_item = find_root_post(item, id_map)
        if not root_item:
            self.log_text.append(f"错误：无法为数据项 {item.get('id', '未知ID')} 找到根帖子")
            return
        if root_item['id'] not in id_map:
            self.log_text.append(f"错误：根帖子 {root_item['id']} 不存在于原始数据中")
            return
        filtered_roots.add(root_item['id'])

    # 构建根帖子的反向映射
    root_map = {}
    for item in original_data:
        root = find_root_post(item, id_map)
        root_map[item['id']] = root['id'] if root else None

    # 收集所有相关数据
    result_ids = set()
    for root_id in filtered_roots:
        # 直接添加根帖子
        result_ids.add(root_id)
        # 收集所有关联数据项
        for item_id in root_map:
            if root_map[item_id] == root_id:
                result_ids.add(item_id)

    # 获取最终数据并去重
    unique_merged_data = [id_map[item_id] for item_id in result_ids if item_id in id_map]

    # 保存结果部分（用户原有代码）
    original_file_path = data_file_path  # 修正变量名
    file_dir = os.path.dirname(original_file_path)
    base_name = os.path.basename(original_file_path)
    output_file = os.path.join(file_dir, f"{os.path.splitext(base_name)[0]}_traced_data.json")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_merged_data, f, indent=4)
        self.log_text.append(f"溯源后的数据已保存到 {output_file}")
        self.traced_file = output_file
    except Exception as e:
        self.log_text.append(f"保存溯源文件时发生错误: {str(e)}")

def reconstruct_structure(self):
    """
    复现原始的社交媒体发帖层次结构：按发帖时间排序，评论和回复关系用缩进表示
    """
    # 获取用户上传的文件路径
    if not hasattr(self, 'imported_files') or not self.imported_files:
        self.log_text.append("没有导入文件，请先选择文件。")
        return

    data_files = self.traced_file  # 获取导入的数据集文件路径

    # 示例：从JSON文件读取数据
    with open(data_files,'r', encoding='utf-8') as file:
        try:
            data = json.load(file)  # 使用 json.load 读取整个文件
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            data = []  # 如果解析失败，给出空列表

    # --- 新功能: build_tree 和 print_tree 功能添加在这里 ---

    def build_tree(data):
        """构建树形结构"""
        tree = {}
        for item in data:
            tree[item['id']] = item

        roots = []  # 根节点
        for item in data:
            parent_id = item.get('parent')
            if parent_id and parent_id in tree:
                parent = tree[parent_id]
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(item)
            else:
                roots.append(item)

        # **移除所有独立节点**
        cleaned_roots = []
        for node in roots:
            if 'children' in node or any(item.get('parent') == node['id'] for item in data):
                cleaned_roots.append(node)

        return cleaned_roots

    # 构建树形结构
    tree = build_tree(data)

    # 打印树形结构
    def print_tree(nodes, level=0, output_file=None):
        """打印树形结构，并保存到文件"""
        lines = []

        def recursive_print(node, level):
            is_forwarded = node.get('datatype') == 'posts' and node.get('parent')
            username = node.get('username', 'Unknown')
            body = node.get('body', '')
            createdAtformatted = node.get('createdAtformatted', '')
            node_id = node.get('id', 'Unknown')

            line = '  ' * level + (
                f"[转发] {username}: {body} {createdAtformatted}" if is_forwarded else f"{username}: {body} {createdAtformatted}")
            # print(line)
            lines.append(line)

            if 'children' in node:
                for child in node['children']:
                    recursive_print(child, level + 1)

        for node in nodes:
            recursive_print(node, level)

        # 将树形结构保存到文件
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                self.log_text.append(f"复现的层次结构已保存到 {output_file}")
            except Exception as e:
                self.log_text.append(f"复现层次结构时发生错误: {str(e)}")

    # 获取与 traced_file 相同路径的文本文件路径
    tree_text_output_path = self.traced_file.rsplit('.', 1)[0] + "_tree.txt"

    # 调用 print_tree，并保存到文件
    print_tree(tree, output_file=tree_text_output_path)


    def visualize_tree(data):
        """使用 Graphviz 可视化树结构"""
        tree = build_tree(data)
        dot = Digraph(comment="Social Media Thread Structure")

        def add_nodes_edges(node):
            """递归添加节点和边"""
            node_label = node.get('username', 'Unknown')  # 只展示 username
            # 判断节点的类型并设置颜色
            if node.get('datatype') == 'posts' and not node.get('parent'):
                dot.node(node['id'], node_label, shape='box', style='filled', fillcolor='lightblue')  # 帖子 - 浅蓝色
            elif node.get('datatype') == 'comments':
                dot.node(node['id'], node_label, shape='ellipse', style='filled', fillcolor='lightgreen')  # 评论 - 浅绿色
            elif node.get('datatype') == 'posts' and node.get('parent'):  # 判断是否是转发
                dot.node(node['id'], node_label, shape='box', style='filled', fillcolor="#FFB347")  # 转发 - 浅橙色
            else:
                dot.node(node['id'], node_label, shape='ellipse', style='filled', fillcolor='lightgray')  # 默认 - 浅灰色

            if 'children' in node:
                for child in node['children']:
                    dot.edge(node['id'], child['id'])
                    add_nodes_edges(child)

        def add_legend(dot):
            """添加图例（Legend）"""
            with dot.subgraph(name="cluster_legend") as legend:
                legend.attr(label="Legend", color="black", fontsize="12", fontname="Arial")
                legend.node("post", "Post", shape="box", style="filled", fillcolor="lightblue")
                legend.node("comment", "Comment", shape="ellipse", style="filled", fillcolor="lightgreen")
                legend.node("forward", "Forwarded Post", shape="box", style="filled", fillcolor="#FFB347")
                legend.edge("post", "comment", style="invis")  # 隐形边，使图例节点对齐
                legend.edge("post", "forward", style="invis")  # 隐形边，使图例节点对齐

        for root in tree:
            add_nodes_edges(root)

        # 添加图例
        add_legend(dot)

        # 获取 PDF 输出路径
        output_pdf_path = self.traced_file.rsplit('.', 1)[0] + "_tree"

        try:
            dot.render(output_pdf_path, format="pdf", cleanup=True)
            self.log_text.append(f"局部树状图已生成: {output_pdf_path}")
        except Exception as e:
            self.log_text.append(f"生成树状图时发生错误: {str(e)}")

    def limit_first_level_nodes(tree, max_children=10):
        """限制根节点的直接子节点数量"""
        for root in tree:
            if 'children' in root and len(root['children']) > max_children:
                root['children'] = root['children'][:max_children]  # 仅保留前 max_children 个子节点
        return tree

    def sample_data(data, sample_size=50):
        """随机选取 sample_size 个帖子"""
        return random.sample(data, min(sample_size, len(data)))

    tree = limit_first_level_nodes(tree, max_children=20)  # 限制第一层节点数
    visualize_tree(tree)
