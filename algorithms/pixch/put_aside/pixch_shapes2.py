
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

image_fname = "25"
image2_fname = "26"
directory = "videos/street3/resized/min1/"

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

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

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

im1shape_nbrs_dfile = top_shapes_dir + directory + "shapes/shape_nbrs/" + image_fname + "_xy_shape_nbrs.data"
with open (im1shape_nbrs_dfile, 'rb') as fp:
   # { "shapeid": { neighbor xy shapeids }, ... }
   im1_xy_shape_nbrs = pickle.load(fp)
fp.close()

im2shape_nbrs_dfile = top_shapes_dir + directory + "shapes/shape_nbrs/" + image2_fname + "_shape_nbrs.data"
with open (im2shape_nbrs_dfile, 'rb') as fp:
   # { "shapeid": [ pixel indexes ], ... }
   im2shape_nbrs = pickle.load(fp)
fp.close()


im1shapes_colors_dfile = top_shapes_dir + directory + "shapes/shapes_colors/" + image_fname + "xy.data"
with open (im1shapes_colors_dfile, 'rb') as fp:
   im1_xy_shapes_colors = pickle.load(fp)
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

# { (x,y), ... }  contains pixel changes between image1 and image2.
cur_pixch = eachf_pixch[ image_fname + '.' + image2_fname ]


image1 = Image.open(top_images_dir + directory + image_fname + ".png")
image_size = image1.size

shapes_pixch_percentages = { (0, 0.2 ) : [ [], [] ], ( 0.2, 0.4 ): [ [], [] ],  (0.4, 0.55 ):  [ [], [] ], (0.55, 1 ): [ [], [] ] } # keys are percentages. less than 20%. less than 40%..... 

im_shapes = [ xy_im1shapes, xy_im2shapes ]

for im1or2 in range(2):
	for shapeid in im_shapes[im1or2]:
		if len( im_shapes[im1or2][shapeid] ) < cv_globals.get_frth_smallest_pixc( image_size):
			continue
		
		cur_s_pixch_ovlp = im_shapes[im1or2][shapeid].intersection(cur_pixch)
		cur_s_pixch_percent = len(cur_s_pixch_ovlp) / len( im_shapes[im1or2][shapeid] )
		
		for percent in shapes_pixch_percentages:
			if cur_s_pixch_percent >= percent[0] and cur_s_pixch_percent < percent[1]:
				shapes_pixch_percentages[percent][im1or2].append( (shapeid, cur_s_pixch_ovlp ) )


pixch_shapes_dir = pixch_dir + "pixch_shapes2/"

matched_shapes = {}   # { shape pixch percentage: [ matches ], ... }
for pixch_percent in shapes_pixch_percentages:

	matched_shapes[pixch_percent] = []

	for pixch_im1shapes in shapes_pixch_percentages[ pixch_percent ][0]:
		#   (shapeid, pixch )
		im1shapeid = pixch_im1shapes[0]
		im1shape_pixels = xy_im1shapes[im1shapeid]
		shape_pixch = pixch_im1shapes[1]
		
		m_pixels, m_mv, m_nbr_mv_groups = same_shapes_functions.match_pixch_shape2( im1shape_pixels, shape_pixch, cur_pixch, im1_rgb_xy_data, im2_rgb_xy_data, image_size, min_colors  )
		if len(m_pixels) == 0:
			continue
		
		matched_shapes[pixch_percent].append( (im1shape_pixels, m_pixels, m_mv, m_nbr_mv_groups ) )


# check if image1 multiple shapes are matching the same im2shape. that would be wrong.
contradict_shapes = {}
for pixch_percent in matched_shapes:
	for m_index, match in enumerate( matched_shapes[pixch_percent] ):
		for m_pixel in match[1]:
			
			if contradict_shapes.get(m_pixel) is None:
				contradict_shapes[m_pixel] = { (pixch_percent, m_index) }
			else:
				contradict_shapes[m_pixel].add( (pixch_percent, m_index) )


print("contradict_shapes")
duplicates = []
distinct_contraS = []
for m_pixel in contradict_shapes:
	if len(contradict_shapes[m_pixel] ) >= 2 and contradict_shapes[m_pixel] not in duplicates:
		distinct_contraS.append( contradict_shapes[m_pixel] )
		
		duplicates.append( contradict_shapes[m_pixel] )



pixch_shapes_ddir = pixch_shapes_dir + "data/"
if not os.path.exists(pixch_shapes_ddir):
	os.makedirs(pixch_shapes_ddir)

matched_shapes_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "matched_shapes.data"
with open(matched_shapes_fpath, 'wb') as fp:
   pickle.dump(matched_shapes, fp)
fp.close()

distinct_contraS_fpath = pixch_shapes_ddir + image_fname + '.' + image2_fname + "distinct_contraS.data"
with open(distinct_contraS_fpath, 'wb') as fp:
   pickle.dump(distinct_contraS, fp)
fp.close()















