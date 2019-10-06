# -*- coding: utf-8 -*-

# gdb "D:\Python-gdbnaut\test\input_files\1_bebug_builds\001_global_char.exe" -ex 'set $to_import_path = "D:\Python-gdbnaut\"' -ex 'set $symbol_name = "symbolname"' -x "D:\Python-gdbnaut\test\0.py"

# pathoftargetbin:
# targetbin:
# symbolname:
# pathofthisscript:
# ```
# # gdb pathoftargetbin -ex "set $symbol_name = \"symbolname"" -x pathofthisscript
# ```

import re
import sys

import os
# print(os.path.abspath("."))


# print(sys.path)
# sys.path.append('../../..')
# print(sys.path)
# import gdbnaut

def fnc_get_arg(str_arg_name):
    """
    GDB の Convenience variable に引数として格納した文字列を取得する
    """

    # 2nd argment: user invoking interactively を指定しない
    # 3rd argment: 実行結果を standard out ではなく string として返却させる)
    str_out = gdb.execute("print " + str_arg_name, False, True)
    str_ret = None
    itr_found = re.finditer(r'".+"', str_out)
    for itr_found_elem in itr_found:
        str_ret = str_out[(itr_found_elem.start()+1):(itr_found_elem.end()-1)] # `"` で囲まれた文字列が argumment
        break

    return str_ret

str_to_import_path = fnc_get_arg("$to_import_path")
str_symbol_name    = fnc_get_arg("$symbol_name")

if ( # 引数が見つからない場合
    (str_to_import_path is None) or 
    (str_symbol_name is None)
    ):

    sys.stderr.write(
        "[error] Script invoked without required argument(s)." + "\n"
    )

    gdb.execute('quit') # 終了
    exit

print(('str_to_import_path:' + str_to_import_path))
print(('str_symbol_name:' + str_symbol_name))

print('__file__:' +(os.path.basename(__file__)))
print('abspath:' + (os.path.abspath(os.path.basename(__file__))))
print('abspath2:' + (os.path.abspath(__file__)))

try:
    print(sys.path)
    sys.path.append(str_to_import_path)
    print(sys.path)
    import gdbnaut

except Exception as e:
    sys.stderr.write(
        "[error] " + str(e) + "\n"
    )
    gdb.execute('quit') # 終了
    exit

print("<start>")
gdb.execute('break main')
gdb.execute('run')



# gdb.execute('quit') 時に 質問されたくないので、 最後まで実行する
gdb.execute('continue')

print("<end>")
gdb.execute('quit')
exit