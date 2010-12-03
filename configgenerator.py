# -*- coding: UTF-8 -*-
#
# .defファイルからsffconverterが使うconfig.xmlを出力するスクリプト
#

from __future__ import with_statement
import sys
import os
import ConfigParser

class XMLElement(object):

    def __init__(self, name, parent = None):
        self.__name = name
        self.__parent = parent
        self.__value = None
        self.__attributes = {}
        self.__children = []

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent

    @property
    def children(self):
        return self.__children

    @property
    def attributes(self):
        return self.__attributes

    def addChild(self, elem):
        elem.parent = self
        self.__children.append(elem)

    def setAttribute(self, name, value):
        self.__attributes[name] = value

    def getAttribute(self, name):
        return self.__attributes[name]

    def __str__(self):
        val = "<" + self.__name
        for k, v in self.__attributes.items():
            val += ' %s="%s"' % (k, v)
        if len(self.__children) == 0 and (self.__value is None):
            val += " />"
        else:
            val += ">"
            if not self.__value is None:
                val += "%s" % self.__value
            for child in self.__children:
                val += str(child)
            val += "</" + self.__name + ">"
        return val

    def prettyprint(self, indent = 2):
        val = " " * indent
        val += "<" + self.__name
        for k, v in self.__attributes.items():
            val += ' %s="%s"' % (k, v)
        if len(self.__children) == 0 and (self.__value is None):
            val += " />"
        else:
            val += ">"
            if not self.__value is None:
                val += "%s" % self.__value
            val += "\n"
            for child in self.__children:
                val += child.prettyprint(indent + 2)
                val += "\n"
            val += " " * indent
            val += "</" + self.__name + ">"
        return val


class ConfigGenerator:

    def __init__(self, parser, dir = None):
        self.__parser = parser
        self.__basedir = dir
        if self.__basedir is None:
            self.__basedir = ''

    def generate(self):
        sprite = self.__parser.get("Files", "sprite")
        palettes = []
        for i in range(1, 13):
            key = "pal%d" % i
            if self.__parser.has_option("Files", key):
                palettes.append(self.__parser.get("Files", key))
            else:
                break
        root = XMLElement("config")
        converter = XMLElement("sffconverter")
        converter.setAttribute("input", os.path.join(self.__basedir, sprite))
        converter.setAttribute("output", os.path.join(self.__basedir, "rebuild.%s" % sprite))
        root.addChild(converter)

        for i, pal in enumerate(palettes):
            group = 1 + int(i / 12)
            palno = i % 12 + 1
            palElement = XMLElement("palette")
            palElement.setAttribute("group", group)
            palElement.setAttribute("number", palno)
            palElement.setAttribute("act", os.path.join(self.__basedir, pal))
            converter.addChild(palElement)
        return root

if __name__ == '__main__':
    input = None
    output = None
    dir = None
    try:
        input = sys.stdin
        output = sys.stdout

        argc = len(sys.argv)
        if argc > 1:
            input = open(sys.argv[1], "r")
            dir = os.path.dirname(sys.argv[1])
        if argc > 2:
            output = open(sys.argv[2], "w")

        parser = ConfigParser.SafeConfigParser()
        parser.readfp(input)
        generator = ConfigGenerator(parser, dir)
        element = generator.generate()
        output.write('<?xml version="1.0"?>\n')
        output.write(element.prettyprint(0))
    finally:
        if not input is None:
            input.close()
        if not output is None:
            output.close()
