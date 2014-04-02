import argparse
import os, sys, subprocess, base64


parser = argparse.ArgumentParser()
parser.add_argument("prog", help="(En/De)cryption Program")
parser.add_argument("infile", help="Input file")
parser.add_argument("outfile", help="Output file")
parser.add_argument("filesize", help="File size")
parser.add_argument("--decrypt", dest="decrypt", action="store_true", help="Decryption flag")
parser.add_argument("-blocksize", dest="blocksize", help="Buffer size")
args = parser.parse_args()

prog = args.prog
infile = args.infile
outfile = args.outfile
filelength = int(args.filesize)
blocksize = int(args.blocksize) or 9000


ecommand = [prog, str(blocksize)]

if args.decrypt:
    print "Decrypting %s... " % infile
else:
    print "Encrypting %s... " % infile

instring = open(infile, 'rb').read()


cl = filelength
while( (cl  % blocksize) != 0):
    cl += 1

a = "\x00" * (cl - filelength)
instring += a

ostring = ""
trailer = 0

while (trailer < cl):
    h1 = subprocess.Popen(ecommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    h1.stdin.write(instring[trailer:trailer+blocksize])
    a = h1.communicate()
    ostring += a[0][:blocksize]
    trailer += blocksize
    h1.stdin.close()
    h1.stdout.close()

if args.decrypt:
    ostring = ostring[:filelength]
    print "%s bytes decrypted" % filelength
else:
    print "%s bytes encrypted." % filelength

print "Writing to %s" % outfile

a = open(outfile,'wb')
a.write(ostring)
a.close()



