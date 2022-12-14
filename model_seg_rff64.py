# -*- coding: utf-8 -*-
"""model_seg_rff64.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12gaNBDGd1EcogagRn8wyDdk70AWHOsAe
"""

import tensorflow as tf
from tensorflow.keras import models, layers
from tensorflow.keras.layers.experimental import RandomFourierFeatures

height,width = 256,256
C = 1

UPSAMPLE_MODE = 'SIMPLE' # DECONV'
NET_SCALING = None
GAUSSIAN_NOISE = 0.1
EDGE_CROP = 16
ACTIVATION = 'relu'

# Build U-Net model
def upsample_conv(filters, kernel_size, strides, padding):
    return layers.Conv2DTranspose(filters, kernel_size, strides=strides, padding=padding)
def upsample_simple(filters, kernel_size, strides, padding):
    return layers.UpSampling2D(strides)

# if UPSAMPLE_MODE=='DECONV':
#     upsample=upsample_conv
# else:
#     upsample=upsample_simple

def create_model(phi_units = 64):
  upsample=upsample_simple

  input_img = layers.Input((width,height,C), name = 'RGB_Input')
  pp_in_layer = input_img
  if NET_SCALING is not None:
      pp_in_layer = layers.AvgPool2D(NET_SCALING)(pp_in_layer)

  pp_in_layer = layers.BatchNormalization()(pp_in_layer)

  c1 = layers.Conv2D(8, (3, 3), activation=ACTIVATION, padding='same') (pp_in_layer)
  c1 = layers.BatchNormalization()(c1)
  c1 = layers.Conv2D(8, (3, 3), padding='same') (c1)
  c1 = layers.BatchNormalization()(c1)
  p1 = layers.MaxPooling2D((2, 2)) (c1)

  c2 = layers.Conv2D(16, (3, 3), activation=ACTIVATION, padding='same') (p1)
  c2 = layers.BatchNormalization()(c2)
  c2 = layers.Conv2D(16, (3, 3), padding='same') (c2)
  c2 = layers.BatchNormalization()(c2)
  p2 = layers.MaxPooling2D((2, 2)) (c2)

  c3 = layers.Conv2D(32, (3, 3), activation=ACTIVATION, padding='same') (p2)
  c3 = layers.BatchNormalization()(c3)
  c3 = layers.Conv2D(32, (3, 3), padding='same') (c3)
  c3 = layers.BatchNormalization()(c3)
  p3 = layers.MaxPooling2D((2, 2)) (c3)

  c4 = layers.Conv2D(64, (3, 3), activation=ACTIVATION, padding='same') (p3)
  c4 = layers.BatchNormalization()(c4)
  c4 = layers.Conv2D(64, (3, 3), padding='same') (c4)
  c4 = layers.BatchNormalization()(c4)
  p4 = layers.MaxPooling2D(pool_size=(2, 2)) (c4)
  #%% Modified by CAJ
  flatten = layers.Flatten()(p4)
  rff = RandomFourierFeatures(output_dim=int(height/16)*int(width/16)*phi_units,trainable=True,name = 'Phi')(flatten)
  resha = layers.Reshape((int(height/16),int(width/16),-1))(rff)
  #%% End modify
  c5 = layers.Conv2D(128, (3, 3), activation=ACTIVATION, padding='same') (resha)#/(p4)
  c5 = layers.BatchNormalization()(c5)
  c5 = layers.Conv2D(128, (3, 3), activation=ACTIVATION, padding='same') (c5)
  c5 = layers.BatchNormalization()(c5)

  u6 = upsample(64, (2, 2), strides=(2, 2), padding='same') (c5)
  u6 = layers.concatenate([u6, c4])
  c6 = layers.Conv2D(64, (3, 3), activation=ACTIVATION, padding='same') (u6)
  c6 = layers.BatchNormalization()(c6)
  c6 = layers.Conv2D(64, (3, 3), activation=ACTIVATION, padding='same') (c6)
  c6 = layers.BatchNormalization()(c6)

  u7 = upsample(32, (2, 2), strides=(2, 2), padding='same') (c6)
  u7 = layers.concatenate([u7, c3])
  c7 = layers.Conv2D(32, (3, 3), activation=ACTIVATION, padding='same') (u7)
  c7 = layers.BatchNormalization()(c7)
  c7 = layers.Conv2D(32, (3, 3), activation=ACTIVATION, padding='same') (c7)
  c7 = layers.BatchNormalization()(c7)

  u8 = upsample(16, (2, 2), strides=(2, 2), padding='same') (c7)
  u8 = layers.concatenate([u8, c2])
  c8 = layers.Conv2D(16, (3, 3), activation=ACTIVATION, padding='same') (u8)
  c8 = layers.BatchNormalization()(c8)
  c8 = layers.Conv2D(16, (3, 3), activation=ACTIVATION, padding='same') (c8)
  c8 = layers.BatchNormalization()(c8)

  u9 = upsample(8, (2, 2), strides=(2, 2), padding='same') (c8)
  u9 = layers.concatenate([u9, c1], axis=3)
  c9 = layers.Conv2D(8, (3, 3), activation=ACTIVATION, padding='same') (u9)
  c9 = layers.BatchNormalization()(c9)
  c9 = layers.Conv2D(8, (3, 3), activation=ACTIVATION, padding='same') (c9)
  c9 = layers.BatchNormalization()(c9)

  d = layers.Conv2D(1, (1, 1), activation='sigmoid') (c9)
  d = layers.Cropping2D((EDGE_CROP, EDGE_CROP))(d)
  d = layers.ZeroPadding2D((EDGE_CROP, EDGE_CROP),name='output')(d)
  if NET_SCALING is not None:
      d = layers.UpSampling2D(NET_SCALING)(d)

  seg_model = models.Model(inputs=[input_img], outputs=[d])
  
  return seg_model