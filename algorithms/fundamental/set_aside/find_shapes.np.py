#
# algorithm for determining the closest match with the color group uses how far away the RGB value is from original
#
#
from libraries import pixel_functions

from PIL import Image
import math
import numpy as np
import os, sys
import winsound

from collections import OrderedDict
from libraries.cv_globals import proj_dir

if proj_dir != "" and proj_dir[-1] != "/":
   proj_dir +='/'

shapes_dir = proj_dir + "/shapes/"
images_dir = proj_dir + "/images/"

image_filename = '25'

directory = "videos/giraffe/resized/min"

if len(sys.argv) >= 2:
   image_filename = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   directory = sys.argv[1]

   print("execute script find_shapes.py. filename " + image_filename + " directory " + directory )


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

target_im_shapes_dir = shapes_dir + directory + "shapes/"


if os.path.exists(target_im_shapes_dir ) == False:
   os.makedirs(target_im_shapes_dir)
   
   

# Load the image and convert to numpy array
original_image = Image.open(images_dir + directory + image_filename + ".png")
original_array = np.array(original_image)

# Get the image size
image_size = original_array.shape[:2]

# Create a meshgrid of the pixel coordinates
xx, yy = np.meshgrid(np.arange(image_size[1]), np.arange(image_size[0]))

# Create a flattened array of the pixel coordinates
coords = np.vstack((yy.ravel(), xx.ravel())).T

# Get the pixel values as a 2D array of shape (num_pixels, 3)
pixels = original_array.reshape((-1, 3))

# Loop through the flattened array of pixel coordinates
for i, coord in enumerate(coords):
      x, y = coord

      # Convert the current pixel index to a 1D index
      current_pixel_index = y * image_size[1] + x

      # initializing current pixel' shape number. This 
      current_shape_id = None
      
      # this is needed for checking if pixel has same color with every pixels in the confirmed shapes
      cur_shape_containing_confirmed_shapes = None
      
      cur_pixel_neighbors = pixel_functions.get_nbr_pixels(current_pixel_index, image_size)      

      # check if current pixel is in other pixel's shapes.
      if shapes.size != 0:
         print( shapes )
         print( shapes_pix )
         sys.exit()
         
         
         
         for shape_id, shapes_lists in reversed(shapes.items()):
            if current_pixel_index in shapes_lists:
               # current pixel is found in existing shape. current shape will be this found shape
               current_shape_id = shape_id
               
               cur_shape_containing_confirmed_shapes = shapes_lists


      # current pixel was not found in all shapes so create its own shape
      if current_shape_id == None:     
         # create shape with current pixel's number as shape's id
         current_shape_id = current_pixel_index
         # make sure to put current pixel in current pixel shape
         
         shapes = np.append( shapes, current_shape_id )
         shapes_pix = np.append( shapes_pix, current_shape_id )
         shapes_pix = shapes_pix[ ..., np.newaxis ]

      cur_shape_pixel_RGB = original_pixel[current_shape_id]



      # iterating each one of current pixel's unfound neighbors
      for neighbor in cur_pixel_neighbors:
         
         neighbor_shape_found, cur_shape_nei_shape_appearance = False, False
         neighbor_shape_index = None  
         
         cur_nbr_containing_shapes = []
         # check if this neighbor is already in the shape
         cur_shape_counter = 0
         for pindexes_l in shapes_pix:
            print( shapes_pix )

            # iterating all neighbor shapes
            if neighbor in pindexes_l:
                  
                  # check if neighbor is already in the same shape as current_pixel_index
                  if shapes[cur_shape_counter] == current_shape_id:
                     neighbor_shape_found = True 
                     break
                  
                  cur_nbr_containing_shapes = shapes_lists
                               
                  neighbor_shape_index = shapes[cur_shape_counter]                
                              
            cur_shape_counter += 1

         if cur_nbr_containing_shapes:
            # neighbor is found in neighbor_shape_index
            # check if all pixels in the  neighbor_shape_index have same appearance as current_shape_id
            # merge two shapes only if they all have the same color
            # merging all pixels in neighbor shape into current shape

            all_pixels_same_clr = None
            for cur_nbr_containing_pixel in cur_nbr_containing_shapes:
               for cur_shape_pixel in shapes[current_shape_id]:
               
                  clrch, brit_thres, brit_ch_v = pixel_functions.compute_appearance_difference(original_pixel[cur_nbr_containing_pixel] ,
                                                 original_pixel[cur_shape_pixel], 30 )
                  
                  # color changed is true or color did not change but brightness is not within threshold
                  if clrch or ( not clrch and not brit_thres ):
                     all_pixels_same_clr = False
                     break

               if all_pixels_same_clr == False:
                  break
                  
            if all_pixels_same_clr != False:
               shapes[current_shape_id].extend(shapes[neighbor_shape_index])
               
               shapes.pop(neighbor_shape_index)       


         if  neighbor_shape_found == False:

            neighbor_pixel_RGB = original_pixel[neighbor]

            # make sure all pixels have same color as neighbor, then you can put neighbor in current_shape_id shape
            all_pixels_same_clr = None
            if cur_shape_containing_confirmed_shapes:
               for pixels in cur_shape_containing_confirmed_shapes:
                  clrch, brit_thres, brit_ch_v = pixel_functions.compute_appearance_difference(original_pixel[pixels], neighbor_pixel_RGB, 30 )
                 
                  if clrch or ( not clrch and not brit_thres ):
                     all_pixels_same_clr = False
                     break
               
               if all_pixels_same_clr != False:
                  
                  # neighbor pixel will be added to current shape
                  shapes[current_shape_id].append(neighbor)                 
            


file = open(target_im_shapes_dir + image_filename + "_shapes.txt", 'w')
file.write(str(shapes))
file.close()


frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)






