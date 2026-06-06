import ikpy.chain
import ikpy.link
import numpy as np


# Defining the 5-axis robot arm manually
arm_chain = ikpy.chain.Chain(name='5_axis_arm', links=[
    # Base reference point
    ikpy.link.OriginLink(),
    
    # 1. WAIST MOTOR (Rotates around Z, lifts up to shoulder)
    ikpy.link.URDFLink(
        name="waist",
        bounds=(np.radians(-90), np.radians(90)), # Limit to 180 deg total
        origin_translation=[0.0, 0.0, 0.1],              # 10cm tall base
        origin_orientation=[0.0, 0.0, 0.0],
        rotation=[0.0, 0.0, 1.0]                  # Z-Axis
    ),
    
    # 2. SHOULDER MOTOR (Rotates around Y, reaches to elbow)
    ikpy.link.URDFLink(
        name="shoulder",
        bounds=(np.radians(-45), np.radians(90)),
        origin_translation=[0.3, 0.0, 0.0],              # 30cm upper arm
        origin_orientation=[0.0, 0.0, 0.0],
        rotation=[0.0, 1.0, 0.0]                  # Y-Axis
    ),
    
    # 3. ELBOW MOTOR (Rotates around Y, reaches to wrist)
    ikpy.link.URDFLink(
        name="elbow",
        bounds=(np.radians(-120), np.radians(120)),
        origin_translation=[0.25, 0.0, 0.0],             # 25cm forearm
        origin_orientation=[0.0, 0.0, 0.0],
        rotation=[0.0, 1.0, 0.0]                  # Y-Axis
    ),
    
    # 4. WRIST MOTOR (Rotates around Y, controls gripper tilt)
    ikpy.link.URDFLink(
        name="wrist",
        bounds=(np.radians(-90), np.radians(90)),
        origin_translation=[0.1, 0.0, 0.0],              # 10cm wrist-to-gripper dist
        origin_orientation=[0.0, 0.0, 0.0],
        rotation=[0.0, 1.0, 0.0]                  # Y-Axis
    ),
    
    # 5. GRIPPER (Typically handles origin_orientation roll, or acts as the end-effector)
    ikpy.link.URDFLink(
        name="gripper",
        bounds=(np.radians(-180), np.radians(180)),
        origin_translation=[0.0, 0.0, 0.0],              # End tip
        origin_orientation=[0.0, 0.0, 0.0],
        rotation=[1.0, 0.0, 0.0]                  # X-Axis (Roll)
    )
])