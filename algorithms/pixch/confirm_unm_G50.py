import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import image_functions, cv_globals, pixel_functions, same_shapes_functions, btwn_amng_files_functions, pixel_shapes_functions, shapes_results_functions


image_fname = "1"
image2_fname = "2"
result_num = '1'
directory = "videos/street6/resized/min1"

if len(sys.argv) >= 2:
   directory = sys.argv[1]
   image_fname = sys.argv[2].split('.')[0]
   image2_fname = sys.argv[2].split('.')[1]

print("directory " + directory + " image_fname " + image_fname + " image2_fname " + image2_fname )

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'


if "min" in directory:
	min_colors = True
else:
	min_colors = False

im1_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image_fname + ".data"
with open (im1_rgb_xy_data_fpath, 'rb') as fp:
   im1_rgb_xy_data = pickle.load(fp)
fp.close()

im2_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image2_fname + ".data"
with open (im2_rgb_xy_data_fpath, 'rb') as fp:
   im2_rgb_xy_data = pickle.load(fp)
fp.close()



pixch_dir = top_shapes_dir + directory + "pixch/"
unm_matched_dir = pixch_dir + "unm_matched/"
unm_matched_ddir = unm_matched_dir + "data/"

matched_shapes_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + '_' + result_num + ".data"
with open (matched_shapes_fpath, 'rb') as fp:
   unm_matched = pickle.load(fp)
fp.close()

cv_globals.store_debug(True)
rgbs = image_functions.get_rgbs( start_r=100, start_g=25, start_b=150, steps=80 )


lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

# getting already matched shapes            ----------------------------------------------
pixch_shapes_dir = pixch_dir + "pixch_shapes" + result_num + '/'
pixch_shapes_ddir = pixch_shapes_dir + "data/"

less50_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open (less50_fpath, 'rb') as fp:
	# [  [ im1 pixels, m_pixels, matched movement, image1 shapeid ], ... ]
   less50_results = pickle.load(fp)
fp.close()

G50_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open (G50_fpath, 'rb') as fp:
	# [  [ [ image1 pixels, im2 matched pixels, matched movement, image1 shapeid ], ... ], ... ]
	G50_results = pickle.load(fp)
fp.close()

alrdy_matched_shapes = []
for match in less50_results:
	# [ im1 pixels, m_pixels, matched movement, image1 shapeid ]
	alrdy_matched_shapes.append( match )

for match in G50_results:
	alrdy_matched_shapes.append( match )

# getting already matched shapes done        ---------------------------------------------


temp_im1fpath = top_shapes_dir + directory + "temp/test.png"
if os.path.exists(temp_im1fpath):
	os.remove(temp_im1fpath)

fourth_pix_size = cv_globals.get_frth_smallest_pixc(image_size)


alrdy_m_lookup = {}
for m_index, match in enumerate(alrdy_matched_shapes):
	for im1pixel in match[0]:
		if alrdy_m_lookup.get(im1pixel) is None:
			alrdy_m_lookup[im1pixel] = {m_index}
		else:
			alrdy_m_lookup[im1pixel].add(m_index)


wrong_matches = set()
for m_index, match in enumerate(unm_matched):
	
	expanded_pixels = pixel_functions.expand_boundary(match[0], image_size, expand_by=2, input_xy=True)
	out_exp = expanded_pixels.difference( match[0] )
	
	alrdy_m_indexes = set()
	for out_exp_pixel in out_exp:
		if alrdy_m_lookup.get(out_exp_pixel) is not None:
			alrdy_m_indexes |= alrdy_m_lookup[out_exp_pixel]
	
	conf_same_movement = False   # confirmed by having the same movement with already matched neighbor
	for alrdy_m_index in alrdy_m_indexes:
		alrdy_m_movement = alrdy_matched_shapes[alrdy_m_index][2]
		
		same_movement = same_shapes_functions.check_same_movement( match[2], alrdy_m_movement )
		if same_movement is True:
			conf_same_movement = True
	
	if conf_same_movement is False:
		wrong_matches.add(m_index)


# check if they are really wrong
wrong_indexes = set()
for m_index in wrong_matches:
	match = unm_matched[m_index]
		
	im1exspanded_pixels = pixel_functions.expand_boundary(match[0], image_size, expand_by=5, input_xy=True)
	im1out_pixels = im1exspanded_pixels.difference( match[0] )

	alrdy_m_indexes = set()
	for im1out_pixel in im1out_pixels:
		if alrdy_m_lookup.get(im1out_pixel) is not None:
			alrdy_m_indexes |= alrdy_m_lookup[im1out_pixel]

	alrdy_m_mvs = set()
	rest_pixels = im1out_pixels
	for alrdy_m_index in alrdy_m_indexes:
		rest_pixels = rest_pixels.difference( alrdy_matched_shapes[alrdy_m_index][0] )
		
		mvs_w_buffer = pixel_shapes_functions.get_mv_with_buffer( alrdy_matched_shapes[alrdy_m_index][2], 2 )
		alrdy_m_mvs |= mvs_w_buffer
	
	if len(rest_pixels) < cv_globals.get_sec_smallest_pixc(image_size):
		continue
	
	matched_pixels, matched_mv = same_shapes_functions.match_pixels_at_specified_mvs( rest_pixels, alrdy_m_mvs, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, 
																					threshold=0.45 )
	
	if len(matched_pixels) == 0:
		wrong_indexes.add(m_index)


# delete wrong matches from unm_matched
deleted = 0
wrong_indexes = list(wrong_indexes)
wrong_indexes.sort()
for wrong_index in wrong_indexes:
	unm_matched.pop(wrong_index - deleted)
	deleted += 1

shapes_results_functions.get_direct_matches( unm_matched, image_size )

confirmed_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + '_' + result_num + "confirmed"
open(confirmed_fpath, "x") # create confirmed file.

with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(unm_matched, fp)
fp.close()















