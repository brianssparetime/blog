#!/usr/bin/env python3

import os
import re
import argparse
import sys
import datetime, time
import subprocess


# proess files with these extensions
img_exts = [
    r'\.jpg$',
    r'\.jpeg$',
    r'\.png$'
    r'\.mov$'
    r'\.mp4$'
]

# for use if none specified in args
target_dirs = [
    'content'
]

orig_dir = 'original_assets'
tn_dir = 'gen_tn_imgs'

exts_re = '(?:' + '|'.join(img_exts) + ')' 



if __name__ == '__main__':

    print("starting...")

    ap = argparse.ArgumentParser()
    #ap.add_argument('-v', '--verbose', action='store_true', help='show more output')
    #ap.add_argument('-f', '--force', action='store_true', default=False, 
    #    help='force regeneration of thumnails even if files already exist')
    ap.add_argument('--move', action='store_true', default=False, 
        help='move  original assets')
    ap.add_argument('--gitrm', action='store_true', default=False, 
        help='git rm --cached  original assets')
    ap.add_argument('dirs', nargs='*', help='directories to look for images')
    args = ap.parse_args()

    if args.dirs:
        if len(args.dirs) == 1:
            target_dirs = (args.dirs)
        else:
            target_dirs = args.dirs 

    def test_file(f):
        return re.search(exts_re, f, re.I)

    imgs = []
    for td in target_dirs:
        tdq = os.path.join(os.getcwd(),td)
        if not tdq.startswith(os.getcwd()):
            print("AWOL!")
            sys.exit()
        print(f'Examining target {td} at {tdq}')

        for root, dirs, files in os.walk(tdq):
            # stay in bounds
            if re.search(tn_dir+'$',root):
                continue

            for f in files:
                if test_file(f):
                    old_name = os.path.join(root,f)
                    print("oldname: {}".format(old_name))
                    #(base, ext) = os.path.splitext(f)
                    if args.gitrm:
                        _ = subprocess.run(["git", "rm", "--cached", old_name])
                    if args.move:
                        new_name = os.path.join(root,orig_dir,f)
                        print("newname: {}".format(new_name))
                        os.makedirs(os.path.join(root,orig_dir),exist_ok=True)
                        os.rename(old_name,new_name)
