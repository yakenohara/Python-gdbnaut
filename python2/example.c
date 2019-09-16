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

typedef enum week {
  Mon = 1,
  Tue,
  Wed,
  Thu,
  Fri,
  Sat = 11,
  Sun
}e_week;

volatile e_week gsym2_e_week = Tue;

void main(void){
    return;
}
