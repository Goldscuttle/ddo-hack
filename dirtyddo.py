#-------------------------------------------------------------------------------
# Name:        dirtyddo
# Purpose:     Alters local DDO client, revealing secrets of Stormreach
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
    this tool extracts key value pairs from a text file,
    then does a global search & replace each key with value

    re.sub doesn't work so i'm using file.seek with the offset of match.span()
    """
    a = 'C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\client_local_English.dat'
    b = 'C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\client_local_English.mod'

    modfile = None
    ddoclient = None
    #modclient = None
    ddodata = None
    try:
        modfile = open('C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\modlist.txt')
        ddoclient = open(a, 'r+b')
        #modclient = open(b, 'wb')
        ddodata = ddoclient.read()
    except IOError:
        print "Error opening data file."
        exit()

    rx_keyval = r'(^[A-Za-z \.]+)=([A-Za-z \.]+$)'

    r1 = re.compile(rx_keyval, re.U)

    lu_row = modfile.readline()
    lines = 0
    try:
        key = None
        var = None
        while lu_row <> "":
            m = r1.match(lu_row)
            if m:
                if len(m.group(2)) <= len(m.group(1)):
                    # formats the key as sequence of hex chars for regex
                    key = "\\x%s" % to_hex(m.group(1), 1).replace("\\x", "\\x00\\x")
                    var = m.group(2)
                    # make a suitably sized array of bytes that our replacement
                    # value will be stored in
                    vbytes = bytearray((len(m.group(1)))*2)
                    for x in xrange(len(m.group(1))):
                        vbytes[x*2] = var[x] # skip odd bytes

                    r2 = re.compile(key, re.DOTALL)
                    matches = r2.finditer(ddodata)
                    r=0
                    for match in matches:
                        #print  m.group(1), match.span()
                        ddoclient.seek(match.span()[0], 0)
                        ddoclient.write(vbytes)
                        r = r + 1
                    if r:
                        print "Line %d: Found %d matches of '%s', made %d replacements with '%s'." % (lines, r, m.group(1), r, m.group(2))
                    else:
                        print "Line %d: Found 0 matches of '%s'." % (lines, m.group(1))
                else:
                    print "Line %d: Replacement value '%s' is too long. Skipped." % (lines, m.group(2))
            else:
                print "No match found for line %d: Skipped %s" % (lines, lu_row)
            lu_row = modfile.readline()
            lines = lines + 1
        #modclient.write(ddodata)
    except IOError:
        print "Error reading from input file."
    finally:
        modfile.close()
        ddoclient.close()
    #modclient.close()

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