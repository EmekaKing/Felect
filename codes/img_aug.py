# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 07:09:54 2020

@author: Emeka
"""
import keras
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from skimage import io


datagen = ImageDataGenerator(
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='reflect', cval=125)  #also try constant, nearest and reflect

# to pick from a folder of folders of images i.e multiclass
dataset = []
import numpy as np
from PIL import Image
import os

image_directory = 'Horizontal/'
SIZE = 600
dataset = []

my_images = os.listdir(image_directory)
for i, image_name in enumerate(my_images):
    if (image_name.split('.')[1] == 'JPG'):
        image = io.imread(image_directory + image_name)
        image = Image.fromarray(image, 'RGB')
        image = image.resize((SIZE,SIZE))
        dataset.append(np.array(image))
        
x = np.array(dataset)

i = 0
for batch in datagen.flow(x,
                          batch_size=16,
                          save_to_dir='new_augmented',
                          save_prefix='aug',
                          save_format='jpg'):
    
    i+=1
    if i > 8:
        break

    
