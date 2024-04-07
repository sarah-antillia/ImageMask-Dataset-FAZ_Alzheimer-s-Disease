# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import cv2
import sys
import glob
import json
import numpy as np
import shutil 
import traceback

class ImageMaskDatasetGenerator:

  def __init__(self, size = 512):
    self.size   = size
    self.RESIZE = (size, size)

  def generate(self, input_dir, output_dir):
    output_images_dir = os.path.join(output_dir,  "images")
    if os.path.exists(output_images_dir):
      shutil.rmtree(output_images_dir)
    if not os.path.exists(output_images_dir):
      os.makedirs(output_images_dir)

    output_masks_dir = os.path.join(output_dir, "masks")
    if os.path.exists(output_masks_dir):
      shutil.rmtree(output_masks_dir)
    if not os.path.exists(output_masks_dir):
      os.makedirs(output_masks_dir)

    subdirs = os.listdir(input_dir)
    for subdir in subdirs:
      full_subdir = os.path.join(input_dir, subdir)
      category = subdir.replace("_all", "")
      self.generate_one(full_subdir, category, output_images_dir, output_masks_dir)

  def generate_one(self, full_subdir, category, 
                   output_images_dir, output_masks_dir ):
    print("=== generate_one {} category {}".format(full_subdir, category))
    image_files  = glob.glob(full_subdir + "/*.png")
    image_files += glob.glob(full_subdir + "/*.jpg")
    print("--- image_files len {}".format(len(image_files)))
    input("--- generate_one")
    for image_file in image_files:
      image = cv2.imread(image_file)
      # Get the width and height of the original image 
      width =  image.shape[1]
      height = image.shape[0]
      print("--- image width:{} height:{}".format(width, height))
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      basename = os.path.basename(image_file)
      basename = basename.replace(".png", ".jpg")
      # Resize the image to be self.RESIZE 
      image = cv2.resize(image, self.RESIZE)
      filename = category + "_" + basename
      output_image_filepath = os.path.join(output_images_dir, filename)
      cv2.imwrite(output_image_filepath, image)
      print("--- Saved {}".format(output_image_filepath))
      if image_file.endswith(".png"): 
        mask_file = image_file.replace(".png", ".json")
      elif image_file.endswith(".jpg"):
        mask_file = image_file.replace(".jpg", ".json")
      output_mask_filepath = os.path.join(output_masks_dir, filename)
 
      # Read the json file includig a set of points of a polygon of mask region. 
      with open(mask_file, 'r') as f:
        data   = json.load(f)        
        shapes = data["shapes"]
        mask_height = data["imageHeight"]
        mask_width  = data["imageWidth"]
        shape  = shapes[0]
        # Get points of a polyogn.
        points = shape["points"]
        # Convert numpy array
        ipoints = np.array(points, np.int32)
        # Create an empty mask of the same size of the original image. 

        print("--- mask_height:{} mask_width:{}".format(mask_height, mask_width))
        mask = np.zeros((mask_width, mask_height, 3), dtype=np.uint8)

        # Fill the polygon region with the white color 
        cv2.fillPoly(mask, pts=[ipoints], color=(255, 255, 255))
        # Resize the mask to be self.RESIZE
        mask = cv2.resize(mask, self.RESIZE)
        cv2.imwrite(output_mask_filepath, mask)
        print("--- Saved {}".format(output_mask_filepath))
  

if __name__ == "__main__":
  try:
     images_dir = "./FAZ_sgementation"
     output_dir = "./FAZ_Alzheimers-Disease_master"
     generator = ImageMaskDatasetGenerator()
     generator.generate(images_dir,output_dir)

  except:
    traceback.print_exc()
        
