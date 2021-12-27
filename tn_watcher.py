#!/opt/local/bin/python3.9

import os
import re
from PIL import Image
import argparse
import sys
import datetime, time
import logging
import sys
import time
import pickle
import hashlib

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from multiprocessing import Manager



# https://stackoverflow.com/questions/8631076/what-is-the-fastest-way-to-generate-image-thumbnails-in-python

# place generated thumbnails in this folder (relative to original image)
# webpack really didn't like .imgs here... be warned
# see        https://stackoverflow.com/questions/69471647/vue-nuxt-webpack-resolve-error-on-require-image-file 
tn_dir = 'gen_tn_imgs'
output_format = 'png'
saved_state_file = 'tn_watcher.state'

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
    r'^x\s+',
    r'unused\\.\w+$',
]

# for use if none specified in args
target_dirs = [
    'content'
]



exts_re = '(?:' + '|'.join(img_exts) + ')' 
ig_re = '(?:' + '|'.join(ignore_patterns) + ')' 

# # https://stackoverflow.com/a/4213255/16594351 - see for new pythons 
# def md5sum(file):
#     md5 = hashlib.md5()
#     with open(file,'rb') as f:
#         for chunk in iter(lambda: f.read(128*md5.block_size),b''):
#             md5.update(chunk)
#     return md5.hexdigest()

# def update_hash(file, file_hash):
#     file_hash[md5sum(file)] = {
#         'mtime' : datetime.datetime.now(),
#         'name' : file
#     }


def get_tn_fname(fn, imgsize):
    newname = re.sub(r'\.(\w+?)$', r'_'+imgsize, fn)
    return  '.'.join([newname, output_format])


def process_img(params):
    img_name, img_path, bForce = params
    im = Image.open(os.path.join(img_path,img_name))
    for imgsize in img_sizes:
        # insert imgsize
        newname = get_tn_fname(img_name, imgsize)
        # split fname and fext
        outd = os.path.join(img_path,tn_dir)

        # skip existing
        if not bForce and os.path.exists(os.path.join(outd,newname)):
            continue

        print('  generating {} for {}'.format(
                os.path.join(tn_dir,newname),
                os.path.join(img_path,img_name)
                ))
        w, h = im.size
        if (max(w,h) > img_sizes[imgsize]):
            im.thumbnail((img_sizes[imgsize], img_sizes[imgsize]))
        os.makedirs(outd,exist_ok=True)
        #im.save(os.path.join(outd,newname),  format=output_format)
        #im.save(os.path.join(outd,newname),  format=output_format, optimize=True, quality=90)
        im.save(os.path.join(outd,newname),  format=output_format, quality=85)
    im.close()



def test_file(root,f):
    if not re.search(exts_re, f, re.I) or re.search(ig_re, f, re.I):
        return False

    # do not breathe our own farts and make tns for tns in the tn_dir
    if re.search(tn_dir+'$',root):
        return False

    # skip folders without markdown
    if not os.path.exists(os.path.join(root, 'index.md')):
        return False

    # ignore images not referenced in markdown
    text = []
    with open(os.path.join(root, 'index.md'), 'r') as fd:
        text = fd.read()
        # strip html comments
        text = re.sub(r'(?=<!--)([\s\S]*?)-->', '',text)
        # https://stackoverflow.com/questions/1084741/regexp-to-strip-html-comments
        if f not in text:
            return False
    return True

def crawl():
    print("starting crawl...")
    imgs = []
    tdq = os.path.join(os.getcwd(),args.target)

    if not tdq.startswith(os.getcwd()):
        print("AWOL!")
        sys.exit()
    print(f'Examining target {args.target} at {tdq}')

    for root, dirs, files in os.walk(tdq):
            for f in files:
                if test_file(root,f):
                        imgs.append([f, root, args.rebuild_force])
                        #update_hash(f, file_hash)

    # TODO: consider replacing with non MP version so update_hash can happen
    #       after successful completion
    
    from multiprocessing import Pool 
    multi_pool = 8
    print("using pool with {mult_pool} workers")
    with Pool(multi_pool) as pool:
        results = pool.map(process_img, imgs)
        pool.close()
        pool.join()

    #save_out(file_hash, name=saved_state_file)


# def save_out(obj, name):
#     with open(name+'.db', 'wb') as f:
#         pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        
# def load_in(name):
#     filename = name+'.pkl'
#     if os.path.isfile(filename):
#         with open(filename, 'rb') as f:
#             return pickle.load(f)
#     else: 
#         print("saved state {} not found".format(filename))
#         return None



class Watcher(FileSystemEventHandler):

    def catch_all_handler(self, event):
        logging.debug(event)

    def on_moved(self, event):
        self.catch_all_handler(event)
        self.on_deleted(event)
        self.on_created(event)

    def on_created(self, event):
        self.catch_all_handler(event)
        f,root = os.path.split(event.src_path)
        if test_file(f,root):
            process_img([f,root, True])

    def on_deleted(self, event):
        self.catch_all_handler(event)
        for s in img_sizes:
            newname = get_tn_fname(event.src_path, s)
            #os.remove(newname)
            logging.debug("  deleted: {}".format(newname))

    def on_modified(self, event):
        self.catch_all_handler(event)
        f,root = os.path.split(event.src_path)
        if test_file(f,root):
            process_img([f,root, True])

    # TODO:  check for md changes and remove unused tns






if __name__ == '__main__':

    # generate thumbnails for images
    print("tn_watcher starting...")


    # this is invoked manually when running locally, and by Netlify's 
    # build command "python3 gen_tn.py && nuxt build && nuxt generate"

    ap = argparse.ArgumentParser()
    ap.add_argument('-v', '--verbose', action='store_true', help='show more output')
    ap.add_argument('-b', '--rebuild', action='store_true', help='rebuild all existing tns')
    ap.add_argument('-f', '--rebuild-force', action='store_true', help='rebuild all existing tns, overwriting, and quit')
    ap.add_argument('-o', '--rebuild-only', action='store_true', help='rebuild all existing tns and quit')
    #ap.add_argument('dirs', nargs='*', help='directories to look for images')
    ap.add_argument('target', help="directory to watch for changed files")

    args = ap.parse_args()


    """
    manager = Manager()
    fh = load_in(saved_state_file)
    file_hash = manager.dict()
    if not fh:
        crawl(file_hash)
    else:
        for k,v in fh:
            file_hash[k] = v
    """


    if args.rebuild or args.rebuild_only or args.rebuild_force:
        print("Rebuilding tns via crawl....")
        crawl()


    if args.rebuild_only or args.rebuild_force:
        sys.exit()

    print("Starting watcher....")
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, args.target, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        # save_out(file_hash, name=saved_state_file)
    observer.join()