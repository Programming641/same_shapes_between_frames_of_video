'''


'''

import glob, os, sys
from libraries.cv_globals import proj_dir, top_images_dir, top_shapes_dir
import winsound
import traceback


# for user input when directly executing tools/execute_scripts.py
directory = "videos/street3/resized"
exec_scriptname = "algorithms/fundamental/putpix_into_clrgrp.py"
# if execute_script is "putpix_into_clrgrp.py" then, please enter clrgrp_type. choices for clrgrp_type are choices for list of colors data 
# files. 
clrgrp_type = "min1"
# ---------------------------------------------

exec_scriptnames = []
if len( sys.argv ) > 1:
   # executed from outside
   directory = sys.argv[1]
   clrgrp_type = sys.argv[2]
   
   exec_scriptnames = [ "algorithms/fundamental/putpix_into_clrgrp.py", "algorithms/preparation/evaluate_images.py",  "algorithms/fundamental/find_shapes.py", "help_lib/crud_shape_boundaries.py",
                        "help_lib/crud_shape_neighbors.py", "help_lib/create_globals.py" ]

   cur_executing_script = ""
   
   try:
   
      # executing tools/execute_scripts.py
      for exec_scriptname in exec_scriptnames:
         cur_executing_script = exec_scriptname
         
         print("executing algorithm " + exec_scriptname )
      
         if "putpix_into_clrgrp.py" in exec_scriptname:
            sys.argv = [ exec_scriptname , directory, clrgrp_type ]
         else:

            if directory != "" and directory[-1] != '/':
               directory +='/'
            
            if clrgrp_type not in directory:
               directory = directory + clrgrp_type
            
            sys.argv = [ exec_scriptname , directory ]

         with open("tools/execute_scripts.py") as exec_scripts:
            exec(exec_scripts.read())

   except Exception as e:
      tb = sys.exc_info()[2]
      print("error occurred in " + cur_executing_script )
      print( traceback.format_exc() )
         
      sys.exit(1)
      




   
   
frequency = 2000  # Set Frequency To 2500 Hertz
duration = 5000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)


 

































