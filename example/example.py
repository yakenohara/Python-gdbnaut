# -*- coding: utf-8 -*-

import gdb
import re
import sys
import os

# gdbnaut をインポートするため、カレントディレクトリが
# "~\Python-gdbnaut\test" にしてから、この相対パスを指定する
sys.path.append('..')
import gdbnaut

sym_name = "bits_35"
out_path = "example.json"

gdb.execute('break main')
gdb.execute('run')

dict_info = gdbnaut.SymbolInfo(sym_name) # Scan
dict_info.save_as(out_path)              # Save as json file

# gdb.execute('quit') 時に 質問されたくないので、 最後まで実行する
gdb.execute('continue')

gdb.execute('quit')
exit