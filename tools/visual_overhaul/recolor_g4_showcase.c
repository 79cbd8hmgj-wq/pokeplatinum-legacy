#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ns/container.h"
#include "palette.h"

static bool Eq(const struct ResourceName *n,const char *s){
    char b[RES_NAME_LENGTH+1]={0}; memcpy(b,n->asChars,RES_NAME_LENGTH); return strcmp(b,s)==0;
}
static bool In(const struct ResourceName *n,const char **names,size_t count){
    for(size_t i=0;i<count;i++) if(Eq(n,names[i])) return true; return false;
}
static bool Green(struct NDSColor c){ return c.g>=16 && c.g>=c.r+3 && c.g>=c.b+2; }
static struct NDSColor GreenGrade(struct NDSColor c){
    unsigned avg=(c.r+2*c.g+c.b)/4;
    c.r=((3*c.r+avg)/4)*90/100;
    c.g=((3*c.g+avg)/4)*90/100;
    c.b=((3*c.b+avg)/4)*90/100;
    return c;
}
static bool BlueWater(struct NDSColor c){ return c.b>=20 && c.b>=c.g+3 && c.g>=12; }
static struct NDSColor WaterGrade(struct NDSColor c){
    if(c.g>1)c.g-=1;
    if(c.r<29)c.r+=1;
    if(c.b<31)c.b+=1;
    return c;
}
int main(int argc,char **argv){
    if(argc!=4){fprintf(stderr,"usage: %s spear|lakes IN OUT\n",argv[0]);return 2;}
    const char *greenNames[]={"beachp","blueglayp","ckado","criff2","enccriff","fenter","grass","hage","lgreen","lgreenp","nectgrass","nhana","nsandp","rhana","sandset","shana","tshadow"};
    const char *waterNames[]={"lake","lakep.1_pl","puddle","puddle_b","puddlep","sea","taki"};
    bool lakes=strcmp(argv[1],"lakes")==0, spear=strcmp(argv[1],"spear")==0;
    if(!lakes&&!spear){fprintf(stderr,"bad profile\n");return 2;}
    FILE *f=fopen(argv[2],"rb"); if(!f)return 3;
    struct NSContainer c={0}; int rc=NSContainer_ReadFromFile(&c,f); fclose(f); if(rc)return rc;
    struct NSChunkTex *chunk=c.chunks[0].texChunk; int pals=0,colors=0;
    for(int i=0;i<chunk->palettes.n;i++){
        struct Palette *p=&VecGet(chunk->palettes,i); int pc=0;
        bool greenPal=In(&p->name,greenNames,sizeof(greenNames)/sizeof(greenNames[0]));
        bool waterPal=lakes && In(&p->name,waterNames,sizeof(waterNames)/sizeof(waterNames[0]));
        for(int j=0;j<p->numColors;j++){
            struct NDSColor before=p->data[j],after=before;
            if(greenPal && Green(before)) after=GreenGrade(before);
            else if(waterPal && BlueWater(before)) after=WaterGrade(before);
            if(before.r!=after.r||before.g!=after.g||before.b!=after.b){p->data[j]=after;pc++;colors++;}
        }
        if(pc){pals++; printf("%.*s: %d\n",RES_NAME_LENGTH,p->name.asChars,pc);}
    }
    FILE *o=fopen(argv[3],"wb"); if(!o){NSContainer_Free(&c);return 4;}
    rc=NSContainer_WriteToFile(&c,o); fclose(o); NSContainer_Free(&c);
    if(rc)return rc;
    printf("%s: %d palettes / %d colors\n",argv[1],pals,colors);
    if(pals<6 || colors<12)return 5;
    return 0;
}
