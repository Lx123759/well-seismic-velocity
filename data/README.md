# 项目数据清单

本目录保存井震联合速度场建模所需的数据（约 1.8 GB，不入 git）。换机器时按下表地址下载，并用 MD5 校验。所有信息于 2026-09-29 核实。

## 1 数据用途一览

| 角色 | 数据 | 说明 |
|---|---|---|
| **主实验（训练与定量评估）** | 官方 Marmousi2 速度 + 配套合成地震 | 与开题任务书一致；运行 `scripts/prepare_marmousi2.py` 得到对齐的 2721×701 数组 |
| 跨模型泛化测试 | 原始 Marmousi、Sigsbee2A、SEG/EAGE Overthrust | 重采样到主实验网格后，用 `scripts/make_synthetic.py` 正演地震 |
| 测井预处理验证（F2） | Taranaki 测井、Central Valley 井 Vp 曲线 | 真实井数据，只做清洗、换算、粗化的验证，不参与训练 |
| 单元测试与快速调试 | Devito 版 Marmousi 子块、OpenFWI 样例 | 小而快，不报告指标 |
| 参考实现 | VelRecover | 插值与界面设计参考 |

## 2 文件清单

| 本地文件 | 内容 | 来源地址 | 许可 | MD5 |
|---|---|---|---|---|
| `marmousi2/vp_marmousi-ii.segy` | 官方 Marmousi2 纵波速度 | https://www.ahay.org/data/marm2/vp_marmousi-ii.segy （Madagascar 镜像；官方页 https://wiki.seg.org/wiki/AGL_Elastic_Marmousi 需浏览器验证） | SEG Wiki 公开 | `4e1bade80fa6c825fc88b8ed6a10abf3` |
| `marmousi/marmousi2_synthetic_seismic.npy` | Marmousi2 合成地震（与上一行配套） | https://zenodo.org/records/14233581 | CC BY 4.0 | `10bf781eb8e5fcc77ef53f866ad89da3` |
| `marmousi2/marmousi_Ip_model.npy` | Marmousi2 纵波阻抗（用于核对对齐关系） | https://zenodo.org/records/14233581 | CC BY 4.0 | `ef3f570f87343d58d6437581b8028710` |
| `marmousi/marmousi_vp.bin` | 原始 Marmousi 速度 | https://zenodo.org/records/16114161 | 见记录页 | `3603290793a5d870fb1290301bc68dbd` |
| `marmousi/vp_marmousi_bi` | Devito 版 Marmousi（Marmousi2 子块） | https://github.com/devitocodes/data/blob/master/Simple2D/vp_marmousi_bi | MIT（Devito） | `dd2c23ff84383a4197b5c3e8e53d7738` |
| `benchmarks/sigsbee/sigsbee2a_stratigraphy.sgy` | Sigsbee2A 真实层速度 | https://www.ahay.org/data/sigsbee/sigsbee2a_stratigraphy.sgy | SMAART JV 公开 | 见下方校验命令 |
| `benchmarks/sigsbee/sigsbee2a_migvel.sgy` | Sigsbee2A 偏移速度（平滑版） | https://www.ahay.org/data/sigsbee/sigsbee2a_migvel.sgy | SMAART JV 公开 | 见下方校验命令 |
| `benchmarks/overthrust/overthrust_3D_true_model.h5` | SEG/EAGE 三维 Overthrust 真实模型 | https://zenodo.org/records/4252588 | CC BY 4.0 | `ae4082cdcebbc7714eedd382d7925804` |
| `benchmarks/openfwi/fva_velocity{1,2,3}.npy` | OpenFWI FlatVel-A 速度样例 | https://zenodo.org/records/7293894 | CC BY 4.0 | `fc67d9ad…`、`782f1320…`、`8fe17ee6…` |
| `taranaki/taranaki-basin-curated-well-logs.tar.gz` | Taranaki 盆地整理测井 | https://zenodo.org/records/3832955 | CDLA-Sharing 1.0 | `71e8c6d10274fcb65ba006612e2939fe` |
| `wells/central_valley/Vp.243Wells.ascii`、`LatLon.243Wells.ascii` | 加州 Central Valley 243 口井 Vp 曲线与井位 | https://zenodo.org/records/7045120 | CC BY 4.0 | `2835af1a921d60701aa025a92a4fc4ba`、`a784700463db34f554ed2bcf8d0fb62c` |
| `reference/VelRecover-1.1.0.zip` | VelRecover 源码 | https://zenodo.org/records/15053268 | 见压缩包 | `793cf016f3656a80b18b2cb23efe30a0` |

由脚本生成（可随时重建）：

| 目录 | 生成命令 | 内容 |
|---|---|---|
| `marmousi2/vp_2721x701.npy`、`seismic_2721x701.npy`、`meta.json` | `python scripts/prepare_marmousi2.py` | 主实验对齐数据 |
| `synthetic/` | `python scripts/make_synthetic.py` | Devito 子块的褶积正演地震，补充实验用 |

## 3 格式、单位与网格

所有二维数组在代码中统一为 **(道, 深度)** 排列、速度单位 **m/s**。

| 数据 | 原始格式 | 原始形状 | 网格间距 | 原始单位 / 取值 | 读取要点 |
|---|---|---|---|---|---|
| Marmousi2 速度 | SEG-Y，每道一列深度 | 13601 道 × 2801 | 1.25 m × 1.25 m | km/s，1.028～4.700 | `load_marmousi2_pair` 抽样 `[::5, ::4]` 并 ×1000 |
| Marmousi2 地震 | NPY float32 | (1, 2721, 701) | 6.25 m × 5 m（深度域） | 无量纲，-1.16～1.09 | 第 0、2720 道全零；相对反射系数约有 1 个采样点的系统偏移 |
| Marmousi2 阻抗 | NPY float32 | (1, 13601, 2801) | 1.25 m | 1515～12347 | 阻抗/速度得密度 1.01～2.63 g/cm³，证明同网格 |
| 原始 Marmousi | BIN float32 无头 | reshape(2301, 751) | 4 m × 4 m | m/s，1500～5500 | `load_velocity` |
| Devito 子块 | BIN float32 无头 | reshape(1601, 401) | 7.5 m × 7.5 m | km/s，1.028～4.700 | `load_velocity`（已 ×1000）；即 Marmousi2 在 7.5 m 网格上第 333 道、第 33 深度点起的子块 |
| Sigsbee2A 层速度 | SEG-Y | 3201 道 × 1201 | 25 ft × 25 ft（7.62 m） | **ft/s**，4716～14800 | 需 ×0.3048 换成 m/s；道头坐标为 0，间距按公开参数 |
| Sigsbee2A 偏移速度 | SEG-Y | 2133 道 × 1201 | 37.5 ft × 25 ft | ft/s，4920～14800 | 平滑版本，可作背景模型参考 |
| Overthrust 三维 | HDF5，键 `m` | (207, 801, 801) = (z, y, x) | 25 m 各向 | **慢度平方 s²/km²**，0.0278～0.444 | 速度 = 1000 / sqrt(m) m/s，即 1500～6000；取某一 y 切片得 801×207 二维剖面 |
| OpenFWI FlatVel-A | NPY float32 | (120, 1, 70, 70) = (样本, 通道, z, x) | 10 m | m/s，1500～4500 | 注意是 (深度, 道) 排列，需转置 |
| Taranaki 测井 | CSV（888 MB，多井单表） | 列：DTC、DEPT、WELLNAME 等 | 约 0.15 m 采样 | DTC μs/ft；DEPT 为真垂深 m | 用 pandas 按 WELLNAME 分组，分块读取 |
| Central Valley 井 | ASCII，逐井分块 | 每块：`Well number: i`、样点数、然后“深度 速度”两列 | 约 0.13 m 采样 | 表头写 km/s，**实际是 m/s** | 井位文件为经度、纬度 |

## 4 真实井数据统计

**Taranaki**：407 口井中 339 口含 DTC（海上 96 口，陆上 243 口）；单井 DTC 深度跨度中位数约 1600 m，最长约 5360 m，超过 1000 m 的有 253 口。约 400 万个有效采样，其中 1.24% 超出 40～200 μs/ft（含负值，最大 645），另有 100 个 -999.25 空值。

**Central Valley**：243 口井，单井中位数约 13,700 个采样，深度 10～6706 m，单井跨度中位数约 1700 m。Vp 最小 1132 m/s，最大 15168 m/s，存在明显超出物理范围的尖峰，适合作为 F2 尖峰剔除的测试数据。

## 5 下载与校验

```bash
# 在项目根目录执行；中断后重复执行即可断点续传
Z=https://zenodo.org/api/records
curl -L -C - -o data/marmousi2/vp_marmousi-ii.segy https://www.ahay.org/data/marm2/vp_marmousi-ii.segy
curl -L -C - -o data/marmousi/marmousi2_synthetic_seismic.npy $Z/14233581/files/marmousi_synthetic_seismic.npy/content
curl -L -C - -o data/taranaki/taranaki-basin-curated-well-logs.tar.gz $Z/3832955/files/taranaki-basin-curated-well-logs.tar.gz/content
tar -xzf data/taranaki/taranaki-basin-curated-well-logs.tar.gz -C data/taranaki
md5sum data/marmousi2/* data/marmousi/* data/benchmarks/*/* data/wells/*/* data/taranaki/*.tar.gz
```

Sigsbee2A 两个文件的 MD5 以首次下载为准，记录在 `data/checksums.md5`。

## 6 已核实的结论与注意事项

- 早期把 Marmousi2 地震与 Devito 子块配对，相关系数接近 0；原因是二者覆盖范围和网格不同。改用官方 Marmousi2 速度后，`vp[::5, ::4]` 与地震逐点对齐，问题已解决。
- Marmousi2 地震不是单一子波的褶积结果：单子波拟合在留出道上相关系数约 0.57，含更真实的波动效应，因此主实验用它，而不是用褶积正演。
- 已评估但未下载的数据：Facies Classification Benchmark（1 GB，只有地震相标签无速度）、F3 测井包（只有井头与分层，没有曲线）、Adele 三维地震（3.5 GB，无速度）、OpenFWI 完整数据集（每类约 6 GB，炮集到速度，与本课题的叠后深度域输入不同）、BP 2004 模型（原 S3 地址已关闭）。
