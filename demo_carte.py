#!/usr/bin/python3


from france import plot_france, carte, DEPARTEMENTS
import numpy.random as rd
import matplotlib.pyplot as plt
import matplotlib.cm as cm


cmap = cm.get_cmap('Greens')

d = dict()
for x in DEPARTEMENTS:
    d[x] = rd.random()
        
fig=plt.figure(figsize=(8,8))

ax=fig.add_subplot(111) # axes pour le dessin
ax2=fig.add_axes([0.01, 0.03, 0.98, 0.03]) # axes pour la color bar

plot_france(ax, d, cmap, ax2, rg=(-.1,1.1))

plt.show()
