import math
import os, sys
import shutil
import pickle

from PIL import Image

from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import image_functions, cv_globals, btwn_amng_files_functions, pixel_functions, same_shapes_functions, shapes_results_functions


image_fname = "28"
image2_fname = "29"
directory = "videos/street3/resized/min1"

# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'

if "min" in directory:
	min_colors = True
else:
	min_colors = False

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_shapes_dir = pixch_dir + "pixch_shapes1/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open (matched_shapes_fpath, 'rb') as fp:
	# [  [ image1 pixels, image2 pixels, matched movement, image1 shapeid, message ], ... ]
	less50_results = pickle.load(fp)
fp.close()

non_confirmed_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "non_confirmed_L50.data"
with open (non_confirmed_fpath, 'rb') as fp:
	# [  [ image1 pixels, image2 pixels, matched movement, image1 shapeid, message ], ... ]
	non_confirmed_L50 = pickle.load(fp)
fp.close()

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open (matched_shapes_fpath, 'rb') as fp:
   G50_results = pickle.load(fp)
fp.close()

didnt_try_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "didnt_try_im1shapeids.data"
with open (didnt_try_fpath, 'rb') as fp:
   didnt_try_im1shapeids = pickle.load(fp)
fp.close()

didnt_match_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "didnt_match_im1shapeids.data"
with open (didnt_match_fpath, 'rb') as fp:
   didnt_match_im1shapeids = pickle.load(fp)
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

rgbs = image_functions.get_rgbs( start_r=100, start_g=25, start_b=150, steps=80 )

lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

test_im1path = top_shapes_dir + directory + "temp/test.png"
test_im2path = top_shapes_dir + directory + "temp/test2.png"

cv_globals.store_debug(True)

all_matches = []
for m_index, match in enumerate(less50_results):
	if m_index in non_confirmed_L50:
		continue
	all_matches.append(match)

for matches in G50_results:
	for match in matches:
		all_matches.append(match)

alrdy_m_lookup = {}
for m_index, match in enumerate(all_matches):
	for im1pixel in match[0]:
		if alrdy_m_lookup.get(im1pixel) is None:
			alrdy_m_lookup[im1pixel] = {m_index}
		else:
			alrdy_m_lookup[im1pixel].add(m_index)


wrong_matches = set()
for match_L_index, matches in enumerate(G50_results):
	for m_index, match in enumerate(matches):
		
		im1pixch = match[0].intersection(btwn_im_pixch)
		im1pixch_percent = len(im1pixch) / len(match[0] )
		
		matched_pixch = match[1].intersection(btwn_im_pixch)
		matched_pixch_percent = len(matched_pixch) / len( match[1] )
		
		percent_diff = abs(im1pixch_percent - matched_pixch_percent )
		if percent_diff < 0.45:
			# im1 pixch and matched pixch should be about the same
			continue
		
		# wrong by pixch difference
		wrong_matches.add( (match_L_index, m_index) )
		
		
for match_L_index, matches in enumerate(G50_results):
	for m_index, match in enumerate(matches):

		expanded_pixels = pixel_functions.expand_boundary( match[0], image_size, expand_by=2, input_xy=True)
		expanded_pixels = expanded_pixels.difference( match[0] )
		
		alrdy_m_indexes = set()
		for im1pixel in  expanded_pixels:
			if alrdy_m_lookup.get(im1pixel) is not None:
				alrdy_m_indexes |= alrdy_m_lookup[im1pixel]
		
		same_mv_found = False
		
		for alrdy_m_index in alrdy_m_indexes:
			
			nbr_mv = all_matches[alrdy_m_index][2]
			same_movement = same_shapes_functions.check_same_movement( match[2], nbr_mv )
			if same_movement is True:
				same_mv_found = True
				break
		
		if same_mv_found is False:
			# no confirmation by already matched neighbors movements
			
			matched_pixels, matched_mv = same_shapes_functions.match_with_expanded_pixels( match[0], image_size, True, im1_rgb_xy_data, im2_rgb_xy_data, min_colors  )
			if matched_pixels is None:
				wrong_matches.add( (match_L_index, m_index) )
				continue
		
			# replace G50_results with new match
			G50_results[match_L_index][m_index] = [ match[0], matched_pixels, matched_mv ]


# delete non confirmed matches
for match_L_index, matches in enumerate(G50_results):
	del_m_indexes = { temp_L_m_index[1] for temp_L_m_index in wrong_matches if temp_L_m_index[0] == match_L_index }
	del_m_indexes = list(del_m_indexes)
	del_m_indexes.sort()
	
	deleted = 0
	for del_m_index in del_m_indexes:
		G50_results[match_L_index].pop( del_m_index - deleted )
		deleted += 1

# get image1 direct matched pixels
for match_L_index, matches in enumerate(G50_results):
	for m_index, match in enumerate(matches):

		im2to1_mv = ( match[2][0] * -1, match[2][1] * -1 )
		mv_pixels_at_im1 = pixel_functions.move_pixels( match[1], im2to1_mv[0], im2to1_mv[1], input_xy=True, im_size=image_size )
		dm_im1pixels = mv_pixels_at_im1.intersection( match[0] )
		
		G50_results[match_L_index][m_index] = [ dm_im1pixels, match[1], match[2] ]
		


# L50 found new matches from same_shapes_functions.match_with_expanded_pixels
matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(G50_results, fp)
fp.close()






























