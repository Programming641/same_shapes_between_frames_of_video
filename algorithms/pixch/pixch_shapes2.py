# show all shapes boundaries.
#
#
from libraries import pixel_functions, pixel_shapes_functions, image_functions, btwn_amng_files_functions, same_shapes_functions, shapes_results_functions

from PIL import Image
import time, winsound
import os, sys, copy
import pickle, shutil, json

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir, top_tests_dir
from libraries import cv_globals

start = time.time()

image_fname = "25"
image2_fname = "26"
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

im1snbrs_fpath = top_shapes_dir + directory + "shapes/shape_nbrs/" + image_fname + "_xy_shape_nbrs.data"
with open (im1snbrs_fpath, 'rb') as fp:
   im1shapes_nbrs = pickle.load(fp)
fp.close()

im2snbrs_fpath = top_shapes_dir + directory + "shapes/shape_nbrs/" + image2_fname + "_xy_shape_nbrs.data"
with open (im2snbrs_fpath, 'rb') as fp:
   im2shapes_nbrs = pickle.load(fp)
fp.close()

im1_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image_fname + ".data"
with open (im1_rgb_xy_data_fpath, 'rb') as fp:
   im1_rgb_xy_data = pickle.load(fp)
fp.close()

im2_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image2_fname + ".data"
with open (im2_rgb_xy_data_fpath, 'rb') as fp:
   im2_rgb_xy_data = pickle.load(fp)
fp.close()

im1_xy_shapeids_by_p_fpath = top_shapes_dir + directory + "shapes/shapeids_by_pixel/xy" + image_fname + ".data"
with open (im1_xy_shapeids_by_p_fpath, 'rb') as fp:
   im1_xy_shapeids_by_p = pickle.load(fp)
fp.close()

im2_xy_shapeids_by_p_fpath = top_shapes_dir + directory + "shapes/shapeids_by_pixel/xy" + image2_fname + ".data"
with open (im2_xy_shapeids_by_p_fpath, 'rb') as fp:
   im2_xy_shapeids_by_p = pickle.load(fp)
fp.close()

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_fpath = pixch_dir + "eachf_pixch.data"
with open (pixch_fpath, 'rb') as fp:
   eachf_pixch = pickle.load(fp)
fp.close()

btwn_im_pixch = eachf_pixch[ image_fname + '.' + image2_fname ]



# getting already matched shapes            ----------------------------------------------
pixch_shapes_dir = pixch_dir + "pixch_shapes1/"
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

unm_matched_dir = pixch_dir + "unm_matched/"
unm_matched_ddir = unm_matched_dir + "data/"

unm_matched_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + "_1.data"
with open (unm_matched_fpath, 'rb') as fp:
	# [  [ [ image1 pixels, im2 matched pixels, matched movement, image1 shapeid ], ... ], ... ]
	unm_matched = pickle.load(fp)
fp.close()

alrdy_matched_shapes = []
for match in less50_results:
	# [ im1 pixels, m_pixels, matched movement, image1 shapeid ]
	alrdy_matched_shapes.append( match )

for match in G50_results:
	alrdy_matched_shapes.append( match )

for match in unm_matched:
	alrdy_matched_shapes.append(match)

alrdy_m_lookup = {}
for m_index, match in enumerate(alrdy_matched_shapes):
	for im1pixel in match[0]:
		if alrdy_m_lookup.get(im1pixel) is None:
			alrdy_m_lookup[im1pixel] = {m_index}
		else:
			alrdy_m_lookup[im1pixel].add(m_index)

# getting already matched shapes done        ---------------------------------------------


im1pixch_shapes = {}
for im1shapeid in xy_im1shapes:
	shape_pixch = xy_im1shapes[im1shapeid].intersection(btwn_im_pixch)
	im1pixch_shapes[im1shapeid] = shape_pixch

cv_globals.store_debug(True)

lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

test_im1fpath = top_shapes_dir + directory + "temp/test.png"

pixch_shapes = pixel_functions.find_shapes(btwn_im_pixch, image_size, input_xy=True )

matched_shapeids = set()
result = []


for pixch_sindex, pixch_pixels in enumerate( pixch_shapes.values() ):
	if len(pixch_pixels) < cv_globals.get_indpnt_shape_size(image_size):
		continue
	
	#image_functions.cr_im_from_pixels( image_fname, directory,   pixch_pixels , pixels_rgb=(255, 255, 0) )

	# get shapes on the pixch_pixels.
	shapeids_on_pixch = set()
	for pixch_pixel in pixch_pixels:
		shapeids_on_pixch |= im1_xy_shapeids_by_p[pixch_pixel]
	shapeids_on_pixch = shapeids_on_pixch.difference(matched_shapeids)
	
	# get the most abundant pixch percent
	# { pixch percent: { shapeids }, ... }
	pixch_percents = {}
	for shapeid_on_pixch in shapeids_on_pixch:
		if len( xy_im1shapes[shapeid_on_pixch] ) < cv_globals.get_third_smallest_pixc(image_size):
			continue
		
		shape_pixch_percent = len( im1pixch_shapes[shapeid_on_pixch] ) / len( xy_im1shapes[shapeid_on_pixch] )
		if shape_pixch_percent < 0.1:
			continue
		pixch_percents[shape_pixch_percent] = {shapeid_on_pixch}
		
		for ano_shapeid in shapeids_on_pixch:
			if shapeid_on_pixch == ano_shapeid or len( xy_im1shapes[ano_shapeid] ) < cv_globals.get_third_smallest_pixc(image_size):
				continue

			ano_s_percent = len( im1pixch_shapes[ano_shapeid] ) / len( xy_im1shapes[ano_shapeid] )
			pixch_percent_diff = abs( ano_s_percent - shape_pixch_percent )
			if pixch_percent_diff > 0.1:
				continue
			pixch_percents[shape_pixch_percent].add(ano_shapeid)


	if len(pixch_percents) == 0:
		continue
	most_abundant_percent, most_abundant_shapeids = max(pixch_percents.items(), key=lambda x: len(x[1]))
	
	if len(most_abundant_shapeids) < 3:
		continue
	
	if most_abundant_percent >= 0.5:
		move_amount = 22
	else:
		move_amount = 16
	
	try_pixels = set()
	try_pixch = set()
	for shapeid in most_abundant_shapeids:
		try_pixels |= xy_im1shapes[shapeid]
		try_pixch |= im1pixch_shapes[shapeid]
	
	if len(try_pixels) < cv_globals.get_extraL_shp_size(image_size):
		continue
	
	matched_pixels, matched_mv = same_shapes_functions.match_pixch_shape2( try_pixels, try_pixch, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, move_amount=move_amount )
	if len(matched_pixels) >= 1:
		
		# checking if matched pixels conflict with already matched shapes
		alrdy_m_indexes = set()
		for try_pixel in try_pixels:
			if alrdy_m_lookup.get(try_pixel) is not None:
				alrdy_m_indexes |= alrdy_m_lookup[try_pixel]
		
		# remove conflict pixels
		for alrdy_m_index in alrdy_m_indexes:
			alrdy_m_movement = alrdy_matched_shapes[alrdy_m_index][2]
			
			same_movement = same_shapes_functions.check_same_movement( matched_mv, alrdy_m_movement )
			if same_movement is False:
				cur_conflict_im1pixels = try_pixels.intersection( alrdy_matched_shapes[alrdy_m_index][0] )
				try_pixels = try_pixels.difference(cur_conflict_im1pixels)
		
		if len(try_pixels) == 0:
			continue
		
		pixels_at_im2 = pixel_functions.move_pixels( try_pixels, matched_mv[0], matched_mv[1], input_xy=True, im_size=image_size )
		mpixels = pixels_at_im2.intersection(matched_pixels)
		
		#image_functions.cr_im_from_pixels( image_fname, directory,   try_pixels , pixels_rgb=(255, 0, 0) )
		#image_functions.cr_im_from_pixels( image2_fname, directory,   mpixels, pixels_rgb=(255, 0, 100) )
		#image_functions.cr_im_from_pixels( image2_fname, directory,   matched_pixels, pixels_rgb=(0, 0, 255) )
		
		matched_shapeids |= most_abundant_shapeids
		result.append( [ try_pixels, mpixels, matched_mv ] )


# removing duplicate matches. if matches already taken previously.
del_indexes = set()
for m_index, match in enumerate(result):
	
	orig_im1p_len = len(match[0] )
	
	alrdy_m_indexes = set()
	for im1pixel in match[0]:
		if alrdy_m_lookup.get(im1pixel) is not None:
			alrdy_m_indexes |= alrdy_m_lookup[im1pixel]

	for alrdy_m_index in alrdy_m_indexes:
		match[0] = match[0].difference( alrdy_matched_shapes[alrdy_m_index][0] )
	
	if len( match[0] ) < cv_globals.get_third_smallest_pixc(image_size):
		del_indexes.add(m_index)
		continue
	
	if len( match[0] ) < orig_im1p_len:
		# no need to delete this match but this needs to be modified
		
		mv_pixels_at_im2 = pixel_functions.move_pixels( match[0], match[2][0], match[2][1], input_xy=True, im_size=image_size )
		matched_pixels = mv_pixels_at_im2.intersection( match[1] )
		
		if len(matched_pixels) < cv_globals.get_sec_smallest_pixc(image_size):
			del_indexes.add(m_index)
			continue
		
		result[m_index] = [ match[0], matched_pixels, match[2] ]


deleted = 0
del_indexes = list(del_indexes)
del_indexes.sort()
for del_index in del_indexes:
	result.pop( del_index - deleted)
	deleted += 1

shapes_results_functions.get_direct_matches( result, image_size )



pixch_shapes_dir = pixch_dir + "pixch_shapes2/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"
if not os.path.exists(pixch_shapes_ddir):
	os.makedirs(pixch_shapes_ddir)

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + ".data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(result, fp)
fp.close()



end = time.time()

elapsed = end - start
print(f"Elapsed time: {elapsed:.4f} seconds")



frequency = 2000  # Set Frequency To 2500 Hertz
duration = 5000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)



























