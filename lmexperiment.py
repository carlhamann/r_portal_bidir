import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import gaussian_filter

def display_image(img, fig_size=15, scale=1, title=None):
    f = plt.figure(figsize=(fig_size,fig_size))
    ax = f.add_subplot(111)                                                                                                                                                
    ax.imshow(np.clip(np.power(img*scale,1/2.2),0,1), origin='lower')
    if title:
        ax.set_title(title)
    ax.axis('off')
    plt.show()

def diff_gauss(img1, img2, fig_size=15, scale=1, title=None):
    diff = np.abs(gaussian_filter(img1 - img2, sigma=3))
    f = plt.figure(figsize=(fig_size,fig_size))
    ax = f.add_subplot(111)
    ax.imshow(np.clip(np.power(diff*scale,1/2.2),0,1), origin='lower')
    if title:
        ax.set_title(title)
    ax.axis('off')
    plt.show()

def display_error(diff):
    f = plt.figure(figsize=(20,20))
    ax = f.add_subplot(111)
    im = ax.imshow(diff, origin='lower', vmax=1.5)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax)
    plt.show()
    
def rmse_pixelwised(img1, img2):
    return np.sqrt(np.sum((img1 - img2) ** 2, axis=2) / 3) 

def rrmse_pixelwised(ref, img):
    # Compute rRMSE
    rmse = np.sqrt(np.sum((img - ref) ** 2, axis=2) / 3)
    ave  = np.sqrt(np.sum(ref**2, axis=2) / 3)
    with np.errstate(divide='ignore', invalid='ignore'):
        rrmse = np.where(ave==0, -1, rmse / ave)
    return rrmse

def rmse(ref, img):
    return np.sqrt(np.sum((ref-img)**2) / (ref.size))

def rrmse(ref, img):
    err = rmse(ref, img)
    ave  = np.sum(ref) / (ref.size)
    return err / ave

def print_errors(ref, img):
    print('RMSE : %.5f' % rmse(ref, img))
    print('rRMSE: %.5f' % rrmse(ref, img))

def normalization(img):
    """Compute normalization factor"""
    w,h,_ = img.shape
    r = img[:,:,0]
    g = img[:,:,1]
    b = img[:,:,2]
    lum = 0.212671 * r + 0.715160 * g + 0.072169 * b
    return np.sum(lum) / (w*h)
