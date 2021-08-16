#!/usr/bin/python3

from france import centre,metrop

import numpy as np
from scipy.spatial import Delaunay


points = np.array([ centre[d] for d in metrop ])
tri = Delaunay(points)

print(points)

import matplotlib.pyplot as plt
plt.triplot(points[:,0], points[:,1], tri.simplices.copy())
#plt.plot(points[:,0], points[:,1], 'o')

#for j, p in enumerate(points):
#    plt.text(p[0]-0.03, p[1]+0.03, j, ha='right') # label the points
#for j, s in enumerate(tri.simplices):
#    p = points[s].mean(axis=0)
#"    plt.text(p[0], p[1], '#%d' % j, ha='center') # label triangles

plt.show()

