#!/usr/bin/env python

__description__ = 'nmap xml script output parser'
__author__ = 'Didier Stevens, modify by Sumedt Jitpukdebodin, modfied by liamosaur'
__version__ = '0.3'
__date__ = '2016/03/07'

import optparse
import xml.dom.minidom
import xml.sax
import glob
import collections

QUOTE = '"'

def ToString(value):
    if type(value) == type(''):
        return value
    else:
        return str(value)

def Quote(value, separator, quote):
    value = ToString(value)
    if separator in value:
        return quote + value + quote
    else:
        return value

def MakeCSVLine(row, separator, quote):
    return separator.join([Quote(value, separator, quote) for value in row])

class cOutput():
    def __init__(self, filename=None):
        self.filename = filename
        if self.filename and self.filename != '':
            self.f = open(self.filename, 'w')
        else:
            self.f = None

    def Line(self, line):
        if self.f:
            self.f.write(line + '\n')
        else:
            print(line)

    def Close(self):
        if self.f:
            self.f.close()
            self.f = None

class cOutputCSV():
    def __init__(self, options):
        if options.output:
            self.oOutput = cOutput(options.output)
        else:
            self.oOutput = cOutput()
        self.options = options

    def Row(self, row):
        self.oOutput.Line(MakeCSVLine(row, self.options.separator, QUOTE))

    def Close(self):
        self.oOutput.Close()


class NmapXmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        self._rows = []
        self._enddate = ''
        self._vendors = ''
        self._addresses = ''
        self._hostnames = ''
        self._script = ''
        self._output = ''

    def startElement(self, name, attrs):
        if name == 'nmaprun':
            self._startDate = attrs.get('startstr')
        if name == 'finished': 
            for row in self._rows: #This is the last element
                row.append('|'.join([attrs.get('timestr')]))
        if name == 'host':
            if attrs.get('hostname') is not None:
                self._hostnames += attrs.get('hostname')
        if name == 'address':
            if attrs.get('addr') is not None:
                self._addresses += attrs.get('addr')
        if name == 'vendor':
            if attrs.get('vendor') is not None:
                self._vendors += attrs.get('vendor')
        if name == 'port':
            self._port = attrs.get('portid')
        if name == 'state':
            if attrs.get('state') is not None:
                self._state = attrs.get('state')
        if name == 'service':
            if attrs.get('name') is not None:
                self._service = attrs.get('name')
        if name == 'script':
            if attrs.get('id') is not None:
                self._script += attrs.get('id')
            if attrs.get('output') is not None:
                self._output += repr(attrs.get('output').encode('ascii').replace('\n  ',''))

    def endElement(self,name):
        if name == 'port': 
            self._row = ['|'.join([self._startDate])]
            self._row.append('|'.join([self._addresses]))
            self._row.append('|'.join([self._vendors]))
            self._row.append('|'.join([self._hostnames]))
            self._row.append('|'.join([self._port]))
            self._row.append('|'.join([self._state]))
            self._row.append('|'.join([self._service]))
            self._row.append('|'.join([self._script]))
            self._row.append('|'.join([self._output]))
            self._rows.append(self._row)
        if name == 'host':
            self._addresses = ''
            self._hostnames = ''
            self._vendors = ''
            self._port = ''
            self._state = ''
            self._service = ''
            self._script = ''
            self._output = ''

    def parse(self, f):
        xml.sax.parse(f, self)
        return self._rows

    def characters(self, data):
        pass


def NmapXmlParser(filenames, options):
    oOuput = cOutputCSV(options)
    oOuput.Row(['Start Time','address', 'vendor','hostname', 'port', 'state', 'service', 'script', 'output','End time'])
    for filename in filenames:
        output = NmapXmlHandler().parse(open(filename, 'r'))
        for row in output:
            oOuput.Row(row)
    oOuput.Close()



def File2Strings(filename):
    try:
        f = open(filename, 'r')
    except:
        return None
    try:
        return map(lambda line:line.rstrip('\n'), f.readlines())
    except:
        return None
    finally:
        f.close()

def ProcessAt(argument):
    if argument.startswith('@'):
        strings = File2Strings(argument[1:])
        if strings == None:
            raise Exception('Error reading %s' % argument)
        else:
            return strings
    else:
        return [argument]

def ExpandFilenameArguments(filenames):
    return list(collections.OrderedDict.fromkeys(sum(map(glob.glob, sum(map(ProcessAt, filenames), [])), [])))

def Main():
    moredesc = '''

Arguments:
@file: process each file listed in the text file specified
wildcards are supported'''

    oParser = optparse.OptionParser(usage='usage: %prog [options] [@]file ...\n' + __description__ + moredesc, version='%prog ' + __version__)
    oParser.add_option('-o', '--output', type=str, default='', help='Output to file')
    oParser.add_option('-s', '--separator', default=';', help='Separator character (default ;)')
    (options, args) = oParser.parse_args()

    if len(args) == 0:
        oParser.print_help()
    else:
        NmapXmlParser(ExpandFilenameArguments(args), options)

if __name__ == '__main__':
    Main()
