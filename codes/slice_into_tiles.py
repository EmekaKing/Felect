# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 13:55:08 2020

@author: Emeka

Usage:
Splitting images into tiles of size 600*600

"""

# import packages
import os
from itertools import product
import rasterio as rio
from rasterio import windows
from PIL import Image

path = os.getcwd()
in_path = os.path.join(path, 'Int_Oblq_Images')
ext =  (".JPG", ".jpeg", ".jpg", ".png")
list_dir = os.listdir(in_path)

#out_path = r'C:/Users/emeka/Documents/2nd semester/Tehp/Int_Oblq_Images/split_folder'
out_path = os.path.join(in_path, 'split_folder')
output_filename = '_{}-{}.jpg'
count = 1

f = []
ff = []
fff = []

def get_tiles(ds, nbim, width=600, height=600):
    image = Image.open(nbim) #
    imwidth, imheight = image.size #
    splitw = imwidth/width #
    splith = imheight/height #
    matrix = int(splitw * splith) #
    # batch = [bt for bt in range(1, matrix + 1)] #
    
    nols, nrows = ds.meta['width'], ds.meta['height']
    offsets = product(range(0, nols, width), range(0, nrows, height)) # batch
    big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
    
    for col_off, row_off in offsets:
        window =windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
        transform = windows.transform(window, ds.transform)
        # batch += count #
        yield window, transform # batch

for file in list_dir:
    if file.endswith(ext):
        fl = file.split('.')[0]
        dfile = fl + output_filename
        dfname = os.path.join(in_path, file)#
        f.append(dfname)#
        ff.append(fl)#
        fff.append(dfile) #

for i, j, k in zip(f, ff, fff): #
    # filename = os.path.basename(inds) #
    # bim = os.path.join(in_path, filename)
    with rio.open(i) as inds: #
        tile_width, tile_height = 600, 600
        
        meta = inds.meta.copy()
        
        for window, transform in get_tiles(inds, i): # batch
            print(window)
            meta['transform'] = transform
            meta['width'], meta['height'] = window.width, window.height
            outpath = os.path.join(out_path, j, k.format(int(window.col_off), int(window.row_off)))# +'_'+str(bch)
            with rio.open(outpath, 'w', **meta) as outds:
                outds.write(inds.read(window=window))
            
#Reference: https://gis.stackexchange.com/questions/285499/how-to-split-multiband-image-into-image-tiles-using-rasterio/290059#290059            
