# -*- coding: utf-8 -*-

import re
from wolfox.fengine.core.base import BaseObject

import logging
logger = logging.getLogger('wolfox.fengine.core.cruiser.result2configs_test')

mm_pattern = r'\(-?(?P<balance>\d+), -?\d+, -?\d+, (?P<times>\d+)\)'
mm_groups = ['balance','times']

#svama2_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+),sma=(?P<sma>\d+)'
#svama2_groups = ['fast','slow','sma','ma_standard']

svama2_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+)'
svama2_groups = ['fast','slow','ma_standard']

svama2b_pattern = r'slow=(?P<slow>\d+),fast=(?P<fast>\d+)'
svama2b_groups = ['fast','slow']

csvama2_pattern = r'slow=(?P<slow>\d+),rstart=(?P<rstart>\d+),rend=(?P<rend>\d+),fast=(?P<fast>\d+)'
csvama2_groups = ['fast','slow','rstart','rend']


svama3_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+),mid=(?P<mid>\d+)'
svama3_groups = ['fast','mid','slow','ma_standard','extend_days']

svama3b_pattern = r'slow=(?P<slow>\d+),mid=(?P<mid>\d+),fast=(?P<fast>\d+)'
svama3b_groups = ['fast','mid','slow']

csvama3_pattern = r'slow=(?P<slow>\d+),rstart=(?P<rstart>\d+),mid=(?P<mid>\d+),fast=(?P<fast>\d+),rend=(?P<rend>\d+)'
csvama3_groups = ['fast','mid','slow','rstart','rend']

#svama2c_pattern = r'threshold=(?P<threshold>\d+),ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+),sma=(?P<sma>\d+)'
#svama2c_groups = ['fast','slow','sma','ma_standard','threshold']

svama2c_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+)'
svama2c_groups = ['fast','slow','ma_standard']

#svama2x_pattern = r'slow=(?P<slow>\d+),sma=(?P<sma>\d+),base=(?P<base>\d+),ma_standard=(?P<ma_standard>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+)'
#svama2x_groups = ['fast','slow','base','sma','ma_standard','extend_days']

svama2x_pattern = r'ma_standard=(?P<ma_standard>\d+),base=(?P<base>\d+),fast=(?P<fast>\d+),slow=(?P<slow>\d+)'
svama2x_groups = ['fast','slow','base','ma_standard']

svama2s_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+)'
svama2s_groups = ['fast','slow','ma_standard','extend_days']

vama3_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+),mid=(?P<mid>\d+)'
vama3_groups = ['fast','mid','slow','ma_standard','extend_days']


#vama2_pattern = r'pre_length=(?P<pre_length>\d+),ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+)'
#vama2_groups = ['fast','slow','pre_length','ma_standard']

vama2_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),fast=(?P<fast>\d+)'
vama2_groups = ['fast','slow','ma_standard']

#vama2x_pattern = r'slow=(?P<slow>\d+),base=(?P<base>\d+),pre_length=(?P<pre_length>\d+),ma_standard=(?P<ma_standard>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+)'
#vama2x_groups = ['fast','slow','base','pre_length','ma_standard','extend_days']

vama2x_pattern = r'ma_standard=(?P<ma_standard>\d+),base=(?P<base>\d+),fast=(?P<fast>\d+),slow=(?P<slow>\d+)'
vama2x_groups = ['fast','slow','base','ma_standard']

ma3_pattern = r'ma_standard=(?P<ma_standard>\d+),slow=(?P<slow>\d+),extend_days=(?P<extend_days>\d+),fast=(?P<fast>\d+),mid=(?P<mid>\d+)'
ma3_groups = ['fast','mid','slow','ma_standard','extend_days']


pmappings = {'svama2':BaseObject(pattern=svama2_pattern,groups=svama2_groups),
        'svama2b':BaseObject(pattern=svama2b_pattern,groups=svama2b_groups),        
        'csvama2':BaseObject(pattern=csvama2_pattern,groups=csvama2_groups),        
        'svama2c':BaseObject(pattern=svama2c_pattern,groups=svama2c_groups),        
        'svama2x':BaseObject(pattern=svama2x_pattern,groups=svama2x_groups),        
        'svama3':BaseObject(pattern=svama3_pattern,groups=svama3_groups),
        'svama3b':BaseObject(pattern=svama3b_pattern,groups=svama3b_groups),        
        'csvama3':BaseObject(pattern=csvama3_pattern,groups=csvama3_groups),
        'svama2s':BaseObject(pattern=svama2s_pattern,groups=svama2s_groups),
        'vama3':BaseObject(pattern=vama3_pattern,groups=vama3_groups),
        'vama2':BaseObject(pattern=vama2_pattern,groups=vama2_groups),
        'vama2x':BaseObject(pattern=vama2x_pattern,groups=vama2x_groups),
        'ma3':BaseObject(pattern=ma3_pattern,groups=ma3_groups),        
        }


def result2configs(name,file_from,file_to):
    if name not in pmappings:
        raise KeyError('%s not in pmappings' % name)
    rf = open(file_from,'r')
    wf = open(file_to,'w+')
    try:
        lines2configs(name,rf,wf)
    finally:
        rf.close()
        wf.close()


def lines2configs(name,rf,wf):
    pattern = re.compile(pmappings[name].pattern)
    groups = pmappings[name].groups
    cmm_pattern = re.compile(mm_pattern)
    for line in rf:
        try:
            s_mm = transform(line,cmm_pattern,mm_groups)
            s_key = transform(line,pattern,groups)
            oline = '    configs.append(config(buyer=fcustom(%s,%s))) \t#%s\n' % (name,s_key,s_mm)
            #print oline
            wf.write(oline)
        except Exception,inst:
            logger.exception(inst)
            if not line.rstrip():
                print u'空行'
            else:
                print u'匹配错误',line
            pass    #空行或者别的
        
def transform(line,pattern,groups):
    x = re.search(pattern,line)
    #print pattern.pattern,line
    lss = []
    for grp in groups:
        lss.append('%s=%3d' % (grp,int(x.group(grp))))
    ss = ','.join(lss)
    return ss


import optparse
if __name__ == '__main__':
    #python result2configs.py -t svama2 -i custom_cruiser_mm_svama2.txt -o svama2_configs.txt     
    #python result2configs.py -t svama2 -i nsvama2.txt -o nsvama2_configs.txt
    logging.basicConfig(filename="r2c.log",level=logging.DEBUG,format='#%(name)s:%(funcName)s:%(lineno)d:%(asctime)s %(levelname)s %(message)s')
    parser = optparse.OptionParser()
    parser.add_option('--type','-t',help="转换类型")    
    parser.add_option('--fin','-i',help="输入文件")
    parser.add_option('--fout','-o',help="输出文件")
    options,arguments = parser.parse_args()
    
    result2configs(options.type,options.fin,options.fout)
 

