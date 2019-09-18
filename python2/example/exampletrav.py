#coding:utf-8
import json
import sys
sys.path.append('..')
import gdbnauttrav


f = open('out_obj_traversed.json', 'r')
jsonData = json.load(f)
f.close()
cls_symbol_info = gdbnauttrav.SymbolInfo(jsonData)

sorted_result = cls_symbol_info.scrape_copy(
    do_sort=True
)
outstr = json.dumps(sorted_result, indent=4)
file = open('out_sorted_obj_traversed.json', 'w')
file.write(outstr)
file.close()

sorted_result = cls_symbol_info.scrape_copy(
    [
        "identifier",
        "value"
    ],
    do_sort=True)
outstr = json.dumps(sorted_result, indent=4)
file = open('out_sorted_obj_traversed_attr.json', 'w')
file.write(outstr)
file.close()

sorted_result = cls_symbol_info.scrape_copy(
    [
        "type_code",
        "type_primitive"
    ],
    scrape=True,
    do_sort=True
)
outstr = json.dumps(sorted_result, indent=4)
file = open('out_sorted_obj_traversed_attr_scrape.json', 'w')
file.write(outstr)
file.close()

sorted_result = cls_symbol_info.scrape_copy(
    dump_only_1stL=True,
    do_sort=True
)
outstr = json.dumps(sorted_result, indent=4)
file = open('out_sorted_obj_traversed_dump_only_1stL.json', 'w')
file.write(outstr)
file.close()

sorted_result = cls_symbol_info.scrape_copy(
    do_sort=True
)

cls_symbol_info = gdbnauttrav.SymbolInfo(sorted_result)

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
