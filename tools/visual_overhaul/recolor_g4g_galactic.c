#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ns/container.h"
#include "palette.h"

static bool Eq(const struct ResourceName *n,const char *s){
    char b[RES_NAME_LENGTH+1]={0};
    memcpy(b,n->asChars,RES_NAME_LENGTH);
    return strcmp(b,s)==0;
}
static bool In(const struct ResourceName *n,const char **names,size_t count){
    for(size_t i=0;i<count;i++) if(Eq(n,names[i])) return true;
    return false;
}
static unsigned Clamp(int v){ return v<0?0:(v>31?31:(unsigned)v); }

static struct NDSColor Grade(struct NDSColor c,int strength){
    int max=c.r; if(c.g>max)max=c.g; if(c.b>max)max=c.b;
    int min=c.r; if(c.g<min)min=c.g; if(c.b<min)min=c.b;
    int avg=(c.r+c.g+c.b)/3;

    if(max-min<=3 && avg>=7 && avg<=28){
        c.r=Clamp((int)c.r-strength);
        c.b=Clamp((int)c.b+strength);
    }
    if(c.r>=c.g+2 && c.g>=c.b+2 && c.r>=16){
        c.r=Clamp((int)c.r-strength);
        c.g=Clamp((int)c.g-1);
        c.b=Clamp((int)c.b+strength);
    }
    if(c.r>=20 && c.g>=18 && c.b<=14){
        c.r=Clamp((int)c.r-1);
        c.g=Clamp((int)c.g-strength);
        c.b=Clamp((int)c.b+1);
    }
    return c;
}

static struct NDSColor WarehouseGrade(struct NDSColor c){
    c=Grade(c,1);
    if(c.g>=c.r+3 && c.g>=c.b+2 && c.g>=14){
        c.g=Clamp((int)c.g-1);
        c.b=Clamp((int)c.b+1);
    }
    return c;
}

int main(int argc,char **argv){
    if(argc!=4){fprintf(stderr,"usage: %s main|lab|warehouse IN OUT\n",argv[0]);return 2;}
    const char *mainNames[]={
        "ginga1","m_dun26_01","m_dun26_02","m_dun26_04","m_dun26_06",
        "m_dun26_10","m_dun26_16","m_dun26_19","m_dun26_30","m_dun26_31",
        "m_dun26_32","m_dun26_35","m_dun26_36","m_dun26_36_2","m_dun26_37",
        "m_dun26_38","map_dun26_05","saku","table_l01","z"
    };
    const char *labNames[]={
        "m_dun26_19","m_dun26_23","m_dun26_25","m_dun26_26","m_dun26_27"
    };
    const char *warehouseNames[]={
        "carpet04_1","carpet04_2","carpet05_1","carpet05_2",
        "counter_b01","counter_b02","counter_g01","counter_g02",
        "floor01","floor03","floor04","floor_b01","floor_b02",
        "libra_01","libra_02","libra_03","libra_04","libra_05",
        "m_comp_01","m_comp_02","m_muse_01","m_muse_03","m_muse_04",
        "m_muse_05","m_muse_06","phouse_01","phouse_03","scho_01","scho_02",
        "shikii_b01","shouse_02","shouse_03","shouse_04",
        "wall03","wall04","wall05","wall_b01"
    };

    bool mainProfile=strcmp(argv[1],"main")==0;
    bool labProfile=strcmp(argv[1],"lab")==0;
    bool warehouseProfile=strcmp(argv[1],"warehouse")==0;
    if(!mainProfile&&!labProfile&&!warehouseProfile){fprintf(stderr,"bad profile\n");return 2;}

    FILE *f=fopen(argv[2],"rb"); if(!f)return 3;
    struct NSContainer c={0};
    int rc=NSContainer_ReadFromFile(&c,f); fclose(f); if(rc)return rc;
    struct NSChunkTex *chunk=c.chunks[0].texChunk;
    int pals=0,colors=0;

    for(int i=0;i<chunk->palettes.n;i++){
        struct Palette *p=&VecGet(chunk->palettes,i);
        bool target=
            (mainProfile && In(&p->name,mainNames,sizeof(mainNames)/sizeof(mainNames[0]))) ||
            (labProfile && In(&p->name,labNames,sizeof(labNames)/sizeof(labNames[0]))) ||
            (warehouseProfile && In(&p->name,warehouseNames,sizeof(warehouseNames)/sizeof(warehouseNames[0])));
        if(!target) continue;
        int pc=0;
        for(int j=0;j<p->numColors;j++){
            struct NDSColor before=p->data[j];
            struct NDSColor after=warehouseProfile?WarehouseGrade(before):Grade(before,1);
            if(before.r!=after.r||before.g!=after.g||before.b!=after.b){
                p->data[j]=after; pc++; colors++;
            }
        }
        if(pc){pals++; printf("%.*s: %d\n",RES_NAME_LENGTH,p->name.asChars,pc);}
    }

    FILE *o=fopen(argv[3],"wb"); if(!o){NSContainer_Free(&c);return 4;}
    rc=NSContainer_WriteToFile(&c,o); fclose(o); NSContainer_Free(&c);
    if(rc)return rc;
    printf("%s: %d palettes / %d colors\n",argv[1],pals,colors);
    if((mainProfile&&pals<8)||(labProfile&&pals<4)||(warehouseProfile&&pals<12)) return 5;
    return 0;
}
