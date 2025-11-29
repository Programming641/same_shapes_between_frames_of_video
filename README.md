## operating enviroment
windows 10 or higher
python3
python library dependencies:   pillow


## run sample videos
just simply run ./execute_scripts.ps1

it will ask for image directory. this is the image video directory under the "images" directory.
to use sample video as example. put "videos/giraffe/

then it will ask for quantization of the resolutions. you can pick from choices "min1, min2, min3, clrgrp1, and so on". go with min1.

### how to see result
you can see the result from each script by using recreate_shapes scripts.

for example, to see the result for find_pixch_shapes.py, run pixch_shapes.py in recreate_shapes/pixch/.

just fill replace following data inside pixch_shapes.py for the result you want to see.

```
image_fname = "2"
image2_fname = "3"
directory = "videos/street6/resized/min1"
```

## limitations
* movement is restricted to 22pixels. if shape move beyond 22pxels, behavior is undefined.
* if the video contain undefinable shapes like rain, fluid like object like water and so on, it may not work correctly.
* video is edited. the algorithms is designed to work with natural sequential frames of video.
* video suddenly changes to different scenes. video has to be smooth transitions of movement.

**if the video does not contain limitations, then the accuracy will be about 95 to almost 100%!**
