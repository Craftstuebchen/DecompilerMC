import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

from fileprovider import FileProvider


class Remapper:

    def __init__(self, file_provider: FileProvider):
        self.file_provider = file_provider

    def download_file(self, url, filename):
        try:
            print(f'Downloading {filename}...')
            f = urllib.request.urlopen(url)
            with open(filename, 'wb') as local_file:
                local_file.write(f.read())
        except urllib.request.HTTPError as e:
            print('HTTP Error')
            print(e)
        except urllib.request.URLError as e:
            print('URL Error')
            print(e)

    def get_mappings(self, version, minecraft_side):
        if Path(f'mappings/{version}/{minecraft_side}.txt').is_file():
            return
        path_to_json = Path(
            f'{self.file_provider.get_mincraft_folder()}/versions/{version}/{version}.json').expanduser()

        if path_to_json.exists() and path_to_json.is_file():
            print(f'Found {version}.json')
            path_to_json = path_to_json.resolve()

            with open(path_to_json) as f:
                jfile = json.load(f)
                url = jfile['downloads'][f'{minecraft_side}_mappings']['url']

                print(f'Downloading the mappings for {version}...')
                self.download_file(url, f'mappings/{version}/{minecraft_side}.txt')
                print('Done!')
        else:
            print(f'ERROR: Missing files')

    def remap(self, version, minecraft_side):
        print('=== Remapping jar using SpecialSource ====')
        t = time.time()
        path = Path(f'{self.file_provider.get_mincraft_folder()}/versions/{version}/{version}.jar').expanduser() # todo download server jar as well
        mapp = Path(f'mappings/{version}/{minecraft_side}.tsrg')
        specialsource = Path(self.file_provider.get_specialsource())

        if path.exists() and mapp.exists() and specialsource.exists():
            path = path.resolve()
            mapp = mapp.resolve()
            specialsource = specialsource.resolve()
            out = Path(f'./src/{version}-{minecraft_side}-temp.jar').resolve()

            subprocess.run(
                f"java -jar \"{specialsource.__str__()}\" --in-jar \"{path.__str__()}\" --out-jar \"{out.__str__()}\" --srg-in \"{mapp.__str__()}\" --kill-lvt",
                shell=True)

            print(f'- New -> {version}-{minecraft_side}-temp.jar')

            t = time.time() - t
            print('Done in %.1fs' % t)
        else:
            print(f'ERROR: Missing files')

    def decompile_fern(self, decomp_version, version, minecraft_side):
        print('=== Decompiling using FernFlower ====')
        t = time.time()

        path = Path(f'./src/{version}-temp.jar')
        fernflower = Path(self.file_provider.get_fernflower())
        if path.exists() and fernflower.exists():
            path = path.resolve()
            fernflower = fernflower.resolve()

            decomp_dir = Path(f"./src/{decomp_version}").resolve()

            subprocess.run(f"java -jar \"{fernflower.__str__()}\" -hes=0 -hdc=0 -dgs=1 -ren=1 \"{path.__str__()}\" \"{decomp_dir}\"", shell=True)

            print(f'- Removing -> {version}-temp.jar')
            os.remove(f'./src/{version}-temp.jar')

            with zipfile.ZipFile(f'./src/{decomp_version}/{version}-temp.jar') as z:
                z.extractall(path=f'./src/{decomp_version}')
            print(f'- Removing -> {decomp_version}/{version}-temp.jar')
            os.remove(f'./src/{decomp_version}/{version}-temp.jar')
            t = time.time() - t
            print('Done in %.1fs' % t)
        else:
            print(f'ERROR: Missing files')

    def decompile_cfr(self, decompVersion, version):
        print('=== Decompiling using CFR ====')
        t = time.time()

        path = Path(f'./src/{version}-{type}-temp.jar')
        cfr = Path(self.file_provider.get_cfr())
        if path.exists() and cfr.exists():
            path = path.resolve()
            cfr = cfr.resolve()
            out_dir = Path(f"./src/{decompVersion}").resolve()
            subprocess.run(
                f"java -jar \"{cfr.__str__()}\" \"{path.__str__()}\" --outputdir \"{out_dir}\" --caseinsensitivefs true",
                shell=True)

            print(f'- Removing -> {version}-temp.jar')
            print(f'- Removing -> summary.txt')
            os.remove(f'./src/{version}-temp.jar')
            os.remove(f'./src/{decompVersion}/summary.txt')

            t = time.time() - t
            print('Done in %.1fs' % t)
        else:
            print(f'ERROR: Missing files')

    def re_map_mapping(self, version, minecraft_side):
        remap_primitives = {"int": "I", "double": "D", "boolean": "Z", "float": "F", "long": "J", "byte": "B",
                            "short": "S"}
        remap_file_path = lambda path: "L" + "/".join(path.split(".")) + ";" if not (
                path in remap_primitives or path[:-2] in remap_primitives) else remap_primitives[
            path] if not "[]" in path else "[" + remap_primitives[path[:-2]]
        with open(f'mappings/{version}/{minecraft_side}.txt', 'r') as inputFile:
            file_name = {}
            for line in inputFile.readlines():
                if line.startswith('#'):  # comment at the top, could be stripped
                    continue
                deobf_name, obf_name = line.split(' -> ')
                if not line.startswith('    '):
                    obf_name = obf_name.split(":")[0]
                    file_name[remap_file_path(deobf_name)] = obf_name  # save it to compare to put the Lb

        with open(f'mappings/{version}/{minecraft_side}.txt', 'r') as inputFile, open(f'mappings/{version}/{minecraft_side}.tsrg',
                                                                            'w+')  as outputFile:
            for line in inputFile.readlines():
                if line.startswith('#'):  # comment at the top, could be stripped
                    continue
                deobf_name, obf_name = line.split(' -> ')
                if line.startswith('    '):
                    obf_name = obf_name.strip()
                    deobf_name = deobf_name.lstrip()
                    method_type, method_name = deobf_name.split(" ")
                    method_type = method_type.split(":")[-1]  # get rid of the line numbers
                    if "(" in method_name and ")" in method_name:  # function
                        variables = method_name.split('(')[-1].split(')')[0]
                        function_name = method_name.split('(')[0]
                        if method_type == "void":
                            method_type = "V"
                        else:
                            method_type = remap_file_path(method_type)
                            method_type = "L" + file_name[
                                method_type] + ";" if method_type in file_name else method_type
                            method_type = "[" + method_type[:-3] + ";" if "[]" in method_type else method_type
                            if "." in method_type:
                                method_type = "/".join(method_type.split("."))
                        if variables != "":
                            variables = [remap_file_path(variable) for variable in variables.split(",")]
                            variables = ["[" + variable[:-3] + ";" if "[]" in variable else variable for variable in
                                         variables]

                            variables = "".join(
                                ["L" + file_name[variable] + ";" if variable in file_name else variable for variable in
                                 variables])
                            if "." in variables:
                                variables = "/".join(variables.split("."))
                        outputFile.write(f'\t{obf_name} ({variables}){method_type} {function_name}\n')
                    else:
                        outputFile.write(f'\t{obf_name} {method_name}\n')

                else:
                    obf_name = obf_name.split(":")[0]
                    outputFile.write(remap_file_path(obf_name)[1:-1] + " " + remap_file_path(deobf_name)[1:-1] + "\n")

    def make_paths(self, version):
        path = Path(f'mappings/{version}')

        if not path.exists():
            path.mkdir(parents=True)
        path = Path(f'src/{version}')
        if not path.exists():
            path.mkdir(parents=True)
        else:
            aw = input(
                f"/src/{version} already exists, wipe it (w), create a new folder (n) or kill the process (k) ? ")
            if aw == "w":
                shutil.rmtree(Path(f"./src/{version}"))
            elif aw == "n":
                version = version + "_" + str(random.getrandbits(128))
            else:
                sys.exit()
            path = Path(f'src/{version}')
            path.mkdir(parents=True)
        return version
