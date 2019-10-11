# -*- coding: utf-8 -*-

#
# 以下コマンドで起動する
# ```
# cd /d "~\Python-gdbnaut\test" && python "~/.py" "symbol_name" "in_path" "out_path"
# ```
#
# note
# 
# - `cd /d "~\Python-gdbnaut\test"`
#   
#   このスクリプトで `sys.path.append('..')` -> `import gdbnaut` する為に、  
#   このスクリプトの配置されているディレクトリに cd する
#

import sys
import collections

# gdbnaut をインポートするため、カレントディレクトリが
# "~\Python-gdbnaut\test" にしてから、この相対パスを指定する
sys.path.append('..')
import gdbnaut_nogdb

str_symbol_name = sys.argv[1]
str_in_path     = sys.argv[2]
str_out_path    = sys.argv[3]

dict_adr = collections.OrderedDict()
int_id = 0
str_pref = "ADR_ID_"
str_adr_fmt = '{:04X}'

def func_substitute_adr(obj_target, tpl_hierarchy):

    global dict_adr
    global int_id

    if ( "address" in obj_target):

        if (obj_target["address"] in dict_adr):
            obj_target["address"] = dict_adr[obj_target["address"]]
            
        else:
            str_substituted_adr = (str_pref + str_adr_fmt.format(int_id))
            int_id += 1
            dict_adr[obj_target["address"]] = str_substituted_adr
            obj_target["address"] = str_substituted_adr


    if ( "dump" in obj_target ):
    
        dict_substituted_dump = collections.OrderedDict()
        
        for str_key, mem_image in obj_target["dump"].items():
            
            if (str_key in dict_adr):
                dict_substituted_dump[dict_adr[str_key]] = mem_image
                
            else:
                str_substituted_adr = (str_pref + str_adr_fmt.format(int_id))
                int_id += 1
                dict_substituted_dump[str_substituted_adr] = mem_image
                dict_adr[str_key] = str_substituted_adr
                
        obj_target["dump"] = dict_substituted_dump
            
    
    # pointer 変数の場合
    if (obj_target["type_code"] == gdbnaut_nogdb.gdb.TYPE_CODE_PTR):
        
        if ( obj_target["value"] in dict_adr):
            obj_target["value"] = dict_adr[obj_target["value"]]
            
        else:
            str_substituted_adr = (str_pref + str_adr_fmt.format(int_id))
            int_id += 1
            dict_adr[obj_target["value"]] = str_substituted_adr
            obj_target["value"] = str_substituted_adr

dict_info = gdbnaut_nogdb.SymbolInfo(str_in_path)
dict_info.traverse(func_substitute_adr)
dict_info.save_as(
    file_path=str_out_path
)
