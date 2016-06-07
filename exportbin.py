#-------------------------------------------------------------------------------
# Name:        ddodxts
# Purpose:     Rips DXT codecs from DDO file: client_surface.dat
#
# Author:      Marcus
#
# Created:     25/10/2015
# Copyright:   (c) Marcus 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import re
import os, sys
import struct
from struct import unpack, pack
import codecs
import binascii

def main():
    """
    this tool finds DXT codecs in ddo client files,
    encodes them in base64, & outputs them to a csv file
    """
    a = 'C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\client_cell_1.dat'
    b = 'C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\client_cell_2.dat'
    c = 'C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\hack\\cell_data.csv'
    surf = None
    try:
        surf = open(a, 'rb')
        data = open(b, 'w')
        ddodata = surf.read()
        # header for csv file
        data.write("Desc, Type, Offset, DataLength, TexelSize, Data1, Data2, Data3, Data4\n")
    except IOError:
        print "Error opening data file."
        exit()
    # To Do: Add scans for DDS DTM
    strings = []
    # DXT1 NO ALPHA
    # would have loved to use: dxt1 = r"(DXT1)([.]{4})([.]{32})([.]{32})"
    # but escaping all those chars is more trouble than it's worth

    rx1 = re.compile('(DXT1)(....)(................................)(................................)', re.DOTALL)
    matches = rx1.finditer(ddodata)

    for match in matches:
        encdata = "%s %s" % (binascii.b2a_base64(match.group(3)), binascii.b2a_base64(match.group(4)))
        encdata = encdata.split()
        # note 2 consecutive commas at end of string; this lets columns match up if opened in excel or open office
        strings.append("?,%s,%d,%d,%d,%s,,\n"\
        % (match.group(1), match.span()[0], match.span()[1]-match.span()[0],to_int(match.group(2)), ','.join(encdata))
        )

    # DXT3 Explicit alpha
    rx3 = re.compile(r'(DXT3)(....)(................................)(................................)(................................)(................................)', re.DOTALL)
    #matches = rx.finditer(ddodata)
    matches = rx3.finditer(ddodata)
    for match in matches:
        encdata = "%s %s %s %s" % (binascii.b2a_base64(match.group(3)), binascii.b2a_base64(match.group(4)), binascii.b2a_base64(match.group(5)), binascii.b2a_base64(match.group(6)))
        encdata = encdata.split()
        strings.append("?,%s,%d,%d,%d,%s\n"\
        % (match.group(1), match.span()[0], match.span()[1]-match.span()[0],to_int(match.group(2)), ','.join(encdata))
        )

    # DXT5 Interpolated alpha
    rx5 = re.compile(r'(DXT5)(....)(................................)(................................)(................................)(................................)', re.DOTALL)
    #matches = rx.finditer(ddodata)
    matches = rx5.finditer(ddodata)
    for match in matches:
        encdata = "%s %s %s %s" % (binascii.b2a_base64(match.group(3)), binascii.b2a_base64(match.group(4)), binascii.b2a_base64(match.group(5)), binascii.b2a_base64(match.group(6)))
        encdata = encdata.split()
        strings.append("?,%s,%d,%d,%d,%s\n"\
        % (match.group(1), match.span()[0], match.span()[1]-match.span()[0],to_int(match.group(2)), ','.join(encdata))
        )
    #clean up
    data.writelines(strings)
    surf.close()
    data.close()

def to_int(t):
    "convert bin data to int"
    return struct.unpack('i', t)[0]

def to_hex(t, nbytes):
    "Format text t as a sequence of nbyte long values separated by \\x."
    chars_per_item = nbytes * 2
    hex_version = binascii.hexlify(t)
    num_chunks = len(hex_version) / chars_per_item
    def chunkify():
        for start in xrange(0, len(hex_version), chars_per_item):
            yield hex_version[start:start + chars_per_item]
    return r'\x'.join(chunkify())

if __name__ == '__main__':
    main()