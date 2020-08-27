# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Generate outputs for figures

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

rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

# Results
#result_dir = os.path.join('results', '20200625')
result_dir = 'Z:\lab\projects\portal_mlt_results\exp_rendering_20200625_7d86dd'
experiments = [
    {
        'brightness_scale': 1,
        'scene_name': 'dragon',
        'path': os.path.join(result_dir, 'portal_box_dragon'),
        'inset_w': 100,
        'inset_h': 50,
        'clip_error_max': 1.5,
        'insets': [
            (400,800,'orangered'),
            (700,150,'royalblue'),
            (1250,650,'greenyellow'),
        ]
    },
    {
        'brightness_scale': 1,
        'scene_name': 'breakfast_room',
        'path': os.path.join(result_dir, 'breakfast_room'),
        'inset_w': 100,
        'inset_h': 50,
        'clip_error_max': 1.5,
        'insets': [
            (120,800,'orangered'),
            (1200,150,'royalblue'),
            (1700,650,'greenyellow'),
        ]
    },
    {
        'brightness_scale': 0.5,
        'scene_name': 'salle_de_bain',
        'path': os.path.join(result_dir, 'salle_de_bain_2'),
        'inset_w': 100,
        'inset_h': 50,
        'clip_error_max': 1.5,
        'insets': [
            (500,500,'orangered'),
            (750,200,'royalblue'),
            (1600,900,'greenyellow'),
        ]
    },
    {
        'brightness_scale': 1.5,
        'scene_name': 'veach_door',
        'path': os.path.join(result_dir, 'veach_door'),
        'inset_w': 100,
        'inset_h': 50,
        'clip_error_max': 1.5,
        'insets': [
            (400,700,'orangered'),
            (1100,200,'royalblue'),
            (1600,900,'greenyellow'),
        ]
    },
]

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

# Base directory of the output
base_output_dir = os.path.join('figures', '20200709', 'rendering')

# Export for supplemental?
export_for_supplemental = False


# +
def plot_and_save_image_with_rect(ex, tech, img):
    # Variables
    scene_name = ex['scene_name']
    print('Processing [scene:%s, tech:%s]' % (scene_name, tech))
    
    # Output directory
    output_dir = os.path.join(base_output_dir, scene_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Image
    img = np.clip(np.power(img*ex['brightness_scale'],1.0/2.2),0,1)
    
    # Main figure
    fig_main = plt.figure(figsize=(w/dpi,h/dpi), dpi=dpi)
    ax_main = plt.Axes(fig_main, [0., 0., 1., 1.])
    ax_main.set_axis_off()
    fig_main.add_axes(ax_main)
    ax_main.imshow(img, interpolation='none')
    plt.tick_params(labelbottom='off')
    plt.tick_params(labelleft="off")
    plt.axis('off')
    
    if export_for_supplemental:
        # Save figure without rects
        plt.savefig(
            os.path.join(output_dir, '%s.png' % tech),
            quality = quality,
            dpi=dpi)
    else:
        # Save figure without rects
        plt.savefig(
            os.path.join(output_dir, 'norect_%s.pdf' % tech),
            quality = quality,
            dpi=dpi)

        if 'insets' in ex:
            for i,p in enumerate(ex['insets']):
                print('Processsing inset [index:%d]' % i)

                sz_x = ex['inset_w']
                sz_y = ex['inset_h']

                ax_main.add_patch(Rectangle(
                    (p[0]-sz_x,p[1]-sz_y),
                    sz_x*2,
                    sz_y*2,
                    edgecolor=p[2],
                    fill=False,
                    linewidth=5))

                # Cropped figure
                cropped = img[p[1]-sz_y:p[1]+sz_y,p[0]-sz_x:p[0]+sz_x,:]
                fig_crop = plt.figure(figsize=(crop_x/dpi,crop_y/dpi), dpi=dpi)

                ax = plt.Axes(fig_crop, [0., 0., 1., 1.])
                ax.set_axis_off()
                fig_crop.add_axes(ax)
                ax.imshow(cropped, interpolation='none')


    #             plt.imshow(cropped, interpolation='none')
                plt.tick_params(labelbottom='off')
                plt.tick_params(labelleft="off")
                plt.axis('off')
                plt.gca().add_patch(Rectangle(
                    (-0.5,-0.5),
                    sz_x*2,
                    sz_y*2,
                    edgecolor=p[2],
                    fill=False,
                    linewidth=20))

                # Save cropped figure
                plt.savefig(
                    os.path.join(output_dir, '%s_inset_%02d.pdf' % (tech, i)),
                    bbox_inches='tight',
                    pad_inches = pad,
                    quality = quality,
                    dpi=dpi)

                plt.close(fig_crop)

        # Save main figure
        plt.figure(fig_main.number)
        plt.savefig(
            os.path.join(output_dir, '%s.pdf' % tech),
            quality = quality,
            dpi=dpi)
    
        #plt.close(fig_main)

def plot_and_save_error_image(ex, tech, img, ref):
    # Variables
    scene_name = ex['scene_name']
    print('Generating error image [scene:%s, tech:%s]' % (scene_name, tech))
    
    # Output directory
    output_dir = os.path.join(base_output_dir, scene_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Compute difference
    diff = rrmse_pixelwised(ref, img)
    print('Max error: %f' % np.amax(diff))
    clip_error_max = ex['clip_error_max']
    if clip_error_max < 0:
        clip_error_max = np.amax(diff)
        
    # Compute error
    error = rrmse(ref, img)
    print('rRMSE [scene:%s, tech:%s] = %.4f' % (scene_name, tech, error))
    
    # Error iamge
    fig_main = plt.figure(figsize=(w/dpi,h/dpi), dpi=dpi)
    ax_main = plt.Axes(fig_main, [0., 0., 1., 1.])
    ax_main.set_axis_off()
    fig_main.add_axes(ax_main)
    ax_main.imshow(np.clip(diff, 0, clip_error_max), cmap='viridis')
#     if not export_for_supplemental:
#         ax_main.text(50, 120, 'rRMSE: %.4f' % error,
#                      fontsize=70,
#                      color='white',
#                      bbox={'facecolor': 'black', 'alpha': 0.5, 'pad': 15})
    plt.tick_params(labelbottom='off')
    plt.tick_params(labelleft="off")
    plt.axis('off')
    
    # Save main figure
    if export_for_supplemental:
        plt.figure(fig_main.number)
        plt.savefig(
            os.path.join(output_dir, 'error_%s.png' % tech),
            quality = quality,
            dpi=dpi)
    else:
        plt.figure(fig_main.number)
        plt.savefig(
            os.path.join(output_dir, 'error_%s.pdf' % tech),
            quality = quality,
            dpi=dpi)
    
    #plt.close(fig_main)
    
def generate_output(ex):
    # Load images
    path = ex['path']
    img_ref = imageio.imread(os.path.join(path, 'ref.hdr'))
    img_mlt_lens = imageio.imread(os.path.join(path, 'lens.hdr'))
    img_mlt_portal = imageio.imread(os.path.join(path, 'portal_lens.hdr'))
    
    # Plot and save
#     plot_and_save_image_with_rect(ex, 'ref', img_ref)
#     plot_and_save_image_with_rect(ex, 'lens', img_mlt_lens)
#     plot_and_save_image_with_rect(ex, 'portal', img_mlt_portal)
    
    # Error images
    plot_and_save_error_image(ex, 'lens', img_mlt_lens, img_ref)
    plot_and_save_error_image(ex, 'portal', img_mlt_portal, img_ref)


# -

for experiment in experiments:
    generate_output(experiment)
