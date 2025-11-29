#
#
from libraries import pixel_functions, pixel_shapes_functions, image_functions, btwn_amng_files_functions, same_shapes_functions

from PIL import Image
import math
import os, sys
import pickle, shutil, json

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir
from libraries import cv_globals

directory = "videos/street6/resized/min1"
if len(sys.argv) >= 2:
   directory = sys.argv[1]
print("directory " + directory)

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

if "min" in directory:
	min_colors = True
else:
	min_colors = False

lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

all_each_files = btwn_amng_files_functions.get_btwn_files_nums( lowest_fnum, highest_fnum )
all_im_rgb_data = btwn_amng_files_functions.get_all_im_xy_data( directory )

cv_globals.store_debug(True)

pixch_dir = top_shapes_dir + directory + "pixch/"
if not os.path.exists(pixch_dir):
	os.makedirs(pixch_dir)

eachf_pixch = {}
for eachf in all_each_files:
	eachf_pixch[eachf] = set()
	
	im1fnum = eachf.split('.')[0]
	im2fnum = eachf.split('.')[1]
	
	im1_rgb_data = all_im_rgb_data[ int(im1fnum ) - lowest_fnum ]
	im2_rgb_data = all_im_rgb_data[ int(im2fnum ) - lowest_fnum ]

	if min_colors:
		for xy in im1_rgb_data:
			if im1_rgb_data[xy] != im2_rgb_data[xy]:
				eachf_pixch[eachf].add(xy)
	
	else:
		for xy in im1_rgb_data:
			clr_diff = pixel_functions.compute_appearance_difference(im1_rgb_data[xy], im2_rgb_data[xy] )
			if clr_diff:
				# color is different
				eachf_pixch[eachf].add(xy)
			
	

	im_pixch_imfpath= pixch_dir + eachf + ".png"
	image_functions.cr_im_from_pixels( im1fnum, directory, eachf_pixch[eachf], save_filepath=im_pixch_imfpath , pixels_rgb=(255,255,0) )



pixch_fpath = pixch_dir + "eachf_pixch.data"
with open(pixch_fpath, 'wb') as fp:
   pickle.dump(eachf_pixch, fp)
fp.close()





















