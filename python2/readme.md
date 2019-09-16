# デバッグビルド
なぜか `i686-w64-mingw32-gcc` にやらせると gdb でダメ
```
gcc example.c -o example.exe -g -O0
```

# 実行
```
gdb example.exe -x example.py
```

# todo

 - gdb.Type が pointer の場合
 - 不明な gdb.Type のハンドリング
 - gdb.Value.name が `None` を返してきた場合のハンドリング
 