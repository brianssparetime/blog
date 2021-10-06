#!/usr/bin/env python3

import os
import re
from PIL import Image
import argparse
import sys

# generate thumbnails for images

# this is invoked manually when running locally, and by Netlify's 
# build command "python3 gen_tn.py && nuxt build && nuxt generate"

ap = argparse.ArgumentParser()
ap.add_argument('dirs', nargs='*', )

args = ap.parse_args()



# place generated thumbnails in this folder (relative to original image)
tn_dir = '.imgs'

# generate these sizes
img_sizes = {
    'large' : 1024,
    'tn' : 256
}

# proess files with these extensions
img_exts = [
    r'\.jpg',
    r'\.jpeg'
]

ignore_patterns = [
    r'\sx$'
]

target_dirs = [
    'content'
]

exts_re = '(?:' + '|'.join(img_exts) + ')$' 
ig_re = '(?:' + '|'.join(ignore_patterns) + ')\.w+$' 

def test_file(f):
    return re.search(exts_re, f, re.I) and not re.search(ig_re, f, re.I)


def process_img(img_name, img_path):
    im = Image.open(os.path.join(img_path,img_name))
    for imgsize in img_sizes:
        max_dim = img_sizes[imgsize]
        im.thumbnail((max_dim,max_dim))
        newname = re.sub(r'\.(\w+)$',r'_'+imgsize+r'.\1', img_name)
        outd = os.path.join(img_path,tn_dir)
        os.makedirs(outd,exist_ok=True)
        im.save(os.path.join(outd,newname))


if args.dirs:
    if len(args.dirs) == 1:
        target_dirs = (args.dirs)
    else:
        target_dirs = args.dirs

print(args.dirs)
print(target_dirs)

for td in target_dirs:
    tdq = os.path.join(os.getcwd(),td)
    if not tdq.startswith(os.getcwd()):
        print("AWOL")
        sys.exit()
    print(f'Examining {td} at {tdq}')
    for root, dirs, files in os.walk(tdq):
        imgs = [ f for f in files if  test_file(f)]
        for img in imgs:
            print ('generating for {}'.format(os.path.join(root,img)))
            process_img(img,root)
