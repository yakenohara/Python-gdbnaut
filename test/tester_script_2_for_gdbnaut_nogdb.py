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

# gdbnaut をインポートするため、カレントディレクトリが
# "~\Python-gdbnaut\test" にしてから、この相対パスを指定する
sys.path.append('..')
import gdbnaut_nogdb

str_symbol_name = sys.argv[1]
str_in_path     = sys.argv[2]
str_out_path    = sys.argv[3]

dict_info = gdbnaut_nogdb.SymbolInfo(str_in_path)
dict_info.save_as(
    file_path=str_out_path,
    do_sort=True
)

