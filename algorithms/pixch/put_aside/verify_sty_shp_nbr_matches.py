
from libraries import pixel_functions, read_files_functions, pixel_shapes_functions, same_shapes_functions

from PIL import Image
import math
import os, sys
import winsound
import pickle

from libraries.cv_globals import top_shapes_dir, top_images_dir, pixch_sty_dir, internal, frth_smallest_pixc, Lshape_size, third_smallest_pixc

im1file = '14'
im2file = "15"
directory = "videos/street3/resized/min"
shapes_type = "intnl_spixcShp"


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'


sty_shapes_nbrs_dir = top_shapes_dir + directory + pixch_sty_dir + "/nbrs/"
sty_shapes_file = sty_shapes_nbrs_dir + "data/" + im1file + "." + im2file + ".data"
with open (sty_shapes_file, 'rb') as fp:
   # [ [ ['28105', '57336'], ['28106', '57343'] ], ... ]
   # [ [ [ image1 shapeid, image1 neighbor ], [ image2 shapeid, image2 neighbor ] ], ... ]
   sty_shapes_nbrs = pickle.load(fp)
fp.close()

nxt_im1 = str( int(im1file) + 1 )
nxt_im2 = str( int(im2file) + 1 )

nxt_sty_shapes_file = sty_shapes_nbrs_dir + "data/" + nxt_im1 + "." + nxt_im2 + ".data"
with open (nxt_sty_shapes_file, 'rb') as fp:
   # [ [ ['28105', '57336'], ['28106', '57343'] ], ... ]
   # [ [ [ image1 shapeid, image1 neighbor ], [ image2 shapeid, image2 neighbor ] ], ... ]
   nxt_sty_shapes_nbrs = pickle.load(fp)
fp.close()

matched_neighbors = []
for each_neighbor in sty_shapes_nbrs:
   cur_neighbors = [each_neighbor]
   found_neighbors = [ temp for temp in nxt_sty_shapes_nbrs if each_neighbor[1][0] == temp[0][0] and each_neighbor[1][1] == temp[0][1] ]
   
   for found_neighbor in found_neighbors:
      cur_neighbors.append( found_neighbor )
   
   if len( cur_neighbors ) > 1:
      matched_neighbors.append( cur_neighbors )



with open(sty_shapes_nbrs_dir + "data/" + im1file + "." + im2file + "verified.data", 'wb') as fp:
   pickle.dump(matched_neighbors, fp)
fp.close()
   





frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)






