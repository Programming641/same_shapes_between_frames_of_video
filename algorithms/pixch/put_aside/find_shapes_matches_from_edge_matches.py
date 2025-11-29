# not found shapes are the shapes that are not found by the find_sty_shapes_from_pixch.py

from libraries import pixel_functions, read_files_functions, pixel_shapes_functions, image_functions

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

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_edge_dir = pixch_dir + "edge/"
pixch_edge_file = pixch_edge_dir + image_filename + "." + image_filename2 + "." + main_filename + ".data"
with open (pixch_edge_file, 'rb') as fp:
   # {'71336': [{(135, 175), ...}, {(143, 179), ...}], ... }
   # { image1 shapeid: [ { all image1 shape's edges including non matched edges }, { image2 edges } ], ... }
   pixch_edges = pickle.load(fp)
fp.close()

original_image = Image.open(top_images_dir + directory + image_filename + ".png")
im_width, im_height = original_image.size

# { shapeid: [(379, 154), (380, 154), (379, 155), (379, 156), ... ], ... }
shapes_boundaries = {}
im2shapes_boundaries = {}
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
   

   shapes_locations_path = top_shapes_dir + directory + "locations/" + image_filename + "_loc.txt"
   im2shapes_locations_path = top_shapes_dir + directory + "locations/" + image_filename2 + "_loc.txt"   
 
 
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

   im2shapes_dfile = shapes_dir + image_filename2 + "shapes.data"
   with open (im2shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im2shapes = pickle.load(fp)
   fp.close()

   for shapeid in im2shapes:
      cur_pixels = set()
      for pixel in im2shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pixel, im_width )
         cur_pixels.add( xy )
      
      im2shapes[shapeid] = cur_pixels

   for shapeid in im2shapes:
      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels( im2shapes[shapeid] )


   shapes_locations_path = s_pixcShp_intnl_dir + "locations/" + image_filename + "_loc.data"
   im2shapes_locations_path = s_pixcShp_intnl_dir + "locations/" + image_filename2 + "_loc.data"


with open (shapes_locations_path, 'rb') as fp:
   #  { '79998': ['25'], '79999': ['25'], ...}
   s_locations = pickle.load(fp)
fp.close()
with open (im2shapes_locations_path, 'rb') as fp:
   im2s_locations = pickle.load(fp)
fp.close()

# {'1': (0, 80, 0, 40), '2': (81, 160, 0, 40), ... }
# { image area number: ( left, right, top, bottom ), ... }
image_areas = image_functions.get_image_areas( image_filename, directory )


# put shapes image areas ordered by image area
im1shapes_by_im_areas = {}
for image_area in image_areas:
   shapes_in_im_area = [ shapeid for shapeid, im_areas in s_locations.items() if str(image_area) in im_areas ]
   
   im1shapes_by_im_areas[image_area] = shapes_in_im_area

im2shapes_by_im_areas = {}
for image_area in image_areas:
   shapes_in_im_area = [ shapeid for shapeid, im_areas in im2s_locations.items() if str(image_area) in im_areas ]
   
   im2shapes_by_im_areas[image_area] = shapes_in_im_area


matches = {}
progress_counter = len( pixch_edges )
for edge_shapeid in pixch_edges:
   print( str( progress_counter ) + " remaining" )
   progress_counter -= 1
   
   im1edges = pixch_edges[edge_shapeid][0]
   im2edges = pixch_edges[edge_shapeid][1]
   
   # [ ( x,y ), ... ]
   im1edges_coords = pixel_functions.get_pixels_pos_in_pix_coord( im1edges )
   im2edges_coords = pixel_functions.get_pixels_pos_in_pix_coord( im2edges )
   
   matched_edges = set(im1edges_coords).intersection( set(im2edges_coords) )
   
   # found the matched pixels in pixels coordinate. now return them back to image coordinate pixels
   im1edges_smallest_x = min( [ xy[0] for xy in im1edges ] )
   im1edges_smallest_y = min( [ xy[1] for xy in im1edges ] )
   matched_edges = { ( xy[0] + im1edges_smallest_x, xy[1] + im1edges_smallest_y ) for xy in matched_edges }

   if len( matched_edges ) > 0:
      # matches -> { edge_shapeid: [ [ image1 shapeids ], [ image2 shapeids ] ], ... }
      matches[edge_shapeid] = [ [], [] ]
      
      # mtc_edges_locations -> {'edge_pix': [5]}
      mtc_edges_locations = pixel_shapes_functions.get_shape_im_locations( image_filename, directory, matched_edges, "edge_pix" )
      # list of integer locations to list of string locations
      mtc_edges_locations["edge_pix"] = [ str(loc) for loc in mtc_edges_locations["edge_pix"] ]

      # shape match is found if enough edge is found on the shape's boundary pixels. 
      # how to determine the "enough edges"?
      # that depends if it already has matched shapes determined by other algorithms.
      #
      # for example. if two shapes. image1 1532, image2 1001 are both matched from pixch stayed shapes.
      # then, more than 40% of edges are needed for it to be called a match.
      #
      # if image1 and image2 shapes have not been made match from other algorithms yet, then
      # matched edges need to be more than 40% of the both boundary pixels.
      #
      # for the small pixel count shapes.
      # matched edges need to be found more than 60% for bigger than second smallest pixel count shapes
      # matched edges need to be found more than 80% for less than second smallest pixel count shapes
      im1shapes_from_cur_loc = []
      im2shapes_from_cur_loc = []
      for mtc_edges_location in mtc_edges_locations["edge_pix"]:
         im1shapes_from_cur_loc.extend( im1shapes_by_im_areas[mtc_edges_location] )
         im2shapes_from_cur_loc.extend( im2shapes_by_im_areas[mtc_edges_location] )
      
      for im1shapeid in im1shapes_from_cur_loc:
         if len( im_shapes[im1shapeid] ) >= frth_smallest_pixc:
            matched_bnd_edges = set( shapes_boundaries[im1shapeid] ).intersection( matched_edges )
            if len( matched_bnd_edges ) / len( shapes_boundaries[im1shapeid] ) < 0.4:
               continue            
         
            matches[edge_shapeid][0].append( im1shapeid )
            
         else:
            # current im1shapeid is smaller than frth_smallest_pixc
            matched_pix_edges = im_shapes[im1shapeid].intersection( matched_edges )
            if len( matched_pix_edges ) / len( im_shapes[im1shapeid] ) < 0.8:
               continue            
      
            matches[edge_shapeid][0].append( im1shapeid )
      
      for im2shapeid in im2shapes_from_cur_loc:
            if len( im2shapes[im2shapeid] ) >= frth_smallest_pixc:
               im2matched_bnd_edges = set( im2shapes_boundaries[im2shapeid] ).intersection( matched_edges )
               if len( im2matched_bnd_edges ) / len( im2shapes_boundaries[im2shapeid] ) < 0.4:
                  continue

               matches[edge_shapeid][1].append( im2shapeid )

            else:
               im2matched_pix_edges = im2shapes[im2shapeid].intersection( matched_edges )          
               if len( im2matched_pix_edges ) / len( im2shapes[im2shapeid] ) < 0.8:
                  continue              

               matches[edge_shapeid][1].append( im2shapeid )

     

with open(pixch_edge_dir + image_filename + "." + image_filename2 + "." + main_filename + "shapes.data", 'wb') as fp:
   pickle.dump(matches, fp)
fp.close() 
      



   































