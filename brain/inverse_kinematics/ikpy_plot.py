import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D

from ikypy_config import arm_chain

ax = matplotlib.pyplot.figure().add_subplot(111, projection='3d')

arm_chain.plot(arm_chain.inverse_kinematics([2, 2, 2]), ax)
matplotlib.pyplot.show()