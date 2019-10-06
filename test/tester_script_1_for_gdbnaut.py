# -*- coding: utf-8 -*-

#
# 以下コマンドで起動する
# ```
# cd /d "~\Python-gdbnaut\test" && gdb "~.exe" -ex "set $symbol_name = \"symbolname\"" -ex "set $out_path = \"outpath\"" -x "~\Python-gdbnaut\test\tester.py"
# ```
#
# note
# 
# - `cd /d "~\Python-gdbnaut\test"`
#   
#   このスクリプトで `sys.path.append('..')` -> `import gdbnaut` する為に、  
#   このスクリプトの配置されているディレクトリに cd する
#   
# - `-ex "set $symbol_name = \"symbolname\""`
#   
#   `-ex` に指定する コマンドは `"` で囲む。 
#   `'` で囲めば、`-ex 'set $symbol_name = "symbolname"'` のように、`"` に対するエスケープが不要になるけど、
#   この記法は mingw-w64-x86_64-gdb 8.3-9 でコケる (`No such file or directory. Undefined command: "".  Try "help".` になる)
#   
# - `-x "~\Python-gdbnaut\test\tester.py"`
#   
#   このスクリプトファイル
#

import gdb
import re
import sys
import os

# gdbnaut をインポートするため、カレントディレクトリが
# "~\Python-gdbnaut\test" にしてから、この相対パスを指定する
sys.path.append('..')
import gdbnaut

def fnc_get_arg(str_arg_name):
    """
    GDB の Convenience variable に引数として格納した文字列を取得する
    """

    # 2nd argment: user invoking interactively を指定しない
    # 3rd argment: 実行結果を standard out ではなく string として返却させる)
    str_out = gdb.execute(("print " + str_arg_name), False, True)
    str_ret = None
    itr_found = re.finditer(r'".+"', str_out)
    for itr_found_elem in itr_found:
        str_ret = str_out[(itr_found_elem.start()+1):(itr_found_elem.end()-1)] # `"` で囲まれた文字列が argumment
        break

    return str_ret

str_symbol_name = fnc_get_arg("$symbol_name") # 解析対象シンボル名の取得
str_out_path    = fnc_get_arg("$out_path")    # 出力先ファイルパスの取得

# print("str_symbol_name:" + str_symbol_name)
# print("str_out_path:" + str_out_path)

if ( # 引数が見つからない場合
    (str_symbol_name is None) or
    (str_out_path is None)
    ):

    sys.stderr.write(
        "[error] Script invoked without required argument(s)." + "\n"
    )

    gdb.execute('quit') # 終了
    exit

print("<start>")
gdb.execute('break main')
gdb.execute('run')

dict_info = gdbnaut.SymbolInfo(str_symbol_name)
dict_info.save_as(str_out_path)

# gdb.execute('quit') 時に 質問されたくないので、 最後まで実行する
gdb.execute('continue')

print("<end>")
gdb.execute('quit')
exit