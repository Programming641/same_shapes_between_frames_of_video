import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import image_functions, cv_globals


image_fname = "2"
image2_fname = "3"
directory = "videos/street6/resized/min1"

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_shapes_dir = pixch_dir + "pixch_shapes1/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open (matched_shapes_fpath, 'rb') as fp:
	# [  [ image1 pixels, image2 pixels, matched movement, image1 shapeid, message ], ... ]
	less50_results = pickle.load(fp)
fp.close()

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open (matched_shapes_fpath, 'rb') as fp:
   G50_results = pickle.load(fp)
fp.close()

shapes_dfile = top_shapes_dir + directory + "shapes/" + image_fname + "xy_shapes.data"
with open (shapes_dfile, 'rb') as fp:
   # { "shapeid": { xy pixels }, ... }
   xy_im1shapes = pickle.load(fp)
fp.close()

cv_globals.store_debug(True)

def create_imdir(imdir):
	# delete and create folder
	if os.path.exists(imdir) == True:
	   shutil.rmtree(imdir)
	os.makedirs(imdir)


def create_images( imdir, result_data, result_name ):

	for each_s_index, each_shapes in enumerate(result_data):
		#  ( im1shape_pixels, matched_pixels, (0,0) )

		
		save_filename = imdir + str( each_s_index )
		
		im1fpath = save_filename + "im1.png"
		image_functions.cr_im_from_pixels( image_fname, directory, each_shapes[0], save_filepath=im1fpath , pixels_rgb=(255,0,0) )
		
		im2fpath = save_filename + "im2.png"
		image_functions.cr_im_from_pixels( image2_fname, directory, each_shapes[1], save_filepath=im2fpath , pixels_rgb=(0,0,255) )




less50_imdir = pixch_shapes_dir + image_fname + "." + image2_fname + "less50/"
create_imdir( less50_imdir )
create_images( less50_imdir, less50_results, "less50" )

G50_imdir = pixch_shapes_dir + image_fname + "." + image2_fname + "G50/"
create_imdir(G50_imdir)
create_images( G50_imdir, G50_results, "G50" )














