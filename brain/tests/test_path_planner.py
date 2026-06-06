from pathlib import Path
import importlib.util
import pytest


def _load_module():
    module_path = Path(__file__).resolve().parent.parent / "path-planner" / "path_planner.py"
    spec = importlib.util.spec_from_file_location("path_planner", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


path_planner = _load_module()


def test_plan_joint_path_basic():
    path = path_planner.plan_joint_path(
        start_angles=(0.0, 0.0),
        target_angles=(10.0, 20.0),
        duration=0.5,
        timestep=0.25,
        max_step_deg=10.0,
        use_scipy=False,
    )

    assert path[0] == [0.0, 0.0]
    assert path[-1] == [10.0, 20.0]
    assert len(path) == 3


def test_plan_joint_path_mismatched_length_raises_error():
    with pytest.raises(ValueError, match="same length"):
        path_planner.plan_joint_path((0.0,), (10.0, 20.0))


def test_plan_joint_path_zero_delta_returns_single_point():
    result = path_planner.plan_joint_path(
        start_angles=(30.0, 45.0),
        target_angles=(30.0, 45.0),
        duration=1.0,
        timestep=0.1,
        max_step_deg=2.0,
        use_scipy=False,
    )

    assert result == [[30.0, 45.0]]


def test_interpolate_joint_path_alias():
    interpolated = path_planner.interpolate_joint_path(
        start_angles=(0.0, 0.0),
        target_angles=(20.0, 20.0),
        duration=0.4,
        timestep=0.2,
        max_step_deg=10.0,
    )
    assert interpolated[0] == [0.0, 0.0]
    assert interpolated[-1] == [20.0, 20.0]
