# Usage

`tester.xlsm` の Test processes をひとつずつ TRUE にして実施する  
最後のプロセス `Test tester_script_2_for_gdbnaut_nogdb.py` の項目を実施したら、  
`\0_expect\2_address_ignored` と `\2_output_files\2_address_ignored` との差分を確認する。  
(`\0_expect\~` が期待値。)

# Tested On

Set #1
 - gcc-core 7.4.0-1
 - gdb 8.1.1-1

Set #2
 - mingw-w64-x86_64-gcc 9.2.0-2
 - mingw-w64-x86_64-gdb 8.3-9

