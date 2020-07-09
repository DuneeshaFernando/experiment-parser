import os
import shutil


def create_directory(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


def delete_files(path, file_name):
    for (dirpath, dirnames, filenames) in os.walk(path):
        if file_name in filenames:
            os.remove(dirpath+'/'+file_name)


def delete_directories(path, directory_name):
    for (dirpath, dirnames, filenames) in os.walk(path):
        if directory_name in dirnames:
            shutil.rmtree(dirpath+'/'+directory_name)
