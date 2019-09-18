# -*- coding: utf-8 -*-

import sys
sys.path.append('..') #note
                     # <- これをしないで `import gdbnaut` すると、
                     #    GDB 内の Python interpreter では `ImportError` になる
                     #    同階層に gdbnaut.py を配置した場合でも、`sys.path.append('.')` が必要になる
import gdbnaut

import sys
import gdb
import json

sys.stdout.write('preparing\n')
gdb.execute('break main')
gdb.execute('run')

sys.stdout.write('start\n')

cls_symbol_info = gdbnaut.SymbolInfo([
    "gsym0_t_st_0",
    "gsym0_t_st_0",
    "gsym1_t_st_a",
    "gsym2_e_week",
    "gsym4_pp",
    "gsym1_t_st_b",
    "main_p",
    "funcpvol",
    "main_p"
])

obj_traversed = cls_symbol_info.info()

outstr = json.dumps(obj_traversed, indent=4)

file = open('out_obj_traversed.json', 'w')
file.write(outstr)
file.close()

obj_traversed = cls_symbol_info.info([
    "identifier",
    "value"
])
outstr = json.dumps(obj_traversed, indent=4)
file = open('out_obj_traversed_attr.json', 'w')
file.write(outstr)
file.close()

obj_traversed = cls_symbol_info.info([
    "type_code",
    "type_primitive"
], scrape=True)
outstr = json.dumps(obj_traversed, indent=4)
file = open('out_obj_traversed_attr_scrape.json', 'w')
file.write(outstr)
file.close()


obj_traversed = cls_symbol_info.info(dump_only_1stL=True)
outstr = json.dumps(obj_traversed, indent=4)
file = open('out_obj_traversed_dump_only_1stL.json', 'w')
file.write(outstr)
file.close()

mytraversed = ""
def clb(obj, hie):
    global mytraversed
    str_hie = ""
    for tmp in hie:
        str_hie += "->" + str(tmp["identifier"])
    mytraversed += str_hie + '\n'

cls_symbol_info.traverse(clb)

file = open('out_mytraversed.json', 'w')
file.write(mytraversed)
file.close()

sys.stdout.write('end\n')

gdb.execute('quit')