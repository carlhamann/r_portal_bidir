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

# # Testing portal BDPT (simplified version)
#
# This notebooks tests `renderer::portal_bdpt_inter1`.

# %load_ext autoreload
# %autoreload 2

import lmenv
env = lmenv.load('.lmenv')

import os
import pickle
import json
import uuid
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import lightmetrica as lm
# %load_ext lightmetrica_jupyter
import lmscene
from lmexperiment import *

lm.init()
lm.log.init('jupyter')
lm.progress.init('jupyter')
lm.info()
lm.comp.load_plugin(os.path.join(env.bin_path, 'accel_embree'))
lm.comp.load_plugin(os.path.join(env.bin_path, 'r_portal_bidir'))
if not lm.Release:
    lm.parallel.init('openmp', num_threads=1)
    lm.debug.attach_to_debugger()
temp_id = uuid.uuid4().hex[0:6]
print(temp_id)
temp_dir = os.path.join('temp', '20200723_'+temp_id)
os.makedirs(temp_dir, exist_ok=True)


def render(scene, name, renderer_name, base_dir, num_verts, **kwargs):
    w = 1920
    h = 1080
    film = lm.load_film('film', 'bitmap', w=w, h=h)
    renderer = lm.load_renderer('renderer', renderer_name,
                                scene=scene,
                                output=film,
                                min_verts=2,
                                max_verts=num_verts,
                                scheduler='time',
                                render_time=30,
                                seed=42,
                                **kwargs)
    out = renderer.render()
    print(json.dumps(out, indent=2))
    film.save(os.path.join(base_dir, name + '.hdr'))
    return np.copy(film.buffer())


def render_reference(scene_name, base_scene_path, num_verts):
    # Base output directory
    base_dir = os.path.join(temp_dir, scene_name)
    os.makedirs(base_dir, exist_ok=True)
    
    # Scene
    lm.reset()
    accel = lm.load_accel('accel', 'embree')
    scene = lm.load_scene('scene', 'default', accel=accel)
    scene_create_func = lmscene.scene_create_func(scene_name)
    portal_mesh = scene_create_func(scene, base_scene_path)
    scene.build()
    
    # Rendering
    img_bdpt = render(scene, 'bdpt', 'bdpt', base_dir, num_verts, portal=portal_mesh)
    display_image(img_bdpt)



# ## Rendering

# Glossy object in the box, connected by a portal, illuminated with environment light
render_reference('portal_box_dragon', base_scene_path=env.scene_path, num_verts=10)

# Double box with portal window which has depth (not a simple polygon)
render_reference('cornell_double_fixed', base_scene_path='scene', num_verts=10)
