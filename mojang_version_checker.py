from distutils.version import LooseVersion

import re

class MojangVersionChecker:

    def check(self, mc_version):
        version = LooseVersion(f"{mc_version}")
        if re.match("^([1-3][0-9])w\\d{1,2}[a-f]$", mc_version):
            return LooseVersion("19w36a") <= version
        elif re.match("^(1\\.([0-9][0-9]?)(\\.[0-9][0-9]?)?)$", mc_version):
            return LooseVersion("1.14.4") <= version
        else:
            return False


