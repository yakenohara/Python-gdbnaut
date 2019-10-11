# attributes

| attribute name | description |
| :------------- | :---------- |
| identifier     |             |
| address        |             |
| size           |             |
| type_code      |             |
| type_declared  |             |
| type_primitive |             |
| value          |             |
| dump           |             |

## special attributes for fields of struct and union 

| attribute name | description |
| :------------- | :---------- |
| bitpos         |             |
| bitsize        |             |

## special attributes for fields of enum

| attribute name | description |
| :------------- | :---------- |
| enum_dict      |             |

# limitation

 - `type_primitive` は信用しないほうがいい
 - 配列、pointer の場合は strip_typedefs() できない
  
 - C でしか動確してないよ

 - デバッグ対象の実行ファイルのパスに ASCII 以外の文字が含まれている場合、  
   `gdb.execute("info sybool 0x??????",False,True)` でコケる