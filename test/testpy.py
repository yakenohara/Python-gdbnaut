# -*- coding: utf-8 -*-

import gdb
import json

def func_test(str_symbol_name):
    print("<str_symbol_name>")
    print(str_symbol_name)
    
    gdbval_target = gdb.lookup_symbol(str_symbol_name)[0].value()
    gdbtyp_target = gdbval_target.type
    
    gdbtyp_target_unqualified = gdbtyp_target.unqualified()
    gdbtyp_target_stripped = gdbtyp_target.strip_typedefs()
    gdbtyp_target_unqualified_stripped = gdbtyp_target.unqualified().strip_typedefs()
    gdbtyp_target_stripped_unqualified = gdbtyp_target.strip_typedefs().unqualified()

    obj_ret = {
        "str":str(gdbtyp_target),
        ".name":str(gdbtyp_target.name),
        "unqalified_str":str(gdbtyp_target_unqualified),
        "unqalified_.name":str(gdbtyp_target_unqualified.name),
        "stripped_str":str(gdbtyp_target_stripped),
        "stripped.name":str(gdbtyp_target_stripped.name),
        "unqalified_stripped_str":str(gdbtyp_target_unqualified_stripped),
        "unqalified_stripped_.name":str(gdbtyp_target_unqualified_stripped.name),
        "stripped_unqalified_str":str(gdbtyp_target_stripped_unqualified),
        "stripped_unqalified_.name":str(gdbtyp_target_stripped_unqualified.name)
    }

    return obj_ret

def func_test2(obj_symbol_name):
    obj_ret = {}

    if(isinstance(obj_symbol_name,list)): # list の場合
        for str_symbol_name in obj_symbol_name:
            obj_out = func_test(str_symbol_name)
            obj_ret[str_symbol_name] = obj_out

    else: # list ではない場合
        obj_out = func_test(obj_symbol_name)
        obj_ret[obj_symbol_name] = obj_out

    return obj_ret


def func_get_json(obj_symbol_name):
    obj_out = func_test2(obj_symbol_name)
    str_ret = json.dumps(obj_out, indent=4)

    return str_ret
