# -*- coding: UTF-8 -*-
"""
@Project ：Pyqt
@File    ：main.py
@IDE     ：PyCharm 
@Author  ：xiaomu-258
@Date    ：2025/1/27 16:52 
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QTextEdit, QTableWidget
)
from PyQt5.QtCore import Qt
import functions  # 引入 functions.py 里的函数

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("项目名称")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧操作区
        left_layout = QVBoxLayout()
        self.import_button = QPushButton("导入文件")
        self.filter_button = QPushButton("筛选词条")
        self.selecttag_button = QPushButton("选择词条")
        self.filter_hashtag_button = QPushButton("根据词条筛选数据集")
        self.trace_data_button = QPushButton("溯源数据")
        self.reconstruct_structure_button = QPushButton("复现层次结构")

        # 设置按钮的大小
        button_size = (150, 50)  # 自定义按钮的大小，可根据需要调整
        self.import_button.setFixedSize(*button_size)
        self.filter_button.setFixedSize(*button_size)
        self.selecttag_button.setFixedSize(*button_size)
        self.filter_hashtag_button.setFixedSize(*button_size)
        self.trace_data_button.setFixedSize(*button_size)
        self.reconstruct_structure_button.setFixedSize(*button_size)

        # 将按钮添加到布局中
        left_layout.addStretch(1)  # 上部分的拉伸项
        left_layout.addWidget(self.import_button)
        # 添加间距
        left_layout.addSpacing(40)  # 这里添加了 40 像素的间距，可根据需要调整
        left_layout.addWidget(self.filter_button)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.selecttag_button)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.filter_hashtag_button)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.trace_data_button)
        left_layout.addSpacing(40)
        left_layout.addWidget(self.reconstruct_structure_button)  # 添加按钮

        left_layout.addStretch(1)  # 下部分的拉伸项

        # 为按钮添加功能，调用 functions.py 里的函数
        self.import_button.clicked.connect(lambda: functions.import_file(self))
        self.filter_button.clicked.connect(lambda: functions.filter_words(self))
        self.selecttag_button.clicked.connect(lambda: functions.selecttag_data(self))
        self.filter_hashtag_button.clicked.connect(lambda: functions.filter_hashtags_data(self))
        self.trace_data_button.clicked.connect(lambda: functions.trace_data(self))
        self.reconstruct_structure_button.clicked.connect(lambda: functions.reconstruct_structure(self))

        # 右侧显示区
        right_layout = QVBoxLayout()

        # 文件表格
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["文件名称", "词条筛选结果", "扩散过程还原"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.horizontalHeader().setSectionResizeMode(0, True)

        # 日志区域
        self.log_label = QLabel("操作日志")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # 布局整理
        right_layout.addWidget(self.file_table)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.log_label)
        right_layout.addWidget(self.log_text)

        # 合并主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

