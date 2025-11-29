
from libraries import pixel_functions, read_files_functions, pixel_shapes_functions, same_shapes_functions

from PIL import Image
import math
import os, sys
import winsound
import pickle

from libraries.cv_globals import top_shapes_dir, top_images_dir, pixch_sty_dir, internal, frth_smallest_pixc, Lshape_size, third_smallest_pixc

im1file = '14'
im2file = "15"

directory = "videos/street3/resized/min"
shapes_type = "intnl_spixcShp"


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'


sty_shapes_dir = top_shapes_dir + directory + pixch_sty_dir + "/"
sty_shapes_file = sty_shapes_dir + "data/" + im1file + "." + im2file + "verified.data"
with open (sty_shapes_file, 'rb') as fp:
   # [('1270', '2072'), ('2062', '2062'), ... ]
   # [ ( image1 shapeid, image2 shapeid ), ... ]
   pixch_sty_shapes = pickle.load(fp)
fp.close()



original_image = Image.open(top_images_dir + directory + im1file + ".png")
im_width, im_height = original_image.size


im1shapes_boundaries = {}
im2shapes_boundaries = {}
if shapes_type == "normal":
   print("shapes_type normal is not supported in " + os.path.basename(__file__) )
   sys.exit(1)
   

elif shapes_type == "intnl_spixcShp":
   s_pixcShp_intnl_dir = top_shapes_dir + directory + "spixc_shapes/" + internal + "/"

   shapes_dir = s_pixcShp_intnl_dir + "shapes/"
   shapes_dfile = shapes_dir + im1file + "shapes.data"
   im2shapes_dfile = shapes_dir + im2file + "shapes.data"

   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im1shapes = pickle.load(fp)
   fp.close()
   
   for shapeid in im1shapes:
      pixels = set()
      for pindex in im1shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pindex, im_width )
         
         pixels.add( xy )
      
      im1shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(pixels)
      
      

   with open (im2shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im2shapes = pickle.load(fp)
   fp.close()


   shape_neighbors_file = s_pixcShp_intnl_dir + "shape_nbrs/" + im1file + "_shape_nbrs.txt"
   im2shape_neighbors_file = s_pixcShp_intnl_dir + "shape_nbrs/" + im2file + "_shape_nbrs.txt"



# {'79999': ['71555', '73953', ...], ...}
im1shapes_neighbors = read_files_functions.rd_dict_k_v_l(im1file, directory, shape_neighbors_file)
im2shapes_neighbors = read_files_functions.rd_dict_k_v_l(im2file, directory, im2shape_neighbors_file)

for shapeid in im2shapes:
   pixels = set()
   for pindex in im2shapes[shapeid]:
      xy = pixel_functions.convert_pindex_to_xy( pindex, im_width )
      pixels.add( xy )
      
   im2shapes[shapeid] = pixels



matched_neighbors = []
progress_counter = len( pixch_sty_shapes )
for each_sty_shapes in pixch_sty_shapes:
   print( str( progress_counter ) + " remaining")
   progress_counter -= 1
   
   for im1neighbor in im1shapes_neighbors[each_sty_shapes[0]]:
      if len( im1shapes[im1neighbor] ) < frth_smallest_pixc:
         continue
      
      im1vicinity_pix = pixel_shapes_functions.get_shape_vicinity_pixels( im1shapes_boundaries[im1neighbor], 15, original_image.size, 1 )
      
      for im2neighbor in im2shapes_neighbors[each_sty_shapes[1]]:
         if len( im2shapes[im2neighbor] ) < frth_smallest_pixc:
            continue

         same_location = im2shapes[im2neighbor].intersection( im1vicinity_pix )
         if len( same_location ) == 0:
            continue

         im1shapes_total = len( im1shapes[im1neighbor] )
         im2shapes_total = len( im2shapes[im2neighbor] )
      
         im1_2pixels_diff = abs( im1shapes_total - im2shapes_total )
         if im1_2pixels_diff != 0:
            if im1shapes_total > im2shapes_total:
               if im1_2pixels_diff / im2shapes_total > 1:
                  continue
            else:
               if im1_2pixels_diff / im1shapes_total > 1:
                  continue
         
         # [(12, 15), (11, 15), ... ]
         im1shp_coord_xy  = pixel_shapes_functions.get_shape_pos_in_shp_coord( im1shapes[im1neighbor], im_width, param_shp_type=0 )  
         im2shp_coord_xy = pixel_shapes_functions.get_shape_pos_in_shp_coord( im2shapes[im2neighbor], im_width, param_shp_type=1 )

         im1im2nbr_match = same_shapes_functions.match_shape_while_moving_it( im1shp_coord_xy, im2shp_coord_xy, match_threshold=0.63)
         if im1im2nbr_match is True:         
            matched_neighbors.append( [ [ each_sty_shapes[0], im1neighbor ], [ each_sty_shapes[1], im2neighbor ] ] )



sty_shapes_nbrs_ddir = sty_shapes_dir + "nbrs/data/"
if os.path.exists(sty_shapes_nbrs_ddir ) == False:
   os.makedirs(sty_shapes_nbrs_ddir)

with open(sty_shapes_nbrs_ddir + im1file + "." + im2file + ".data", 'wb') as fp:
   pickle.dump(matched_neighbors, fp)
fp.close()
   




frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)






