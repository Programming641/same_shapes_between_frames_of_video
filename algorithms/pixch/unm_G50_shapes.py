# this is to test unmatched pixch shapes from find_moving_shapes.py
#
#
from libraries import pixel_functions, pixel_shapes_functions, image_functions, btwn_amng_files_functions, same_shapes_functions

from PIL import Image
import time, math
import os, sys, copy
import pickle, shutil, json

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir
from libraries import cv_globals

start = time.time()

image_fname = "1"
image2_fname = "2"
result_num = '1'
directory = "videos/sea/resized/min1"

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

cv_globals.store_debug(True)
rgbs = image_functions.get_rgbs( start_r=100, start_g=25, start_b=150, steps=80 )


lowest_fnum, highest_fnum = btwn_amng_files_functions.get_low_highest_filenums( directory )
image1 = Image.open(top_images_dir + directory + str(lowest_fnum) + ".png")
image_size = image1.size



pixch_shapes_dir = pixch_dir + "pixch_shapes" + result_num + '/'
pixch_shapes_ddir = pixch_shapes_dir + "data/"

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open (matched_shapes_fpath, 'rb') as fp:
	# [  [ im1 pixels, m_pixels, matched movement, image1 shapeid ], ... ]
   less50_results = pickle.load(fp)
fp.close()

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open (matched_shapes_fpath, 'rb') as fp:
	# [  [ [ image1 pixels, im2 matched pixels, matched movement, image1 shapeid ], ... ], ... ]
	G50_results = pickle.load(fp)
fp.close()


matched_im1shapeids = set()
for match in G50_results:
	for im1pixel in match[0]:
		matched_im1shapeids |= im1_xy_shapeids_by_p[im1pixel]

unmatched_shapeids = set( xy_im1shapes.keys() ).difference(matched_im1shapeids)

G50_unmatched_shapeids = set()
for unm_shapeid in unmatched_shapeids:
	if len( xy_im1shapes[unm_shapeid] ) < cv_globals.get_frth_smallest_pixc(image_size):
		continue
	
	shape_pixch = xy_im1shapes[unm_shapeid].intersection(btwn_im_pixch)
	shape_pixch_percent = len(shape_pixch) / len( xy_im1shapes[unm_shapeid] )
	if shape_pixch_percent >= 0.5:
		G50_unmatched_shapeids.add(unm_shapeid)
	
	



temp_im1fpath = top_shapes_dir + directory + "temp/test.png"
if os.path.exists(temp_im1fpath):
	os.remove(temp_im1fpath)

fourth_pix_size = cv_globals.get_frth_smallest_pixc(image_size)

alrdy_matched_shapes = []
for match in less50_results:
	# [ im1 pixels, m_pixels, matched movement, image1 shapeid ]
	alrdy_matched_shapes.append( match )

for matches in G50_results:
	for match in matches:
		# [ image1 pixels, im2 matched pixels, matched movement, image1 shapeid ]
		alrdy_matched_shapes.append( match )



def get_largest_alrdy_m_nbrs( alrdy_m_nbr_indexes, expanded_pixels ):

	done_alrdy_matches = set()
	del_alrdy_matches = set() # if the match overlaps with another match and another should be taken, then the match will not be in the alrdy_matched_nbrs.
	
	for alrdy_m_index in alrdy_m_nbr_indexes:
		for ano_alrdy_m_index in alrdy_m_nbr_indexes:

			if alrdy_m_index == ano_alrdy_m_index:
				continue
			if (alrdy_m_index, ano_alrdy_m_index) in done_alrdy_matches:
				continue
			
			done_alrdy_matches.add( ( alrdy_m_index, ano_alrdy_m_index ) )
			done_alrdy_matches.add( ( ano_alrdy_m_index, alrdy_m_index ) )
			
			im1_pixels_ovlp = alrdy_matched_shapes[alrdy_m_index][0].intersection( alrdy_matched_shapes[ano_alrdy_m_index][0] )
			im2_pixels_ovlp = alrdy_matched_shapes[alrdy_m_index][1].intersection( alrdy_matched_shapes[ano_alrdy_m_index][1] )
			
			if len(im1_pixels_ovlp) >= 1 or len(im2_pixels_ovlp) >= 1:
				# alrdy_m_index and ano_alrdy_m_index overlaps with each other. now check which one has the most pixels in expanded_pixels.
				
				alrdy_m_expanded_ovlp = alrdy_matched_shapes[alrdy_m_index][0].intersection( expanded_pixels )
				ano_alrdy_m_expanded_ovlp = alrdy_matched_shapes[ano_alrdy_m_index][0].intersection( expanded_pixels)
				
				if len(alrdy_m_expanded_ovlp) > len(ano_alrdy_m_expanded_ovlp):
					del_alrdy_matches.add(ano_alrdy_m_index)
				elif len(ano_alrdy_m_expanded_ovlp) > len(alrdy_m_expanded_ovlp):
					del_alrdy_matches.add(alrdy_m_index)
				else:
					# if both have the same overlap size in the expanded_pixels, just pick either one.
					del_alrdy_matches.add(ano_alrdy_m_index)
	
	
	result_alrdy_m_nbrs = alrdy_m_nbr_indexes.difference(del_alrdy_matches)
	return result_alrdy_m_nbrs



result = []
for im1unm_shapeid in G50_unmatched_shapeids:
	if len( xy_im1shapes[im1unm_shapeid] ) < cv_globals.get_frth_smallest_pixc(image_size):
		continue
	
	matched_pixels, matched_mv = same_shapes_functions.match_with_expanded_pixels( xy_im1shapes[im1unm_shapeid], image_size, True, im1_rgb_xy_data, im2_rgb_xy_data, min_colors  )
	if matched_pixels is not None:
		result.append( [ xy_im1shapes[im1unm_shapeid], matched_pixels, matched_mv, im1unm_shapeid ] )
		
	else:
		# it could not match up to this point ( after gone through algorithms/pixch/pixch_shapes.py and /algorithms/pixch/find_moving_shapes.py suggest the shape has either disappeared or 
		# has highly deformed.
		
		expanded_pixels = pixel_functions.expand_boundary(im1shapes_boundaries[im1unm_shapeid], image_size, expand_by=5, input_xy=True)
		expanded_pixels = expanded_pixels.difference( xy_im1shapes[im1unm_shapeid] )
		
		# because im1unm_shapeid may have high deformations, match with only surrounding pixels
		exp_mpixels, m_mv, out_pixels = same_shapes_functions.match_by_mov_pixels_against_im( expanded_pixels, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, 
																out_im=True, move_amount=22, m_threshold=cv_globals.m_threshold )
		if len(exp_mpixels) >= 1:
			matched_pixels, m_mv = same_shapes_functions.match_pixels_at_specified_mvs( xy_im1shapes[im1unm_shapeid], {m_mv}, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors )
			if len(matched_pixels) == 0:
				continue
			result.append( [ xy_im1shapes[im1unm_shapeid], matched_pixels, m_mv ] )
		
		else:
			# failed matching by expanded pixels
			# expanded_pixels are suspected to have large deformations. to identify which pixels have large deformations, I need to lower the threshold
			exp_mpixels, m_mv, out_pixels = same_shapes_functions.match_by_mov_pixels_against_im( expanded_pixels, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, 
																	out_im=True, move_amount=22, m_threshold=0 )
			
			im2to1_mv = ( m_mv[0] * -1, m_mv[1] * -1 )
			m_im1pixels = pixel_functions.move_pixels( exp_mpixels, im2to1_mv[0], im2to1_mv[1], input_xy=True, im_size=image_size )
			
			exp_def_pixels = expanded_pixels.difference(m_im1pixels)
			exp_def_pixels |= xy_im1shapes[im1unm_shapeid]
			
			# get expanded pixels from exp_def_pixels
			expanded_pixels2 = pixel_functions.expand_boundary(exp_def_pixels, image_size, expand_by=5, input_xy=True)
			expanded_pixels2 = expanded_pixels2.difference( exp_def_pixels )
			
			m_im1pixels |= expanded_pixels2

			exp_mpixels, m_mv, out_pixels = same_shapes_functions.match_by_mov_pixels_against_im( m_im1pixels, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors, 
																									out_im=True, move_amount=22, m_threshold=cv_globals.m_threshold )
			
			if len(exp_mpixels) == 0:
				# failed expanded pixels
				continue
			
			def_matched_pixels, m_mv = same_shapes_functions.match_pixels_at_specified_mvs( exp_def_pixels, {m_mv}, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors )
			if len(def_matched_pixels) == 0:
				continue
			
			im2to1_mv = ( m_mv[0] * -1, m_mv[1] * -1)
			def_m_im1pixels = pixel_functions.move_pixels( def_matched_pixels, im2to1_mv[0], im2to1_mv[1], input_xy=True, im_size=image_size )
			
			exp_def_shapes = pixel_functions.find_shapes2(exp_def_pixels, im1_rgb_xy_data, image_size, min_colors, input_xy=True)
			m_im1_def_pixels = set()
			for exp_def_pixels in exp_def_shapes.values():
				ovlp_pixels = exp_def_pixels.intersection(def_m_im1pixels)
				if len(ovlp_pixels) >= 1:
					m_im1_def_pixels |= exp_def_pixels
				
			result.append( [ m_im1_def_pixels, def_matched_pixels, m_mv ] )



unm_matched_dir = pixch_dir + "unm_matched/"
unm_matched_ddir = unm_matched_dir + "data/"
if not os.path.exists(unm_matched_ddir):
	os.makedirs(unm_matched_ddir)

matched_shapes_fpath = unm_matched_ddir + image_fname + '.' + image2_fname + "_1.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(result, fp)
fp.close()

end = time.time()

elapsed = end - start
print(f"Elapsed time: {elapsed:.4f} seconds")





















