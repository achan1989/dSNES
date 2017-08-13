# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from dsnes import util

class Memory:
    def __init__(self):
        self.data = None
        self.size = 0

    def allocate(self, source, size=0):
        if util.is_filelike(source):
            data = source.read()
            bytes_read = len(data)
            if size > 0:
                assert bytes_read == size, (
                    "Read {} bytes, expected {}".format(bytes_read, size))
            self.data = data
            self.size = bytes_read

        else:
            raise TypeError("source is an unsupported type")
