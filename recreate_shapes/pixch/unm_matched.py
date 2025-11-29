import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import image_functions, cv_globals


image_fname = "1"
image2_fname = "2"
result_num = '1'
directory = "videos/street6/resized/min1"

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

pixch_dir = top_shapes_dir + directory + "pixch/"
unm_matched_dir = pixch_dir + "unm_matched/"
unm_matched_ddir = unm_matched_dir + "data/"

matched_shapes_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + '_' + result_num + ".data"
if os.path.exists(matched_shapes_fpath):
	with open (matched_shapes_fpath, 'rb') as fp:
	   unm_matched_shapes = pickle.load(fp)
	fp.close()

cv_globals.store_debug(True)

def create_images( result, imdir_name ):

	unm_matched_imdir = unm_matched_dir + image_fname + "." + image2_fname + imdir_name + '/'
	# delete and create folder
	if os.path.exists(unm_matched_imdir) == True:
	   shutil.rmtree(unm_matched_imdir)
	os.makedirs(unm_matched_imdir)

	all_im1pixels = set()
	all_im2pixels = set()
	for each_s_index, each_shapes in enumerate(result):
		
		save_filename = unm_matched_imdir + str( each_s_index )
		
		im1fpath = save_filename + "im1.png"
		image_functions.cr_im_from_pixels( image_fname, directory, each_shapes[0], save_filepath=im1fpath , pixels_rgb=(255,0,0) )
		
		im2fpath = save_filename + "im2.png"
		image_functions.cr_im_from_pixels( image2_fname, directory, each_shapes[1], save_filepath=im2fpath , pixels_rgb=(0,0,255) )

		all_im1pixels |= each_shapes[0]
		all_im2pixels |= each_shapes[1]

	image_functions.cr_im_from_pixels( image_fname, directory, all_im1pixels , pixels_rgb=(255, 0,255) )
	image_functions.cr_im_from_pixels( image2_fname, directory, all_im2pixels , pixels_rgb=(255,0, 255) )


create_images(unm_matched_shapes, "result" + result_num )
























