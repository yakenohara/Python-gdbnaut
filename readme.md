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

 - C でしか動確してないよ

 - デバッグ対象の実行ファイルのパスに ASCII 以外の文字が含まれている場合、  
   `gdb.execute("info sybool 0x??????",False,True)` でコケる

# Known issues

## Real name in typedef expression

 - 配列宣言とポインタ変数宣言に対しては、Real name を取得できない  

   mingw-w64-x86_64-gcc 9.2.0-2 & mingw-w64-x86_64-gdb 8.3-9 環境、  
   gcc-core 7.4.0-1 & gdb 8.1.1-1 環境 で発生。

 - struct, union, enum に対する typedef を使用した変数を宣言しても、Real name を取得できない  

   例えば、`typedef struct st_name{ char c; int i; }st;` のように宣言していた場合、  
   `type_primitive` の値は `struct st_name` になるべきだけど、`st` となってしまう。

   gcc-core 7.4.0-1 & gdb 8.1.1-1 環境で発生。  
   GDBが返す gdb.Type オブジェクトの .name 属性が `None` になってしまうために発生する。  