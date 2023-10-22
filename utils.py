import sys

class Utils:

    @staticmethod
    def is_windows():
        return sys.platform == 'win32'