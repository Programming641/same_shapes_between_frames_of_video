from libraries import btwn_amng_files_functions
from libraries import pixel_shapes_functions
from libraries import pixel_functions

import os, sys
from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
import pickle
import math
from PIL import ImageTk, Image


def  get_shapes_nbrs( shapes_boundaries, im_size ):
   shapes_neighbors = {}
   
   for shapeid in shapes_boundaries:
      shape_nbr_pixels = set()
      shapes_neighbors[shapeid] = set()
      
      for boundary_pixel in shapes_boundaries[shapeid]:
         nbr_pixels = pixel_functions.get_nbr_pixels(boundary_pixel, im_size, input_xy=True)
         shape_nbr_pixels |= nbr_pixels

      for ano_shapeid in shapes_boundaries:
         if ano_shapeid == shapeid:
            continue
         overlap_pixels = shape_nbr_pixels.intersection( shapes_boundaries[ano_shapeid] )
         
         if len(overlap_pixels) >= 1:
            shapes_neighbors[shapeid].add(ano_shapeid)

   return shapes_neighbors



def do_create( im_file, directory, return_nbrs=False ):


   # directory is specified but does not contain /
   if directory != "" and directory[-1] != ('/'):
      directory +='/'

   original_image = Image.open(top_images_dir + directory + im_file + ".png")
   im_width, im_height = original_image.size

   shapes_dir = top_shapes_dir + directory + "shapes/"
   shape_neighbors_path = shapes_dir + 'shape_nbrs/'
   if not os.path.isdir(shape_neighbors_path):
      os.makedirs(shape_neighbors_path)


   shapes_boundary_path = shapes_dir + "boundary/" + im_file + ".data"
   with open (shapes_boundary_path, 'rb') as fp:
      shapes_boundaries = pickle.load(fp)
   fp.close()

   shape_neighbor_file = shape_neighbors_path + im_file + "_shape_nbrs.data"
      
   shapes_neighbors = get_shapes_nbrs( shapes_boundaries, original_image.size  )
   
   with open(shape_neighbor_file, 'wb') as fp:
      pickle.dump(shapes_neighbors, fp)
   fp.close()
   
   xy_shapes_neighbors = {}
   for shapeid in shapes_neighbors:
      xy_shapeid = pixel_functions.convert_pindex_to_xy( shapeid, im_width )
      
      xy_shapes_neighbors[xy_shapeid] = pixel_functions.convert_pindexes_to_xy( shapes_neighbors[shapeid], original_image.size )
   
   xy_shape_neighbors_file = shape_neighbors_path + im_file + "_xy_shape_nbrs.data"
   with open(xy_shape_neighbors_file, 'wb') as fp:
      pickle.dump(xy_shapes_neighbors, fp)
   fp.close()







if __name__ == '__main__':

   if len( sys.argv ) >= 2:
      image_filename = sys.argv[0][0: len( sys.argv[0] ) - 4 ]
      directory = sys.argv[1]
      
      do_create( image_filename, directory )
   else:


      im1file = "8"
      directory = "videos/street6/resized/min1"
   
      do_create( im1file, directory )
















