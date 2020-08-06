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

# # Visual debugging

# %load_ext autoreload
# %autoreload 2

import lmenv
env = lmenv.load('.lmenv')

import os
import numpy as np
import imageio
import json
# %matplotlib inline
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pythreejs as three
import time

import lightmetrica as lm
# %load_ext lightmetrica_jupyter
import lmscene
from vis import *

# %widen

lm.init()
lm.log.init('jupyter')
lm.progress.init('jupyter')
lm.info()
lm.comp.load_plugin(os.path.join(env.bin_path, 'accel_embree'))
lm.comp.load_plugin(os.path.join(env.bin_path, 'r_portal_bidir'))
if not lm.Release:
    lm.parallel.init('openmp', num_threads=1)
    lm.debug.attach_to_debugger()
else:
    lm.parallel.init('openmp', num_threads=1)

temp_dir = os.path.join('temp', '20200507_3')

# ## Scene setup

# +
accel = lm.load_accel('accel', 'embree')
scene = lm.load_scene('scene', 'default', accel=accel)
#lmscene.veach_door(scene, 'scene')
#lmscene.plane2(scene, 'scene')
#lmscene.fireplace_room(scene, env.scene_path)

#lmscene.mitsuba_knob_with_area_light(scene, 'scene')
# lmscene.mitsuba_knob_with_env_light_const(scene, 'scene')
# portal_mesh = lm.load_mesh('portal', 'wavefrontobj',
#     path=os.path.join('scene', 'mitsuba_knob', 'portal.obj'))

#portal_mesh = lmscene.portal_box_dragon(scene, env.scene_path)
#portal_mesh = lmscene.plane2_portal(scene, 'scene')
#portal_mesh = lmscene.plane2_portal(scene, 'scene')
portal_mesh = lmscene.cornell_double_fixed(scene, env.scene_path)

scene.build()
# -

lm.debug.print_asset_tree()

# ## Rendering

# ### Visualizing scene

th_scene, th_camera, th_renderer = display_scene(scene)


# ### Rendering

# +
def render(scene, name, **kwargs):
    w = 854
    h = 480
#     w = 1920
#     h = 1080
    film = lm.load_film('film', 'bitmap', w=w, h=h)
    renderer = lm.load_renderer('renderer', name,
        scene=scene,
        output=film,
        min_verts=6,
        max_verts=6,
        scheduler='time',
        render_time=20,
        samples_per_iter=10,
        **kwargs)
    out = renderer.render()
    print(json.dumps(out, indent=2))
    film.save(os.path.join(temp_dir, name + '.hdr'))
    return np.copy(film.buffer())

def display_image(img, fig_size=15, scale=1):
    f = plt.figure(figsize=(fig_size,fig_size))
    ax = f.add_subplot(111)                                                                                                                                                
    ax.imshow(np.clip(np.power(img*scale,1/2.2),0,1), origin='lower')
    ax.axis('off')
    plt.show()
    

def diff_gauss(img1, img2, scale=1):
    diff = np.abs(gaussian_filter(img1 - img2, sigma=3))
    f = plt.figure(figsize=(20,20))
    ax = f.add_subplot(111)
    ax.imshow(np.clip(np.power(diff*scale,1/2.2),0,1), origin='lower')
    plt.show()


# +
# Common material for light
common_mat_params = {
    'transparent': True,
    'opacity': 0.8,
#     'size': 0.1,
#     'scale': 0.1
    'size': 0.1,
    'scale': 0.1,
}

done = 0
count = 0
count2 = 0
count3 = 0

def on_poll(j):
    global done, count, count2, count3
    if done:
        return
    id = j['id']
    if id == 'path':
        if count > 0:
            return
        display_path(th_scene, vs=j['path'], color='#0000cc', **common_mat_params)
        count += 1
    if id == 'path2':
        if count2 > 20:
            return
        display_path(th_scene, vs=j['path'], color='#cc0000', **common_mat_params)
        count2 += 1
    if id == 'proposed_path':
        if count3 > 20:
            return
        display_path(th_scene, vs=j['path'], color='#cc0000', **common_mat_params)
        count3 += 1
    if id == 'mut_portal_perturbed_ray':
        display_ray(th_scene, j['o'], j['d'], color='#ff0000', **common_mat_params)
    if id == 'done':
        done = True

lm.debug.reg_on_poll(on_poll)
# -

display_portal_mesh(th_scene, portal_mesh)

img = render(scene, 'portal_bdpt_fixed',
    #seed=42,
    portal=portal_mesh)
display_image(img)

# + active=""
# from ipywidgets import embed
# embed.embed_minimal_html(os.path.join(temp_dir,'export.html'), views=th_renderer, title='Renderer')
#
#
#
