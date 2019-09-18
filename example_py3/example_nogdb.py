#coding:utf-8
import json
import sys
sys.path.append('..')
import gdbnaut_nogdb


cls_symbol_info = gdbnaut_nogdb.SymbolInfo('out_obj_traversed.json')

cls_symbol_info.save_as(
    file_path='out_sorted_obj_traversed.json',
    do_sort=True
)
cls_symbol_info.save_as(
    file_path='out_sorted_obj_traversed_attr.json',
    attr=[
        "identifier",
        "value"
    ],
    do_sort=True
)
cls_symbol_info.save_as(
    file_path='out_sorted_obj_traversed_attr_scrape.json',
    attr=[
        "type_code",
        "type_primitive"
    ],
    scrape=True,
    do_sort=True
)
cls_symbol_info.save_as(
    file_path='out_sorted_obj_traversed_dump_only_1stL.json',
    dump_only_1stL=True,
    do_sort=True
)

sorted_result = cls_symbol_info.info(
    do_sort=True
)

cls_symbol_info = gdbnaut_nogdb.SymbolInfo(sorted_result)

mytraversed = ""
def clb(obj, hie):
    global mytraversed
    str_hie = ""
    for tmp in hie:
        str_hie += "->" + str(tmp["identifier"])
    mytraversed += str_hie + '\n'

cls_symbol_info.traverse(clb)

file = open('out_sorted_mytraversed.json', 'w')
file.write(mytraversed)
file.close()
