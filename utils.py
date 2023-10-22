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


# Importing win32 module... have no idea how to do it better than this :(
if Utils.is_windows():
    from win32_setctime import setctime