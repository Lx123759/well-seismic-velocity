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
