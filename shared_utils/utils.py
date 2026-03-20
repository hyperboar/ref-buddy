import os
import sys

class Utils:

    @staticmethod
    def is_windows():
        return sys.platform == 'win32'

    @staticmethod
    def sync_file_timestamps(src, dest):
        """
        Transfer create date and modify date from src to dest file.
        Also changes SOURCE timestamp if modify time < create time.
        """
        cr_time = os.path.getctime(src)
        md_time = os.path.getmtime(src)

        # this changes SOURCE timestamp
        if md_time < cr_time:
            cr_time = md_time
            os.utime(src, (cr_time, md_time))
            if Utils.is_windows():
                setctime(src, cr_time)

        os.utime(dest, (cr_time, md_time))

        if Utils.is_windows():
            setctime(dest, cr_time)

    @staticmethod
    def get_path_os_specific(path: str) -> str:
        if Utils.is_windows():
            return path.replace('/', '\\')
        return path

    @staticmethod
    def select_file_cmd_os_specific(path: str) -> str:
        if Utils.is_windows():
            return f'C:\\Windows\\explorer.exe /root, "{Utils.get_path_os_specific(path)}", /select'
        return f'open -R "{path}"'

    @staticmethod
    def is_debugging():
        import sys
        return sys.gettrace() is not None


# Importing win32 module... have no idea how to do it better than this :(
if Utils.is_windows():
    from win32_setctime import setctime