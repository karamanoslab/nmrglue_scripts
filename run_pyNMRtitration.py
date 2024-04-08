from pyNMRtitration import NmrEditor
from glob import glob

#this script can be run from any directory as long as the directory nmrglue_scripts is in your PYTHONPATH
#Adjust the path dirs and input text files, make sure the scale is set to ppm of hz appropriately

dpath='./titr'
dirs=['1', '3', '6', '9']
specs=['%s/%s/test.ft2' %(dpath, dir) for dir in dirs]
#inp=['./138.N_test.txt']
inp=glob('%s/txt/*.txt'%dpath)

for i in inp: 
    nmr_editor = NmrEditor(i, specs, scale='ppm')
