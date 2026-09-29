from pathlib import Path

import numpy as np
import pytest

from velbuilder.io.marmousi import load_marmousi2_pair, load_velocity

DATA = Path(__file__).resolve().parent.parent / "data"
needs = pytest.mark.skipif(not (DATA / "marmousi2/vp_marmousi-ii.segy").exists(), reason="未下载 Marmousi2 数据")


@needs
def test_marmousi2_pair_aligned():
    vp, seis = load_marmousi2_pair(DATA / "marmousi2/vp_marmousi-ii.segy",
                                   DATA / "marmousi/marmousi2_synthetic_seismic.npy")
    assert vp.shape == seis.shape == (2721, 701)
    assert 1000 < vp.min() < 1100 and vp.max() == pytest.approx(4700, abs=1)
    # 地震能量应在水底（约 450 m，第 90 个采样）以下才出现
    assert np.abs(seis[1:-1, :80]).mean() < 0.1 * np.abs(seis[1:-1, 100:]).mean()


def test_load_velocity_rejects_unknown(tmp_path):
    p = tmp_path / "x.bin"
    np.zeros(4, np.float32).tofile(p)
    with pytest.raises(ValueError):
        load_velocity(p)
