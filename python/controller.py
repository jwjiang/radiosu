__author__ = 'jwjiang'

import login
import updates
import info
import sys
import os
import glob
import shutil


def main():
    base_url = "https://osu.ppy.sh/d/"

    link_list = updates.getupdates()
    if count is None:
        meta_list = info.getinfo(link_list)
    else:
        meta_list = info.getinfo(link_list, count)

    current_path = os.path.abspath(os.getcwd())
    zips_path = ''.join([current_path, '/../holding/'])
    songs_path = ''.join([current_path, '/../Songs/'])
    if not os.path.exists(zips_path):
        os.mkdir(zips_path)
    if not os.path.exists(songs_path):
        os.mkdir(songs_path)
    session = login.WebLogin(username, password)

    download_count = 0
    total = len(meta_list)
    print('total = ' + str(total))
    for x in range(total):
        download_url = ''.join([base_url, link_list[x]])
        data = session.download(download_url)
        if data is None:
            total -= 1
            continue

        name = sanitize_name(meta_list[x][0])
        download(zips_path, name, data)
        manipulate_files(zips_path, songs_path, name, meta_list[x])

        progress = ''.join([str(x+1),'/', str(total)])
        print(''.join([name, '.mp3 saved, ', progress]))

        download_count += 1
        # re-auth every 100 downloads
        # if download_count % 100 == 0:
        #    session = login.WebLogin(username, password)

    print(''.join([str(total), ' songs saved to ', songs_path]))

def sanitize_name(name):
    name = name.replace('/', '-')
    name = name.replace('$', 's')
    return name

def download(zips_path, name, data):
    file_full = os.path.join(zips_path, name + '.zip')
    with open(file_full, 'wb') as beatmap:
        beatmap.write(data)
    return name

def manipulate_files(zips_path, songs_path, name, meta_list_tuple):
    # unzip archive
    os.system(''.join(['unzip ', zips_path, '"', name, '.zip" -d ', zips_path, ' > /dev/null']))

    # remove .mp3 files that are less than 500kb (get rid of sound effects)
    # os.system(''.join(['find ', zips_path, ' -name "*.*3" -size -1500k -delete']))

    # set mp3 metadata and rename
    # os.system(''.join(['mv ', zips_path, '*.*3 ', songs_path, '"', name, '.mp3"']))
    shutil.copy2(find_biggest(zips_path), ''.join([songs_path, name, '.mp3']))
    # os.system(''.join(['mv ', find_biggest(zips_path), ' ', songs_path, '"', name, '.mp3"']))
    info.setinfo(''.join([songs_path, name, '.mp3']), meta_list_tuple)

    # delete all other files
    os.system(''.join(['rm -r -f ', zips_path, '*']))

def find_biggest(zips_path):
    biggest = max(glob.iglob(''.join([zips_path, '*[Mm][Pp]3'])), key=os.path.getsize)
    return biggest

if __name__ == "__main__":
    args = sys.argv

    # check for username and password
    if len(args) > 4:
        print "Incorrect number of arguments"
        print "Argument pattern: username password (number of songs to download)"
        exit(1)
    elif len(args) == 4:
        username = args[1]
        password = args[2]
        count = int(args[3])
    elif len(args) == 3:
        username = args[1]
        password = args[2]
        count = None
    else:
        print "Incorrect number of arguments"
        print "Argument pattern: username password (number of songs to download)"
        exit(1)
    main()