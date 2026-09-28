import numpy as np
import pytest

from velbuilder.core.synthetic import reflectivity, ricker, synthesize_depth_seismic


def test_ricker_peak_at_center():
    w = ricker(25.0, 0.001)
    assert w.argmax() == len(w) // 2
    assert w.max() == pytest.approx(1.0)


def test_reflectivity_two_layer_constant_density():
    vp = np.array([[2000.0] * 5 + [3000.0] * 5])
    r = reflectivity(vp, use_density=False)
    assert r[0, 5] == pytest.approx(0.2)
    assert np.count_nonzero(r) == 1


def test_synthetic_event_aligned_with_interface():
    vp = np.full((3, 200), 2000.0)
    vp[:, 100:] = 3000.0
    seis = synthesize_depth_seismic(vp, dz=5.0, freq=30.0)
    assert seis.shape == vp.shape
    assert np.all(np.abs(np.abs(seis).argmax(axis=1) - 100) <= 1)
    assert np.abs(seis).max() == pytest.approx(1.0)


def test_rejects_non_positive_velocity():
    with pytest.raises(ValueError):
        synthesize_depth_seismic(np.zeros((2, 10)), dz=5.0)
