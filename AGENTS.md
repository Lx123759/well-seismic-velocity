# 给 AI 编程助手的项目说明（Codex / Claude Code 通用）

本文件在每次会话开始时自动读取。开始任何工作前，先读完本文件，再读 `TODO.md` 找到下一项未完成任务。

## 项目

《软件工程实践》课程项目：测井约束下基于深度学习的井震联合速度场建模方法与系统实现。
学生：刘星（2023015617，软件工程23-4班），指导教师：周洪涛。全部交付截止 2026-12-31。

所有回复、注释、文档、提交信息使用**中文**。

## 权威文档（冲突时按此顺序为准）

1. `docs/03_算法方案.md` —— 数据、划分、网络、训练、实验的具体参数
2. `docs/02_软件设计说明书.md` —— 分层架构、模块接口（第 8 节）、数据库（第 6 节）、界面
3. `docs/01_需求规格说明书.md` —— F1～F6、非功能需求 N1～N8
4. `data/README.md` —— 每个数据文件的来源、单位、网格、读取方法
5. 开题任务书 docx —— 由 `.work/build_proposal.py` 生成，**不要直接改 docx**，改脚本后运行 `python .work/build_proposal.py`

实现与文档不一致时：先停下来说明差异，经用户同意后同时修改代码和文档，不要悄悄偏离。

## 环境

- 一律使用项目虚拟环境：`.venv\Scripts\python`（PowerShell）或 `.venv/Scripts/python`（bash）。不要用系统 Python，不要往系统 Python 装包。
- GPU：RTX 4060 Laptop 8 GB，torch 2.14 + CUDA 12.6。
- 新增依赖：先 `.venv\Scripts\python -m pip install 包名`，再把固定版本写入 `requirements.txt`。
- 测试：`.venv\Scripts\python -m pytest -q`，提交前必须全部通过。

## 必须遵守的约定

- **数组排列**：所有二维剖面为 `(道, 深度)`，即 `data[trace, depth]`。OpenFWI 原始数据是 `(深度, 道)`，读入时转置。
- **单位**：速度一律 m/s，深度 m。读入时立刻换算：Marmousi2 SEG-Y 与 Devito 文件为 km/s（×1000）；Sigsbee2A 为 ft/s（×0.3048）；Overthrust HDF5 为慢度平方 s²/km²（v = 1000/sqrt(m)）。
- **主实验数据**：官方 Marmousi2，用 `velbuilder.io.marmousi.load_marmousi2_pair` 或 `scripts/prepare_marmousi2.py` 生成的 `data/marmousi2/vp_2721x701.npy`、`seismic_2721x701.npy`。网格 dx=6.25 m、dz=5 m。第 0 和第 2720 道地震全零，要排除。
- **训练/测试划分**：测试区为第 1350～1699 道，隔离带 1318～1349 与 1700～1731。**测试区的数据绝不能进入训练或验证**，这是实验结果是否可信的关键。
- **分层**：`core/`（算法）不得导入 PySide6 或 `io/`；`io/` 不得导入 `core/`；`gui/` 只调用 `services/`。
- **导入顺序**：凡是同时用到 matplotlib 和 PySide6 的入口，必须先 `import matplotlib.pyplot` 再导入 PySide6，否则会报 `_SixMetaPathImporter` 错误（设计说明书 10.4 节）。
- **原始数据只读**：不修改、不移动 `data/` 下的原始文件；生成的文件写到新文件名。
- **随机性**：训练、抽井、切片使用固定种子（默认 0），保证结果可复现。
- **实验结果**：如实记录。指标没达到开题书目标（MAPE ≤ 8%、盲井 RMSE 比基线降低 20%）时，写明实测值与原因，不要调整测试集或指标定义来“凑”结果。

## 不要做的事

- 不要提交 `data/` 下的大文件、`.venv/`、`node_modules/`、模型权重（`.gitignore` 已配置，用 `git add 具体文件`，不要 `git add -A` 之前不看 `git status`）。
- 不要删除或重写 `docs/`、`TODO.md` 中已有内容，除非任务明确要求。
- 不要把任何 API Key 写进代码、配置或提交记录。
- 不要 `git push --force`、`git reset --hard`。

## 工作流程（每项任务都按这个顺序）

1. 读 `TODO.md`，选第一个未勾选的任务；在 GitHub Issue（#1～#18）里找对应条目。
2. 读相关文档章节，确认接口与参数。
3. 写代码 + 写测试（`tests/test_<模块>.py`），数值函数用解析解或手算小例子验证。
4. 运行全部测试，通过后在 `TODO.md` 勾选该项。
5. 提交：一个任务一次提交，中文提交信息说明做了什么和为什么，信息末尾写 `Closes #编号`。
6. 向用户汇报：完成了什么、测试结果、与文档不一致的地方、下一项任务是什么。

## 当前状态（2026-09-29）

- 准备工作与设计阶段文档草稿已完成；下一步：请指导教师确认设计文档，然后按 `TODO.md` 第二节开始 v0.1 编码，从 Issue #1（F1 数据读取与校验）开始。
- 已实现：`io/marmousi.py`（Marmousi 系列读取）、`core/synthetic.py`（褶积正演），测试 6 项通过。
