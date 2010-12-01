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
        self.__encodedData = None
        self.__minX = 0
        self.__minY = 0
        self.__maxX = 0
        self.__maxY = 0
        self.__palette = None

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

    @data.deleter
    def data(self):
        del self.__data

    #
    # Methods
    #
