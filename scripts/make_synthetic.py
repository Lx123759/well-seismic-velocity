"""由 Marmousi2 截取段速度模型生成逐点对齐的深度域合成地震，供训练与评估使用。

用法：python scripts/make_synthetic.py [--dz 7.5] [--freq 25] [--snr 0]
输出：data/synthetic/marmousi2_vp.npy、marmousi2_seismic.npy、meta.json 和预览图
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from velbuilder.core.synthetic import synthesize_depth_seismic  # noqa: E402
from velbuilder.io.marmousi import load_velocity  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dz", type=float, default=7.5, help="网格间距 (m)，Devito 预设模型给出 dx = dz = 7.5 m")
    ap.add_argument("--freq", type=float, default=25.0, help="Ricker 子波主频 (Hz)")
    ap.add_argument("--dt", type=float, default=0.001, help="正演时间采样间隔 (s)")
    ap.add_argument("--snr", type=float, default=0.0, help="信噪比（振幅比），0 表示不加噪")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    vp = load_velocity(ROOT / "data/marmousi/vp_marmousi_bi")
    seis = synthesize_depth_seismic(vp, args.dz, args.freq, args.dt,
                                    noise_snr=args.snr or None, seed=args.seed)

    out = ROOT / "data/synthetic"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "marmousi2_vp.npy", vp)
    np.save(out / "marmousi2_seismic.npy", seis)
    meta = {
        "source": "data/marmousi/vp_marmousi_bi",
        "layout": "(trace, depth)",
        "shape": list(vp.shape),
        "vp_unit": "m/s",
        "vp_range": [float(vp.min()), float(vp.max())],
        "dx_m": args.dz, "dz_m": args.dz,
        "wavelet": f"Ricker {args.freq} Hz", "dt_s": args.dt,
        "density": "Gardner", "snr": args.snr, "seed": args.seed,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax[0].imshow(vp.T, aspect="auto", cmap="jet")
    ax[0].set_title("Vp (m/s)")
    ax[1].imshow(seis.T, aspect="auto", cmap="gray", vmin=-0.3, vmax=0.3)
    ax[1].set_title("depth-domain synthetic seismic")
    fig.tight_layout()
    fig.savefig(out / "preview.png", dpi=80)
    print("saved to", out, "shape", vp.shape)


if __name__ == "__main__":
    main()
