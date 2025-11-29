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

image_fname = "1"
image2_fname = "2"
directory = "videos/street4/resized/min1"

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

lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size

cv_globals.store_debug(True)

im1_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image_fname + ".data"
with open (im1_rgb_xy_data_fpath, 'rb') as fp:
   im1_rgb_xy_data = pickle.load(fp)
fp.close()

im2_rgb_xy_data_fpath = top_shapes_dir + directory + "shapes/im_rgb_xy_data/" + image2_fname + ".data"
with open (im2_rgb_xy_data_fpath, 'rb') as fp:
   im2_rgb_xy_data = pickle.load(fp)
fp.close()


def get_matches(result ):
	for m_index,  match in enumerate(result):
		all_matches.append(match)


all_matches = []

pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_shapes_dir = pixch_dir + "pixch_shapes1/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"

L50_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open (L50_fpath, 'rb') as fp:
	# [  [ image1 pixels, image2 pixels, matched movement, image1 shapeid, message ], ... ]
	less50_results = pickle.load(fp)
fp.close()

G50_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open (G50_fpath, 'rb') as fp:
   G50_results = pickle.load(fp)
fp.close()

unm_matched_dir = pixch_dir + "unm_matched/"
unm_matched_ddir = unm_matched_dir + "data/"

matched_shapes_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + "_1.data"
if os.path.exists(matched_shapes_fpath):
	with open (matched_shapes_fpath, 'rb') as fp:
	   unm_matched_shapes = pickle.load(fp)
	fp.close()

get_matches(unm_matched_shapes)

pixch_shapes2_dir = pixch_dir + "pixch_shapes2/"
pixch_shapes2_ddir = pixch_shapes2_dir + "data/"
pixch_shapes2_fpath = pixch_shapes2_ddir + image_fname + '.' + image2_fname + ".data"
with open (pixch_shapes2_fpath, 'rb') as fp:
   pixch_shapes2 = pickle.load(fp)
fp.close()

get_matches(pixch_shapes2)


unm_m_fpath = pixch_shapes2_ddir + image_fname + '.' + image2_fname + "unm_matched.data"
with open (unm_m_fpath, 'rb') as fp:
   unm_m_shapes2 = pickle.load(fp)
fp.close()


get_matches(less50_results)
get_matches(unm_m_shapes2)

for match in G50_results:	
	all_matches.append(match)


all_matched_pixels = [ set(), set() ]
for match in all_matches:
	all_matched_pixels[0] |= match[0]
	all_matched_pixels[1] |= match[1]


alrdy_m_shapes_lookup = {}
for m_index, match in enumerate(all_matches):
	for im1pixel in match[0]:
		if alrdy_m_shapes_lookup.get(im1pixel) is None:
			alrdy_m_shapes_lookup[im1pixel] = {m_index}
		else:
			alrdy_m_shapes_lookup[im1pixel].add(m_index)



all_im_pixels = set()
for x in range(image_size[0] ):
	for y in range(image_size[1] ):
		all_im_pixels.add( (x,y) )

im1unm_pixels = all_im_pixels.difference( all_matched_pixels[0] )
im2unm_pixels = all_im_pixels.difference( all_matched_pixels[1] )


im1unm_shapes = pixel_functions.find_shapes2(im1unm_pixels, im1_rgb_xy_data, image_size, min_colors, input_xy=True)

result = []

for im1unm_spixels in im1unm_shapes.values():
	
	expanded_pixels = pixel_functions.expand_boundary(im1unm_spixels, image_size, expand_by=2, input_xy=True)
	out_exp_p = expanded_pixels.difference(im1unm_spixels)
	
	alrdy_m_nbr_indexes = set()
	for out_pixel in out_exp_p:	
		if alrdy_m_shapes_lookup.get(out_pixel) is None:
			continue
		alrdy_m_nbr_indexes |= alrdy_m_shapes_lookup[out_pixel]

	all_im1attached_pixels = set()
	all_im2attached_pixels = set()
	
	for alrdy_m_nbr_index in alrdy_m_nbr_indexes:
		
		im1attached_pixels = all_matches[alrdy_m_nbr_index][0].intersection(out_exp_p)
		
		im1to2_mv = all_matches[alrdy_m_nbr_index][2]
		im2attached_pixels = pixel_functions.move_pixels( im1attached_pixels, im1to2_mv[0], im1to2_mv[1], input_xy=True, im_size=image_size )
		
		all_im1attached_pixels |= im1attached_pixels
		all_im2attached_pixels |= im2attached_pixels
	

	if len(all_im1attached_pixels) == 0 or len(all_im2attached_pixels) == 0:
		continue

	m_attached_pixels, matched_mv = same_shapes_functions.match_shape_while_moving_it3( all_im1attached_pixels, all_im2attached_pixels, im1_rgb_xy_data, im2_rgb_xy_data, 
																						image_size, min_colors, best_match=True, ignore_clrs=True )
	
	if len(m_attached_pixels) == 0:
		continue
	mvs_w_buffer = pixel_shapes_functions.get_mv_with_buffer( matched_mv, 2 )
	
	matched_pixels, matched_mv = same_shapes_functions.match_pixels_at_specified_mvs( im1unm_spixels, mvs_w_buffer, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, threshold=0.1 )
	if len(matched_pixels) >= 1:		
		result.append( [ im1unm_spixels, matched_pixels, matched_mv ] )




pixch_shapes_dir = pixch_dir + "pixch_shapes3/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"
if not os.path.exists(pixch_shapes_ddir):
	os.makedirs(pixch_shapes_ddir)

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "unm_matched.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(result, fp)
fp.close()



























