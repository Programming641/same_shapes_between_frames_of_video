# find matches between pixel change shape boundaries and large shape boundaries

from PIL import Image
import re, pickle
import math

import os, sys
from libraries.cv_globals import proj_dir, debug, top_shapes_dir, top_images_dir
from libraries import read_files_functions, pixel_shapes_functions, image_functions


directory = "videos/street3/resized/min"
main_filename = "10"
im1file = "10"
im2file = "11"
rest_of_filename = ""

shapes_type = "intnl_spixcShp"

pixch_im_fname = im1file + "." + im2file

if len(sys.argv) > 1:
   im1file = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   im2file = sys.argv[1][0: len( sys.argv[1] ) - 4 ]
   
   rest_of_filename = sys.argv[2][0: len( sys.argv[2] ) - 4 ]

   directory = sys.argv[3]

   print("execute script findim_pixch.py. file1 " + im1file + " file2 " + im2file + " directory " + directory )




# directory is specified but does not contain /
if directory != "" and directory[-1] != ('/'):
   directory +='/'

pixch_imdir = directory + "pixch/"

pixch_shapes_locations_path = top_shapes_dir + pixch_imdir + "locations/" + pixch_im_fname + "_loc.txt"
pixch_s_locations = read_files_functions.rd_ldict_k_v_l( pixch_im_fname, pixch_imdir, pixch_shapes_locations_path )


original_image = Image.open(top_images_dir + directory + main_filename + ".png")
im_width, im_height = original_image.size



# returned value has below form
# shapes[shapes_id][pixel_index] = {}
# shapes[shapes_id][pixel_index]['x'] = x
# shapes[shapes_id][pixel_index]['y'] = y
pixch_shapes = read_files_functions.rd_shapes_file(pixch_im_fname, pixch_imdir)

shapes_boundaries = {}
if shapes_type == "normal":
   pixch_bnd_n_Lshp_bnd_dir = top_shapes_dir + directory + "pixch_bnd_n_Lshp_nbr_bnd/normal/"

   shapes = read_files_functions.rd_shapes_file(main_filename, directory)
   im2shapes = read_files_functions.rd_shapes_file(im2file, directory)
   
   shapes_locations_path = top_shapes_dir + directory + "locations/" + main_filename + "_loc.txt"
   s_locations = read_files_functions.rd_ldict_k_v_l( main_filename, directory, shapes_locations_path )

   # get boundary pixels of all shapes
   for shapeid in shapes:
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(shapes[shapeid] )   

   shape_neighbors_file = top_shapes_dir + directory + "shape_nbrs/" + main_filename + "_shape_nbrs.txt"

elif shapes_type == "intnl_spixcShp":
   pixch_bnd_n_Lshp_bnd_dir = top_shapes_dir + directory + "pixch_bnd_n_Lshp_nbr_bnd/intnl_spixcShp/"


   s_pixcShp_intnl_dir = top_shapes_dir + directory + "s_pixc_shapes/" + "internal/"

   s_pixcShp_intnl_loc_dir = s_pixcShp_intnl_dir + "locations/"
   shapes_locations_path = s_pixcShp_intnl_loc_dir + main_filename + "_loc.txt"
   s_locations = read_files_functions.rd_ldict_k_v_l( main_filename, directory, shapes_locations_path )

   shape_neighbors_file = s_pixcShp_intnl_dir + "shape_nbrs/" + main_filename + "_shape_nbrs.txt"

   shapes_dir = s_pixcShp_intnl_dir + "shapes/"
   shapes_dfile = shapes_dir + main_filename + "shapes.data"

   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      shapes = pickle.load(fp)
   fp.close()


   # get boundary pixels of all shapes
   for shapeid, pindexes in shapes.items():
      cur_shape_pixels = { }
      for pindex in pindexes:
         cur_shape_pixels[pindex] = {}
            
         y = math.floor( int(pindex) / im_width)
         x  = int(pindex) % im_width 
      
         cur_shape_pixels[pindex]['x'] = x
         cur_shape_pixels[pindex]['y'] = y

      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels )






else:
   print("ERROR at find_pixch_shpbnd_n_Lshp_nbr_bnd.py shapes_type " + shapes_type + " is not supported" )
   sys.exit()


pixch_bnd_n_Lshp_bnd_ddir = pixch_bnd_n_Lshp_bnd_dir + "data/"
pixch_bnd_n_Lshp_bnd_file = main_filename + ".data"

if os.path.exists(pixch_bnd_n_Lshp_bnd_dir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_dir )
if os.path.exists(pixch_bnd_n_Lshp_bnd_ddir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_ddir )


shapes_in_im_areas = {}
for shapeid in shapes:
   for s_locs in s_locations:
      if shapeid in s_locs.keys():
         shapes_in_im_areas[shapeid] = s_locs[ list(s_locs.keys())[0] ]
         break
pixch_shapes_in_im_areas = {}
for shapeid in pixch_shapes:
   for s_locs in pixch_s_locations:
      if shapeid in s_locs.keys():
         pixch_shapes_in_im_areas[shapeid] = s_locs[ list(s_locs.keys())[0] ]
         break




pixch_shapes_boundaries = {}
# get boundary pixels of all shapes
for shapeid in pixch_shapes:
   pixch_shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(pixch_shapes[shapeid] )


# [ {"shapeid": ["nbr_shapeid", "nbr_shapeid", ...] }, ...  ]
shape_nbrs = read_files_functions.rd_ldict_k_v_l(main_filename, directory, shape_neighbors_file)

mainim_stats = image_functions.get_image_stats( main_filename, directory, shapes_type=shapes_type )
# [(6267, ['69738', ... ]),... ]   [ ( pixel counts, [ list of shapes that have this pixel count ] ), ... ]
# list is ordered by descending pixel counts 
mainim_stats = sorted(mainim_stats.items(), reverse=True)


def find_neighbor_bnd_matches( orig_shapeid, nbr_shapeid ):
   already_processed.append( orig_shapeid )
   if nbr_shapeid is None:   
      cur_shape_nbrs = [ cur_shape_nbrs.values() for cur_shape_nbrs in shape_nbrs if shapeid in cur_shape_nbrs.keys() ][0]
   else:
      cur_shape_nbrs = [ cur_shape_nbrs.values() for cur_shape_nbrs in shape_nbrs if nbr_shapeid in cur_shape_nbrs.keys() ][0]

   if len( cur_shape_nbrs ) > 1:
      print("ERROR at find_pixch_shpbnd_n_Lshp_nbr_bnd.py:find_neighbor_bnd_matches.  there should be only one list of neighbors")
      sys.exit()

   for cur_shape_nbr in list(cur_shape_nbrs)[0]:
      if cur_shape_nbr in already_processed or cur_shape_nbr in cur_already_processed:
         continue


      # getting all current shape's boundary pixels
      # {{'x': 190, 'y': 30}, {'x': 190, 'y': 31},.... }
      cur_nbr_bnd_pixels = shapes_boundaries[ cur_shape_nbr ].values()      

      # check if current shape boundaries and any of the pixel change shapes boundaries match
      # checking all pixel change shapes
      for pixch_shapeid in pixch_shapes_boundaries:
         
         same_area = any(item in shapes_in_im_areas[cur_shape_nbr] for item in pixch_shapes_in_im_areas[pixch_shapeid])
      
         if not same_area:
            # skip this pixel change shape because it is not in any of the same image areas as current shape
            continue
         
         cur_pixch_bnd_match = False
         for pixch_pixel in pixch_shapes_boundaries[pixch_shapeid].values():
            if pixch_pixel in cur_nbr_bnd_pixels:
               # current pixel change shape's boundary pixel found in main shape's boundary pixels
               pixch_matches[ orig_shapeid ]["nbrs"].append( cur_shape_nbr )
               pixch_matches[ orig_shapeid ]["pixch_pixels"].append( pixch_pixel )
               
               cur_pixch_bnd_match = True
         
         if cur_pixch_bnd_match is True:
         
            already_processed.append( cur_shape_nbr )      
            find_neighbor_bnd_matches( orig_shapeid, cur_shape_nbr )
               
               
      cur_already_processed.append( cur_shape_nbr )


print("main processing now begins")

pixch_matches = {}
already_processed = []
for pcount_shapes in mainim_stats:
   
   # looping list of shapes for each pixel counts
   for shapeid in pcount_shapes[1]:
      print("shapeid " + shapeid )

      cur_already_processed = []
      
      if len( shapes[ shapeid ] ) < 50:
         continue

      pixch_matches[ shapeid ] = {}
      pixch_matches[ shapeid ]["nbrs"] = []
      pixch_matches[shapeid]["pixch_pixels"] = []
      
      # getting all current shape's boundary pixels
      # {{'x': 190, 'y': 30}, {'x': 190, 'y': 31},.... }
      cur_shp_bnd_pixels = shapes_boundaries[ shapeid ].values()

      # check if current shape boundaries and any of the pixel change shapes boundaries match
      # checking all pixel change shapes
      for pixch_shapeid in pixch_shapes_boundaries:
         
         same_area = any(item in shapes_in_im_areas[shapeid] for item in pixch_shapes_in_im_areas[pixch_shapeid])
      
         if not same_area:
            # skip this pixel change shape because it is not in any of the same image areas as current shape
            continue

         
         cur_pixch_bnd_match = False
         for pixch_pixel in pixch_shapes_boundaries[pixch_shapeid].values():
            if pixch_pixel in cur_shp_bnd_pixels:
               # current pixel change shape's boundary pixel found in main shape's boundary pixels
               pixch_matches[ shapeid ]["pixch_pixels"].append( pixch_pixel )
               cur_pixch_bnd_match = True
               
         
      if cur_pixch_bnd_match is True:
         find_neighbor_bnd_matches( shapeid, None )
      
      pixch_empty = False
      if len( pixch_matches[shapeid]["pixch_pixels"] ) == 0:
         pixch_empty = True
      nbrs_empty = False
      if len( pixch_matches[shapeid]["nbrs"] ) == 0:
         nbrs_empty = True       

      if pixch_empty is True and nbrs_empty is True:
         pixch_matches.pop( shapeid )





with open(pixch_bnd_n_Lshp_bnd_ddir + pixch_bnd_n_Lshp_bnd_file, 'wb') as fp:
   pickle.dump(pixch_matches, fp)
fp.close()











