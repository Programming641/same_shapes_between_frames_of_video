import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir, top_tests_dir
from libraries import image_functions, cv_globals, pixel_functions, btwn_amng_files_functions, same_shapes_functions, shapes_results_functions


image_fname = "1"
image2_fname = "2"
directory = "videos/street4/resized/min1"

if len(sys.argv) >= 2:
	directory = sys.argv[1]
	image_fname = sys.argv[2].split('.')[0]
	image2_fname = sys.argv[2].split('.')[1]

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

if "min" in directory:
	min_colors = True
else:
	min_colors = False


shapes_dfile = top_shapes_dir + directory + "shapes/" + image_fname + "xy_shapes.data"
with open (shapes_dfile, 'rb') as fp:
   # { "shapeid": { xy pixels }, ... }
   xy_im1shapes = pickle.load(fp)
fp.close()

im2shapes_dfile = top_shapes_dir + directory + "shapes/" + image2_fname + "xy_shapes.data"
with open (im2shapes_dfile, 'rb') as fp:
   # { "shapeid": { xy pixels }, ... }
   xy_im2shapes = pickle.load(fp)
fp.close()

im1boundary_fpath = top_shapes_dir + directory + "shapes/boundary/" + image_fname + "xy.data"
with open (im1boundary_fpath, 'rb') as fp:
   im1shapes_boundaries = pickle.load(fp)
fp.close()

im2boundary_fpath = top_shapes_dir + directory + "shapes/boundary/" + image2_fname + "xy.data"
with open (im2boundary_fpath, 'rb') as fp:
   im2shapes_boundaries = pickle.load(fp)
fp.close()


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

im1_xy_shapeids_by_p_fpath = top_shapes_dir + directory + "shapes/shapeids_by_pixel/xy" + image_fname + ".data"
with open (im1_xy_shapeids_by_p_fpath, 'rb') as fp:
   im1_xy_shapeids_by_p = pickle.load(fp)
fp.close()

im2_xy_shapeids_by_p_fpath = top_shapes_dir + directory + "shapes/shapeids_by_pixel/xy" + image2_fname + ".data"
with open (im2_xy_shapeids_by_p_fpath, 'rb') as fp:
   im2_xy_shapeids_by_p = pickle.load(fp)
fp.close()

im1_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image_fname + ".data"
with open (im1_rgb_xy_data_fpath, 'rb') as fp:
   im1_rgb_xy_data = pickle.load(fp)
fp.close()

im2_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image2_fname + ".data"
with open (im2_rgb_xy_data_fpath, 'rb') as fp:
   im2_rgb_xy_data = pickle.load(fp)
fp.close()

pixch_fpath = pixch_dir + "eachf_pixch.data"
with open (pixch_fpath, 'rb') as fp:
   eachf_pixch = pickle.load(fp)
fp.close()

btwn_im_pixch = eachf_pixch[ image_fname + '.' + image2_fname ]

lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

shapes_dfile = top_shapes_dir + directory + "shapes/" + image_fname + "xy_shapes.data"
with open (shapes_dfile, 'rb') as fp:
   # { "shapeid": { xy pixels }, ... }
   xy_im1shapes = pickle.load(fp)
fp.close()

cv_globals.store_debug(True)
rgbs = image_functions.get_rgbs( start_r=50, start_g=100, start_b=0, steps=80 )

test_imfpath = top_shapes_dir + directory + "temp/test.png"
test_im2fpath = top_shapes_dir + directory + "temp/test2.png"


def get_result_lookup( result, result_name ):

	result_lookups = [ {}, {} ] # [ { pixel: { result indexes }, ... }, { pixel: { result indexes }, ... } ]
	for m_index, match in enumerate(result):
		for im1or2 in range(2):

			for pixel in match[im1or2]:
				if result_lookups[im1or2].get(pixel) is None:
					result_lookups[im1or2][pixel] = {m_index}
				else:
					result_lookups[im1or2][pixel].add(m_index)

	return result_lookups


def get_mpixels_on_shapes( shapeids_on_mpixels, im_shapes, mpixels ):

	mpixels_pixch50 = set()
	for shapeid_on_mpixels in shapeids_on_mpixels:
		mpixels_on_shape = mpixels.intersection( im_shapes[shapeid_on_mpixels] )
		if len(mpixels_on_shape) < cv_globals.get_third_smallest_pixc(image_size):
			continue
		
		outside_exp = pixel_functions.expand_boundary( mpixels_on_shape, image_size, expand_by=5, input_xy=True)
		outside_exp = outside_exp.difference(mpixels_on_shape)
		
		pixch = outside_exp.intersection(btwn_im_pixch)
		pixch_percent = len(pixch) / len(outside_exp)
		if pixch_percent >= 0.5:
			mpixels_pixch50 |= mpixels_on_shape

	mpixels_pixch_less50 = mpixels.difference(mpixels_pixch50)
	
	# most pixels are less than 50% pixch but some pixels are more than 50% pixch. this suggests that mpixels_pixch50 maybe matched by accident.
	pixch_L50_percent = len(mpixels_pixch_less50) / len(mpixels)
	if pixch_L50_percent >= cv_globals.m_threshold and len(mpixels_pixch50) >= 1:
		return mpixels_pixch50
	
	else:
		return set()



# convert G50_results to the same data format as less50_results.
G50_results_rev = []
for match_L in G50_results:
	for match in match_L:
		G50_results_rev.append(match)


im_L50_lookups = get_result_lookup(less50_results, "L50")

# if the L50 shape's neighbors have the same movement, then it is likely to be correct
confirmed_by_nbr_mv = set() # { confirmed indexes of less50_results }

for m_index, match in enumerate(less50_results):
	
	exp_im1pixels = pixel_functions.expand_boundary(match[0], image_size, expand_by=2, input_xy=True)
	exp_im1pixels = exp_im1pixels.difference( match[0] )
	
	L50_nbr_indexes = set()
	for exp_im1pixel in exp_im1pixels:
		if im_L50_lookups[0].get(exp_im1pixel) is not None:
			L50_nbr_indexes |= im_L50_lookups[0][exp_im1pixel]
	
	for L50_nbr_index in L50_nbr_indexes:
		same_movement = same_shapes_functions.check_same_movement( match[2], less50_results[L50_nbr_index][2] )
		if same_movement is True:
			confirmed_by_nbr_mv.add(m_index)	


m_indexes = { index_num for index_num in range(len(less50_results) ) }
non_confirmed = m_indexes.difference(confirmed_by_nbr_mv)

print("checkpoint1")

pixch50_surroundings = set() # wrong by more than 50% pixch in the surroundings. lots of pixel changes indicate that the L50 shape maybe wrong
for m_index, match in enumerate(less50_results):
	
	im1_outside_exp = pixel_functions.expand_boundary(match[0], image_size, expand_by=5, input_xy=True)
	im1_outside_exp = im1_outside_exp.difference( match[0] )
	
	im2_outside_exp = pixel_functions.expand_boundary(match[1], image_size, expand_by=5, input_xy=True)
	im2_outside_exp = im2_outside_exp.difference( match[1] )
	
	im1_outside_pixch = im1_outside_exp.intersection(btwn_im_pixch)
	im2_outside_pixch = im2_outside_exp.intersection(btwn_im_pixch)
	
	im1_out_pixch_percent = len(im1_outside_pixch) / len(im1_outside_exp)
	im2_out_pixch_percent = len(im2_outside_pixch) / len(im2_outside_exp)
	
	if im1_out_pixch_percent > 0.5 or im2_out_pixch_percent > 0.5:
		pixch50_surroundings.add(m_index)

non_confirmed |= pixch50_surroundings

print("checkpoint2")

non_confirmed_rev = non_confirmed.copy()
for non_conf_index in non_confirmed:
	
	non_conf_match = less50_results[non_conf_index]
		
	mpixels, m_mv = same_shapes_functions.match_with_expanded_pixels( non_conf_match[0], image_size, True, im1_rgb_xy_data, im2_rgb_xy_data, min_colors )
	if mpixels is not None:
		# found match
		non_confirmed_rev.remove(non_conf_index)
		# this match is more likely correct than the original, so replace it.
		
		less50_results[non_conf_index] = [ non_conf_match[0], mpixels, m_mv, non_conf_match[3] ]

print("checkpoint3")

for m_index, match in enumerate(less50_results):

	# check if matched pixels are on multiple original shapes.
	shapeids_on_mpixels = set()

	if match[3] == "matched_from_im2":
		for matched_im1pixel in match[0]:
			shapeids_on_mpixels |= im1_xy_shapeids_by_p[matched_im1pixel]
		
		# for matched pixels on each shape, check for the more than 50% surrounding pixel changes.
		mpixels_pixch50 = get_mpixels_on_shapes( shapeids_on_mpixels, xy_im1shapes, match[0] )
		if len(mpixels_pixch50) == 0:
			continue
		non_confirmed_rev.add(m_index)
		
	else:
		for matched_im2pixel in match[1]:
			shapeids_on_mpixels |= im2_xy_shapeids_by_p[matched_im2pixel]
		
		mpixels_pixch50 = get_mpixels_on_shapes( shapeids_on_mpixels, xy_im2shapes, match[1] )
		if len(mpixels_pixch50) == 0:
			continue

		non_confirmed_rev.add(m_index)

print("checkpoint4")

# delete non confirmed matches from less50
non_confirmed_rev = list(non_confirmed_rev)
non_confirmed_rev.sort()

deleted = 0
for non_confirmed_index in non_confirmed_rev:
	less50_results.pop(non_confirmed_index - deleted)
	deleted += 1

shapes_results_functions.get_direct_matches( less50_results, image_size )



# L50 found new matches from same_shapes_functions.match_with_expanded_pixels
matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(less50_results, fp)
fp.close()


















