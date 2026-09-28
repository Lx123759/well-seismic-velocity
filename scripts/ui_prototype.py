"""主窗口静态原型：搭出布局并截图到 docs/fig/ui_main.png，供设计说明书使用。

用法：python scripts/ui_prototype.py [--show]   不加 --show 时离屏渲染并保存截图
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

if "--show" not in sys.argv:
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

import pyqtgraph as pg  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QAction, QFont  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QComboBox, QDockWidget, QDoubleSpinBox, QFormLayout, QGroupBox,
    QMainWindow, QProgressBar, QPushButton, QSpinBox, QStatusBar, QTabWidget,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)


def velocity_image():
    path = ROOT / "data/synthetic/marmousi2_vp.npy"
    if path.exists():
        return np.load(path)
    x, z = np.meshgrid(np.arange(1601), np.arange(401), indexing="ij")
    return (1500 + 8 * z + 200 * np.sin(x / 150)).astype(np.float32)


def build_window():
    win = QMainWindow()
    win.setWindowTitle("井震联合速度场建模系统 v0.1 — 工程：Marmousi2 实验")
    win.resize(1400, 820)

    for name in ["文件", "数据", "预处理", "建模", "评估", "导出", "帮助"]:
        win.menuBar().addMenu(name)
    tb = win.addToolBar("主工具栏")
    for group in (["新建", "打开", "保存"], ["导入地震", "导入测井"],
                  ["预处理", "初始模型"], ["训练", "预测"], ["评估", "导出"]):
        for name in group:
            tb.addAction(QAction(name, win))
        tb.addSeparator()

    # 左侧工程树
    tree = QTreeWidget()
    tree.setHeaderLabel("工程")
    items = {
        "数据体": ["地震（合成，1601×401）", "真值速度 Vp", "背景模型（IDW）"],
        "井": ["W1", "W2", "W3", "W4", "W5", "B1 ★盲井", "B2 ★盲井"],
        "建模任务": ["#1 IDW  完成", "#2 克里金  完成", "#3 U-Net λ=5  训练中"],
    }
    for top, children in items.items():
        node = QTreeWidgetItem([top])
        for c in children:
            node.addChild(QTreeWidgetItem([c]))
        tree.addTopLevelItem(node)
        node.setExpanded(True)
    dock_tree = QDockWidget("工程树")
    dock_tree.setWidget(tree)
    win.addDockWidget(Qt.LeftDockWidgetArea, dock_tree)

    # 中部绘图区
    tabs = QTabWidget()
    plot = pg.PlotWidget()
    plot.setBackground("w")
    img = pg.ImageItem(velocity_image())
    img.setColorMap(pg.colormap.get("turbo"))
    plot.addItem(img)
    plot.invertY(True)
    plot.setLabel("bottom", "道号")
    plot.setLabel("left", "深度采样点")
    for tr in (200, 450, 700, 1150, 1400):
        plot.addLine(x=tr, pen=pg.mkPen("k", width=2))
    for tr in (900, 1000):
        plot.addLine(x=tr, pen=pg.mkPen("m", width=2, style=Qt.DashLine))
    bar = pg.ColorBarItem(values=(1500, 4700), colorMap=img.getColorMap(), label="Vp (m/s)")
    bar.setImageItem(img, insert_in=plot.getPlotItem())
    tabs.addTab(plot, "速度剖面")
    for name in ["地震剖面", "误差剖面", "井曲线对比", "训练损失"]:
        tabs.addTab(QWidget(), name)
    win.setCentralWidget(tabs)

    # 右侧参数面板
    panel = QWidget()
    lay = QVBoxLayout(panel)
    box = QGroupBox("AI 建模参数")
    form = QFormLayout(box)
    method = QComboBox()
    method.addItems(["测井约束 U-Net", "IDW", "普通克里金", "RBF"])
    form.addRow("方法", method)
    for label, lo, hi, val in [("井数下限", 1, 20, 3), ("井数上限", 1, 20, 8), ("切片宽度", 32, 512, 128),
                               ("批大小", 1, 64, 16), ("最大轮数", 1, 500, 100)]:
        sb = QSpinBox()
        sb.setRange(lo, hi)
        sb.setValue(val)
        form.addRow(label, sb)
    for label, val, dec in [("井约束权重 λ", 5.0, 1), ("学习率", 0.001, 4)]:
        ds = QDoubleSpinBox()
        ds.setDecimals(dec)
        ds.setValue(val)
        form.addRow(label, ds)
    lay.addWidget(box)
    lay.addWidget(QPushButton("开始训练"))
    lay.addWidget(QPushButton("停止"))
    lay.addWidget(QPushButton("加载权重并预测"))
    lay.addStretch()
    dock_param = QDockWidget("参数面板")
    dock_param.setWidget(panel)
    win.addDockWidget(Qt.RightDockWidgetArea, dock_param)

    # 底部日志
    log = QTextEdit()
    log.setReadOnly(True)
    log.setFont(QFont("Consolas", 9))
    log.setPlainText(
        "[10:20:41] 已加载工程 Marmousi2 实验\n"
        "[10:20:55] 背景模型（IDW，5 口井）生成完成，用时 0.4 s\n"
        "[10:21:03] 开始训练 #3：U-Net，λ=5，设备 CUDA (RTX 4060 Laptop)\n"
        "[10:23:17] 第 12 轮  训练损失 0.0031  验证损失 0.0042"
    )
    dock_log = QDockWidget("日志")
    dock_log.setWidget(log)
    win.addDockWidget(Qt.BottomDockWidgetArea, dock_log)
    win.resizeDocks([dock_log], [130], Qt.Vertical)

    status = QStatusBar()
    prog = QProgressBar()
    prog.setValue(12)
    prog.setFormat("训练中 %p%")
    status.addPermanentWidget(prog)
    status.showMessage("光标：道 812，深度 245，Vp = 3326 m/s")
    win.setStatusBar(status)
    return win


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 9))
    win = build_window()
    if "--show" in sys.argv:
        win.show()
        sys.exit(app.exec())
    win.show()
    app.processEvents()
    out = ROOT / "docs/fig"
    out.mkdir(parents=True, exist_ok=True)
    win.grab().save(str(out / "ui_main.png"))
    print("saved", out / "ui_main.png")


if __name__ == "__main__":
    main()
