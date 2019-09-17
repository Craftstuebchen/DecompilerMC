import glob
import json
import os

from completer import askCompleter
from fileprovider import FileProvider
from mojang_data_fetcher import MojangDataFetcher
from mojang_version_checker import MojangVersionChecker
from remapper import Remapper


def complete(text, state):
    return (glob.glob(os.path.expanduser(text)+'*') + [None])[state]


if __name__ == "__main__":

    version_checker = MojangVersionChecker()
    data_fetcher = MojangDataFetcher(version_checker)

    completer = askCompleter(data_fetcher.get_available_versions())

    latest_snapshot = data_fetcher.get_latest_version("snapshot")
    latest_release = data_fetcher.get_latest_version("release")
    print(f"snapshot: {latest_snapshot}")
    print(f"release: {latest_release}")

    version = completer.ask("Which version do you choose? ")
    print(version)
    exit(0)

    file_provider = FileProvider("./lib")

    remapper = Remapper(file_provider)

    print("Please Run once the snapshot/version on your computer via Minecraft Launcher so it can download it")
    decompiler = input("Please input you decompiler choice: fernflower or cfr (default: fernflower)")
    decompiler = decompiler if decompiler in ["fernflower", "cfr"] else "cfr"
    version = input("Please input a valid version starting from 19w36a : ") or "19w36a"
    decompVersion = remapper.make_paths(version)
    r = input('Download mappings? (y/n): ')
    if r == 'y':
        remapper.get_mappings(version, "client")
        remapper.get_mappings(version, "server")

    r = input('Remap mappings to tsrg? (y/n): ')
    if r == 'y':
        remapper.re_map_mapping(version, "client")
        remapper.re_map_mapping(version, "server")

    r = input('Remap? (y/n): ')
    if r == 'y':
        remapper.remap(version, "client")
    r = input('Decompile? (y/n): ')
    if r == 'y':
        if decompiler == "cfr":
            remapper.decompile_cfr(decompVersion, version)
        else:
            remapper.decompile_fern(decompVersion, version)
    print("===FINISHED===")
    input("Press Enter key to exit")
