# 项目数据清单

本目录保存井震联合速度场建模所需的数据。下载大型数据后，建议先根据下表校验文件大小和 MD5。

| 数据 | 本地文件 | 用途 | 状态 | 参考地址 | MD5 |
|---|---|---|---|---|---|
| Marmousi 速度模型 | `marmousi/marmousi_vp.bin` | 速度场真值/监督标签 | 已有，6,912,204 字节 | `https://zenodo.org/api/records/16114161/files/marmousi_vp.bin/content` | `3603290793a5d870fb1290301bc68dbd` |
| Marmousi 双精度/备用模型 | `marmousi/vp_marmousi_bi` | 备用速度模型 | 已有，2,568,004 字节 | 项目本地文件 | — |
| 合成地震数据 | `marmousi/marmousi2_synthetic_seismic.npy` | 地震输入 | 已有，7,629,812 字节 | 项目本地文件 | — |
| Taranaki 测井数据 | `taranaki/taranaki-basin-curated-well-logs.tar.gz` | 测井曲线与井位 | **文件不完整**，当前 8,214,504 字节 | `https://zenodo.org/api/records/3832955/files/taranaki-basin-curated-well-logs.tar.gz/content` | `71e8c6d10274fcb65ba006612e2939fe` |
| VelRecover 参考实现 | `reference/VelRecover-1.1.0.zip` | 速度插值与界面设计参考 | 已有，8,278,419 字节 | `https://zenodo.org/api/records/15053268/files/VelRecover-1.1.0.zip/content` | `793cf016f3656a80b18b2cb23efe30a0` |

## 补齐 Taranaki 数据

该压缩包记录大小应为 228,743,380 字节。网络可用时，在项目根目录执行以下命令即可从断点继续下载：

```powershell
curl.exe -L -C - --retry 5 --retry-delay 3 `
  -o data\taranaki\taranaki-basin-curated-well-logs.tar.gz `
  https://zenodo.org/api/records/3832955/files/taranaki-basin-curated-well-logs.tar.gz/content

(Get-FileHash data\taranaki\taranaki-basin-curated-well-logs.tar.gz -Algorithm MD5).Hash
```

校验结果应为：

```text
71E8C6D10274FCB65BA006612E2939FE
```

压缩包解开后应至少包含 `coords.csv`、`logs.csv` 和 `LICENSE.txt`。

## 当前环境检查结果

- `marmousi2_synthetic_seismic.npy` 的文件头记录形状为 `(1, 2721, 701)`、数据类型为 `float32`。
- `marmousi_vp.bin` 的大小为 1,728,051 个 `float32`，需要结合数据来源说明确定二维尺寸后再读取。
- 当前 Python 环境没有安装 `torch`、`lasio` 和 `segyio`，后续实现训练和 LAS/SEG-Y 读取时需要补充依赖。
- 本次尝试下载 Taranaki 数据时，环境无法解析 `zenodo.org`，因此未覆盖现有的部分文件。

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
