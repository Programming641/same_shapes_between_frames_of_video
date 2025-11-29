import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import image_functions, cv_globals


image_fname = "1"
image2_fname = "2"
directory = "videos/street6/resized/min1"

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_shapes_dir = pixch_dir + "pixch_shapes2/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + ".data"
with open (matched_shapes_fpath, 'rb') as fp:
   pixch_shapes2 = pickle.load(fp)
fp.close()

cv_globals.store_debug(True)

imdir = pixch_shapes_dir + image_fname + '.' + image2_fname + '/'
if os.path.exists(imdir) == True:
   shutil.rmtree(imdir)
os.makedirs(imdir)

for m_index, match in enumerate(pixch_shapes2):
	
	im1fpath = imdir + str(m_index) + "im1.png"
	im2fpath = imdir + str(m_index) + "im2.png"
	
	image_functions.cr_im_from_pixels( image_fname, directory, match[0], save_filepath=im1fpath , pixels_rgb=(255,0,0) )
	image_functions.cr_im_from_pixels( image2_fname, directory, match[1], save_filepath=im2fpath , pixels_rgb=(0,0, 255) )



unm_m_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "unm_matched.data"
if os.path.exists(unm_m_fpath):
	with open (unm_m_fpath, 'rb') as fp:
	   unm_m_shapes = pickle.load(fp)
	fp.close()

	unm_m_imdir = pixch_shapes_dir + image_fname + '.' + image2_fname + "unm_matched/"
	if os.path.exists(unm_m_imdir) == True:
	   shutil.rmtree(unm_m_imdir)
	os.makedirs(unm_m_imdir)

	for m_index, match in enumerate(unm_m_shapes):
		
		im1fpath = unm_m_imdir + str(m_index) + "im1.png"
		im2fpath = unm_m_imdir + str(m_index) + "im2.png"
		
		image_functions.cr_im_from_pixels( image_fname, directory, match[0], save_filepath=im1fpath , pixels_rgb=(255,0,0) )
		image_functions.cr_im_from_pixels( image2_fname, directory, match[1], save_filepath=im2fpath , pixels_rgb=(0,0, 255) )




























