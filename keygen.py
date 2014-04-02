#!/usr/bin/env python

import os, argparse, re
import random
import itertools

parser = argparse.ArgumentParser()
parser.add_argument('key1', help="First key")
parser.add_argument('key2', help="Second key")
parser.add_argument('-fs',dest='fragment_size', help='Fragment Size')
parser.add_argument('-l', dest='length', help='Length')

args = parser.parse_args()

fragment_size = args.fragment_size or "4-12"
length = args.length or 3000


ubound = int(fragment_size.split('-')[0])
tbound = int(fragment_size.split('-')[1])
length = int(length)
assert(ubound % 2 == 0)
assert(tbound % 2 == 0)
assert(length > 100)



primes = [2,3,5,7,11,13,17]
limit = range(112)


k1 = []
k2 = []


def choosePrimes():
    r1 = []
    r2 = []
    r1 = random.sample(primes, 2)
    r2 = random.sample(r1, 1)
    out = [r1,r2]
    random.shuffle(out)
    return out

divisions = []
poss = range(ubound, tbound, 2)

while(length > 0):
    s = a = random.choice(poss)
    while(s > 0 and length > 0):
        s -= 1
        length -= 1
    if length != 0:
        divisions.append(a)
    else:
        divisions.append(a-s)

for div in divisions:
    a,b = choosePrimes()
    at = reduce(lambda x,y: x*y, a)
    bt = reduce(lambda x,y: x*y, b)
    if at > bt:
        tall = True
        u = set(a) - set(b)
        u = list(u)[0]
    else:
        tall = False
        u = set(b) - set(a)
        u = list(u)[0]
    w = ['+','-']
    random.shuffle(w)
    offset = random.choice(primes)
    k1.append(':'+ str(at) + ':' + w[0] + ':' + str(offset))
    k2.append(':'+ str(bt) + ':' + w[1] + ':' + str(offset))
    ls = map(lambda x: x*offset, limit)
    if tall:
        for i in range(div):
            l = random.choice(ls)
            k1.append(l % 256)
            k2.append(l*u % 256)
    else:
        for i in range(div):
            l = random.choice(ls)
            k1.append(l*u % 256)
            k2.append(l % 256)

k1 = map(lambda x: str(x), k1)
k2 = map(lambda x: str(x), k2)
key1 = "\n".join(k1)
key2 = "\n".join(k2)

key1h = open(args.key1,'w')
key2h = open(args.key2,'w')

key1h.write(key1)
key2h.write(key2)

    
