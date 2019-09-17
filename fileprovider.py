import platform


class FileProvider:

    def __init__(self, lib_dir):
        self.__lib_dir = lib_dir

    def get_mincraft_folder(self, os=platform.system()):
        if os == "Linux":
            return "needs to be defined"
        elif os == "Darwin":
            return "~/Library/Application Support/minecraft"
        elif os == "Windows":
            return "~/AppData/Roaming/.minecraft"
        else:
            return os

    def get_fernflower(self):
        return f"{self.__lib_dir}/fernflower.jar"

    def get_cfr(self):
        return f"{self.__lib_dir}/cfr-0.146.jar"

    def get_specialsource(self):
        return f"{self.__lib_dir}/SpecialSource-1.8.6.jar"