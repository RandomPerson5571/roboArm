import xml.etree.ElementTree as ET

import ikpy.chain
import ikpy.link
import numpy as np
from ikpy.urdf import URDF
from pathlib import Path

_URDF_PATH = Path(__file__).resolve().parent.parent.parent / "cads" / "main_assembly.urdf"
_IKPY_URDF_CACHE = Path(__file__).resolve().parent / "_ikpy_urdf_cache.urdf"

SERVO_NAMES = ("base", "shoulder", "elbow", "wrist", "gripper")


def _prepare_urdf_for_ikpy(source: Path, cache: Path) -> Path:
    """Make the Onshape URDF compatible with ikpy (root base link, revolute joints)."""
    if cache.exists() and cache.stat().st_mtime >= source.stat().st_mtime:
        return cache

    tree = ET.parse(source)
    root = tree.getroot()
    for joint in root.findall("joint"):
        joint_type = joint.attrib.get("type")
        if joint_type == "fixed":
            axis = joint.find("axis")
            if axis is not None:
                joint.remove(axis)
        elif joint_type == "continuous":
            joint.attrib["type"] = "revolute"
            limit = joint.find("limit")
            if limit is None:
                limit = ET.SubElement(joint, "limit")
            limit.set("lower", str(-np.pi))
            limit.set("upper", str(np.pi))

    tree.write(cache, encoding="unicode", xml_declaration=True)
    return cache


def _active_links_mask(links: list) -> list[bool]:
    return [
        not isinstance(link, ikpy.link.OriginLink)
        and getattr(link, "joint_type", None) != "fixed"
        for link in links
    ]


_ikpy_urdf_path = _prepare_urdf_for_ikpy(_URDF_PATH, _IKPY_URDF_CACHE)
_chain_links = [ikpy.link.OriginLink()] + URDF.get_urdf_parameters(
    str(_ikpy_urdf_path),
    base_elements=["root"],
)
arm_chain = ikpy.chain.Chain(
    _chain_links,
    active_links_mask=_active_links_mask(_chain_links),
    name="main_assembly",
    urdf_metadata={"base_elements": ["root"], "urdf_file": str(_ikpy_urdf_path)},
)
