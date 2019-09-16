import glob
import os

from fileprovider import FileProvider
from remapper import Remapper


def complete(text, state):
    return (glob.glob(os.path.expanduser(text)+'*') + [None])[state]


if __name__ == "__main__":
    minecraft_home = "~/Library/Application Support/minecraft"

    file_provider = FileProvider("./lib")

    remapper = Remapper(file_provider)

    print("Please Run once the snapshot/version on your computer via Minecraft Launcher so it can download it")
    decompiler = input("Please input you decompiler choice: fernflower or cfr (default: cfr)")
    decompiler = decompiler if decompiler in ["fernflower", "cfr"] else "cfr"
    version = input("Please input a valid version starting from 19w36a : ") or "19w36a"
    decompVersion = remapper.make_paths(version)
    r = input('Download mappings? (y/n): ')
    if r == 'y':
        remapper.get_mappings(version)

    r = input('Remap mappings to tsrg? (y/n): ')
    if r == 'y':
        remapper.re_map_mapping(version)

    r = input('Remap? (y/n): ')
    if r == 'y':
        remapper.remap(version)
    r = input('Decompile? (y/n): ')
    if r == 'y':
        if decompiler == "cfr":
            remapper.decompile_cfr(decompVersion, version)
        else:
            remapper.decompile_fern(decompVersion, version)
    print("===FINISHED===")
    input("Press Enter key to exit")
