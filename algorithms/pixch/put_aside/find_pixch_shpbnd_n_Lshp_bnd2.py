# find matches between pixel change shape boundaries and large shape boundaries
# this sees if pixel change matched with image1 shape boundaries also matches with image2 shape boundaries.

from PIL import Image
import re, pickle

import os, sys
from libraries.cv_globals import proj_dir, top_shapes_dir, top_images_dir
from libraries import read_files_functions, pixel_shapes_functions, image_functions

if proj_dir != "" and proj_dir[-1] != "/":
   proj_dir +='/'


directory = "videos/street3/resized/min"
main_filename = "11"
im1file = "10"
im2file = "11"
rest_of_filename = ""
pixch_im_fname = im1file + "." + im2file
shapes_type = "intnl_spixcShp"




if len(sys.argv) > 1:
   im1file = sys.argv[0][0: len( sys.argv[0] ) - 4 ]

   im2file = sys.argv[1][0: len( sys.argv[1] ) - 4 ]
   
   rest_of_filename = sys.argv[2][0: len( sys.argv[2] ) - 4 ]

   directory = sys.argv[3]

   print("execute script " + os.path.basename(__file__) + " im1file " + im1file + " file2 " + im2file + " directory " + directory )




# directory is specified but does not contain /
if directory != "" and directory[-1] != ('/'):
   directory +='/'


pixch_imdir = directory + "pixch/"

pixch_shapes_locations_path = top_shapes_dir + pixch_imdir + "locations/" + pixch_im_fname + "_loc.txt"
pixch_s_locations = read_files_functions.rd_ldict_k_v_l( pixch_im_fname, pixch_imdir, pixch_shapes_locations_path )
# returned value has below form
# shapes[shapes_id][pixel_index] = {}
# shapes[shapes_id][pixel_index]['x'] = x
# shapes[shapes_id][pixel_index]['y'] = y
pixch_shapes = read_files_functions.rd_shapes_file(pixch_im_fname, pixch_imdir)


shapes_boundaries = {}
im2shapes_boundaries = {}
if shapes_type == "normal":
   pixch_bnd_n_Lshp_bnd_dir = top_shapes_dir + directory + "pixch_bnd_n_Lshp_bnd/normal/"

   shapes_locations_path = top_shapes_dir + directory + "locations/" + main_filename + "_loc.txt"


   shapes = read_files_functions.rd_shapes_file(main_filename, directory)
   im2shapes = read_files_functions.rd_shapes_file(im2file, directory)

   # get boundary pixels of all shapes
   for shapeid in shapes:
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(shapes[shapeid] )
   for shapeid in im2shapes:
      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(im2shapes[shapeid] )

elif shapes_type == "intnl_spixcShp":
   pixch_bnd_n_Lshp_bnd_dir = top_shapes_dir + directory + "pixch_bnd_n_Lshp_bnd/intnl_spixcShp/"

   s_pixcShp_intnl_dir = top_shapes_dir + directory + "s_pixc_shapes/" + "internal/"
   s_pixcShp_intnl_loc_dir = s_pixcShp_intnl_dir + "locations/"   
   shapes_locations_path = s_pixcShp_intnl_loc_dir + filename1 + "_loc.txt"   

   shapes_dir = s_pixcShp_intnl_dir + "shapes/"


   shapes_dfile = shapes_dir + filename1 + "shapes.data"
   im2shapes_dfile = shapes_dir + filename2 + "shapes.data"

   with open (shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      shapes = pickle.load(fp)
   fp.close()

   with open (im2shapes_dfile, 'rb') as fp:
      # { '79999': ['79999', ... ], ... }
      # { 'shapeid': [ pixel indexes ], ... }
      im2shapes = pickle.load(fp)
   fp.close()      

   # get boundary pixels of all shapes
   for shapeid, pindexes in shapes.items():
      cur_shape_pixels = { }
      for pindex in pindexes:
         cur_shape_pixels[pindex] = {}
            
         y = math.floor( int(pindex) / im_width)
         x  = int(pindex) % im_width 
      
         cur_shape_pixels[pindex]['x'] = x
         cur_shape_pixels[pindex]['y'] = y

      # {1: {'x': 190, 'y': 30}, 2: {'x': 190, 'y': 31},.... }
      shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels )


   # get boundary pixels of all shapes
   for shapeid, pindexes in shapes.items():
      cur_shape_pixels = { }
      for pindex in pindexes:
         cur_shape_pixels[pindex] = {}
            
         y = math.floor( int(pindex) / im_width)
         x  = int(pindex) % im_width 
      
         cur_shape_pixels[pindex]['x'] = x
         cur_shape_pixels[pindex]['y'] = y

      # {1: {'x': 190, 'y': 30}, 2: {'x': 190, 'y': 31},.... }
      im2shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(cur_shape_pixels )


else:
   print("ERROR at " +  os.path.basename(__file__) + " shapes_type " + shapes_type + " is not supported")
   sys.exit()


s_locations = read_files_functions.rd_ldict_k_v_l( main_filename, directory, shapes_locations_path )

pixch_bnd_n_Lshp_bnd_ddir = pixch_bnd_n_Lshp_bnd_dir + "data/"
pixch_bnd_n_Lshp_bnd_file = "pixch" + im1file + "." + im2file + "Lshp" + main_filename + ".data"
matched_im1and2_fname = im1file + "." + im2file + ".data"

if os.path.exists(pixch_bnd_n_Lshp_bnd_dir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_dir )
if os.path.exists(pixch_bnd_n_Lshp_bnd_ddir ) == False:
   os.makedirs(pixch_bnd_n_Lshp_bnd_ddir )



shapes_in_im_areas = {}
for shapeid in shapes:
   
   for s_locs in s_locations:
      if shapeid in s_locs.keys():
         shapes_in_im_areas[shapeid] = s_locs[ list(s_locs.keys())[0] ]
         break
pixch_shapes_in_im_areas = {}
for shapeid in pixch_shapes:
   
   for s_locs in pixch_s_locations:
      if shapeid in s_locs.keys():
         pixch_shapes_in_im_areas[shapeid] = s_locs[ list(s_locs.keys())[0] ]
         break




pixch_shapes_boundaries = {}
# get boundary pixels of all shapes
for shapeid in pixch_shapes:
   pixch_shapes_boundaries[shapeid] = pixel_shapes_functions.get_boundary_pixels(pixch_shapes[shapeid] )




mainim_stats = image_functions.get_image_stats( main_filename, directory, shapes_type=shapes_type )
# [(6267, ['69738', ... ]),... ]   [ ( pixel counts, [ list of shapes that have this pixel count ] ), ... ]
# list is ordered by descending pixel counts 
mainim_stats = sorted(mainim_stats.items(), reverse=True)

pixch_matches = {}
for pcount_shapes in mainim_stats:
   
   # looping list of shapes for each pixel counts
   for shapeid in pcount_shapes[1]:
      print("shapeid " + shapeid )

      # getting all current shape's pixels
      # {'69738': {'x': 158, 'y': 196}, '69737': {'x': 157, 'y': 196},... }
      cur_shp_pixels = shapes[ shapeid ]

      
      if len( cur_shp_pixels ) < 50:
         continue

      pixch_matches[ shapeid ] = {}
      
      # getting all current shape's boundary pixels
      # {1: {'x': 190, 'y': 30}, 2: {'x': 190, 'y': 31},.... }
      cur_shp_bnd_pixels = shapes_boundaries[ shapeid ].values()

      # check if current shape boundaries and any of the pixel change shapes boundaries match
      # checking all pixel change shapes
      for pixch_shapeid in pixch_shapes_boundaries:
         
         
         same_area = any(item in shapes_in_im_areas[shapeid] for item in pixch_shapes_in_im_areas[pixch_shapeid])
      
         if not same_area:
            # skip this pixel change shape because it is not in any of the same image areas as current shape
            continue

         pixch_matches[shapeid][pixch_shapeid] = []

         for pixch_pixel in pixch_shapes_boundaries[pixch_shapeid].values():
            if pixch_pixel in cur_shp_bnd_pixels:
               # current pixel change shape's boundary pixel found in main shape's boundary pixels
               pixch_matches[ shapeid ][pixch_shapeid].append( pixch_pixel )
            
         if len( pixch_matches[shapeid][pixch_shapeid] ) == 0:
            pixch_matches[shapeid].pop( pixch_shapeid )

      if len( pixch_matches[shapeid] ) == 0:
         pixch_matches.pop( shapeid )


# now that I have pixel change shape's boundary pixel matches with large normal shape, check to see if image2 large shape's boundaries
# have matchs with pixel change shapes boundaries.
# pixch_matches form below
# {"image shapeid": {"pixel change shapeid": [ list of matched boundary pixels ], "pixel change shapeid": [ list of matched boundary pixels ], ... }, ... }
im1and2_matches = {}
# im1and2_matches => { "main image shapeid": [ "image2 shapeid", "pixel change shapeid", [ matched pixel change shape's pixels ]  ]
for im_shapeid, pixch_shape in pixch_matches.items():
   im1and2_matches[ im_shapeid ] = []

   print("im_shapeid " + im_shapeid )

   # image2 shapeid found counter for current pixch_shapeid 
   cur_match_counter = 0
   for im2shapeid in im2shapes_boundaries:
      # getting all current shape's boundary pixels
      # {1: {'x': 190, 'y': 30}, 2: {'x': 190, 'y': 31},.... }
      cur_shp_pixels = im2shapes_boundaries[ im2shapeid ].values()
      if len( cur_shp_pixels ) < 50:
         continue
      
      for pixch_shapeid in pixch_shape:
            
         cur_pixch_shapeid_found = False
   
         for pixch_pixel in pixch_shapes_boundaries[pixch_shapeid].values():   
         
            if pixch_pixel in cur_shp_pixels:
               if not cur_pixch_shapeid_found:
                  im1and2_matches[ im_shapeid ].append( [] )
                  im1and2_matches[ im_shapeid ][ cur_match_counter ].append( im2shapeid )
                  im1and2_matches[ im_shapeid ][ cur_match_counter ].append( pixch_shapeid )
                  im1and2_matches[ im_shapeid ][ cur_match_counter ].append( [ pixch_pixel ] )
                  
                  cur_pixch_shapeid_found = True
               else:
                  im1and2_matches[ im_shapeid ][ cur_match_counter ][2].append( pixch_pixel )

         # finished current im2shapeid with current pixch_shapeid
         if cur_pixch_shapeid_found:
            cur_match_counter += 1
            

   # finished looping current im_shapeid
   if len( im1and2_matches[ im_shapeid ] ) == 0:
      im1and2_matches.pop( im_shapeid )


with open(pixch_bnd_n_Lshp_bnd_ddir + pixch_bnd_n_Lshp_bnd_file, 'wb') as fp:
   pickle.dump(pixch_matches, fp)
fp.close()

with open(pixch_bnd_n_Lshp_bnd_ddir + matched_im1and2_fname, 'wb') as fp:
   pickle.dump(im1and2_matches, fp)
fp.close()













