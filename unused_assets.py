#!/usr/bin/env python3

import os
import re
import argparse
import sys
import datetime, time

timings = []
timings.append(datetime.datetime.now())

unused_name = 'unused'
exts = []

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)



# proess files with these extensions
img_exts = [
    r'\.jpg$',
    r'\.jpeg$',
    r'\.png$'
    r'\.mov$'
    r'\.mp4$'
]

ignore_patterns = [
    r'\sx\\.\w+$',
    r'^x\s+'
]

# for use if none specified in args
target_dirs = [
    'content'
]

tn_dir = 'gen_tn_imgs'

exts_re = '(?:' + '|'.join(img_exts) + ')' 
ig_re = '(?:' + '|'.join(ignore_patterns) + ')' 



if __name__ == '__main__':

    print("starting...")

    ap = argparse.ArgumentParser()
    #ap.add_argument('-v', '--verbose', action='store_true', help='show more output')
    #ap.add_argument('-f', '--force', action='store_true', default=False, 
    #    help='force regeneration of thumnails even if files already exist')
    ap.add_argument('--rename', action='store_true', default=False, 
        help='rename unused assets with .unused before extension')
    ap.add_argument('dirs', nargs='*', help='directories to look for images')
    args = ap.parse_args()

    if args.dirs:
        if len(args.dirs) == 1:
            target_dirs = (args.dirs)
        else:
            target_dirs = args.dirs 

    def test_file(f):
        return re.search(exts_re, f, re.I) # and not re.search(ig_re, f, re.I)
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




    imgs = []
    for td in target_dirs:
        tdq = os.path.join(os.getcwd(),td)
        if not tdq.startswith(os.getcwd()):
            print("AWOL!")
            sys.exit()
        print(f'Examining target {td} at {tdq}')

        for root, dirs, files in os.walk(tdq):
            # do not breathe our own farts and make tns for tns in the tn_dir
            if re.search(tn_dir+'$',root):
                continue

            text = []
            if not os.path.exists(os.path.join(root, 'index.md')):
                print(f"skipping {root} for lacking index.md")
                continue

            with open(os.path.join(root, 'index.md'), 'r') as fd:
                text = fd.read()
                # strip html comments
                text = re.sub(r'(?=<!--)([\s\S]*?)-->', '',text)
                # https://stackoverflow.com/questions/1084741/regexp-to-strip-html-comments
                #print(text)

            for f in files:
                if test_file(f):
                    if f not in text:
                        print("Unused asset: {}".format(os.path.join(root,f)))
                        if args.rename:
                            old_name = os.path.join(root,f)
                            (base, ext) = os.path.splitext(f)
                            if ext not in exts:
                                exts.append(ext)
                            new_name = ''.join([base,'.',unused_name,ext])
                            print("newname: {}".format(new_name))
                            new_name = os.path.join(root,new_name)
                            os.rename(old_name,new_name)

    print("saw extensions:  {}".format(exts))
    