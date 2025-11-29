# not found shapes are the shapes that are not found by the find_sty_shapes_from_pixch.py

from libraries import pixel_functions, read_files_functions, pixel_shapes_functions, same_shapes_functions

from PIL import Image
import math
import os, sys
import winsound
import pickle

from libraries.cv_globals import top_shapes_dir, top_images_dir, frth_smallest_pixc, Lshape_size, internal

main_filename = "10"
image_filename = '10'
image_filename2 = "11"

directory = "videos/street3/resized/min"
top_edge_dir = "videos/street3/resized/"
shapes_type = "intnl_spixcShp"


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

original_image = Image.open(top_images_dir + directory + image_filename + ".png")
im_width, im_height = original_image.size

pixch_dir = top_shapes_dir + directory + "pixch/"
sty_shapes_dfile = pixch_dir + "sty_shapes/"  + image_filename + "." + image_filename2 + "." + image_filename + ".data"
with open (sty_shapes_dfile, 'rb') as fp:
   sty_shapes = pickle.load(fp)
fp.close()

pixch_edge_dir = pixch_dir + "edge/"
if os.path.exists(pixch_edge_dir ) == False:
   os.makedirs(pixch_edge_dir)


edge_dir = top_shapes_dir + top_edge_dir + "edges/" + shapes_type + "/"
edge_dfile = edge_dir + "data/" + image_filename + ".data"
with open (edge_dfile, 'rb') as fp:
   # # [ [ shapeid1, shapeid2, shapeid1's edge pixel, shapeid2's edge pixel ], ... ]
   edges = pickle.load(fp)
fp.close()

all_edges = set()
for edge in edges:
   xy = pixel_functions.convert_pindex_to_xy( edge[2], im_width )
   all_edges.add( xy )
   xy = pixel_functions.convert_pindex_to_xy( edge[3], im_width )
   all_edges.add( xy )


im2edge_dfile = edge_dir + "data/" + image_filename2 + ".data"
with open (im2edge_dfile, 'rb') as fp:
   # # [ [ shapeid1, shapeid2, shapeid1's edge pixel, shapeid2's edge pixel ], ... ]
   im2edges = pickle.load(fp)
fp.close()

im2all_edges = set()
for edge in im2edges:
   xy = pixel_functions.convert_pindex_to_xy( edge[2], im_width )
   im2all_edges.add( xy )
   xy = pixel_functions.convert_pindex_to_xy( edge[3], im_width )
   im2all_edges.add( xy )
  


# { shapeid: [(379, 154), (380, 154), (379, 155), (379, 156), ... ], ... }
shapes_boundaries = {}
if shapes_type == "normal":
   # return value form is
   # shapes[shapes_id][pixel_index] = {}
   # shapes[shapes_id][pixel_index]['x'] = x
   # shapes[shapes_id][pixel_index]['y'] = y
   im_shapes = read_files_functions.rd_shapes_file(image_filename, directory)

   for shapeid in im_shapes:
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels( im_shapes[shapeid] )

   for shapeid in im_shapes:
      cur_pixels = set()
      for pixel in im_shapes[shapeid].keys():
         xy = pixel_functions.convert_pindex_to_xy( pixel, im_width )
         cur_pixels.add( xy )
      
      im_shapes[shapeid] = cur_pixels
      
   
elif shapes_type == "intnl_spixcShp":
   s_pixcShp_intnl_dir = top_shapes_dir + directory + "spixc_shapes/" + internal + "/"
   shapes_dir = s_pixcShp_intnl_dir + "shapes/"

   shapes_dfile = shapes_dir + image_filename + "shapes.data"
   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im_shapes = pickle.load(fp)
   fp.close()

   for shapeid in im_shapes:
      cur_pixels = set()
      for pixel in im_shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pixel, im_width )
         cur_pixels.add( xy )
      
      im_shapes[shapeid] = cur_pixels

   for shapeid in im_shapes:
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels( im_shapes[shapeid] )


match_results = {}
for shapeid in im_shapes:
   if shapeid in sty_shapes:
      continue
   
   # {(231, 63), (244, 82), ... }
   pixels = pixel_shapes_functions.get_shape_vicinity_pixels( shapes_boundaries[shapeid], 13, original_image.size, 1 )
   
   vicinity_edges = pixels.intersection( all_edges )
   im2vicinity_edges = pixels.intersection( im2all_edges )
   
   if len(vicinity_edges) < 20 or len(im2vicinity_edges) < 20:
      # not enough pixels to judge if edges match.
      continue

   # just random color because I need it to use get_shapes_pos_in_shp_coord function.
   edge_color = { shapeid: ( 255, 0, 0 ) }
   im1edge = { shapeid: list( vicinity_edges ) }
   im1edge_pixels = pixel_shapes_functions.get_shapes_pos_in_shp_coord( im1edge, im_width, edge_color, param_shp_type=1 )
   
   im2edge = { shapeid: list( im2vicinity_edges ) }
   im2_edge_pixels = pixel_shapes_functions.get_shapes_pos_in_shp_coord( im2edge, im_width, edge_color, param_shp_type=1 )

   edge_match = same_shapes_functions.find_shapes_match( im1edge_pixels, im2_edge_pixels, shapeid )
   
   if len( edge_match ) > 0:
      # match is found
      match_results[shapeid] = [ vicinity_edges, im2vicinity_edges ] 









with open(pixch_edge_dir + image_filename + "." + image_filename2 + "." + main_filename + ".data", 'wb') as fp:
   pickle.dump(match_results, fp)
fp.close()



frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)






