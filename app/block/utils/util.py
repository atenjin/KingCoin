#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from app.config import block_file_name, MAX_SIZE
from app.db.dbserialize import PyAutoFile


def open_block_file(file_index, block_pos, szmode, autofile=True):
    """

    :param file_index:
    :param block_pos:
    :param szmode:
    :param autofile:
    :return:
    :rtype file | PyAutoFile
    """
    if file_index == -1:
        return None
    f = None
    try:
        f = open(block_file_name(file_index), szmode)
    except (IOError, Exception), e:
        if f is not None:
            f.close()
        # TODO add log
        return None
    pyautofile = PyAutoFile(f)
    # szmode = ''
    # 设置文件指针到 block_pos 记录的位置
    if block_pos != 0 and szmode.find('a') == -1 and szmode.find('w') == -1:  # 就是文件只是r
        pyautofile.seek(block_pos, 0)
    return pyautofile if autofile else pyautofile.release_file()


nCurrentBlockFile = 1


def append_block_file(autofile=True):
    """

    :param autofile:
    :return: return False or (file, file_index)
    :rtype bool | tuple
    """
    global nCurrentBlockFile
    while True:
        # file type, not PyAutoFile
        f = open_block_file(nCurrentBlockFile, 0, "ab", autofile=autofile)
        if not f:
            return None
        f.seek(0, 2)
        # FAT32 filesize max 4GB, fseek and ftell max 2GB, so we must stay under 2GB
        if f.tell() < (0x7F000000 - MAX_SIZE):
            file_ret = nCurrentBlockFile
            # loop exist at this place
            return f, file_ret
        f.close()
        nCurrentBlockFile += 1
        pass
    # unreached
    pass


def main():
    pass


if __name__ == '__main__':
    main()
