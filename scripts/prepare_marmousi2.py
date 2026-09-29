"""把官方 Marmousi2 速度模型抽样到配套地震网格，保存为主实验使用的 NPY。

用法：python scripts/prepare_marmousi2.py
输出：data/marmousi2/vp_2721x701.npy（m/s）、seismic_2721x701.npy、meta.json
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from velbuilder.io.marmousi import MARMOUSI2_SPACING, MARMOUSI2_STEP, load_marmousi2_pair  # noqa: E402


def main():
    out = ROOT / "data/marmousi2"
    vp, seis = load_marmousi2_pair(out / "vp_marmousi-ii.segy",
                                   ROOT / "data/marmousi/marmousi2_synthetic_seismic.npy")
    np.save(out / "vp_2721x701.npy", vp)
    np.save(out / "seismic_2721x701.npy", seis)
    meta = {
        "vp_source": "data/marmousi2/vp_marmousi-ii.segy（官方 1.25 m 网格）",
        "seismic_source": "data/marmousi/marmousi2_synthetic_seismic.npy（Zenodo 14233581）",
        "layout": "(trace, depth)",
        "shape": list(vp.shape),
        "subsample_step": list(MARMOUSI2_STEP),
        "dx_m": MARMOUSI2_SPACING[0], "dz_m": MARMOUSI2_SPACING[1],
        "vp_unit": "m/s",
        "vp_range": [float(vp.min()), float(vp.max())],
        "dead_traces": [0, vp.shape[0] - 1],
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", vp.shape, "to", out)


if __name__ == "__main__":
    main()
