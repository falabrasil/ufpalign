#!/usr/bin/env python
#
# author: nov 2020
# cassio batista - https://cassota.gitlab.io

# https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value

import sys
import os
from itertools import zip_longest

if __name__ == '__main__':
    fb_map, ds_map = {}, {}
    for filename in ('ali_male.mm', 'ali_female.mm'):
        with open('workspace/%s' % filename) as f:
            m2m = f.readlines()
        for i, ali in enumerate(m2m):
            ds, fb = ali.split()
            for p in fb.split('|')[:-1]:
                if ':' in p:
                    if p in fb_map.keys():
                        fb_map[p] += 1
                    else:
                        fb_map[p] = 1
            for p in ds.split('|')[:-1]:
                if ':' in p:
                    if p in ds_map.keys():
                        ds_map[p] += 1
                    else:
                        ds_map[p] = 1

print('%+10s\t\t%+10s' % ('Dataset', 'FalaBrasil'))
print('-------------------------------------')
for i, (ds, fb) in enumerate(zip_longest(
        sorted(ds_map.items(), key=lambda item: item[1], reverse=True),
        sorted(fb_map.items(), key=lambda item: item[1], reverse=True))):
    ds_k, ds_v = None, 0
    if ds is not None:
        ds_k, ds_v = ds
    fb_k, fb_v = None, 0
    if fb is not None:
        fb_k, fb_v = fb
    print('%-8s %s\t\t%-8s %s' % (ds_k, ds_v, fb_k, fb_v))
