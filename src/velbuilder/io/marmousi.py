"""Marmousi 系列原始数据读取。统一返回 (道, 深度) 排列、单位 m/s 的 float32 数组。"""
from pathlib import Path

import numpy as np

# 文件名 -> (形状, 原始单位换算到 m/s 的系数)
_VELOCITY_FILES = {
    "vp_marmousi_bi": ((1601, 401), 1000.0),   # Marmousi2 截取段，原始单位 km/s
    "marmousi_vp.bin": ((2301, 751), 1.0),     # Marmousi 原始模型，原始单位 m/s
}


def load_velocity(path):
    """读取无文件头的 float32 速度模型，返回 (n_traces, n_depth) 的 m/s 数组。"""
    path = Path(path)
    if path.name not in _VELOCITY_FILES:
        raise ValueError(f"未知的速度模型文件：{path.name}")
    shape, scale = _VELOCITY_FILES[path.name]
    data = np.fromfile(path, dtype=np.float32)
    if data.size != shape[0] * shape[1]:
        raise ValueError(f"{path.name} 大小为 {data.size} 个采样，与预期形状 {shape} 不符")
    return data.reshape(shape) * np.float32(scale)


def load_seismic_npy(path, drop_dead_traces=True):
    """读取 (1, n_traces, n_samples) 的地震 npy，返回二维数组；可去掉全零道。"""
    data = np.load(path)
    if data.ndim == 3 and data.shape[0] == 1:
        data = data[0]
    if data.ndim != 2:
        raise ValueError(f"地震数据应为二维，实际形状 {data.shape}")
    if drop_dead_traces:
        data = data[np.abs(data).max(axis=1) > 0]
    return data.astype(np.float32)


# 官方 Marmousi2 速度模型为 1.25 m 网格（13601×2801）；配套合成地震为 2721×701，
# 即模型横向每 5 点、纵向每 4 点抽样一次（道距 6.25 m、深度采样 5 m）。
MARMOUSI2_STEP = (5, 4)
MARMOUSI2_SPACING = (6.25, 5.0)


def load_marmousi2_pair(vp_segy, seismic_npy):
    """读取官方 Marmousi2 速度（SEG-Y，km/s）与配套地震，返回逐点对齐的 (vp m/s, seismic)。

    两者形状均为 (2721, 701)，排列为 (道, 深度)。地震首尾两道为全零道，保留以维持对齐，
    使用方应在切片或评估时排除。
    """
    import segyio

    with segyio.open(str(vp_segy), ignore_geometry=True) as f:
        vp = segyio.tools.collect(f.trace[:])
    sx, sz = MARMOUSI2_STEP
    vp = (vp[::sx, ::sz] * 1000.0).astype(np.float32)
    seis = load_seismic_npy(seismic_npy, drop_dead_traces=False)
    if vp.shape != seis.shape:
        raise ValueError(f"速度 {vp.shape} 与地震 {seis.shape} 形状不一致，请检查是否为官方 Marmousi2 文件")
    return vp, seis
