# -*- coding: utf-8 -*-

import sys
sys.path.append('.') #note
                     # <- これをしないで `import variable_tree` すると、
                     #    GDB 内の Python interpreter では `ImportError` になる
import variable_tree

import sys
import gdb
import json

sys.stdout.write('preparing\n')
gdb.execute('break main')
gdb.execute('run')

sys.stdout.write('start\n')

obj_traversed = variable_tree.func_make_variable_tree("gsym0_t_st_0")
#obj_traversed = variable_tree.func_make_variable_tree("gsym1_t_st_a")
#obj_traversed = variable_tree.func_make_variable_tree("gsym2_e_week")


outstr = json.dumps(obj_traversed, indent=4)

file = open('out.json', 'w')
file.write(outstr)
file.close()

sys.stdout.write('end\n')

gdb.execute('quit')