"""生成开题任务书配图：系统架构图、功能结构图、井震联合建模技术路线图。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).parent / "fig"
OUT.mkdir(exist_ok=True)

INK = "#1f2933"
LINE = "#52606d"
FILLS = ["#dbe9f6", "#e3f1e6", "#fdf0d5", "#ece4f5", "#f5e1e1"]


def box(ax, x, y, w, h, text, fill, fs=10, bold=False, ec=LINE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.003,rounding_size=0.012",
                                fc=fill, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
            fontweight="bold" if bold else "normal", linespacing=1.35)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=LINE, lw=1.0, shrinkA=0, shrinkB=0))


def new_canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def architecture():
    fig, ax = new_canvas(8.6, 5.4)
    layers = [
        ("表示层\n(PySide6 GUI)", ["工程管理界面","数据浏览与\n剖面显示", "建模参数与\n训练监控", "结果评估与\n导出界面"]),
        ("业务逻辑层\n(Service)", ["工程与数据服务", "预处理与\n井震标定服务", "建模任务调度\n(后台线程)", "评估与报告服务"]),
        ("算法层\n(Core)", ["测井曲线处理\n(DT→Vp/滤波/粗化)", "传统插值基线\n(IDW/克里金/RBF)", "深度学习模型\n(测井约束 U-Net)", "精度指标\n(RMSE/MAPE/SSIM)"]),
        ("数据访问层\n(DAO / IO)", ["SEG-Y/NPY/BIN\n地震与速度读写", "LAS/CSV\n测井读写", "SQLite\n工程元数据", "模型权重 .pt\n结果文件"]),
    ]
    top, lh, gap = 0.95, 0.19, 0.045
    for i, (name, items) in enumerate(layers):
        y = top - (i + 1) * lh - i * gap
        box(ax, 0.01, y, 0.16, lh, name, FILLS[i], fs=10, bold=True)
        ax.add_patch(FancyBboxPatch((0.19, y), 0.80, lh, boxstyle="round,pad=0.003,rounding_size=0.012",
                                    fc="white", ec=LINE, lw=0.8, ls="--"))
        iw = (0.80 - 0.025 * 5) / 4
        for j, it in enumerate(items):
            box(ax, 0.19 + 0.025 + j * (iw + 0.025), y + 0.025, iw, lh - 0.05, it, FILLS[i], fs=8.3)
        if i < len(layers) - 1:
            arrow(ax, 0.59, y - 0.004, 0.59, y - gap + 0.004)
    fig.savefig(OUT / "architecture.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def function_tree():
    fig, ax = new_canvas(9.2, 4.6)
    box(ax, 0.30, 0.83, 0.40, 0.12, "井震联合速度场建模系统", FILLS[0], fs=12, bold=True)
    mods = [
        ("F1 数据管理", ["工程新建/打开", "地震数据导入", "测井数据导入", "井位坐标管理"]),
        ("F2 预处理与标定", ["测井异常值清洗", "DT→Vp 转换", "测井粗化滤波", "井旁道提取"]),
        ("F3 初始模型构建", ["IDW 插值", "克里金插值", "RBF 插值", "低频背景模型"]),
        ("F4 AI 速度建模", ["样本集生成", "网络训练", "训练过程监控", "速度场预测"]),
        ("F5 可视化与评估", ["剖面与井曲线", "误差分布图", "盲井检验", "精度指标统计"]),
        ("F6 成果导出", ["数据体导出", "图件导出", "评估报告生成", "模型权重管理"]),
    ]
    w = 0.145
    g = (1 - w * 6) / 7
    ax.plot([g + w / 2, 1 - g - w / 2], [0.74, 0.74], color=LINE, lw=1.0)
    ax.plot([0.5, 0.5], [0.83, 0.74], color=LINE, lw=1.0)
    for i, (m, subs) in enumerate(mods):
        x = g + i * (w + g)
        arrow(ax, x + w / 2, 0.74, x + w / 2, 0.663)
        box(ax, x, 0.56, w, 0.10, m, FILLS[1 + i % 4], fs=9.3, bold=True)
        ax.plot([x + 0.008, x + 0.008], [0.557, 0.44 - 3 * 0.11 + 0.042], color=LINE, lw=0.8)
        for k, s in enumerate(subs):
            yy = 0.44 - k * 0.11
            box(ax, x + 0.022, yy, w - 0.03, 0.085, s, "white", fs=8.3)
            ax.plot([x + 0.008, x + 0.019], [yy + 0.042, yy + 0.042], color=LINE, lw=0.8)
    fig.savefig(OUT / "function_tree.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def roadmap():
    fig, ax = new_canvas(9.0, 4.0)
    box(ax, 0.01, 0.70, 0.17, 0.18, "地震数据\n(叠后剖面/合成记录)", FILLS[0], fs=9)
    box(ax, 0.01, 0.40, 0.17, 0.18, "测井数据\n(声波 DT / Vp 曲线)", FILLS[0], fs=9)
    box(ax, 0.01, 0.10, 0.17, 0.18, "井位与时深关系", FILLS[0], fs=9)
    box(ax, 0.23, 0.70, 0.17, 0.18, "振幅归一化\n网格重采样", FILLS[1], fs=9)
    box(ax, 0.23, 0.40, 0.17, 0.18, "测井清洗、DT→Vp\n粗化到地震尺度", FILLS[1], fs=9)
    box(ax, 0.23, 0.10, 0.17, 0.18, "井插值低频模型\n(IDW / 克里金)", FILLS[1], fs=9)
    for y in (0.79, 0.49, 0.19):
        arrow(ax, 0.18, y, 0.23, y)
        arrow(ax, 0.40, y, 0.46, y)
    arrow(ax, 0.315, 0.40, 0.315, 0.28)
    box(ax, 0.46, 0.10, 0.19, 0.80,
        "测井约束 U-Net\n\n输入通道：\n地震振幅\n低频背景速度\n井位掩码\n\n损失函数：\n全局 MSE\n+ λ·井点约束项", FILLS[2], fs=9)
    box(ax, 0.71, 0.56, 0.13, 0.18, "速度场\n预测结果", FILLS[3], fs=9.5, bold=True)
    box(ax, 0.71, 0.26, 0.13, 0.18, "传统插值\n基线结果", FILLS[4], fs=9)
    arrow(ax, 0.65, 0.65, 0.71, 0.65)
    ax.plot([0.315, 0.315], [0.10, 0.04], color=LINE, lw=1.0)
    ax.plot([0.315, 0.775], [0.04, 0.04], color=LINE, lw=1.0)
    arrow(ax, 0.775, 0.04, 0.775, 0.26)
    box(ax, 0.88, 0.30, 0.11, 0.40, "精度评估\n\n盲井检验\nRMSE\nMAPE\nSSIM", FILLS[0], fs=9)
    arrow(ax, 0.84, 0.65, 0.88, 0.58)
    arrow(ax, 0.84, 0.35, 0.88, 0.42)
    fig.savefig(OUT / "roadmap.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    function_tree()
    roadmap()
    print("ok", sorted(p.name for p in OUT.iterdir()))
