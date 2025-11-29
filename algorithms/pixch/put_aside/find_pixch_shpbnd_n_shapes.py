# find matches between pixel change shape boundaries and large shape boundaries

from PIL import Image
import re, pickle
import math

import os, sys
from libraries.cv_globals import proj_dir, debug, top_shapes_dir, top_images_dir, internal, pixch_bnd_dir
from libraries import read_files_functions, pixel_shapes_functions, image_functions


directory = "videos/street3/resized/min"
main_filename = "13"
im1file = "12"
im2file = "13"
rest_of_filename = ""

shapes_type = "intnl_spixcShp"

pixch_im_fname = im1file + "." + im2file

if len(sys.argv) > 1:
   im1file = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   im2file = sys.argv[1][0: len( sys.argv[1] ) - 4 ]
   
   rest_of_filename = sys.argv[2][0: len( sys.argv[2] ) - 4 ]

   directory = sys.argv[3]

   print("execute script " + os.path.basename(__file__) + im1file + " file2 " + im2file + " directory " + directory )




# directory is specified but does not contain /
if directory != "" and directory[-1] != ('/'):
   directory +='/'

pixch_bnd_n_Lshp_bnd_dir = top_shapes_dir + directory + pixch_bnd_dir + "/"
pixch_bnd_n_Lshp_bnd_ddir = pixch_bnd_n_Lshp_bnd_dir + "data/"
pixch_bnd_n_Lshp_bnd_file = im1file + "." + im2file + "allShp" + main_filename + ".data"

if os.path.exists(pixch_bnd_n_Lshp_bnd_dir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_dir )
if os.path.exists(pixch_bnd_n_Lshp_bnd_ddir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_ddir )

pixch_imdir = directory + "pixch/"


original_image = Image.open(top_images_dir + directory + main_filename + ".png")
im_width, im_height = original_image.size



# returned value has below form
# shapes[shapes_id][pixel_index] = {}
# shapes[shapes_id][pixel_index]['x'] = x
# shapes[shapes_id][pixel_index]['y'] = y
pixch_shapes = read_files_functions.rd_shapes_file(pixch_im_fname, pixch_imdir)

if shapes_type == "normal":
   shapes = read_files_functions.rd_shapes_file(main_filename, directory)
   im2shapes = read_files_functions.rd_shapes_file(im2file, directory)
   
   shapes_locations_path = top_shapes_dir + directory + "locations/" + main_filename + "_loc.txt"
   s_locations = read_files_functions.rd_ldict_k_v_l( main_filename, directory, shapes_locations_path )
elif shapes_type == "intnl_spixcShp":
   s_pixcShp_intnl_dir = top_shapes_dir + directory + "spixc_shapes/" + internal + "/"

   s_pixcShp_intnl_loc_dir = s_pixcShp_intnl_dir + "locations/"
   shapes_locations_path = s_pixcShp_intnl_loc_dir + main_filename + "_loc.data"

   with open (shapes_locations_path, 'rb') as fp:
      # {'79999': ['25'], ...}
      s_locations = pickle.load(fp)
   fp.close()

   shapes_dir = s_pixcShp_intnl_dir + "shapes/"
   shapes_dfile = shapes_dir + main_filename + "shapes.data"
   im2shapes_dfile = shapes_dir + im2file + "shapes.data"

   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      shapes = pickle.load(fp)
   fp.close()

   with open (im2shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im2shapes = pickle.load(fp)
   fp.close()

else:
   print("ERROR at find_matches_btwn_pixch_shpbnd_n_Lshp_bnd.py shapes_type " + shapes_type + " is not supported" )
   sys.exit()



shapes_boundaries = {}
im2shapes_boundaries = {}
if shapes_type == "normal":

   # get boundary pixels of all shapes
   for shapeid in shapes:
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(shapes[shapeid] )

   for shapeid in im2shapes:
      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(im2shapes[shapeid] )

elif shapes_type == "intnl_spixcShp":
   # get boundary pixels of all shapes
   for shapeid, pindexes in shapes.items():
      cur_shape_pixels = set()
      for pindex in pindexes:
         y = math.floor( int(pindex) / im_width)
         x  = int(pindex) % im_width 
      
         cur_shape_pixels.add( (x,y) )
         
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels )

   for shapeid, pindexes in im2shapes.items():
      cur_shape_pixels = set()
      for pindex in pindexes:
         y = math.floor( int(pindex) / im_width)
         x  = int(pindex) % im_width 
      
         cur_shape_pixels.add( (x,y) )

      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels )


pixch_shapes_boundaries = set()
# get boundary pixels of all shapes
for shapeid in pixch_shapes:
   cur_shape_pixels = set()
   for xy in pixch_shapes[shapeid].values():
      cur_shape_pixels.add( (xy['x'], xy['y']) )

   pixch_shapes_boundaries |= set( pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels ) )


all_pixch_bnd_n_shp_bnd = set()
for shapeid in shapes_boundaries:
   # shapes_boundaries[shapeid] -> [(2, 0), ...]
   cur_pixch_bnd_n_shp_bnd = set( shapes_boundaries[shapeid] ).intersection( pixch_shapes_boundaries )
   
   all_pixch_bnd_n_shp_bnd |= cur_pixch_bnd_n_shp_bnd


with open(pixch_bnd_n_Lshp_bnd_ddir + pixch_bnd_n_Lshp_bnd_file, 'wb') as fp:
   pickle.dump(all_pixch_bnd_n_shp_bnd, fp)
fp.close()













