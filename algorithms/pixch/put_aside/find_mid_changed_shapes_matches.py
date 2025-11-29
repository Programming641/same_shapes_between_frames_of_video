from libraries import pixel_functions, read_files_functions, pixel_shapes_functions, image_functions, same_shapes_functions, btwn_amng_files_functions

from PIL import Image
import math
import os, sys
import winsound, time
import pickle

from libraries.cv_globals import top_shapes_dir, top_images_dir, internal, frth_smallest_pixc, third_smallest_pixc


main_file = "15"
im1file = '14'
im2file = "15"
shapes_type = "intnl_spixcShp"
directory = "videos/street3/resized/min"

if len(sys.argv) >= 2:
   # excluding .png extension 
   im1file = sys.argv[0][0: len( sys.argv[0] ) - 4 ]
   im2file = sys.argv[1][0: len( sys.argv[1] ) - 4 ]
   main_file = sys.argv[2][0: len( sys.argv[2] ) - 4 ]
   directory = sys.argv[3]
   
   shapes_type = "intnl_spixcShp"
   
   print("execute find_mid_changed_shapes_matches.py " + directory + " " + im1file + " " + main_file )


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

pixch_ddir = top_shapes_dir + directory + "pixch/data/"
pixch_shapes_file = pixch_ddir + im1file + "." + im2file + "." + main_file + "mid_ch.data"
with open (pixch_shapes_file, 'rb') as fp:
   # ['23', '52', '56', ... ]
   # [ midium pixels changed shapes ]
   mid_ch_shapes = pickle.load(fp)
fp.close()


changed_shapes_dir = top_shapes_dir + directory + "pixch/ch_shapes/mid_ch_sty/"
if os.path.exists(changed_shapes_dir ) == False:
   os.makedirs(changed_shapes_dir )
changed_shapes_ddir = changed_shapes_dir + "data/"
if os.path.exists(changed_shapes_ddir ) == False:
   os.makedirs(changed_shapes_ddir )
save_result_fpath = changed_shapes_ddir + im1file + "." + im2file + "." + main_file + ".data"

swapped_files = False
if main_file == im2file:
   im2file = im1file
   swapped_files = True

original_image = Image.open(top_images_dir + directory + main_file + ".png")
im_width, im_height = original_image.size


shapes_dir = top_shapes_dir + directory + "shapes/"
shapes_dfile = shapes_dir + main_file + "shapes.data"
with open (shapes_dfile, 'rb') as fp:
   # { '79999': ['79999', ... ], ... }
   # { 'shapeid': [ pixel indexes ], ... }
   im1shapes = pickle.load(fp)
fp.close()


im2shapes_dfile = shapes_dir + im2file + "shapes.data"   
with open (im2shapes_dfile, 'rb') as fp:
   # { '79999': ['79999', ... ], ... }
   # { 'shapeid': [ pixel indexes ], ... }
   im2shapes = pickle.load(fp)
fp.close()


im1shape_neighbors_filepath = shapes_dir + "shape_nbrs/" + main_file + "_shape_nbrs.data"
im2shape_neighbors_filepath = shapes_dir + "shape_nbrs/" + im2file + "_shape_nbrs.data"


with open (im1shape_neighbors_filepath, 'rb') as fp:
   im1shapes_neighbors = pickle.load(fp)
fp.close()

with open (im2shape_neighbors_filepath, 'rb') as fp:
   im2shapes_neighbors = pickle.load(fp)
fp.close()

if "min" in directory:
   min_colors = True
else:
   min_colors = False

# { shapeid: (r,g,b), ... }
im1shapes_colors = pixel_shapes_functions.get_all_shapes_colors(main_file, directory, shapes_type=shapes_type, min_colors=min_colors)
im2shapes_colors = pixel_shapes_functions.get_all_shapes_colors(im2file, directory, shapes_type=shapes_type, min_colors=min_colors)

im2shape_by_pindex = {}
for shapeid in im2shapes:
   for pindex in im2shapes[shapeid]:
      im2shape_by_pindex[pindex] = shapeid


im1shapes_in_shp_coord = {}
for shapeid in im1shapes:
   if len( im1shapes[shapeid] ) < third_smallest_pixc:
      continue
   
   im1shapes_in_shp_coord[shapeid] = pixel_shapes_functions.get_shape_pos_in_shp_coord( im1shapes[shapeid], im_width, param_shp_type=0 )


im2shapes_in_shp_coord = {}
for shapeid in im2shapes:
   if len( im2shapes[shapeid] ) < third_smallest_pixc:
      continue
   
   im2shapes_in_shp_coord[shapeid] = pixel_shapes_functions.get_shape_pos_in_shp_coord( im2shapes[shapeid], im_width, param_shp_type=0 )


all_shapes_matches = []


max_progress_num = len( mid_ch_shapes )
cur_progress_num = len( mid_ch_shapes )
prev_progress_num = len( mid_ch_shapes )
remaining_chars = ""
for mid_ch_shape in mid_ch_shapes:
   remaining_chars = btwn_amng_files_functions.show_progress( max_progress_num, cur_progress_num, prev_progress_num, remaining_chars=remaining_chars, in_step=10 )
   prev_progress_num = cur_progress_num
   cur_progress_num -= 1


   if len( im1shapes[mid_ch_shape] ) < frth_smallest_pixc:
      continue

   # getting im2shapes that have pixels located in the same place as mid_ch_shape's pixels
   im2shapes_at_same_loc = []
   found_im2shapes = set()
   
   for mid_ch_s_pindex in im1shapes[mid_ch_shape]:
      cur_found_im2shape = im2shape_by_pindex[ mid_ch_s_pindex ]
      
      if min_colors is True:
         if im1shapes_colors[mid_ch_shape] != im2shapes_colors[cur_found_im2shape]:
            continue
      else:
         appear_diff = pixel_functions.compute_appearance_difference(im1shapes_colors[mid_ch_shape], im2shapes_colors[cur_found_im2shape] )
         if appear_diff is True:
            # different appearance
            continue
            
      
      im2shapes_at_same_loc.append( cur_found_im2shape  )
      found_im2shapes.add( im2shape_by_pindex[ mid_ch_s_pindex ] )
   
   largest_count = None
   largest_cnt_shape = None
   for temp_im2shape in found_im2shapes:
      cur_count = im2shapes_at_same_loc.count( temp_im2shape )
      
      if largest_count is None:
         largest_count = cur_count
         largest_cnt_shape = temp_im2shape
      elif largest_count < cur_count:
         largest_count = cur_count
         largest_cnt_shape = temp_im2shape
   
   if len( found_im2shapes ) == 0:
      continue
   
   # now I have image2 shape that have most pixels of mid_ch_shape, check if both neighbor shapes match
   
   matched_im2nbrs = set()
   mid_ch_s_nbr_total = 0
   cur_matched_im1_2neighbor = []
   for mid_ch_s_neighbor in im1shapes_neighbors[mid_ch_shape]:
      if len( im1shapes[mid_ch_s_neighbor] ) < third_smallest_pixc:
         continue

      mid_ch_s_nbr_total += 1
      for im2neighbor in im2shapes_neighbors[largest_cnt_shape]:
         if len( im2shapes[im2neighbor] ) < third_smallest_pixc or im2neighbor in cur_matched_im1_2neighbor:
            continue

         if min_colors is True:
            if im2shapes_colors[im2neighbor] != im1shapes_colors[mid_ch_s_neighbor]:
               continue
         else:
            appear_diff = pixel_functions.compute_appearance_difference( im2shapes_colors[im2neighbor], im1shapes_colors[mid_ch_s_neighbor] )
            if appear_diff is True:
               continue
         
         if len( im1shapes_in_shp_coord[mid_ch_s_neighbor] ) > len( im2shapes_in_shp_coord[im2neighbor] ):
            bigger_pixels = im1shapes_in_shp_coord[mid_ch_s_neighbor]
            smaller_pixels = im2shapes_in_shp_coord[im2neighbor]
         else:
            bigger_pixels = im2shapes_in_shp_coord[im2neighbor]
            smaller_pixels = im1shapes_in_shp_coord[mid_ch_s_neighbor]     
         
         
         
         nbr_temp_match = same_shapes_functions.match_shape_while_moving_it( bigger_pixels, smaller_pixels )
         if nbr_temp_match is True:
            matched_im2nbrs.add( im2neighbor )
            cur_matched_im1_2neighbor.append( im2neighbor )
            
            break


   if len( matched_im2nbrs ) > 0 and len( matched_im2nbrs ) / mid_ch_s_nbr_total > 0.35:

      if swapped_files is True:
         all_shapes_matches.append( ( largest_cnt_shape, mid_ch_shape ) )
      else:
         all_shapes_matches.append( ( mid_ch_shape, largest_cnt_shape ) )










with open(save_result_fpath, 'wb') as fp:
   pickle.dump(all_shapes_matches, fp)
fp.close()



































