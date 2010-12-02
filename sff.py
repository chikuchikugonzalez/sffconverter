# -*- coding: UTF-8 -*-
#
# 新MUGENのSFFv2用クラス

import struct
import array

# PCX
import pcx

class SFFPalette(object):
    """SFFのパレットデータクラス"""

    #
    # Constructors
    #
    def __init__(self):
        self.__groupNo = 0
        self.__paletteNo = 0
        self.__data = None
        self.__colors = 256
        self.__reversed = False

    #
    # Properties
    #
    @property
    def group(self):
        """Get Palette Group Number"""
        return self.__groupNo
    @group.setter
    def group(self, value):
        """Set Palette Group Number"""
        self.__groupNo = value

    @property
    def number(self):
        """Get Palette Number"""
        return self.__paletteNo
    @number.setter
    def number(self, value):
        """Set Palette Number"""
        self.__paletteNo = value

    @property
    def data(self):
        """Get Palette Data"""
        return self.__data
    @data.setter
    def data(self, value):
        """Set Palette Data"""
        self.__data = value

    @property
    def colors(self):
        return self.__colors
    @colors.setter
    def colors(self, value):
        self.__colors = value

    @property
    def reversed(self):
        return self.__reversed
    @reversed.setter
    def reversed(self, value):
        self.__reversed = value

    #
    # Methods
    #
    def dataAsRGBA(self):
        bytes = array.array('c')
        for i in range(0, len(self.data), 3):
            r = self.data[i]
            g = self.data[i + 1]
            b = self.data[i + 2]
            a = '\x00'
            if self.reversed:
                bytes.append(a)
                bytes.append(b)
                bytes.append(g)
                bytes.append(r)
            else:
                bytes.append(r)
                bytes.append(g)
                bytes.append(b)
                bytes.append(a)
        if self.reversed:
            bytes.reverse()
        dataset = bytes.tostring()
        if len(dataset) < 1024:
            for i in range(len(dataset), 1024):
                dataset += '\x00'
        elif len(dataset) > 1024:
            dataset = dataset[:1024]
        return dataset


class SFFSprite(object):
    """スプライトデータクラス"""

    #
    # Constructors
    #
    def __init__(self):
        self.__groupNo = 0
        self.__imageNo = 0
        self.__axis = None
        self.__width = 0
        self.__height = 0
        self.__linkedIndex = 0
        self.__paletteNumber = 0
        self.__data = None
        self.__compressedData = None

    #
    # Properties
    #
    @property
    def group(self):
        return self.__groupNo
    @group.setter
    def group(self, value):
        self.__groupNo = value

    @property
    def number(self):
        return self.__imageNo
    @number.setter
    def number(self, value):
        self.__imageNo = value

    @property
    def axis(self):
        return self.__axis
    @axis.setter
    def axis(self, value):
        self.__axis = value

    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self, value):
        self.__width = value

    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self, value):
        self.__height = value

    @property
    def linkedIndex(self):
        return self.__linkedIndex
    @linkedIndex.setter
    def linkedIndex(self, value):
        self.__linkedIndex = value

    @property
    def paletteNumber(self):
        return self.__paletteNumber
    @paletteNumber.setter
    def paletteNumber(self, value):
        self.__paletteNumber = value

    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def compressedData(self):
        if self.__compressedData is None:
            self.__compressedData = SFFSprite.__compressData(self.__data)
        return self.__compressedData

    #
    # Methods
    #
    @staticmethod
    def __compressData(data):
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
                    if count == 1:
                        val = struct.unpack('<B', prev)[0]
                        if (val & 0xC0) == 0x40:
                            # Run Length
                            bytes.append(struct.pack('<B', 65))
                            bytes.append(prev)
                        else:
                            # Plain
                            bytes.append(prev)
                    else:
                        length = count
                        while length > 0:
                            dataLength = 1
                            if length > 63:
                                dataLength = 63
                            else:
                                dataLength = length
                            length -= 63

                            bytes.append(struct.pack('<B', (64 | dataLength)))
                            bytes.append(prev)
                    prev = byte
                    count = 1
        return bytes.tostring()


class SFF(object):
    """SFFファイルクラス"""

    #
    # Constructors
    #
    def __init__(self):
        self.__palettes = []
        self.__sprites = []
        self.__defaultPaletteNumber = 0

    #
    # Properties
    #
    @property
    def palettes(self):
        return self.__palettes

    @property
    def sprites(self):
        return self.__sprites

    #
    # Methods
    #
    def addPalette(self, fp, group, number, reversed = False):
        palette = SFFPalette()
        palette.group = group
        palette.number = number
        palette.reversed = reversed
        palette.data = fp.read()
        self.palettes.append(palette)

    def setDefaultPaletteNumber(self, palIndex = 0):
        old = self.__defaultPaletteNumber
        self.__defaultPaletteNumber = palIndex
        return old

    def read(self, fp):
        # Reading Signatures
        signature = fp.read(12)
        if not signature == "ElecbyteSpr\x00":
            raise "Input source is not Elecbyte Sprite File"
        version = fp.read(4)
        if not version == "\x00\x01\x00\x01":
            raise "Input source is not supported SFF Version"

        # Reading Headers
        print "<Read Headers>",
        numGroups, numSprites = struct.unpack('<II', fp.read(8))
        subfileOffset, headerSize = struct.unpack('<II', fp.read(8))
        print "done."

        # Reading sprites
        print "<Read Sprites>"
        offset = subfileOffset
        paletteIndex = self.__defaultPaletteNumber
        paletteData = '\x00' * 768
        _index = 0
        for i in range(0, numSprites):
            print "\tReading sprite %d..." % _index,
            _index += 1

            # Reading Sprite
            fp.seek(offset, 0)      # Seeking to sprite offset
            sprite = SFFSprite()

            # Reading
            nextOffset = struct.unpack('<I', fp.read(4))[0]
            dataSize = struct.unpack('<I', fp.read(4))[0]
            axisX, axisY = struct.unpack('<HH', fp.read(4))
            groupNo, imageNo = struct.unpack('<HH', fp.read(4))
            linkedIndex = struct.unpack('<H', fp.read(2))[0]
            sharedMode = struct.unpack('<B', fp.read(1))[0]

            # Set
            sprite.group = groupNo
            sprite.number = imageNo
            sprite.axis = (axisX, axisY)
            sprite.linkedIndex = linkedIndex

            # Read pcx
            if linkedIndex == 0:
                fp.seek(offset + 32, 0)
                data = fp.read(dataSize)

                # Check Palette
                if sharedMode == 0:
                    # Reading palette
                    palette = SFFPalette()
                    palette.group = groupNo
                    palette.number = imageNo
                    paletteData = data[-768:]
                    palette.data = paletteData

                    self.__palettes.append(palette)
                    if (groupNo == 9000 and imageNo == 0) or (groupNo == 0 and imageNo == 0):
                        paletteIndex = self.__defaultPaletteNumber
                    else:
                        paletteIndex = len(self.__palettes) - 1
                else:
                    data += paletteData
                    # Set Palette Number if Head Sprite
                    if (groupNo == 9000 and imageNo == 0) or (groupNo == 0 and imageNo == 0):
                        paletteIndex = self.__defaultPaletteNumber

                pcxImage = pcx.PCXImage()
                pcxImage.load(data)

                sprite.width = pcxImage.width
                sprite.height = pcxImage.height
                sprite.data = pcxImage.data
                sprite.paletteNumber = paletteIndex
            else:
                # Clone
                sprite.width = self.__sprites[linkedIndex].width
                sprite.height = self.__sprites[linkedIndex].height
                sprite.paletteNumber = self.__sprites[linkedIndex].paletteNumber
            self.__sprites.append(sprite)
            offset = nextOffset

            # Debug
            print "done."

    def write(self, fp):
        # Pre-process
        print "Pre-Processing...",
        headerSize = 512
        numberOfSprites = len(self.sprites)
        numberOfPalettes = len(self.palettes)
        spriteNodeListSize = 28 * numberOfSprites
        paletteMapSize = 16 * numberOfPalettes
        paletteMapOffset = 512
        spriteNodeListOffset = 512 + paletteMapSize

        dataOffset = spriteNodeListOffset + spriteNodeListSize
        totalDataSize = 1024 * numberOfPalettes
        for spr in self.sprites:
            if spr.linkedIndex == 0:
                totalDataSize += (len(spr.compressedData) + 4)
        print "done."

        # Writing
        # Writing Headers
        print "Writing Headers...",
        fp.write("ElecbyteSpr\x00")         # Signature
        fp.write("\x00\x00\x00\x02")        # Version Number
        fp.write("\x00" * 10)               # Unknown Area
        fp.write(struct.pack('<I', paletteMapOffset))       # Palette Map Offset
        fp.write("\x00" * 6)                # Unknown Area, 2
        fp.write(struct.pack('<I', spriteNodeListOffset))       # Sprite List Node Offset
        fp.write(struct.pack('<I', numberOfSprites))            # Number of Sprites
        fp.write("\x00\x02\x00\x00")        # Unknown Area, 3, 0x00020000
        fp.write(struct.pack('<I', numberOfPalettes))           # Number of Palettes
        fp.write(struct.pack('<I', dataOffset))         # Literal Data Offset (Palette Bank Offset)
        fp.write(struct.pack('<I', totalDataSize))      # Literal Data Size
        fp.write(struct.pack('<I', totalDataSize + headerSize + spriteNodeListSize + paletteMapSize))       # All
        fp.write(struct.pack('<I', 0))                  # Translation Data Size
        fp.write("\x00" * 444)                  # Unused
        print "done."

        # Writing Palette Maps
        print "Writing Palette Maps...",
        paletteDataOffset = 0   #dataOffset
        for pal in self.palettes:
            fp.write(struct.pack('<H', pal.group))      # GroupNo
            fp.write(struct.pack('<H', pal.number))     # ItemNo
            fp.write(struct.pack('<I', pal.colors))     # Number of Colors
            fp.write(struct.pack('<I', paletteDataOffset))  # Offset into data
            fp.write(struct.pack('<I', 1024))           # Palette data length (0: linked)
            paletteDataOffset += 1024
        print "done."

        # Writing Sprite Node
        print "Writing Sprite Node List...",
        spriteDataOffset = (1024 * numberOfPalettes)    #dataOffset + (1024 * numberOfPalettes)
        spriteDataOffsetMapping = {}
        index = 0
        for spr in self.sprites:
            spriteDataLength = 0
            _offset = spriteDataOffset
            if spr.linkedIndex == 0:
                spriteDataLength = len(spr.compressedData) + 4
            else:
                _offset = spriteDataOffsetMapping[spr.linkedIndex]
            spriteDataOffsetMapping[index] = _offset
            fp.write(struct.pack('<H', spr.group))          # Group No
            fp.write(struct.pack('<H', spr.number))         # Item No
            fp.write(struct.pack('<H', spr.width))          # Width
            fp.write(struct.pack('<H', spr.height))         # Height
            fp.write(struct.pack('<HH', spr.axis[0], spr.axis[1]))      # Axis X, Axis Y
            fp.write(struct.pack('<H', spr.linkedIndex))    # Index number of the linked sprite (if linked)
            fp.write(struct.pack('<B', 2))                  # format (RLE8)
            fp.write(struct.pack('<B', 8))                  # Color depth (8bit)
            fp.write(struct.pack('<I', _offset))            # Offset into data
            fp.write(struct.pack('<I', spriteDataLength))   # Data length (0: linked)
            fp.write(struct.pack('<H', spr.paletteNumber))  # Palette Number (Palette Index)
            fp.write(struct.pack('<H', 0))                  # Flags (0:Literal Data, other: Translate
            spriteDataOffset += spriteDataLength
            index += 1
        print "done."

        # Writing Palette Data
        print "Writing Palette Data...",
        for pal in self.palettes:
            fp.write(pal.dataAsRGBA())
        print "done."
        # Writing sprite data
        print "Writing Sprite Data...",
        for spr in self.sprites:
            if spr.linkedIndex == 0:
                data = spr.compressedData
                spriteDataLength = len(spr.data)
                fp.write(struct.pack('<I', spriteDataLength))
                fp.write(data)
        print "done."
