"""由速度模型正演深度域合成地震剖面，保证地震与速度逐点对齐。

做法：逐道把深度域反射系数按双程旅时映射到时间轴，与 Ricker 子波褶积，
再按各深度点的双程旅时采样回深度网格。子波在深度域随速度自然拉伸，
与叠前深度偏移剖面的特征一致。
"""
import numpy as np


def ricker(freq, dt, length=0.2):
    """零相位 Ricker 子波。freq 为主频 (Hz)，dt 为采样间隔 (s)。"""
    t = np.arange(-length / 2, length / 2 + dt / 2, dt)
    a = (np.pi * freq * t) ** 2
    return ((1 - 2 * a) * np.exp(-a)).astype(np.float32)


def gardner_density(vp):
    """Gardner 公式估算密度 (g/cm^3)，vp 单位 m/s；水层 (vp<1600) 取 1.0。"""
    rho = 0.31 * np.power(vp, 0.25)
    return np.where(vp < 1600, 1.0, rho).astype(np.float32)


def reflectivity(vp, use_density=True):
    """沿深度方向（最后一维）计算法向入射反射系数，输出与 vp 同形状，首个采样为 0。"""
    imp = vp * gardner_density(vp) if use_density else vp
    r = np.zeros_like(vp, dtype=np.float32)
    r[..., 1:] = (imp[..., 1:] - imp[..., :-1]) / (imp[..., 1:] + imp[..., :-1])
    return r


def synthesize_depth_seismic(vp, dz, freq=25.0, dt=0.001, use_density=True,
                             noise_snr=None, seed=None):
    """正演深度域合成地震。

    vp: (n_traces, n_depth) 速度，单位 m/s
    dz: 深度采样间隔 (m)
    noise_snr: 若给定，按该信噪比（振幅比）加入高斯白噪声
    返回与 vp 同形状、按最大绝对值归一化到 [-1, 1] 的 float32 数组。
    """
    vp = np.asarray(vp, dtype=np.float64)
    if vp.ndim != 2:
        raise ValueError("vp 应为 (n_traces, n_depth) 的二维数组")
    if np.any(vp <= 0):
        raise ValueError("速度必须为正值")

    n_traces, n_depth = vp.shape
    refl = reflectivity(vp, use_density).astype(np.float64)
    # 各深度点的双程旅时：t(0)=0，t(k)=sum(2*dz/v)
    twt = np.zeros_like(vp)
    twt[:, 1:] = np.cumsum(2.0 * dz / vp[:, :-1], axis=1)

    wavelet = ricker(freq, dt).astype(np.float64)
    n_t = int(np.ceil(twt[:, -1].max() / dt)) + len(wavelet)
    t_axis = np.arange(n_t) * dt
    out = np.empty_like(vp)
    for i in range(n_traces):
        spikes = np.zeros(n_t)
        idx = np.rint(twt[i] / dt).astype(int)
        np.add.at(spikes, idx, refl[i])
        trace_t = np.convolve(spikes, wavelet, mode="same")
        out[i] = np.interp(twt[i], t_axis, trace_t)

    if noise_snr:
        rng = np.random.default_rng(seed)
        out += rng.normal(0.0, out.std() / noise_snr, out.shape)

    peak = np.abs(out).max()
    if peak > 0:
        out /= peak
    return out.astype(np.float32)
