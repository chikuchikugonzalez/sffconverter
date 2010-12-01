# -*- coding: UTF-8 -*-
#
# PCXファイルオブジェクト

import struct
import array

class PCXImage(object):

    #
    # Constructors
    #
    def __init__(self):
        self.__data = None
        self.__compresseddData = None
        self.__minX = 0
        self.__minY = 0
        self.__maxX = 0
        self.__maxY = 0
        self.__palette = None
        self.__bytesPerLine = 0

    #
    # Properties
    #
    @property
    def data(self):
        """Get PCX Image Data (Uncompressed)"""
        return self.__data
    @data.setter
    def data(self, value):
        """Set PCX Image Data"""
        self.__data = value
        self.__compressedData = __compressData(value)

    @property
    def compressedData(self):
        """Get Compressed PCX Image Data"""
        return self.__compressedData
    @compressedData.setter
    def compressedData(self, value):
        """Set Compressed PCX Image Data"""
        self.__compressedData = value
        self.__data = PCXImage.__decompressData(value, self.width * self.height)

    @property
    def dimension(self):
        """Get PCX Image Dimensions"""
        return (self.__minX, self.__minY, self.__maxX, self.__maxY)
    @dimension.setter
    def dimension(self, value):
        """Set Image Dimension"""
        self.__minX = value[0]
        self.__minY = value[1]
        self.__maxX = value[2]
        self.__maxY = value[3]

    @property
    def width(self):
        """Get Image Width"""
        return self.__maxX - self.__minX + 1
    @property
    def height(self):
        """Get Image Height"""
        return self.__maxY - self.__minY + 1

    @property
    def palette(self):
        return self.__palette
    @palette.setter
    def palette(self, value):
        self.__palette = value

    #
    # Methods
    #
    def load(self, data):
        # Read PCX Properties
        dims = struct.unpack('<HHHH', data[4:12])
        self.dimension = dims
        self.__bytesPerLine = struct.unpack('<H', data[66:68])[0]
        dataLength = self.__bytesPerLine * self.height

        # Uncompressing
        self.compressedData = data[128:-769]

    @staticmethod
    def __decompressData(data, maxLength):
        """Uncompressing PCX Image data as RLE"""
        bytes = array.array('c')
        length = len(data)
        i = 0
        total = 0
        while i < length:
            byte = data[i]
            val = struct.unpack('<B', byte)[0]
            if (val & 0xC0) == 0xC0:
                # Run Length
                count = val & 0x3F
                byte = data[i + 1]
                i += 1
            else:
                count = 1
            i += 1

            # Append
            for j in range(0, count):
                bytes.append(byte)
                total += 1
                if total >= maxLength:
                    # Over
                    return bytes.tostring()
        return bytes.tostring()

    @staticmethod
    def __compressData(data):
        """Compressing PCX Image Data as RLE"""
        bytes = array.array('c')
        prev = None
        count = 0
        for byte in data:
            if prev is None:
                prev = byte
                count = 1
            else:
                if prev == byte:
                    count += 1
                else:
                    # Compressing
                    val = struct.unpack('<B', prev)[0]
                    if count == 1:
                        if val & 0xC0 == 0xC0:
                            # Run Length
                            bytes.append(struct.pack('<B', count))
                            bytes.append(prev)
                        else:
                            # Plain
                            bytes.append(prev)
                    else:
                        # Run Length
                        unit = count // 63
                        c = count
                        for i in range(0, unit):
                            rl = 63
                            if c < 63:
                                rl = c
                            c -= 63
                            bytes.append(struct.pack('<B', (0xC0 | rl)))
                            bytes.append(prev)
                    prev = byte
                    count = 1
        return bytes.tostring()
