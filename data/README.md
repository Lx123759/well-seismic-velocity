# 项目数据清单

本目录保存井震联合速度场建模所需的数据。下载大型数据后，建议先根据下表校验文件大小和 MD5。

| 数据 | 本地文件 | 用途 | 状态 | 参考地址 | MD5 |
|---|---|---|---|---|---|
| Marmousi 速度模型 | `marmousi/marmousi_vp.bin` | 跨模型泛化测试 | 已有，MD5 校验通过 | `https://zenodo.org/api/records/16114161/files/marmousi_vp.bin/content` | `3603290793a5d870fb1290301bc68dbd` |
| Marmousi 二维模型（Devito 版） | `marmousi/vp_marmousi_bi` | 速度场真值/监督标签 | 已有，MD5 与来源一致 | `https://raw.githubusercontent.com/devitocodes/data/master/Simple2D/vp_marmousi_bi` | `dd2c23ff84383a4197b5c3e8e53d7738` |
| Marmousi2 合成地震 | `marmousi/marmousi2_synthetic_seismic.npy` | 地震输入，与下两行 Marmousi2 模型配套 | 已有，MD5 与来源一致 | `https://zenodo.org/api/records/14233581/files/marmousi_synthetic_seismic.npy/content` | `10bf781eb8e5fcc77ef53f866ad89da3` |
| Marmousi2 纵波速度（官方全模型） | `marmousi2/vp_marmousi-ii.segy` | 速度真值/监督标签 | 已有，155,653,444 字节 | `https://www.ahay.org/data/marm2/vp_marmousi-ii.segy`（Madagascar 镜像；官方页面 https://wiki.seg.org/wiki/AGL_Elastic_Marmousi ） | `4e1bade80fa6c825fc88b8ed6a10abf3` |
| Marmousi2 纵波阻抗 | `marmousi2/marmousi_Ip_model.npy` | 验证地震与模型的对应关系 | 已有，MD5 校验通过 | `https://zenodo.org/api/records/14233581/files/marmousi_Ip_model.npy/content` | `ef3f570f87343d58d6437581b8028710` |
| Taranaki 测井数据 | `taranaki/taranaki-basin-curated-well-logs.tar.gz` | 测井曲线与井位 | 已有，MD5 校验通过；解压后为 coords.csv（井位）、logs.csv（407 口井，888 MB）| `https://zenodo.org/api/records/3832955/files/taranaki-basin-curated-well-logs.tar.gz/content` | `71e8c6d10274fcb65ba006612e2939fe` |
| VelRecover 参考实现 | `reference/VelRecover-1.1.0.zip` | 速度插值与界面设计参考 | 已有，8,278,419 字节 | `https://zenodo.org/api/records/15053268/files/VelRecover-1.1.0.zip/content` | `793cf016f3656a80b18b2cb23efe30a0` |

## 下载 Taranaki 数据

压缩包大小 228,743,380 字节，下载中断时可在项目根目录执行以下命令断点续传，然后解压：

```bash
curl -L -C - --retry 5 -o data/taranaki/taranaki-basin-curated-well-logs.tar.gz   https://zenodo.org/api/records/3832955/files/taranaki-basin-curated-well-logs.tar.gz/content
md5sum data/taranaki/taranaki-basin-curated-well-logs.tar.gz   # 应为 71e8c6d10274fcb65ba006612e2939fe
tar -xzf data/taranaki/taranaki-basin-curated-well-logs.tar.gz -C data/taranaki
```

数据许可为 CDLA-Sharing 1.0，是 CSV 格式而非 LAS。

## 数据来源（2026-09-29 核实）

- **`vp_marmousi_bi`**：来自开源地震正演框架 Devito 的测试数据仓库 [devitocodes/data](https://github.com/devitocodes/data/blob/master/Simple2D/vp_marmousi_bi)（2016-11-07 提交，说明为 “larger 2D marmousi”），本地文件 MD5 与仓库文件一致。Devito 在 `examples/seismic/preset_models.py` 中按形状 (1601, 401)、网格间距 (7.5 m, 7.5 m) 读取。
  - 即横向 12 km、纵向 3 km。速度范围 1028～4700 m/s 与 Marmousi2 的水层和最高速度一致，推测是 Marmousi2 的中段重采样版本；Devito 只称其为“2D Marmousi model”，报告中按“Devito 提供的 Marmousi 二维模型”引用。
- **`marmousi2_synthetic_seismic.npy`**：来自 Zenodo 数据集 [Marmousi2](https://zenodo.org/records/14233581)（CC BY 4.0，原始数据出自休斯敦大学 AGL），与同一数据集的阻抗模型配套，MD5 一致。
- **`vp_marmousi-ii.segy`**：Marmousi2 官方纵波速度模型，13601 道 × 2801 采样，网格 1.25 m，单位 km/s，速度 1.028～4.700。由阻抗除以速度反推的密度 99.9% 落在 1.01～2.63 g/cm³，确认两者同网格对齐。
- **对应关系**：地震 2721×701 = 模型按横向每 5 点、纵向每 4 点抽样（道距 6.25 m、深度采样 5 m，深度域）。即 `vp[::5, ::4]` 与地震逐点对齐（残余偏移约 1 个采样点）。
- **Devito 模型与 Marmousi2 的关系**：`vp_marmousi_bi` 是 Marmousi2 重采样到 7.5 m 后，从第 333 道、第 33 个深度点开始截取的 1601×401 子块（横向 2.5～14.5 km，纵向 0.25～3.25 km），逐点平均误差 3.7 m/s。

## 数据格式（2026-09-29 核对）

| 文件 | 类型 | 形状（读取方式） | 取值范围 | 单位 |
|---|---|---|---|---|
| `marmousi_vp.bin` | float32，无文件头 | `np.fromfile(f, np.float32).reshape(2301, 751)`，即（道, 深度） | 1500～5500 | **m/s** |
| `vp_marmousi_bi` | float32（不是双精度），无文件头 | `np.fromfile(f, np.float32).reshape(1601, 401)`，即（道, 深度） | 1.028～4.700 | **km/s** |
| `marmousi2_synthetic_seismic.npy` | float32 | `np.load(f)[0]`，形状（2721, 701），即（道, 采样点） | -1.16～1.09 | 无量纲 |

注意：
- 两个速度模型的单位不同，读取后要先统一单位。
- 地震数据首尾两道（第 0 道、第 2720 道）全为 0，使用前应去掉。

### Taranaki 声波曲线统计（2026-09-29）

- 407 口井中有 339 口含声波时差 DTC（海上 96 口，陆上 243 口），单位 μs/ft，深度列 DEPT 为真垂深（m）。
- 单井 DTC 深度跨度中位数约 1600 m，最长约 5360 m；跨度超过 1000 m 的有 253 口。
- 共约 400 万个有效 DTC 采样，其中 1.24% 超出 40～200 μs/ft 的合理范围（含负值，最大 645），另有 100 个 -999.25 空值。F2 测井清洗需要处理这些异常值。

## 已知问题

- **（已解决）** 旧合成地震与 `vp_marmousi_bi` 对不上：地震覆盖 Marmousi2 全宽，而 Devito 模型只是其中一块，网格也不同。下载官方 Marmousi2 速度模型后，地震与 `vp[::5, ::4]` 逐点对齐，可直接组成训练样本对。
- 该地震不是简单的褶积模型：用单一子波拟合，留出道上的相关系数约 0.57，说明它包含更真实的波动效应，比 `scripts/make_synthetic.py` 的褶积正演更接近实际。

## 建议补充的数据

以下候选数据已从现有检索结果中筛选，均与速度建模、井震联合或地震深度学习有关。它们暂时只记录元数据和下载入口，建议按优先级下载，避免一次性占用大量磁盘空间。

| 优先级 | 数据集 | 适合用途 | DOI/入口 |
|---|---|---|---|
| 高 | Training data and test data sets for simultaneous inversion of velocity density based on U-T | 获取成对的地震、速度和密度训练/测试样本，适合验证 U-Net 数据管线 | `10.5281/zenodo.7965402`，https://zenodo.org/records/7965402 |
| 高 | Marmousi2 | 补充 Marmousi2 的速度、密度或地震基准数据 | `10.5281/zenodo.14233581`，https://zenodo.org/records/14233581 |
| 高 | Compressional Velocity data from 243 Central Valley Wells | 增加真实井的 Vp 曲线，用于测井约束和泛化测试 | `10.5281/zenodo.7045120`，https://zenodo.org/records/7045120 |
| 高 | Netherlands F3 Interpretation Dataset | 获取公开地震剖面和解释结果，用于地震剖面可视化与测试 | `10.5281/zenodo.1471548`，https://zenodo.org/records/1471548 |
| 中 | Multi-scale velocity models for the Ridgecrest region, CA | 验证多尺度速度场和不同空间分辨率下的误差 | `10.5281/zenodo.10740715`，https://zenodo.org/records/10740715 |
| 中 | Adele 3D seismic survey SEG-Y | 测试 SEG-Y 读取、切片和三维数据接口 | `10.5281/zenodo.4299758`，https://zenodo.org/records/4299758 |
| 中 | MR3D - Synthetic Resistivity Well Logs Dataset | 扩展井数据预处理和多曲线输入实验 | `10.5281/zenodo.11002012`，https://zenodo.org/records/11002012 |
| 中 | Facies Classification Benchmark | 增加地震图像分类/分割的辅助实验数据 | `10.5281/zenodo.3755060`，https://zenodo.org/records/3755060 |
| 低 | Seismic refraction, reflection and free-air gravity data of OBS2020-3 | 研究真实海洋地震数据格式和复杂噪声场景 | `10.5281/zenodo.14241669`，https://zenodo.org/records/14241669 |
| 低 | Dataset and Trained Models for shallow-to-deep velocity model building via diffusion models | 对比扩散模型速度建模方法和公开模型结果 | `10.5281/zenodo.19790506`，https://zenodo.org/records/19790506 |

### 推荐收集顺序

1. 先补齐 Taranaki 测井数据。
2. 下载 `10.5281/zenodo.7965402`，它最适合直接验证监督训练流程。
3. 下载 Marmousi2 和 Central Valley Wells，分别补充合成真值与真实井曲线。
4. 再下载 Netherlands F3 或 Adele 数据，完善地震数据读取和可视化测试。

下载前需要在 Zenodo 页面确认文件大小、许可协议和实际文件格式；大型数据集不建议仅凭记录标题批量下载。
