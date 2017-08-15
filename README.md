# EBLtool
Python scripts to assist drawing EBL patterns
by Sun Smallwhite (Sun Sibai) <sun.niasw@gmail.com> (<niasw@pku.edu.cn>)
in Institute of Physics, Chinese Academy of Sciences, 2016
MIT license: you can do anything you want with these codes as long as you provide attribution back to me and don’t hold me liable.

-------------
Drawing patterns in old version LEdit is really an awful experience. No background image function, awful griding, poor compatibility and complex operations. But we have no choice, because the owner of Raith150 requires so. Theoretically, EBL pattern only contains vector graphs. As far as I know, [inkscape](https://inkscape.org/en/) is the best open source software to deal with those simple geometric objects accurately. Therefore, I decided to use the user-friendly inkscape to draw my patterns and use these scripts to translate them into LEdit files.

-------------
Dependence:
> python3, inkscape, LEdit, Raith150 (you can change the code to suit your lithography system)
Optional:
> bash

The basic translation process is shown as below:

> 0. Copy drawing.svg to a new filename, resize the initial rectangle as you need.
> 1. Optical/electronic beam microscope image --import--> image object in the new drawing file you just copied.
> 2. Scale and rotate the images at the right position in inkscape (local coordinates), marks in the images may help you align them together. Some advanced microscopes can generate image coordinates, if you are lucky with these microscopes, you can rely on these coordinates instead of marks.
> 3. Draw your patterns. Currently, rectangles, polygons and paths are available. (Since we can see the images showing where marks, samples and maybe bad areas are, we don't need to care about the coordinates of each object anymore.)
> 4. Run patchedges\_svg.py to patch the drawing if your patterns are crossing multple writing fields. (In our lab, we choose the side length of writing field to be 100 um. It is a balance between exposing speed and accuracy. Small writing fields mean high accuracy but low speed, vice versa to the large ones. Since the exposing stops at the edges of the writing fields, some small coordinate errors will cause exposing dose insufficient. So we should draw patches to enhance the exposing time at these edges. The script patchedges\_svg.py can automatically patches all the edges as you set the right coordinate shift.)
> 5. Run svg2tco.py to generate LEdit commands (tco) from the patched vector graph (svg) file, remove 0 width rectangles and repeating commands. (In this step, multiple local areas can be joined together as you give the right global coordinate shifts of the local areas.)
> 6. Open LEdit, load your mark pattern file, choose a new layer, run the command (tco) file. Export as gds file.
> 7. Bring it to the Raith150, set the dose, coat PMMA, pre-bake, load in, operate the machine, set starting point, run expose, load out, develop, fix, post-bake, done!

------------------
Notice:
> 1. The relationship between local coordinates, start points, global coordinates and writing fields are written in comments along with the python codes. Please check them. The parameters you should input are related to these coordinates.
> 2. If you are using unix, linux, iOS or other unix-like system, you can use the bash scripts to make an auto-run. A simple example is shown in run\_test.sh. We are using run\_tco\_270um.sh currently. And run\_tco\_tang.sh is for the chip setup of our elder post-doc named Jing Tang.

Good luck

------------------
