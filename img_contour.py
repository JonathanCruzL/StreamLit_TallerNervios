# -*- coding: utf-8 -*-
"""img_contour.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xAzaOO6lie9c6HUxYPjZN4DU5KcZVuKv
"""

import matplotlib.pyplot as plt
from skimage import segmentation
import numpy as np

def img_contour(img,mask):
  plt.figure(figsize = (5,5))
  plt.imshow(img, cmap = "gray")
  edges_est = segmentation.clear_border(np.squeeze(mask))
  plt.contour(edges_est,[0.5],colors=['red'])
  plt.axis('off')
  plt.show()