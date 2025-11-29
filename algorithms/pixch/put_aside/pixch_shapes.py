
#
#
from libraries import pixel_functions, pixel_shapes_functions, image_functions, btwn_amng_files_functions, same_shapes_functions, shapes_results_functions
from help_lib import crud_shapes

from PIL import Image
import time, winsound
import os, sys, copy, logging
import pickle, shutil, json

from collections import OrderedDict
from libraries.cv_globals import top_shapes_dir, top_images_dir
from libraries import cv_globals

start = time.time()

image_fname = "1"
image2_fname = "2"
directory = "videos/fire/resized/min1"

if len(sys.argv) >= 2:
	directory = sys.argv[1]
	image_fname = sys.argv[2].split('.')[0]
	image2_fname = sys.argv[2].split('.')[1]

# Configure logging
logging.basicConfig(
    filename='app.log',         # file name
    level=logging.INFO,         # minimum level to log
    format='%(asctime)s - %(levelname)s - %(message)s'  # log format
)

script_path = os.path.abspath(__file__)
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

image1 = Image.open(top_images_dir + directory + image_fname + ".png")
image_size = image1.size

cur_pixch = eachf_pixch[ image_fname + '.' + image2_fname ]

temp_imfpath = top_shapes_dir + directory + "temp/test.png"

im_rgb_xy_data = [ im1_rgb_xy_data, im2_rgb_xy_data ]
im_shapes_cp = [ copy.deepcopy(xy_im1shapes), xy_im2shapes ] # for image1, image shapes will be updated during the loop. so copy is necessary
im_shapes = [ xy_im1shapes, xy_im2shapes ] # for image1, image shapes will be updated during the loop. so copy is necessary
im_shapes_nbrs = [ im1shapes_nbrs, im2shapes_nbrs ]
im_fnames = [ image_fname, image2_fname ]
im_shapes_boundaries = [ im1shapes_boundaries, im2shapes_boundaries ]
im_xy_shapeids_by_p = [ im1_xy_shapeids_by_p, im2_xy_shapeids_by_p ]




def perform_matching( shape_pixels, im1or2, shapeid, done_shapes, message='' ):
	global matched_im2pixels
	
	oppos_im = abs(im1or2 - 1)

	cur_s_pixch = shape_pixels.intersection(cur_pixch )
	cur_s_pixch_percent = len(cur_s_pixch) / len( shape_pixels )

	matched = "did_not_try"    # true: tried and matched.   did_not_try: did not even try so did not make a match.   false:  tried but failed
	if cur_s_pixch_percent < 0.5:

		m_pixels, m_mv = same_shapes_functions.match_pixch_shape2( shape_pixels, cur_s_pixch,
																				im_rgb_xy_data[im1or2], im_rgb_xy_data[oppos_im], image_size, min_colors )
		if len(m_pixels) >= 1:
			if im1or2 == 0:
				matched_im2pixels |= m_pixels
				less50_results.append( [ shape_pixels, m_pixels, m_mv, message ] )
			else:
				m_mv = ( m_mv[0] * -1, m_mv[1] * -1 )
				less50_results.append( [ m_pixels, shape_pixels, m_mv, "matched_from_im2" ] )
			
			return True # matched
		
		else:
			matched = False
		

	else:
		# for pixch more than 50% shapes, match with neighbors. make sure neighbors are about the same size. for really big shapes, they probably would not be 
		# able to find neighbors about their size. so exclude them in this algorithm.
		
		if len(shape_pixels) >= cv_globals.get_indpnt_shape_size(image_size) * 2:
			# big enoug. it can try to match on its own
			
			#  [  ( matched percent, matched_pixels, (move_RL, move_UD) ), ... ]
			all_matches = same_shapes_functions.match_pixch_shape2( shape_pixels, cur_s_pixch,
																				im_rgb_xy_data[im1or2], im_rgb_xy_data[oppos_im], image_size, min_colors, move_amount=22, return_all_m=True )
			
			actual_matches = shapes_results_functions.get_real_matches_from_all_m2( all_matches )
			if len(actual_matches) == 1:
				if im1or2 == 0:
					G50_results.append( [ ( shape_pixels,  actual_matches[0][1], actual_matches[0][2], message ) ] )
				else:
					im1to2_mv = ( actual_matches[0][2][0] * -1, actual_matches[0][2][1] * -1 )
					G50_results.append( [ ( actual_matches[0][1], shape_pixels, im1to2_mv, "matched_from_im2" ) ] )
				return True


		try_pixels = shape_pixels.copy()
		try_pixch = cur_s_pixch.copy()
		try_shapeids = {shapeid}
		
		for nbr_shapeid in im_shapes_nbrs[im1or2][shapeid]:
			if nbr_shapeid in done_shapes:
				continue
			# check if neighbor size is satisfactory
			size_diff = same_shapes_functions.size_diff_by_percent( shape_pixels, im_shapes[im1or2][nbr_shapeid] )
			if size_diff is True:
				# size is different more than threshold
				continue

			try_pixels |= im_shapes[im1or2][nbr_shapeid]
			
			nbr_pixch = im_shapes[im1or2][nbr_shapeid].intersection(cur_pixch )
			try_pixch |= nbr_pixch
			try_shapeids.add(nbr_shapeid)
			
			if len(try_pixels) < cv_globals.get_indpnt_shape_size(image_size ) * 2 or len(try_shapeids) < 3:
				continue

			m_pixels, m_mv = same_shapes_functions.match_pixch_shape2( try_pixels, try_pixch,
																				im_rgb_xy_data[im1or2], im_rgb_xy_data[oppos_im], image_size, min_colors,  move_amount=22 )
			if len(m_pixels) >= 1:
				# check if really all shapes matches are made. not just one shape matched 90% then another shape matched 30%.
				
				match_ok = True
				shapes_matches = []
				cur_m_im2pixels = set()
				for m_shapeid in try_shapeids:
					mv_pixels = pixel_functions.move_pixels( im_shapes[im1or2][m_shapeid], m_mv[0], m_mv[1], input_xy=True, im_size=image_size )
					shape_m_pixels = mv_pixels.intersection(m_pixels)
					shape_m_percent = len(shape_m_pixels) / len( im_shapes[im1or2][m_shapeid] )
					if shape_m_percent < 0.5:
						# match check failed
						match_ok = False
						break
					
					if im1or2 == 0:
						cur_m_im2pixels |= shape_m_pixels
						shapes_matches.append( [ im_shapes[im1or2][m_shapeid], shape_m_pixels, m_mv, message ] )
					else:
						m_mv = ( m_mv[0] * -1, m_mv[1] * -1)
						shapes_matches.append( [ shape_m_pixels, im_shapes[im1or2][m_shapeid], m_mv, "matched_from_im2" ] )
				
				if match_ok:
					matched_im2pixels |= cur_m_im2pixels
					G50_results.append( shapes_matches )
					done_shapes |= try_shapeids
					matched = True
					break

			else:
				# tried but failed
				matched = False

	return matched



less50_results = []
G50_results = []
didnt_try_im1shapeids = set()
didnt_match_im1shapeids = set()

matched_im2pixels = set()  # to search fro shapes from image2 to image1, only search from unfound image2 shapes.
matched_im2shapeids = set()


for im1or2 in range(2):
	# if image1 shape did not match, it may be because image1 shape is combined shape. so it is necessary to match from image2 to image1. but only do unmatched shapes from matching image1 to image2.
	oppos_im = abs(im1or2 - 1)
	done_shapes = set()

	for shapeid in im_shapes_cp[im1or2] :

		if len( im_shapes_cp[im1or2][shapeid] ) < cv_globals.get_frth_smallest_pixc( image_size) :
			continue
		
		if im1or2 == 1 and shapeid in matched_im2shapeids:
			# current image2 shape is matched
			continue

		matched = perform_matching( im_shapes_cp[im1or2][shapeid], im1or2, shapeid, done_shapes )

		if matched is True:
			continue
		
		if im1or2 == 0 and matched is False and len( im_shapes_cp[im1or2][shapeid] ) >= cv_globals.get_frth_smallest_pixc(image_size) * 2.5:
			# only for image1. if the shape is the combined shape, they likely did not make a match.

			split_shapes = pixel_shapes_functions.split_comb_shape( im_shapes_cp[0][shapeid], cv_globals.get_frth_smallest_pixc(image_size), 
																	image_size, boundary_pixels=im_shapes_boundaries[0][shapeid] )
			if len(split_shapes) == 0:
				didnt_match_im1shapeids.add(shapeid)
				continue

			# update shapes
			crud_shapes.delete_shapeids( {shapeid}, im_shapes[0], im_shapes_boundaries[0], im_shapes_nbrs[0], im_xy_shapeids_by_p[0], im_shapes_colors[0] )
			logging.info("shapeid" + str(shapeid) + " is deleted from " + directory + image_fname + " in script " + script_path  )
			
			created_shapeids = crud_shapes.create_shapeids( split_shapes, im_shapes[0], im_shapes_boundaries[0], im_shapes_nbrs[0], im_xy_shapeids_by_p[0], im_shapes_colors[0], im_rgb_xy_data[0],
															image_size, min_colors )
			logging.info("shapeids" + str(created_shapeids) + " are created for file " + directory + image_fname + " in script " + script_path )
			
			# now perform matching
			for created_shapeid in created_shapeids:
				matched = perform_matching( im_shapes[0][created_shapeid], 0, created_shapeid, done_shapes, message="matched_by_split_shape" )
				if matched is False:
					didnt_match_im1shapeids.add(created_shapeid)
		
		elif im1or2 == 0 and matched == "did_not_try":
			didnt_try_im1shapeids.add(shapeid)
		
	
	
	if im1or2 == 0:
		# prepare matched image2 shapes to match from unmatched image2 shapes 
		for im2shapeid in xy_im2shapes:
			if len( xy_im2shapes[im2shapeid] ) < cv_globals.get_frth_smallest_pixc( image_size):
				continue
			# to search from image2 shapes to image1. get the unmatched image2 shapes
			matched_pixels = xy_im2shapes[im2shapeid].intersection( matched_im2pixels )
			matched_percent = len(matched_pixels) / len( xy_im2shapes[im2shapeid] )
			if matched_percent >= cv_globals.m_threshold:
				matched_im2shapeids.add(im2shapeid)
	
	



pixch_shapes_dir = pixch_dir + "pixch_shapes1/"
pixch_shapes_ddir = pixch_shapes_dir + "data/"
if not os.path.exists(pixch_shapes_ddir):
	os.makedirs(pixch_shapes_ddir)

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "less50.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(less50_results, fp)
fp.close()

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "G50.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(G50_results, fp)
fp.close()

didnt_try_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "didnt_try_im1shapeids.data"
with open(didnt_try_fpath, 'wb') as fp:
   pickle.dump(didnt_try_im1shapeids, fp)
fp.close()

didnt_match_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "didnt_match_im1shapeids.data"
with open(didnt_match_fpath, 'wb') as fp:
   pickle.dump(didnt_match_im1shapeids, fp)
fp.close()


# shapes are modified
with open(shapes_dfile, 'wb') as fp:
   pickle.dump(xy_im1shapes, fp)
fp.close()

with open(im1boundary_fpath, 'wb') as fp:
   pickle.dump(im1shapes_boundaries, fp)
fp.close()

with open(im1snbrs_fpath, 'wb') as fp:
   pickle.dump(im1shapes_nbrs, fp)
fp.close()

with open(im1_xy_shapeids_by_p_fpath, 'wb') as fp:
   pickle.dump(im1_xy_shapeids_by_p, fp)
fp.close()


end = time.time()

elapsed = end - start
print(f"Elapsed time: {elapsed:.4f} seconds")


frequency = 2000  # Set Frequency To 2500 Hertz
duration = 5000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)















