
from libraries import pixel_shapes_functions, read_files_functions, pixel_functions, same_shapes_functions

from PIL import Image
import math
import os, sys
import winsound
import pickle

from libraries.cv_globals import proj_dir, internal, frth_smallest_pixc, Lshape_size

if proj_dir != "" and proj_dir[-1] != "/":
   proj_dir +='/'

top_shapes_dir = proj_dir + "/shapes/"
top_images_dir = proj_dir + "/images/"


image_filename = '11'
image_filename2 = "12"
shapes_type = "intnl_spixcShp"

directory = "videos/street3/resized/min"

if len(sys.argv) >= 2:
   image_filename = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   directory = sys.argv[1]

   print("execute script find_shapes.py. filename " + image_filename + " directory " + directory )


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

pixch_ddir = top_shapes_dir + directory + "pixch/data/"

im1pixch_shapes_file = pixch_ddir + image_filename + "." + image_filename2 + "." + image_filename + "shapes.data"
im2pixch_shapes_file = pixch_ddir + image_filename + "." + image_filename2 + "." + image_filename2 + "shapes.data"

with open (im1pixch_shapes_file, 'rb') as fp:
   # ['2', '68', ... ]
   # [ shapeid, ... ]
   im1pixch_shapes = pickle.load(fp)
fp.close()
with open (im2pixch_shapes_file, 'rb') as fp:

   im2pixch_shapes = pickle.load(fp)
fp.close()

original_image = Image.open(top_images_dir + directory + image_filename + ".png")
im_width, im_height = original_image.size

im1shapes_boundaries = {}
im2shapes_boundaries = {}
if shapes_type == "normal":
   # return value form is
   # shapes[shapes_id][pixel_index] = {}
   # shapes[shapes_id][pixel_index]['x'] = x
   # shapes[shapes_id][pixel_index]['y'] = y
   im1shapes = read_files_functions.rd_shapes_file(image_filename, directory)
   im2shapes = read_files_functions.rd_shapes_file(image_filename2, directory)

   # get boundary pixels of all shapes
   for shapeid in im1shapes:
      im1shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(im1shapes[shapeid] )
   # get boundary pixels of all shapes
   for shapeid in im2shapes:
      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(im2shapes[shapeid] )   

   
   im1shapes_locations_path = top_shapes_dir + directory + "locations/" + image_filename + "_loc.data"   
   im2shapes_locations_path = top_shapes_dir + directory + "locations/" + image_filename2 + "_loc.data"   
   
   im1nbrs_filepath = top_shapes_dir + directory + "shape_nbrs/" + image_filename + "_shape_nbrs.txt"
   im2nbrs_filepath = top_shapes_dir + directory + "shape_nbrs/" + image_filename2 + "_shape_nbrs.txt"

elif shapes_type == "intnl_spixcShp":
   s_pixcShp_intnl_dir = top_shapes_dir + directory + "spixc_shapes/" + internal + "/"

   shapes_dir = s_pixcShp_intnl_dir + "shapes/"
   shapes_dfile = shapes_dir + image_filename + "shapes.data"
   im2shapes_dfile = shapes_dir + image_filename2 + "shapes.data"

   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im1shapes = pickle.load(fp)
   fp.close()
   
   with open (im2shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im2shapes = pickle.load(fp)
   fp.close() 


   for shapeid in im1shapes:
      cur_shape_pixels = []
      for pindex in im1shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pindex, im_width )
         cur_shape_pixels.append( xy )

      im1shapes[shapeid] = cur_shape_pixels


   for shapeid in im2shapes:
      cur_shape_pixels = []
      for pindex in im2shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pindex, im_width )
         cur_shape_pixels.append( xy )

      im2shapes[shapeid] = cur_shape_pixels



   im1shapes_locations_path = s_pixcShp_intnl_dir + "locations/" + image_filename + "_loc.data"   
   im2shapes_locations_path = s_pixcShp_intnl_dir + "locations/" + image_filename2 + "_loc.data" 

   im1nbrs_filepath = s_pixcShp_intnl_dir + "shape_nbrs/" + image_filename + "_shape_nbrs.txt"
   im2nbrs_filepath = s_pixcShp_intnl_dir + "shape_nbrs/" + image_filename2 + "_shape_nbrs.txt"



with open (im1shapes_locations_path, 'rb') as fp:
   # {'2': ['1'], ... }
   im1shapes_locations = pickle.load(fp)
fp.close() 
with open (im2shapes_locations_path, 'rb') as fp:
   im2shapes_locations = pickle.load(fp)
fp.close() 

# {"shapeid": ["nbr_shapeid", "nbr_shapeid", ...], ...  }
im1shapes_nbrs = read_files_functions.rd_dict_k_v_l(image_filename, directory, im1nbrs_filepath)
im2shapes_nbrs = read_files_functions.rd_dict_k_v_l(image_filename2, directory, im2nbrs_filepath)

im1shapes_colors = pixel_shapes_functions.get_all_shapes_colors(image_filename, directory, shapes_type=shapes_type)
im2shapes_colors = pixel_shapes_functions.get_all_shapes_colors(image_filename2, directory, shapes_type=shapes_type)


def get_neighbors( cur_im_pixels, im_pixch_shape, already_taken_nbrs, cur_im_shapes, pixch_shape="" ):

   for im1nbr in im1shapes_nbrs[im_pixch_shape]:
      if im1nbr in already_taken_nbrs:
         continue

      already_taken_nbrs.append( im1nbr )
      # if current shape is pixch shape then, take its neighbors only if they are pixch shapes
      if pixch_shape == "pixch":
         if im1nbr in im1pixch_shapes:
            cur_im_pixels.extend( im1shapes[im1nbr] )
            cur_im_shapes[im1nbr] = im1shapes[im1nbr]
         else:
            # there is no need to find its neighbors if itself is not pixch shape.
            continue

      else:
         cur_im_pixels.extend( im1shapes[im1nbr] )
         cur_im_shapes[im1nbr] = im1shapes[im1nbr]
         
         if len( cur_im_pixels ) < Lshape_size:
            continue


      # check if im1pixch_shape's direct neighbor's neighbors are pixch shapes.
      nbr_is_pixch_shape = [ nbr for nbr in im1shapes_nbrs[im1nbr] if nbr in im1pixch_shapes ]

      for each_pixch_shape in nbr_is_pixch_shape:
         already_taken_nbrs.append( each_pixch_shape )
         get_neighbors( cur_im_pixels, each_pixch_shape, already_taken_nbrs, cur_im_shapes, pixch_shape="pixch" )
         


      return cur_im_pixels


def im2get_neighbors( cur_im_pixels_len, im_pixch_shape, already_taken_nbrs, cur_im_shapes, pixch_shape="" ):

   for im2nbr in im2shapes_nbrs[im_pixch_shape]:
      if im2nbr in already_taken_nbrs:
         continue

      already_taken_nbrs.append( im2nbr )
      # if current shape is pixch shape then, take its neighbors only if they are pixch shapes
      if pixch_shape == "pixch":
         if im2nbr in im2pixch_shapes:
            cur_im_pixels_len += len( im2shapes[im2nbr] )
            cur_im_shapes[im2nbr] = im2shapes[im2nbr]
         else:
            # there is no need to find its neighbors if itself is not pixch shape.
            continue

      else:
         cur_im_pixels_len += len( im2shapes[im2nbr] )
         cur_im_shapes[im2nbr] = im2shapes[im2nbr]
         
         if cur_im_pixels_len < Lshape_size:
            continue


      # check if im1pixch_shape's direct neighbor's neighbors are pixch shapes.
      nbr_is_pixch_shape = [ nbr for nbr in im2shapes_nbrs[im2nbr] if nbr in im2pixch_shapes ]

      for each_pixch_shape in nbr_is_pixch_shape:
         already_taken_nbrs.append( each_pixch_shape )
         im2get_neighbors( cur_im_pixels_len, each_pixch_shape, already_taken_nbrs, cur_im_shapes, pixch_shape="pixch" )
         


      return cur_im_pixels_len





# { pixch_shapeid: ( [ im1shapes ], [im2shapes ] ), ... }
all_matches = {}
progress_counter = len( im1pixch_shapes )
for im1pixch_shape in im1pixch_shapes:
   print( str( progress_counter ) + " remaining" )
   progress_counter -= 1
   
   
   if len( im1shapes[im1pixch_shape] ) < frth_smallest_pixc:
      continue
   
   already_taken_nbrs = []
   already_taken_nbrs.append( im1pixch_shape )
   
   # {'5588': [(388, 13), (388, 12), ... }
   # { shapeid: [ (x,y), ... ], shapeid: [ (x,y), ... ], ... }
   cur_im1shapes = {}
   cur_im1shapes[im1pixch_shape] = im1shapes[im1pixch_shape]
   cur_im1pixels = im1shapes[im1pixch_shape]
   
   cur_im1pixels = get_neighbors( cur_im1pixels, im1pixch_shape, already_taken_nbrs, cur_im1shapes )
  
   # {(395, 4), (381, 69), ... }
   vicinity_pixels = pixel_shapes_functions.get_shape_vicinity_pixels( cur_im1pixels, 15, original_image.size, param_shp_type=1 )
   
   # cur_im1pixels can get huge. so delete it, because I don't need its contents from here on. just need pixel counts
   cur_im1pixels_len = len( cur_im1pixels )
   del cur_im1pixels

   # {5588: [5, 10, 15]}
   cur_im1pixch_shape_loc = pixel_shapes_functions.get_shape_im_locations( image_filename, directory, vicinity_pixels, int(im1pixch_shape) )
   # converting integers of locations to strings of locations
   cur_im1pixch_shape_loc[int(im1pixch_shape)] = [ str(location) for location in cur_im1pixch_shape_loc[int(im1pixch_shape)] ]

   # {'5588': [(128, 128, 128), (10, 13), (10, 12), ... }
   # { shapeid: [ shape color , (x,y), (x,y), ... ], ... }
   cur_im1shapes = pixel_shapes_functions.get_shapes_pos_in_shp_coord( cur_im1shapes, im_width, im1shapes_colors, param_shp_type=1 )
   
   for im2pixch_shape in im2pixch_shapes:
      if len( im2shapes[im2pixch_shape] ) < frth_smallest_pixc:
         continue

      same_locations = set( im2shapes_locations[im2pixch_shape] ).intersection( set( cur_im1pixch_shape_loc[int(im1pixch_shape)] ) )
      
      if len( same_locations ) == 0:
         continue

      im2already_taken_nbrs = []
      im2already_taken_nbrs.append( im2pixch_shape )
   
      cur_im2shapes = {}
      cur_im2shapes[im2pixch_shape] = im2shapes[im2pixch_shape]
      
      cur_im2pixels_len = len( im2shapes[im2pixch_shape] )
   
      cur_im2pixels_len = im2get_neighbors( cur_im2pixels_len, im2pixch_shape, im2already_taken_nbrs, cur_im2shapes )
      
      # if pixel amounts are so different, then skip it.
      im_pixels_diff = abs( cur_im1pixels_len - cur_im2pixels_len )
      if im_pixels_diff > cur_im1pixels_len * 0.8:
         continue

      cur_im2shapes = pixel_shapes_functions.get_shapes_pos_in_shp_coord( cur_im2shapes, im_width, im2shapes_colors, param_shp_type=1 )

      same_shapes_functions.find_shapes_match( cur_im1shapes, cur_im2shapes, im1pixch_shape )
      


with open(pixch_ddir  + image_filename + "." + image_filename2 + "matched_shapes.data", 'wb') as fp:
   pickle.dump(all_matches, fp)
fp.close()





frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)



































