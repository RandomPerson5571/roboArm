import math
from pathlib import Path
import importlib.util
import pytest


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "inverse-kinematics" / "kinematics.py"
    spec = importlib.util.spec_from_file_location("kinematics", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kinematics = _load_module()


def test_compute_ik_angles_planar_elbow_up():
    angles = kinematics.compute_ik_angles(
        target_xyz_cm=(10.0, 0.0, 0.0),
        link_lengths_cm=(10.0, 10.0),
        elbow_up=True,
        use_chain_solver=False,
    )

    assert math.isclose(angles["base"], 0.0, abs_tol=1e-6)
    assert math.isclose(angles["shoulder"], 60.0, abs_tol=1e-6)
    assert math.isclose(angles["elbow"], 120.0, abs_tol=1e-6)


def test_compute_ik_angles_planar_elbow_down():
    angles = kinematics.compute_ik_angles(
        target_xyz_cm=(10.0, 0.0, 0.0),
        link_lengths_cm=(10.0, 10.0),
        elbow_up=False,
        use_chain_solver=False,
    )

    assert math.isclose(angles["base"], 0.0, abs_tol=1e-6)
    assert math.isclose(angles["shoulder"], -60.0, abs_tol=1e-6)
    assert math.isclose(angles["elbow"], 240.0, abs_tol=1e-6)


def test_compute_ik_angles_out_of_reach_raises_error():
    with pytest.raises(ValueError, match="out of reach"):
        kinematics.compute_ik_angles(
            target_xyz_cm=(50.0, 0.0, 0.0),
            link_lengths_cm=(10.0, 10.0),
            use_chain_solver=False,
        )


def test_compute_ik_angles_invalid_arguments_raise_value_error():
    with pytest.raises(ValueError, match="exactly three values"):
        kinematics.compute_ik_angles(target_xyz_cm=(1.0, 2.0), link_lengths_cm=(10.0, 10.0))
