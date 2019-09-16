/*
gcc test.c -o test.exe -g -O0
gdb test.exe
break main
run
pi
import sys
sys.path.append('.')
import testpy
import json
print(testpy.func_get_json([
    "gsym0",
    "gsym1",
    "gsym2",
    "gsym3",
    "gsym4",
    "gsym4_p",
    "gsym4_pp",
    "gsym4t",
    "gsym4t_p",
    "gsym4t_pp",
    "gsym5",
    "gsym6_0",
    "gsym6_1",
    "gsym6_p",
    "gsym7",
    "gsym8"
    ]))
*/

struct typ_t0{
    char f0;
    char f1;
};
volatile struct typ_t0 gsym0 = {
    (-1),
    1
};

typedef struct typ_t1{
    char f0;
    char f1;
}typ_t1_t;
volatile typ_t1_t gsym1 = {
    (-2),
    2
};

typedef struct{
    char f0;
    char f1;
}typ_t2_t;
volatile typ_t2_t gsym2 = {
    (-3),
    3
};

typedef enum week {
  Mon = 1,
  Tue,
  Wed,
  Thu,
  Fri,
  Sat = 11,
  Sun
}week_e;
volatile week_e gsym3 = Tue;

volatile int gsym4 = (-1);
volatile int *gsym4_p = &gsym4;
volatile int **gsym4_pp = &gsym4_p;

typedef unsigned int   t_uint32;

volatile t_uint32 gsym4t = (-2);
volatile t_uint32 *gsym4t_p = &gsym4t;
volatile t_uint32 **gsym4t_pp = &gsym4t_p;


volatile int gsym5[2] = {(-1), 1};

volatile int gsym6_0 = (-1);
volatile int gsym6_1 = (-2);
volatile int *gsym6_p[2] = {
    &gsym6_0,
    &gsym6_1
};

struct typ_t7{
    char f0;
    char f1;
};
volatile struct typ_t7 gsym7[2] = {
    {
        (-1),
        1
    },{
        (-2),
        2
    }
};
typedef struct typ_t8{
    char f0;
    char f1;
}typ_t8_t;
volatile typ_t8_t gsym8[2] = {
    {
        (-1),
        1
    },{
        (-2),
        2
    }
};

typedef unsigned int   t_uint32;
typedef unsigned short t_uint16;
typedef unsigned char  t_uint08;

typedef union un_0_0{
    t_uint16     sym0_t_uint16;
    t_uint08     sym1_t_uint08[2];
}t_un_0_0;

typedef struct st_0_1{
    t_uint08     :4;
    t_uint08     sym1_t_uint08:1;
    t_uint08     sym2_t_uint08:1;
    t_uint08     sym3_t_uint08:1;
    t_uint08     :1;
}t_st_0_1;

typedef struct st_0{
    t_un_0_0     sym0_t_un_0_0[2];
    t_uint32     sym1_t_uint32;
    t_st_0_1     sym2_t_st_0_1[2];
}t_st_0;

volatile t_st_0 gsym0_t_st_0[2] = {
    {   //   index [0] -------------------------
        {
            4080,   //sym0_t_un_0_0[0] -> sym0_t_uint16
            61455   //sym0_t_un_0_0[1] -> sym0_t_uint16
        },
        252645135,  //sym1_t_uint32
        {
            {
                1,  //sym2_t_st_0_1[0] -> sym1_t_uint08
                0,  //sym2_t_st_0_1[0] -> sym2_t_uint08
                1   //sym2_t_st_0_1[0] -> sym3_t_uint08
            },{
                0,  //sym2_t_st_0_1[1] -> sym1_t_uint08
                1,  //sym2_t_st_0_1[1] -> sym2_t_uint08
                0   //sym2_t_st_0_1[1] -> sym3_t_uint08
            }
        }
    },{ //   index [1] -------------------------
        {
            4080,   //sym0_t_un_0_0[0] -> sym0_t_uint16
            61455   //sym0_t_un_0_0[1] -> sym0_t_uint16
        },
        252645135,  //sym1_t_uint32
        {
            {
                1,  //sym2_t_st_0_1[0] -> sym1_t_uint08
                0,  //sym2_t_st_0_1[0] -> sym2_t_uint08
                1   //sym2_t_st_0_1[0] -> sym3_t_uint08
            },{
                0,  //sym2_t_st_0_1[1] -> sym1_t_uint08
                1,  //sym2_t_st_0_1[1] -> sym2_t_uint08
                0   //sym2_t_st_0_1[1] -> sym3_t_uint08
            }
        }
    }
};
typedef struct st_a{
    char   sym0_ch;
    short  sym1_sh;
    int    sym2_it;
    long   sym3_lg;
    float  sym4_fl;
    double sym5_dl;
}t_st_a;
struct st_a gsym1_t_st_a = {
    'a',   //sym0_ch
    1,     //sym1_sh
    2,     //sym2_it
    3,     //sym3_lg
    11.2F, //sym4_fl
    22.4F  //sym5_dl
};

void main(void){
    return;
}
