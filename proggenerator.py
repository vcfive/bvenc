#!/usr/bin/env python

import os, argparse, re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('ifilename', help='Input file name')
parser.add_argument('ofilename', help='Output file name')
parser.add_argument('--decrypt', action='store_true', dest='flag_d', help='Create program for decrypting messages sent from other key')

args = parser.parse_args()


ifilename = args.ifilename
ofilename = args.ofilename
flag_d = args.flag_d or False


class ProgGenerator():
    def __init__(self, ifilename, ofilename, flag_d):
        self.ifilename = ifilename
        self.ofilename = ofilename
        self.flag_d = flag_d
        self.idstart = ['a',0]
        self.numcheck = re.compile('[0-9]+$')

    def load_input(self):
        h = open(self.ifilename, 'r')
        self.lines = h.readlines()
        h.close()
        fractures = []
        fsize = 0
        for l in self.lines:
            if ':' in l:
                if fsize:
                    fractures.append(fsize)
                fsize = 0
            elif self.check_number(l):
                fsize += 1
        if fsize:
            fractures.append(fsize)
        self.fractures = fractures
        self.linecount = reduce(lambda x,y: x+y, fractures)
        nms = ""
        nms += "unsigned char * tpoint = malloc(sizeof(char)*%s);\n" % self.linecount
        nms += "unsigned char * incr = tpoint;\n"
        nms += "unsigned char * res = tpoint;\n"
        nms += "int oflag = 0;\n"
        nms += "int i = 0;\n"
        nms += "int sm = 1;\n"
        nms += "int * fractures = malloc(sizeof(int)*%s);\n" % len(fractures)
        i = 0
        for fz in fractures:
           nms += "fractures[%s] = %s;\n" % (i, fz)
           i += 1
        self.nms = nms
        
    def get_unique_id(self):
        a = self.idstart[0] + str(self.idstart[1])
        self.idstart[1] += 1
        return a

    def check_number(self,l):
        return self.numcheck.match(l) is not None

    def prepare_output(self):
        track = {"unclosed": False,
                 "counter": "",
                 "snumber": 0,
                 "sign": '+',
                 "shift": 0}
        acc = []
        for l in self.lines:
            l = l.strip()
            if ':' in l:
                if track["unclosed"]:
                    acc.append("%s++;" % track["counter"] )
                    acc.append("}")
                    if self.flag_d:
                        acc.append("incr = tpoint;")
                        acc.append("i = 0;")
                        acc.append("sm = 1;")
                        acc.append("while(i < fractures[%s]) {" % track["snumber"])
                        acc.append("if(i % 2 == 0){")
                        acc.append("sm = sm + *incr;")
                        acc.append("}")
                        acc.append("else {")
                        acc.append("sm = sm - *incr;")
                        acc.append("}")
                        acc.append("incr++;")
                        acc.append("i++;")
                        acc.append("}")
                        acc.append("i = 0;")
                        acc.append("incr = tpoint;")
                        acc.append("while(i < fractures[%s]) {" % track["snumber"])
                        acc.append("*incr = *incr - sm;")
                        acc.append("incr++;")
                        acc.append("i++;")
                        acc.append("}")
                    acc.append("tpoint = tpoint + fractures[%s];" % track["snumber"])
                    track["snumber"] += 1
                    track["unclosed"] = False
                num = int(l.split(':')[1])
                varname = self.get_unique_id()
                if not self.flag_d:
                    acc.append("incr = tpoint;")
                    acc.append("i = 0;")
                    acc.append("sm = 1;")
                    acc.append("while(i < fractures[%s]) {" % track["snumber"])
                    acc.append("if(i % 2 == 0){")
                    acc.append("sm = sm + *incr;")
                    acc.append("}")
                    acc.append("else {")
                    acc.append("sm = sm - *incr;")
                    acc.append("}")
                    acc.append("incr++;")
                    acc.append("i++;")
                    acc.append("}")
                    acc.append("i = 0;")
                    acc.append("incr = tpoint;")
                    acc.append("while(i < fractures[%s]) {" % track["snumber"])
                    acc.append("*incr = *incr + sm;")
                    acc.append("incr++;")
                    acc.append("i++;")
                    acc.append("}")
                acc.append("int %s = 0;" % varname )
                acc.append("while( %s < %s ) {" % (varname, num) )
                acc.append("incr = tpoint;")
                track["sign"] = l.split(':')[2]
                track["counter"] = varname
                track["unclosed"] = True
                track["shift"] = l.split(':')[3]
            elif self.check_number(l):
                acc.append("*incr = *incr %s %s;" % (track["sign"], l ) )
                acc.append("incr++;")
        if track["unclosed"]:
            acc.append("%s++;" % track["counter"] )
            acc.append("}")
            if self.flag_d:
                acc.append("incr = tpoint;")
                acc.append("i = 0;")
                acc.append("sm = 1;")
                acc.append("while(i < fractures[%s]) {" % track["snumber"])
                acc.append("if(i % 2 == 0){")
                acc.append("sm = sm + *incr;")
                acc.append("}")
                acc.append("else {")
                acc.append("sm = sm - *incr;")
                acc.append("}")
                acc.append("incr++;")
                acc.append("i++;")
                acc.append("}")
                acc.append("i = 0;")
                acc.append("incr = tpoint;")
                acc.append("while(i < fractures[%s]) {" % track["snumber"])
                acc.append("*incr = *incr - sm;")
                acc.append("incr++;")
                acc.append("i++;")
                acc.append("}")
        self.follower = "\n".join(acc) + "\n"

    
    def write_out(self):
        h = open(self.ofilename + '.temp.c', 'w')
        t = "#include <stdio.h>\n"
        t += "#include <stdlib.h>\n"
        t += "int main(int argc, char ** argv) {\n"
        #
        wr = "int ttl = 0;\n"
        wr += "if(argc != 2) return 1;"
        wr += "int max = atoi(argv[1]);\n"
        wr += "while(1){\n"
        wr += "tpoint = res;\n"
        wr += "int c = 0;\n"
        wr += "char* ch = tpoint;\n"
        wr += "char hold;\n"
        wr += "while(c < %s){\n" % self.linecount
        wr += "hold = getchar();\n"
        wr += "ttl++;"
        if not self.flag_d:
            wr += "if(ttl > max) oflag = 1;\n"
        wr += "*ch = hold;\n"
        wr += "ch++;\n"
        wr += "c++;\n"
        wr += "}\n"
        wr += "ch = tpoint;\n"
        #
        rw = "c = 0;\n"
        rw += "while(c < %s){\n" % self.linecount
        rw += "putchar(*ch);\n"
        if self.flag_d:
            rw += "if(ttl > max) oflag = 1;\n"
        rw += "ch++;\n"
        rw += "c++;\n"
        rw += "}\n"
        rw += "if(oflag==1) return 0;\n"
        rw += "}\n"
        rw += "return 0;\n"
        rw += "}\n"
        a = t + self.nms + wr + self.follower + rw
        h.write(a)
        h.close()

    def compile(self):
        s = subprocess.Popen(['gcc', self.ofilename + '.temp.c', '-o', self.ofilename])
        s.wait()
        s = subprocess.Popen(['rm', self.ofilename + '.temp.c'])
        s.wait()
        
if __name__=='__main__':
    pg = ProgGenerator(ifilename, ofilename, flag_d)
    pg.load_input()
    pg.prepare_output()
    pg.write_out()
    pg.compile()

