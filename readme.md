  
# limitation

 - `type_primitive` は信用しないほうがいい
 - C でしか動確してないよ
 - 配列、pointer の場合は strip_typedefs() できない
 - デバッグ対象の実行ファイルのパスに ASCII 以外の文字が含まれている場合、  
   `gdb.execute("info sybool 0x??????",False,True)` でコケる