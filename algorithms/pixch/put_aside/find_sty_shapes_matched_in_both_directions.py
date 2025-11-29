# if most of pixel changes occur near the shape boundaries and not inside the shape, then the shape
# moved only a little
from libraries import pixel_functions, read_files_functions, pixel_shapes_functions

import tkinter
from PIL import ImageTk, Image
import math
import os, sys
import winsound
import pickle
import pathlib

from libraries import btwn_amng_files_functions
from libraries.cv_globals import top_shapes_dir, top_images_dir, frth_smallest_pixc, Lshape_size, internal


directory = "videos/street3/resized/min"
shapes_type = "intnl_spixcShp"


# directory is specified but does not contain /
if directory != "" and directory[-1] != '/':
   directory +='/'


pixch_dir = top_shapes_dir + directory + "pixch/"
pixch_sty_shapes_dir = pixch_dir + "sty_shapes/"


# loop all "sty_shapes" files
data_dir = pathlib.Path(pixch_sty_shapes_dir)


btwn_frames_files = []
for data_file in data_dir.iterdir():
   data_filename = os.path.basename(data_file)
   
   # check if the file has the following form. if so, then the target file is found
   # 10.11.10.data   11.12.11.data and so on.
   filename_split_by_period = data_filename.split(".")
   
   if len( filename_split_by_period ) != 4:
      continue
   
   fst_filename = filename_split_by_period[0]
   scnd_filename = filename_split_by_period[1]
   trd_filename = filename_split_by_period[2]
   data_extension = filename_split_by_period[3]
   
   if not fst_filename.isnumeric() or not scnd_filename.isnumeric() or not trd_filename.isnumeric() or data_extension != "data":
      continue   
   
   btwn_frames_files.append( data_filename )
   

ordered_files = btwn_amng_files_functions.put3btwn_files_in_order( btwn_frames_files )


prev_file = None
for data_file in ordered_files:
   if prev_file is None:
      prev_file = data_file
      continue
   else:
      prev_filename_split_by_period = prev_file.split(".")
      prev_fst_filename = prev_filename_split_by_period[0]
      prev_scnd_filename = prev_filename_split_by_period[1]   
      
      filename_split_by_period = data_file.split(".")

      fst_filename = filename_split_by_period[0]
      scnd_filename = filename_split_by_period[1]

      if prev_fst_filename == fst_filename and prev_scnd_filename == scnd_filename:
         # same file found. example -> 11.12.11  11.12.12
         
         with open (pixch_sty_shapes_dir + prev_file, 'rb') as fp:
            # [('1367', '1366'), ('2072', '2874'), ... ]
            # [ ( matched image1 shapeid , matched image2 shapeid ), ... ]
            prev_pixch_sty_shapes = pickle.load(fp)
         fp.close()     
      
         with open (pixch_sty_shapes_dir + data_file, 'rb') as fp:
            # [('1367', '1366'), ('2072', '2874'), ... ]
            # [ ( matched image1 shapeid , matched image2 shapeid ), ... ]
            pixch_sty_shapes = pickle.load(fp)
         fp.close()
      
         print("prev_file " + prev_file + " current data file " + data_file )
         
         both_directions_matched_shapes = []
         # find shapes that match from both directions
         for prev_shapes in prev_pixch_sty_shapes:
            
            for cur_shapes in pixch_sty_shapes:
               if prev_shapes[0] == cur_shapes[0] and prev_shapes[1] == cur_shapes[1]:
                  both_directions_matched_shapes.append( prev_shapes )
    


         with open(pixch_sty_shapes_dir + fst_filename + "." + scnd_filename + ".data", 'wb') as fp:
            pickle.dump(both_directions_matched_shapes, fp)
         fp.close()         

    
   prev_file = data_file
         
         
         
   














































      
   
   

































