import os

from params.params import Params


def clean_folder(path_out):
    for file in os.listdir(path_out):
        if file.endswith(Params().MP4):
            os.remove(os.path.join(path_out, file))
