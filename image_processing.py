from multiprocessing import Process, Pool
from PIL import Image
import glob
import dhash
import os





def run(folders=None):
    pool.map(cleanup, folders)



def cleanup(folder=['.']):
    l_of_f = list()
    hashes = dict()
    k = list()

    if folder:
        print(f"called cleanup...{folder}")
        l_of_f = get_list_of_files(folder)
    else:
        print(f"called cleanup...{folder}")
        l_of_f = get_list_of_files(folder)

    print(f"generating histogram of {len(l_of_f)} images in {folder}")
    hashes = generate_histogram_of_images(l_of_f)

    print(f"getting {len(hashes.keys())} keys from hash in {folder}")
    k = [(len(hashes[i]), i) for i in hashes.keys()]
    
    print(f"deleting duplicates in {folder}")
    delete_duplicates(hashes)

    try:
        print(f"unique image ratio in {folder}: {len(k)/len(l_of_f)}")
    except ZeroDivisionError:
        print("unique image ratio is {folder}: ZeroDivisionEror")
    
    try:
        return len(k)/len(l_of_f)
    except ZeroDivisionError:
        return 0


def process_img(img):
    img = Image.open(img)
    row, col = dhash.dhash_row_col(img, size=8)
    return dhash.format_hex(row, col)


def get_list_of_files(folder='./', format="*.jpg"):
    if folder:
        return glob.glob(folder + format)
    else:
        return glob.glob(format)


def generate_histogram_of_images(list_of_files):
    known_hashes = dict()
    print(f"starting generate_historgram with {len(list_of_files)} files")
    for l in list_of_files:
        if process_img(l) in known_hashes:
            print(f"generating dhash for {l} is a duplicate")
            known_hashes[process_img(l)].append(l)
        else:
            # print(f"generating dhash for {l} is not a duplicate")
            known_hashes[process_img(l)] = [l]
    return known_hashes


def delete_duplicates(known_hashes):
    k = [(len(known_hashes[i]), i) for i in known_hashes.keys()]
    print(f"called delete_duplicates on a hash with {len(known_hashes.keys())} keys")
    for item in k:
        for i in known_hashes[item[1]][:-1]:
            try:
                print(f"unlinking {i}")
                os.unlink(i)
            except FileNotFoundError:
                # maybe the file was already deleted?
                print(f"tried unlinking {i} but it was already gone")
                pass






if __name__ == '__main__':
    # remember to include a trailing slash
    folders = []
    pool = Pool(8)
    print("starting up...")
    run(folders=folders)
    pool.close()
