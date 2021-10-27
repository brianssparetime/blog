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
ap.add_argument('-v', '--verbose', action='store_true', help='show more output')
ap.add_argument('-f', '--force', action='store_true', default=False, help='force regeneration of thumnails even if files already exist')
ap.add_argument('dirs', nargs='*', help='directories to look for images')

args = ap.parse_args()



# place generated thumbnails in this folder (relative to original image)
# webpack really didn't like .imgs here... be warned
# see        https://stackoverflow.com/questions/69471647/vue-nuxt-webpack-resolve-error-on-require-image-file 
tn_dir = 'gen_tn_imgs'

output_format = 'png'

# generate these sizes
img_sizes = {
    'large' : 800,
    'tn' : 200
}

# proess files with these extensions
img_exts = [
    r'\.jpg$',
    r'\.jpeg$',
    r'\.png$'
]

ignore_patterns = [
    r'\sx\\.\w+$',
    r'^x\s+'
]

# for use if none specified in args
target_dirs = [
    'content'
]
if args.dirs:
    if len(args.dirs) == 1:
        target_dirs = (args.dirs)
    else:
        target_dirs = args.dirs


exts_re = '(?:' + '|'.join(img_exts) + ')' 
ig_re = '(?:' + '|'.join(ignore_patterns) + ')' 

def test_file(f):
    return re.search(exts_re, f, re.I) and not re.search(ig_re, f, re.I)
    # print(f'testing {f}')
    # for ext in img_exts:
    #     if re.search(ext, f, re.I):
    #         print(f"{f} has right extension")
    #         for ig in ignore_patterns:
    #             if re.search(ig, f, re.I):
    #                 print(f"{f} contains ignore pattern")
    #                 return False
    #         return True
    # return False


def process_img(img_name, img_path):
    im = Image.open(os.path.join(img_path,img_name))
    for imgsize in img_sizes:
        # insert imgsize
        newname = re.sub(r'\.(\w+)$',r'_'+imgsize+r'.\1', img_name)
        # split fname and fext
        nfn, nfe = os.path.splitext(newname)
        newname = '.'.join([nfn, output_format])
        outd = os.path.join(img_path,tn_dir)
        if not args.force and os.path.exists(os.path.join(outd,newname)):
            if args.verbose:
                print(f"ignoring existing file: {os.path.join(outd,newname)}")
            continue
        if args.verbose:
            print ('generating {} for {}'.format(
                os.path.join(tn_dir,newname),
                os.path.join(img_path,img_name)
                ))
        w, h = im.size
        if (max(w,h) > img_sizes[imgsize]):
            im.thumbnail((img_sizes[imgsize], img_sizes[imgsize]))
        os.makedirs(outd,exist_ok=True)
        im.save(os.path.join(outd,newname),  format=output_format)


for td in target_dirs:
    tdq = os.path.join(os.getcwd(),td)
    if not tdq.startswith(os.getcwd()):
        print("AWOL!")
        sys.exit()
    print(f'Examining {td} at {tdq}')
    for root, dirs, files in os.walk(tdq):
        # do not breathe our own farts and make tns for tns in the tn_dir
        if re.search(tn_dir+'$',root):
            print(f"ignoring {root}")
            continue
        imgs = [ f for f in files if  test_file(f)]
        for img in imgs:
            process_img(img,root)
