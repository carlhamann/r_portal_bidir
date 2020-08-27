# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Generate errorbar

# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib import rc
import matplotlib.patheffects as PathEffects
import numpy as np
import os
import itertools
import imageio
import pickle
import itertools as it
import tempfile
import math
from ipywidgets import widgets
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Rectangle
import matplotlib as mpl

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

dpi = 100
quality = 80
#w = 1920
w = 1200
h = 50
output_dir = os.path.join('temp', '20200709')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gradient = np.linspace(0, 1, w)
gradient = np.vstack([gradient]*h)

# +
fig = plt.figure(figsize=(w/dpi,h/dpi), dpi=dpi)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(gradient)
plt.tick_params(labelbottom='off')
plt.tick_params(labelleft="off")
plt.axis('off')

fs = 25
y = 35
ef = [PathEffects.withStroke(linewidth=5, foreground='k')]
ax.text(10, y, '$0$', fontsize=fs, color='white').set_path_effects(ef)
ax.text(w-100, y, '$1.5<$',fontsize=fs, color='white').set_path_effects(ef)
ax.text(w/2-60, y, 'rRMSE',fontsize=fs, color='white').set_path_effects(ef)

plt.savefig(
    os.path.join(output_dir, 'colorbar.pdf'),
    #quality = quality,
    dpi=dpi)
# -


