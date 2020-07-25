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

# # Testing portal BDPT

# %load_ext autoreload
# %autoreload 2

import lmenv
env = lmenv.load('.lmenv')

import os
import json
import numpy as np
import imageio
# %matplotlib inline
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import lightmetrica as lm
# %load_ext lightmetrica_jupyter
import lmscene

# +
lm.init()

# Only one thread for debugging
if not lm.Release:
    lm.parallel.init('openmp', num_threads=1)
    lm.debug.attach_to_debugger()
    
lm.log.init('jupyter')
lm.progress.init('jupyter')
lm.info()
# -

temp_dir = os.path.join('temp', '20200512')


def cornell_double(scene):
    camera = lm.load_camera('camera1', 'pinhole',
        position=[0, 1, 5],
        center=[0, 1, 0],
        up=[0,1,0],
        vfov=43.001194,
        aspect=16/9)
    scene.add_primitive(camera=camera)
    model = lm.load_model('model', 'wavefrontobj',
        path=os.path.join('scene', 'custom', 'cornell_double.obj'))
    scene.add_primitive(model=model)


accel = lm.load_accel('accel', 'sahbvh')
scene = lm.load_scene('scene', 'default', accel=accel)
lmscene.plane2(scene, 'scene')
scene.build()


# +
def render(scene, name, **kwargs):
    if not lm.Release:
        w = 64
        h = 48
    else:
        w = 640
        h = 480
    film = lm.load_film('film', 'bitmap', w=w, h=h)
    renderer = lm.load_renderer('renderer', name,
        scene=scene,
        output=film,
        min_verts=3,
        max_verts=3,
        scheduler='time',
        render_time=60,
        seed=20,
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



# + active=""
# img_pt = render(scene, 'pt_naive_path')
# display_image(img_pt)
# -

img_bdpt = render(scene, 'bdpt')
display_image(img_bdpt)

# + active=""
# diff_gauss(img_pt, img_bdpt, 100)
# -

s=1
portal_plane2 = [
    [-s,0,-s],
    [-s,0, s],
    [ s,0,-s]
]
portal_cornell_double = [
    [0.26494, 0.73506, 0.96],
    [-0.265938, 0.73506, 0.96],
    [0.26494, 1.25494, 0.96]
]

img_bdpt_portal = render(scene, 'bdpt_portal', portal=portal_plane2)
display_image(img_bdpt_portal)

diff_gauss(img_bdpt_portal, img_bdpt, 100)


