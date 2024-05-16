# let's start with the Imports 
from PIL import Image
from pillow_heif import register_heif_opener
import os

from os import listdir
from os.path import isfile, join

# for reading heic and convert heic files to jpg
register_heif_opener()

img_dir = 'images'
files = [f for f in listdir(img_dir) if isfile(join(img_dir, f))]
files = [f for f in files if f.split('.')[-1] == 'HEIC']

jpg_out_dir = 'outputs/jpeg_original'
os.makedirs(jpg_out_dir, exist_ok=True)

jpg_resized_out_dir = 'outputs/jpeg_resized'
os.makedirs(jpg_resized_out_dir, exist_ok=True)

maxed_height = 800

for fn in files:
  fp = img_dir + '/' + fn
  # convert heic to jpg
  heic_img = Image.open(fp)
  jpg_fn = jpg_out_dir + '/' + fn.split('.')[0] + '.jpg'
  heic_img.save(jpg_fn, format="JPEG", optimize = True, quality = 100)
  
  # resize jpg
  jpg_resized_fn = jpg_resized_out_dir + '/' + fn.split('.')[0] + '.jpg'
  img = Image.open(jpg_fn)
  img.thumbnail((maxed_height, maxed_height))
  img.save(jpg_resized_fn)
