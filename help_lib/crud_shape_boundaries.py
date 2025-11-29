
import os, sys
from PIL import ImageTk, Image
from libraries import pixel_shapes_functions, pixel_functions
from libraries.cv_globals import top_shapes_dir, top_images_dir
import pickle
import math


def do_create( im_fname , directory ):

   # directory is specified but does not contain /
   if directory != "" and directory[-1] != '/':
      directory +='/'

   original_image = Image.open(top_images_dir + directory + im_fname + ".png")
   im_width, im_height = original_image.size

   boundary_dir = top_shapes_dir + directory + "shapes/boundary/"
   if os.path.exists(boundary_dir) == False:
      os.makedirs(boundary_dir)

   # returned value has below form
   # shapes[shapes_id]: [ pindex, ... ]
   shapes_dir = top_shapes_dir + directory + "shapes/"
   shapes_dfile = shapes_dir + im_fname + "shapes.data"
   with open (shapes_dfile, 'rb') as fp:
      shapes = pickle.load(fp)
   fp.close()

   shapes_boundaries = {}
   for shapeid in shapes:
      pixels_xy = set()
      for pixel in shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pixel, im_width )
            
         pixels_xy.add( xy )
         
      shapes[shapeid] = pixels_xy

      # [(263, 90), (262, 91), (262, 92), ... ]
      shapes_boundaries[shapeid] = set(  pixel_shapes_functions.get_boundary_pixels(shapes[shapeid] ) )

   with open(boundary_dir + im_fname + ".data" , 'wb') as fp:
      pickle.dump(shapes_boundaries, fp)
   fp.close()
   
   # create xy shapes boundaries
   xy_shapes_dfile = shapes_dir + im_fname + "xy_shapes.data"
   with open (xy_shapes_dfile, 'rb') as fp:
      xy_shapes = pickle.load(fp)
   fp.close()
   
   xy_shapes_boundaries = {}
   for shapeid in xy_shapes:

      # [(263, 90), (262, 91), (262, 92), ... ]
      xy_shapes_boundaries[shapeid] = set(  pixel_shapes_functions.get_boundary_pixels(xy_shapes[shapeid] ) )

   with open(boundary_dir + im_fname + "xy.data" , 'wb') as fp:
      pickle.dump(xy_shapes_boundaries, fp)
   fp.close()


def do_delete( im_fname , directory, target_shapeids ):

   # directory is specified but does not contain /
   if directory != "" and directory[-1] != '/':
      directory +='/'

   boundary_dir = top_shapes_dir + directory + "shapes/boundary/"
   boundary_dfile = boundary_dir + im_fname + ".data"

   with open (boundary_dfile, 'rb') as fp:
      boundary_shapes = pickle.load(fp)
   fp.close()

   for target_shapeid in target_shapeids:
      boundary_shapes.pop( target_shapeid )

   with open(boundary_dir + im_fname + ".data" , 'wb') as fp:
      pickle.dump(boundary_shapes, fp)
   fp.close()   


def do_update( im_fname , directory, target_shapeids ):

   # directory is specified but does not contain /
   if directory != "" and directory[-1] != '/':
      directory +='/'

   original_image = Image.open(top_images_dir + directory + im_fname + ".png")
   im_width, im_height = original_image.size

   boundary_dir = top_shapes_dir + directory + "shapes/boundary/"
   boundary_dfile = boundary_dir + im_fname + ".data"
   with open (boundary_dfile, 'rb') as fp:
      boundary_shapes = pickle.load(fp)
   fp.close()

   # returned value has below form
   # shapes[shapes_id]: [ pindex, ... ]
   shapes_dir = top_shapes_dir + directory + "shapes/"
   shapes_dfile = shapes_dir + im_fname + "shapes.data"
   with open (shapes_dfile, 'rb') as fp:
      shapes = pickle.load(fp)
   fp.close()
   
   for shapeid in target_shapeids:

      pixels_xy = set()
      for pixel in shapes[shapeid]:
         xy = pixel_functions.convert_pindex_to_xy( pixel, im_width )
            
         pixels_xy.add( xy )
         
      shapes[shapeid] = pixels_xy

      # [(263, 90), (262, 91), (262, 92), ... ]
      boundary_shapes[shapeid] = pixel_shapes_functions.get_boundary_pixels( shapes[shapeid] )

   with open(boundary_dir + im_fname + ".data" , 'wb') as fp:
      pickle.dump(boundary_shapes, fp)
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


























