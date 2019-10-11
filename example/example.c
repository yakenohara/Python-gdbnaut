/* compile by following

```
> gcc example.c -o example.exe -g -O0
> gdb example.exe -x example.py
```

*/

#include <stdio.h>

typedef unsigned char  uint08;
typedef unsigned int   uint32;
typedef int            sint32;

typedef union{
    uint32     bits;
    sint32     bits_singed;
}uni;

typedef struct{
    uint08    :4; //padding
    uint08    b1:1;
    uint08    b2:1;
    uint08    b3:1;
    uint08    :1;  //padding
    uni       bits_32;
}st;

volatile const st bits_35 = {
    1,
    0,
    1,
    {
        (-1)
    }
};

int main(void){
    printf("%d", bits_35.bits_32.bits_singed);
    return 0;
}
