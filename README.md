# 井震联合速度场建模系统（velbuilder）

《软件工程实践》课程项目：**测井约束下基于深度学习的井震联合速度场建模方法与系统实现**。

以测井速度作为井点约束、地震数据作为横向结构引导，用测井约束 U-Net 预测二维速度场，
并与 IDW、克里金、RBF 等传统插值方法对比。最终交付一套 PySide6 桌面软件。

> 当前进度：项目骨架与数据准备（v0.1 开发前）。

## 目录结构

```
src/velbuilder/
  io/         数据访问层：SEG-Y/NPY/BIN、LAS/CSV、SQLite 工程库
  core/       算法层：测井处理、插值、深度学习模型、精度指标（不依赖界面）
  services/   业务逻辑层：流程编排、后台任务
  gui/        表示层：PySide6 界面
scripts/      数据生成等命令行脚本
docs/         需求规格说明书、设计说明书等文档
tests/        pytest 测试
data/         数据目录（大文件不入库，见 data/README.md）
.work/        开题任务书生成脚本与图件
```

## 环境配置

要求 Windows 10/11、Python 3.10 及以上。有 NVIDIA 显卡时安装 CUDA 版 PyTorch，没有显卡时安装 CPU 版即可。

```bash
python -m venv .venv
.venv\Scripts\activate

# CUDA 12.6 版 PyTorch（无 GPU 时去掉 --index-url，安装 CPU 版）
pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
```

## 准备数据

1. 按 [data/README.md](data/README.md) 中的地址下载原始数据，并校验 MD5。
2. 生成与速度模型逐点对齐的深度域合成地震：

```bash
python scripts/make_synthetic.py            # 默认 dz=10 m，25 Hz Ricker 子波，不加噪
python scripts/make_synthetic.py --snr 5    # 加噪版本
```

输出位于 `data/synthetic/`（`marmousi2_vp.npy`、`marmousi2_seismic.npy`、`meta.json`、`preview.png`）。

## 运行测试

```bash
pytest
pytest --cov=velbuilder     # 统计覆盖率
```

## 许可证

[MIT](LICENSE)
