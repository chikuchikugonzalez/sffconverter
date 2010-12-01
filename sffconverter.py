# -*- coding: UTF-8 -*-
#
# SFFコンバータ 本体

# sys
from __future__ import with_statement
import os
import sys

# xml
import xml.sax

# SFF
import sff

class Configuration(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.__input = None
        self.__output = None
        self.__palettes = []

        # Parser
        self.__inConverterSection = False

    #
    # Properties
    #
    @property
    def input(self):
        return self.__input
    @property
    def output(self):
        return self.__output
    @property
    def palettes(self):
        return self.__palettes

    #
    # Methods
    #

    def startElement(self, name, attrs):
        if self.__inConverterSection:
            if name == 'palette':
                pal = {}
                pal['group'] = int(attrs['group'])
                pal['number'] = int(attrs['number'])
                pal['act'] = attrs['act']
                self.__palettes.append(pal)
        if name == 'sffconverter':
            self.__inConverterSection = True
            self.__input = attrs['input']
            self.__output = attrs['output']

    def endElement(self, name):
        if name == 'sffconverter':
            self.__inConverterSection = False

    def loadFromXML(self, fp):
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        parser.setContentHandler(self)
        parser.parse(fp)

        #print self.__palettes

if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = Configuration()
        with open(sys.argv[1], 'r') as fp:
            config.loadFromXML(fp)

        # SFF
        sff = sff.SFF()

        # Append Default Palettes
        for palinfo in config.palettes:
            with open(palinfo['act'], "rb") as fp:
                sff.addPalette(fp, palinfo['group'], palinfo['number'])
        with open(config.input, "rb") as fp:
            sff.read(fp)

        # Debug
        print "#Sprites = %d, #Palettes = %d" % (len(sff.sprites), len(sff.palettes))
        for pal in sff.palettes:
            print "<pal %d.%d>" % (pal.group, pal.number)
            print "Length = %d" % len(pal.dataAsRGBA())
        for spr in sff.sprites:
            print "<spr %d.%d>" % (spr.group, spr.number)
            print "%dx%d,%dx%d" % (spr.axis[0], spr.axis[1], spr.width, spr.height)
            if spr.linkedIndex == 0:
                print "Length = %d / %d" % (len(spr.data), len(spr.compressedData))

        # Write
        with open(config.output, "wb") as fp:
            sff.write(fp)

    else:
        print "Usage: %s converter_config.xml" % sys.argv[0]
