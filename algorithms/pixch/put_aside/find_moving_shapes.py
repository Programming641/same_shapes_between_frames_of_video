# show all shapes boundaries.
#
#
from libraries import pixel_functions, pixel_shapes_functions, image_functions, btwn_amng_files_functions, same_shapes_functions

from PIL import Image
import time
import os, sys, copy
import pickle, shutil, json

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir
from libraries import cv_globals

start = time.time()

image_fname = "26"
image2_fname = "27"
directory = "videos/street3/resized/min1"

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

im1shapes_nbrs_fpath = top_shapes_dir + directory + "shapes/shape_nbrs/" + image_fname + "_xy_shape_nbrs.data"
with open (im1shapes_nbrs_fpath, 'rb') as fp:
   im1shapes_nbrs = pickle.load(fp)
fp.close()

im2shapes_nbrs_fpath = top_shapes_dir + directory + "shapes/shape_nbrs/" + image2_fname + "_xy_shape_nbrs.data"
with open (im2shapes_nbrs_fpath, 'rb') as fp:
   im2shapes_nbrs = pickle.load(fp)
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



pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_fpath = pixch_dir + "eachf_pixch.data"
with open (pixch_fpath, 'rb') as fp:
   eachf_pixch = pickle.load(fp)
fp.close()

btwn_im_pixch = eachf_pixch[ image_fname + '.' + image2_fname ]


lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

temp_imfpath = top_shapes_dir + directory + "temp/test.png"

im_xy_shapes = [ xy_im1shapes, xy_im2shapes ]
im_shapes_boundaries = [ im1shapes_boundaries, im2shapes_boundaries ]
im_rgb_xy_data = [ im1_rgb_xy_data, im2_rgb_xy_data ]


def del_redundant_ovlp_from_matches():

	done_matches = set()
	del_matches = set() # if removing overlap pixels results in no pixels, then delete them
	for m_index, match in enumerate(result):
		
		for ano_m_index, ano_match in enumerate(result):
			if m_index == ano_m_index:
				continue
			if (m_index, ano_m_index) in done_matches:
				continue
			
			done_matches.add( (m_index, ano_m_index) )
			done_matches.add( (ano_m_index, m_index) )
			
			im1overlap = match[0].intersection(ano_match[0] )
			if len(im1overlap) >= 1:
				# delete from ano_match
				result[ano_m_index][0] = result[ano_m_index][0].difference(im1overlap)
				im1to2_mv = result[ano_m_index][2]
				
				result[ano_m_index][1], matched_mv  = same_shapes_functions.match_pixels_at_specified_mvs( result[ano_m_index][0], {im1to2_mv}, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors )
				
				if len( result[ano_m_index][0] ) == 0 or len( result[ano_m_index][1] ) == 0:
					del_matches.add(ano_m_index)

	deleted = 0
	del_matches = list(del_matches)
	del_matches.sort()
	for del_index in del_matches:
		result.pop( del_index - deleted)
		deleted += 1



im_outside_bnd_pixch = [ None, None ]
for im1or2 in range(2):
	cur_im_bnd_pixels = set()
	for shapeid in im_shapes_boundaries[im1or2]:
		cur_im_bnd_pixels |= im_shapes_boundaries[im1or2][shapeid]
	
	cur_im_bnd_pixch = btwn_im_pixch.intersection(cur_im_bnd_pixels)
	cur_im_outside_bnd_pixch = btwn_im_pixch.difference(cur_im_bnd_pixch)
	
	im_outside_bnd_pixch[im1or2] = cur_im_outside_bnd_pixch

cv_globals.store_debug(True)

#image_functions.cr_im_from_pixels( image_fname, directory, im_outside_bnd_pixch[0], pixels_rgb=(255,255,0) )
#image_functions.cr_im_from_pixels( image2_fname, directory, im_outside_bnd_pixch[1], pixels_rgb=(0,255, 255) )


# getting moving shapes
im_shapes_w_pixch = [ set(), set() ]
im_s_w_pixch_pixels = [ set(), set() ]

for im1or2 in range(2):
	for shapeid in im_xy_shapes[im1or2]:
		if len( im_xy_shapes[im1or2][shapeid] ) < cv_globals.get_frth_smallest_pixc(image_size ):
			continue
		
		shape_pixch = im_xy_shapes[im1or2][shapeid].intersection(im_outside_bnd_pixch[im1or2] )
		shape_pixch_percent = len(shape_pixch) / len( im_xy_shapes[im1or2][shapeid] )
		
		if shape_pixch_percent >= 0.1:
			im_shapes_w_pixch[im1or2].add(shapeid)
			im_s_w_pixch_pixels[im1or2] |= im_xy_shapes[im1or2][shapeid]


#image_functions.cr_im_from_pixels( image_fname, directory, im_s_w_pixch_pixels[0], pixels_rgb=(255,0,0) )
#image_functions.cr_im_from_pixels( image2_fname, directory, im_s_w_pixch_pixels[1], pixels_rgb=(0, 0, 255) )

result = []

im1pixch_shapes = pixel_functions.find_shapes(im_s_w_pixch_pixels[0], image_size, input_xy=True )

matched_shapeids = set()
for gen_shapeid in im1pixch_shapes:

	if len( im1pixch_shapes[gen_shapeid] ) >= cv_globals.get_extraL_shp_size(image_size) * 3:

		matched_pixels, matched_mv = same_shapes_functions.match_shape_while_moving_it3( im1pixch_shapes[gen_shapeid], im_s_w_pixch_pixels[1], im_rgb_xy_data[0], im_rgb_xy_data[1], 
																					image_size, min_colors, best_match=True, end_move=23 )
		if len(matched_pixels) >= 1:

			# matched. now match against image to get actually matching pixels.
			matched_pixels, matched_mv = same_shapes_functions.match_pixels_at_specified_mvs( im1pixch_shapes[gen_shapeid], {matched_mv}, im_rgb_xy_data[0], im_rgb_xy_data[1], 
																			image_size, min_colors, threshold=cv_globals.m_threshold )				
			if len(matched_pixels) >= 1:
				print("result index " + str( len(result) ) + " matched at checkpoint1")
				result.append( [ im1pixch_shapes[gen_shapeid], matched_pixels, matched_mv ] )
				for pixel in im1pixch_shapes[gen_shapeid]:
					matched_shapeids |= im1_xy_shapeids_by_p[pixel]

				continue # matched


	# try to match with other pixch neighbors
	# get the original pixch shapeids in it
	pixch_shapeids = set()
	for pixel in im1pixch_shapes[gen_shapeid]:
		pixch_shapeids |= im1_xy_shapeids_by_p[pixel]
	
	for pixch_shapeid in pixch_shapeids:
		if pixch_shapeid in matched_shapeids:
			continue
		pixch_nbrs = im1shapes_nbrs[pixch_shapeid]
		pixch_nbrs = pixch_nbrs.intersection(im_shapes_w_pixch[0] )
		
		try_pixels = xy_im1shapes[pixch_shapeid].copy()
		try_count = 1 # at least 3 shapes are needed for matching.
		try_shapeids = {pixch_shapeid}
		
		for pixch_nbr in pixch_nbrs:
			if len( xy_im1shapes[pixch_nbr] ) < cv_globals.get_sec_smallest_pixc(image_size):
				continue

			#size_diff = same_shapes_functions.size_diff_by_percent( xy_im1shapes[pixch_shapeid],  xy_im1shapes[pixch_nbr] )
			#if size_diff is True:
			#	continue

			try_pixels |= xy_im1shapes[pixch_nbr]
			try_count += 1
			try_shapeids.add(pixch_nbr)
			
			if try_count < 3:
				continue
			
			matched_pixels, matched_mv = same_shapes_functions.match_shape_while_moving_it3( try_pixels, im_s_w_pixch_pixels[1], im_rgb_xy_data[0], im_rgb_xy_data[1], 
																							image_size, min_colors, best_match=True, end_move=23 )
			if len(matched_pixels) == 0:
				# match failed. initialize data
				try_pixels = xy_im1shapes[pixch_shapeid].copy()
				try_count = 1 # at least 3 shapes are needed for matching.
				try_shapeids = {pixch_shapeid}
				continue

			# check if enough pixels matched from multiple shapes from try_shapeids. not just one big shape matched and all other small shapes did not match at all.
			matched_count = 1
			reset_try_pixels = xy_im1shapes[pixch_shapeid].copy()
			reset_try_shapeids = {pixch_shapeid}
			
			im2to1_mv = ( matched_mv[0] * -1, matched_mv[1] * -1 )
			matched_im1pixels = pixel_functions.move_pixels( matched_pixels, im2to1_mv[0], im2to1_mv[1], input_xy=True, im_size=image_size )
			
			for try_shapeid in try_shapeids:
				shape_mpixels = matched_im1pixels.intersection( xy_im1shapes[try_shapeid] )
				shape_mpercent = len(shape_mpixels) / len( xy_im1shapes[try_shapeid] )
				
				if try_shapeid not in reset_try_shapeids and shape_mpercent >= 0.5:
					matched_count += 1
					reset_try_pixels |= xy_im1shapes[try_shapeid]
					reset_try_shapeids.add(try_shapeid)
			
			if matched_count < 3:
				try_pixels = reset_try_pixels
				try_count = matched_count
				try_shapeids = reset_try_shapeids
				continue
			
			# matched. now get actually matching pixels.
			matched_pixels, matched_mv = same_shapes_functions.match_pixels_at_specified_mvs( try_pixels, {matched_mv}, im_rgb_xy_data[0], im_rgb_xy_data[1], 
																			image_size, min_colors, threshold=cv_globals.m_threshold )	
			if len(matched_pixels) == 0:
				try_pixels = xy_im1shapes[pixch_shapeid].copy()
				try_count = 1 # at least 3 shapes are needed for matching.
				try_shapeids = {pixch_shapeid}
				continue
			print("result index " + str( len(result) ) + " matched at checkpoint2")
			result.append( [ try_pixels, matched_pixels, matched_mv ] )
			matched_shapeids |= try_shapeids
			break


# result may very well contain the matches that have redundant overlapping pixels. delete them
del_redundant_ovlp_from_matches()




unmatched_shapeids = im_shapes_w_pixch[0].difference(matched_shapeids)
unm_pixels = set()
for unm_shapeid in unmatched_shapeids:
	unm_pixels |= xy_im1shapes[unm_shapeid]
image_functions.cr_im_from_pixels( image_fname, directory, unm_pixels, pixels_rgb=(255,0,0) )


moving_shapes_dir = pixch_dir + "moving_shapes/"
moving_shapes_ddir = moving_shapes_dir + "data/"
if not os.path.exists(moving_shapes_ddir):
	os.makedirs(moving_shapes_ddir)

matched_shapes_fpath = moving_shapes_ddir + image_fname + '.' + image2_fname + "_1.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(result, fp)
fp.close()

unm_shapeids_fpath = moving_shapes_ddir + image_fname + '.' + image2_fname + "_unmatched_shapeids.data"
with open(unm_shapeids_fpath, 'wb') as fp:
   pickle.dump(unmatched_shapeids, fp)
fp.close()



end = time.time()

elapsed = end - start
print(f"Elapsed time: {elapsed:.4f} seconds")





















