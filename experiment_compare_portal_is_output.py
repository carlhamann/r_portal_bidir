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

# # Generate output for figure
#
# Experiment: comparison vs. Bitterli et al.

# %load_ext autoreload
# %autoreload 2

# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib import rc
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
from lmexperiment import *

result_path = 'C:/Users/carlh/Desktop/Masterarbeit'
base_output_dir = os.path.join('figures', '20200709', 'compare_portal_is')

# +
# Resolution
w = 1920
h = 1080

# DPI
dpi=100

# JPEG quality (max: 100)
quality = 80

# Cropped image size
crop_x = w/3
crop_y = crop_x/2

# Remove white border
pad = -0.04

# Export for supplemental?
export_for_supplemental = False


# +
def plot_and_save_image(tech, img, scene_name, brightness_scale):
    # Variables
    print('Processing [scene:%s, tech:%s]' % (scene_name, tech))
    
    # Output directory
    output_dir = os.path.join(base_output_dir, scene_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Image
    img = np.clip(np.power(img*brightness_scale,1.0/2.2),0,1)
    
    # Main figure
    fig_main = plt.figure(figsize=(w/dpi,h/dpi), dpi=dpi)
    ax_main = plt.Axes(fig_main, [0., 0., 1., 1.])
    ax_main.set_axis_off()
    fig_main.add_axes(ax_main)
    ax_main.imshow(img, interpolation='none')
    plt.tick_params(labelbottom='off')
    plt.tick_params(labelleft="off")
    plt.axis('off')
    
    # Save figure without rects
    if export_for_supplemental:
        ext = 'png'
    else:
        ext = 'pdf'
    plt.savefig(
        os.path.join(output_dir, '%s.%s' % (tech, ext)),
        quality = quality,
        dpi=dpi)

def compute_rmse(tech, ref, img, scene_name, **kwargs):
    error = rrmse(ref, img)
    print('rRMSE [scene:%s, tech:%s] = %.4f' % (scene_name, tech, error))

def generate_output(path, **ex):
    # Load images
    #img_ref = imageio.imread(os.path.join(path, 'ref.hdr'))
    img_pt_portal = imageio.imread(os.path.join(path, 'bdpt.hdr'))
    img_mlt_portal = imageio.imread(os.path.join(path, 'portal_bdpt.hdr'))
    
    # Plot and save
#     plot_and_save_image('ref', img_ref, **ex)
#     plot_and_save_image('portal_pt', img_pt_portal, **ex)
#     plot_and_save_image('ours', img_mlt_portal, **ex)
    
    # Compute RMSE
    compute_rmse('portal_pt', img_mlt_portal, img_pt_portal, **ex)
    #compute_rmse('ours', img_ref, img_mlt_portal, **ex)


# -

generate_output(
    path=os.path.join(result_path, 'portal_box_dragon'),
    scene_name='portal_box_dragon',
    brightness_scale=1)
#generate_output(
#    path=os.path.join(result_path, 'portal_box_dragon_2'),
#    scene_name='dragon_indirect',
#    brightness_scale=1)
