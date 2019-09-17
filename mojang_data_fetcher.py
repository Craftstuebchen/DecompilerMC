import requests

from mojang_version_checker import MojangVersionChecker


class MojangDataFetcher:

    def __init__(self, version_checker: MojangVersionChecker):
        self.__version_checker = version_checker
        versions = self.__fetch_versions()
        self.__latest = versions["latest"]
        self.__versions = {x["id"]: x for x in filter(lambda elem: self.__version_checker.check(elem["id"]), versions["versions"])}

    def __fetch_versions(self):
        data = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
        return data.json()

    def get_version_meta_by_id(self, id):
        return self.__versions[id]

    def get_latest_version(self, release_type):
        return self.__latest[f"{release_type}"]

    def get_files_and_mappings(self, id):
        data = requests.get(self.get_version_meta_by_id(id)["url"]).json()
        return {
            "client_jar" : data["downloads"]["client"]["url"],
            "client_mappings": data["downloads"]["client_mappings"]["url"],
            "server_jar": data["downloads"]["server"]["url"],
            "server_mappings": data["downloads"]["server_mappings"]["url"]
        }

    def get_available_versions(self):
        return list(self.__versions.keys())

