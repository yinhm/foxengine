# -*- coding: utf-8 -*-

#60分钟处理

from wolfox.fengine.core.shortcut import *
from wolfox.fengine.normal.funcs import *
import wolfox.fengine.normal.sfuncs as s
from wolfox.fengine.core.d1ex import tmax,derepeatc,derepeatc_v,equals,msum,scover,rsub,xfollow,range4
from wolfox.fengine.core.d1match import *
from wolfox.fengine.core.d1idiom import *
from wolfox.fengine.core.d1indicator import cmacd,score2
from wolfox.fengine.core.d1 import lesser,bnot
from wolfox.foxit.base.tutils import linelog
from time import time

import logging
logger = logging.getLogger('wolfox.fengine.normal.hfuncs')    

def prepare_hour(stock,begin,end):
    linelog('prepare hour:%s' % stock.code)
    t = get_hour(stock.code,begin,end)
    stock.hour = t[CLOSE].copy()
    #stock.hour_open = t[OPEN].copy()
    #stock.hour_low = t[LOW].copy()
    #stock.hour_high = t[HIGH].copy()
    #stock.hour_v = t[VOLUME].copy()
    stock.hour[range4(len(stock.hour))] = stock.transaction[CLOSE]   #消除第4小时数据收盘与当日收盘价的差异，日收盘价为最后均价
    prepare_hmacd(stock)
    stock.hmxc = hour2day(xc0s(t[OPEN],stock.hour,t[HIGH],t[LOW],ma1=13) > 0)
    mdiff,mdea = macd_ruv3(t[OPEN],stock.hour,t[HIGH],t[LOW],t[VOLUME])
    mxc = cross(mdea,mdiff) > 0
    stock.xru3 = hour2day(mxc)
    mdiff,mdea = macd_ruv(t[OPEN],stock.hour,t[HIGH],t[LOW],t[VOLUME])
    mxc = cross(mdea,mdiff) > 0
    stock.xru = hour2day(mxc)
    ma3 = ma(stock.hour,3)
    ma7 = ma(stock.hour,7)
    ma13 = ma(stock.hour,13)
    ma30 = ma(stock.hour,30)
    stock.ma4_up = hour2day(gand((ma3>ma7),gand(ma7>ma13),gand(ma13>ma30),strend(ma3)>0,strend(ma7)>0,strend(ma13)>0,strend(ma30)>0))
    #stop_config(stock,t[HIGH],t[LOW])
    #prepare_up1(stock)

def prepare_up1(stock):
    #linelog('prepare up1:%s' % stock.code)
    #up = stock.hour * 10000 / rollx(stock.hour,1) >= 10200
    down =stock.hour_high - stock.hour < (stock.hour-stock.hour_open)*2/3
    ol = stock.hour > stock.hour_open
    tk = stock.hour_low > rollx(stock.hour_high)
    up = stock.hour * 10000 / gmin(rollx(stock.hour,1),stock.hour_open) > 10200
    stock.up1 =  xfollow(hour2day1(gand(up,down,ol,tk)),stock.transaction[VOLUME])
    stock.open2 = hour2day2(stock.hour_open)

def prepare_index(stock,begin,end):
    linelog('prepare hour:%s' % stock.code)
    t = get_hour(stock.code,begin,end)
    stock.hour = t[CLOSE].copy()
    stock.hour_open = t[OPEN].copy()
    stock.hour_low = t[LOW].copy()
    stock.hour_high = t[HIGH].copy()
    stock.hour_v = t[VOLUME].copy()
    stock.hour[range4(len(stock.hour))] = np.cast['int32'](stock.transaction[CLOSE])   #消除第4小时数据收盘与当日收盘价的差异，日收盘价为最后均价
    down =stock.hour_high - stock.hour < (stock.hour-stock.hour_open)*2/3
    ol = stock.hour > stock.hour_open
    stock.up1 =  xfollow(hour2day1(gand(down,ol)),stock.transaction[VOLUME])
    stock.open2 = hour2day2(stock.hour_open)

def stop_config(stock,shigh,slow):
    stoped = (shigh == slow)
    stock.stoped1 = hour2day1(stoped)
    stock.stoped2 = hour2day2(stoped)
    stock.stoped3 = hour2day3(stoped)    
    stock.stoped4 = hour2day4(stoped)

def prepare_hmacd(stock):
    #linelog('prepare hmacd:%s' % stock.code)    
    pdiff,pdea = cmacd(stock.hour)
    upcross_t = gand(cross(pdea,pdiff)>0,strend(pdiff)>0)     
    upcross = gand(upcross_t,pdiff<100) #<100才保险
    downcross = gand(cross(pdea,pdiff)<0,strend(pdiff)<0) 
    stock.hup_t = hour2day(upcross_t)
    stock.hup = hour2day(upcross)
    stock.hdown = hour2day(downcross)
    upcross2 = gand(cross(pdea,pdiff)>0,strend(pdiff)>0)
    dsub = rsub(pdiff,upcross2)
    csub = rsub(stock.hour,upcross2)
    stock.hdev = hour2day(band(greater(dsub),lesser(csub))) #小时线背离
    stock.mup_100 = hour2day(gand(pdiff>pdea,pdiff<100,strend(pdiff)>0,strend(pdea)>0))
    #stock.hgreater = hour2day4(pdiff>pdea)
    stock.xup = hour2day(gand(pdiff>pdea,strend(pdiff)>0,strend(pdea)>0))

def tsvama2_old(stock,fast,slow):
    t = stock.transaction
    svap,v2i = stock.svap_ma_67 
    ma_svapfast = ma(svap,fast)
    ma_svapslow = ma(svap,slow)
    trend_ma_svapfast = strend(ma_svapfast) > 0
    trend_ma_svapslow = strend(ma_svapslow) > 0
    cross_fast_slow = gand(cross(ma_svapslow,ma_svapfast)>0,trend_ma_svapfast,trend_ma_svapslow)
    msvap = transform(cross_fast_slow,v2i,len(t[VOLUME]))
    linelog('%s:%s' % (tsvama2.__name__,stock.code))
    return gand(stock.golden,msvap,stock.above)    

def gmacd5(stock,ldown=30,astart=60): #
    t = stock.transaction
    
    mdiff,mdea = cmacd(stock.g5)   

    xcross = gand(cross(mdea,mdiff) > 0)

    linelog(stock.code)

    #ss = sfollow(xcross,stock.mup,3)
    ss = band(xcross,stock.mup)

    #gf1 = gand(stock.g20>5000,stock.g20<9500)

    xatr = stock.atr * BASE / t[CLOSE]     
    
    signal = gand(ss,stock.above,stock.t5,strend(stock.ma4)>0,t[VOLUME]>0,mdiff>=mdea,strend(stock.ref.ma4)>0,xatr>=astart)
    
    return signal

def hxud(stock):
    '''
        vfilter = gand(svma<vma*3/5,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)   #2/3    
        评估:总盈亏值=9798,交易次数=18  期望值=9714
                总盈亏率(1/1000)=9798,平均盈亏率(1/1000)=544,盈利交易率(1/1000)=777
                平均持仓时间=50,持仓效率(1/1000000)=10880
                赢利次数=14,赢利总值=10024
                亏损次数=4,亏损总值=226
                平盘次数=0
        vfilter = gand(svma<vma*2/3,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)  #无意义
        评估:总盈亏值=10410,交易次数=25 期望值=6500
                总盈亏率(1/1000)=10410,平均盈亏率(1/1000)=416,盈利交易率(1/1000)=760
                平均持仓时间=43,持仓效率(1/1000000)=9674
                赢利次数=19,赢利总值=10799
                亏损次数=6,亏损总值=389
                平盘次数=0
        vfilter = gand(svma<vma*1/2,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)  #说明svma越小越好,最近越缩量越好
        评估:总盈亏值=2785,交易次数=5   期望值=1000
                总盈亏率(1/1000)=2785,平均盈亏率(1/1000)=557,盈利交易率(1/1000)=1000
                平均持仓时间=57,持仓效率(1/1000000)=9771
                赢利次数=5,赢利总值=2785
                亏损次数=0,亏损总值=0
                平盘次数=0

    '''
    t = stock.transaction
    linelog(stock.code)
    xatr = stock.atr * BASE / t[CLOSE]     

    ss = syntony(stock.hup,stock.hmxc,3)
    #ss = sfollow(stock.hup,stock.hmxc,3)

    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/5,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)   #2/3    

    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)

    s=stock
    signal = gand(ss,vfilter,mcf>1000,mcf<1050,stock.t5,stock.above,strend(stock.ma4)>0,strend(stock.ma3)>0,xatr>45,xatr<60,stock.ma1<stock.ma2,stock.ma1>stock.ma3,s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g20<=8000,s.g5<s.g20,s.g20>=3000)
    return signal

def hmacd(stock):
    t = stock.transaction    
    linelog(stock.code)
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/2,svma>vma*2/3)
    s=stock
    magic = gand(s.g20 >= s.g120,s.g60 >= s.g120,s.g120 >= s.g250,s.g5<s.g20,s.g20<=8000,s.g20>=3000)
    xatr = stock.atr * BASE / t[CLOSE]
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)
    
    signal = gand(stock.above,stock.t5,stock.hup,vfilter,magic,xatr>45,xatr<60,mcf<900,stock.ma4_up)
    return signal

def hmacd_seller(stock,buy_signal,**kwargs):
    signal = greater(msum2(stock.hdown,5),1)
    return signal

def hdev(stock):
    ''' 
        2005-2009无法找到好的策略
    '''
    t = stock.transaction    
    linelog(stock.code)
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/5)
    #vfilter = gand(svma<vma*3/5,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)   #2/3        

    xatr = stock.atr * BASE / t[CLOSE]
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)
    
    ma3 = ma(t[CLOSE],3)
    ma7 = ma(t[CLOSE],7)
    c37 = gand(cross(ma7,ma3)>0,strend(ma3)>0)
    sc = sfollow(stock.hdev,c37,3)

    s=stock
    #signal = gand(stock.hdev,stock.t5,vfilter,mcf>1000,stock.g5<stock.g60,s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g20<=8000)
    magic = gand(stock.g5<stock.g20,s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g20<=8000,s.g20>=3000)
    signal = gand(sc,stock.t5,strend(stock.ma4)>0,vfilter,mcf<900)
    return signal

def hmacd2(stock):
    ''' 无大用
    '''
    t = stock.transaction    
    linelog(stock.code)
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*2/3)
    #vfilter = gand(svma<vma*3/4,t[VOLUME]<vma)
    #vfilter = gand(svma<vma*3/5,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)   #2/3        

    xatr = stock.atr * BASE / t[CLOSE]
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)
    
    #ma3 = ma(t[CLOSE],3)
    #ma7 = ma(t[CLOSE],7)
    #c37 = gand(cross(ma7,ma3)>0,strend(ma3)>0)
    #sc = sfollow(stock.hdev,c37,3)
    
    ss = gand(msum(stock.hup,5)>1,stock.hup)    #5日内的第二次上叉

    s=stock
    #signal = gand(stock.hdev,stock.t5,vfilter,mcf>1000,stock.g5<stock.g60,s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g20<=8000)
    #magic = gand(s.g20 >= s.g60,s.g60 <= s.g120,s.g120 <= s.g250)#,s.g20<=8000)
    magic = gand(s.g5>s.g60,s.g20 >= s.g60,s.g60 <= s.g120,s.g20<=8000)
    signal = gand(ss,stock.t5,stock.t4,vfilter,mcf<900,xatr>60,magic)
    return signal

def hemv1b(stock,fast=15,base=120):
    t = stock.transaction

    em = emv(t[HIGH],t[LOW],t[VOLUME])
    mv1 = msum2(em,fast)
    mvbase = msum2(em,base)

    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)

    vfilter = gand(svma<=vma*3/4)

    baseline = cached_zeros(len(t[CLOSE]))

    thumb = gand(stock.magic,stock.g20>3000)

    ss = sfollow(cross(baseline,mv1)>0,stock.hup,30)

    ecross = gand(ss,thumb,strend(mv1)>0,stock.t5,stock.above,strend(mvbase)>0,vfilter)
    linelog(stock.code)
    return ecross

def hmxru3(stock):
    ''' 成交量分配后的macd,采用supdown3
        评估:总盈亏值=6163,交易次数=22  期望值=3733
                总盈亏率(1/1000)=6163,平均盈亏率(1/1000)=280,盈利交易率(1/1000)=863
                平均持仓时间=48,持仓效率(1/1000000)=5833
                赢利次数=19,赢利总值=6389
                亏损次数=3,亏损总值=226
                平盘次数=0
    '''
    t = stock.transaction
    mxc = stock.xru3
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*2/3,svma>vma/2,t[VOLUME]<=vma*2/3)
    xatr = stock.atr * BASE / t[CLOSE]     
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)
    
    s = stock
    signal = gand(s.above,mxc,vfilter,strend(stock.ma4)>0,stock.t5,xatr>=50,stock.magic,stock.ma1<stock.ma2,stock.ma1>stock.ma3,mcf<1000)
    linelog(stock.code)
    return signal

def hmxru(stock):
    ''' 成交量分配后的macd,采用supdown
        vfilter = svma < vma * 2/3    
        评估:总盈亏值=4813,交易次数=14  期望值=5444
                总盈亏率(1/1000)=4813,平均盈亏率(1/1000)=343,盈利交易率(1/1000)=928
                平均持仓时间=50,持仓效率(1/1000000)=6860
                赢利次数=13,赢利总值=4876
                亏损次数=1,亏损总值=63
                平盘次数=0
        vfilter = gand(svma<vma*2/3,t[VOLUME]<=vma*2/3)
        评估:总盈亏值=3810,交易次数=8   期望值=1000
                总盈亏率(1/1000)=3810,平均盈亏率(1/1000)=476,盈利交易率(1/1000)=1000
                平均持仓时间=65,持仓效率(1/1000000)=7323
                赢利次数=8,赢利总值=3810
                亏损次数=0,亏损总值=0
                平盘次数=0

    '''
    t = stock.transaction
    mxc = stock.xru
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*2/3,t[VOLUME]<=vma*2/3)
    #vfilter = gand(svma<vma*2/3)
    xatr = stock.atr * BASE / t[CLOSE]     
    ma0 = ma(t[CLOSE],3)
    ndown = bnot(gand(t[CLOSE]<ma0,ma0<stock.ma1,stock.ma1<stock.ma2))
    s = stock
    sv = greater(msum(t[VOLUME] > 0,120),100)   #确保新股上市前100天无信号    
    signal = gand(mxc,stock.above,vfilter,strend(stock.ma4)>0,stock.t5,xatr>=60,stock.magic,stock.ma1<stock.ma2,stock.ma1>stock.ma3,ndown)


    linelog(stock.code)
    return signal

def hspring(stock,threshold=-30):
    ''' 对于结果
        下影越短越好，close-low/close 也是越短越好
    '''
    t = stock.transaction
    linelog('spring:%s' % stock.code)
    
    s11 = gand(stock.ks >=-5,stock.ks<0,stock.ref.ks<=threshold)
    s12 = gand(stock.ks >=5,stock.ks<20,stock.ref.ks<=threshold)
    s1 = bor(s11,s12)
    s21 = gand(stock.ks>=5,stock.ks<75,stock.ref.ks<=threshold)

    signals = bor(s1,s21)

    ss = sfollow(signals,stock.hup,10)


    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*7/8,svma>vma/2,t[VOLUME]<=vma*2/3)    
    return gand(ss,stock.magic,stock.above,vfilter)

def mxru3(stock):
    ''' 成交量分配后的macd,采用supdown3

        sfollow = 15
        评估:总盈亏值=5596,交易次数=21  期望值=5782
                总盈亏率(1/1000)=5596,平均盈亏率(1/1000)=266,盈利交易率(1/1000)=904
                平均持仓时间=46,持仓效率(1/1000000)=5782
                赢利次数=19,赢利总值=5689
                亏损次数=2,亏损总值=93
                平盘次数=0
        sfollow = 30
        评估:总盈亏值=7176,交易次数=27  期望值=6973
                总盈亏率(1/1000)=7176,平均盈亏率(1/1000)=265,盈利交易率(1/1000)=888
                平均持仓时间=46,持仓效率(1/1000000)=5760
                赢利次数=24,赢利总值=7292
                亏损次数=3,亏损总值=116
                平盘次数=0
    '''
    t = stock.transaction
    mdiff,mdea = macd_ruv3(t[OPEN],t[CLOSE],t[HIGH],t[LOW],t[VOLUME])
    mxc = cross(mdea,mdiff) > 0
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    #vfilter = gand(svma<vma*7/8,svma>vma/2,t[VOLUME]<=vma,t[CLOSE]>stock.ma1,cf)
    vfilter = gand(svma<vma*2/3,t[VOLUME]<=vma*4/3)
    xatr = stock.atr * BASE / t[CLOSE]     
    signal = gand(mxc)
    linelog(stock.code)
    signal = sfollow(signal,stock.hup,30)
    return gand(signal,vfilter,stock.magic,strend(stock.ma4)>0,stock.t5,xatr>=50,t[CLOSE]>stock.ma3)


def mxru(stock):
    ''' 成交量分配后的macd,采用supdown
        评估:总盈亏值=6744,交易次数=18  期望值=12466
                总盈亏率(1/1000)=6744,平均盈亏率(1/1000)=374,盈利交易率(1/1000)=944
                平均持仓时间=54,持仓效率(1/1000000)=6925
                赢利次数=17,赢利总值=6774
                亏损次数=1,亏损总值=30
                平盘次数=0
    '''
    t = stock.transaction
    mdiff,mdea = macd_ruv(t[OPEN],t[CLOSE],t[HIGH],t[LOW],t[VOLUME])
    mxc = cross(mdea,mdiff) > 0
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    #vfilter = gand(svma<vma*7/8,svma>vma/2,t[VOLUME]<=vma,t[CLOSE]>stock.ma1,cf)
    vfilter = gand(svma<vma*2/3,t[VOLUME]<=vma*2/3)
    xatr = stock.atr * BASE / t[CLOSE]     
    signal = gand(mxc)
    linelog(stock.code)

    signal = sfollow(signal,stock.hup,30)
    return gand(signal,vfilter,stock.magic,strend(stock.ma4)>0,stock.t5,xatr>=50,t[CLOSE]>stock.ma4)


def emv2(stock,fast=10,slow=100):
    ''' fast,slow = 10,100
        评估:总盈亏值=4297,交易次数=15  期望值=1000
                总盈亏率(1/1000)=4297,平均盈亏率(1/1000)=286,盈利交易率(1/1000)=1000
                平均持仓时间=44,持仓效率(1/1000000)=6500
                赢利次数=15,赢利总值=4297
                亏损次数=0,亏损总值=0
                平盘次数=0
        fast,slow=17,88
        评估:总盈亏值=4132,交易次数=14  期望值=4338
                总盈亏率(1/1000)=4132,平均盈亏率(1/1000)=295,盈利交易率(1/1000)=857
                平均持仓时间=50,持仓效率(1/1000000)=5900
                赢利次数=12,赢利总值=4268
                亏损次数=2,亏损总值=136
                平盘次数=0
        
    '''
    t = stock.transaction

    em = emv(t[HIGH],t[LOW],t[VOLUME])
   
    mv1 = ma(em,fast)
    mv2 = ma(em,slow)

    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)

    vfilter = gand(svma<=vma*2/3)#,t[VOLUME]<=vma*2/3)
 
    thumb = gand(stock.magic,stock.g20>3000)

    signal = gand(cross(mv2,mv1)>0,strend(mv2)>0,mv2<0)
    ss = syntony(signal,stock.hup,5)
    xatr = stock.atr * BASE / t[CLOSE]     
    ecross = gand(ss,thumb,stock.t5,vfilter,xatr>50,strend(stock.ma4)>0,stock.above)
    linelog(stock.code)
    return ecross

def xudh(stock,xfunc=xc0s,astart=45):
    ''' 
        评估:总盈亏值=5146,交易次数=21  期望值=3223
                总盈亏率(1/1000)=5146,平均盈亏率(1/1000)=245,盈利交易率(1/1000)=952
                平均持仓时间=47,持仓效率(1/1000000)=5212
                赢利次数=20,赢利总值=5222
                亏损次数=1,亏损总值=76
                平盘次数=0
        原： 牺牲效率提高成功率
        评估:总盈亏值=7295,交易次数=21  期望值=2496
                总盈亏率(1/1000)=7295,平均盈亏率(1/1000)=347,盈利交易率(1/1000)=904
                平均持仓时间=48,持仓效率(1/1000000)=7229
                赢利次数=19,赢利总值=7573
                亏损次数=2,亏损总值=278
                平盘次数=0
        
    '''
    t = stock.transaction
    mxc = xfunc(t[OPEN],t[CLOSE],t[HIGH],t[LOW],ma1=13) > 0

    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)

    vfilter = gand(svma<vma*2/3)
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)

    stdea = strend(stock.dea)
    stdiff = strend(stock.diff)
    st = gand(stdea<=-3,stdea>=-4,stdiff<=-5,stdiff>=-6)

    xatr = stock.atr * BASE / t[CLOSE]     

    #logger.debug('tlen,hlen=%s,%s' %(len(mxc),len(stock.hup)))
    ss = sfollow(mxc,stock.hup,3)

    signal = gand(ss,vfilter,stock.thumb,stock.above,stock.t5,mcf>1000,stock.ma1<stock.ma2,stock.ma1>stock.ma3,st,xatr>=astart)
    linelog(stock.code)
    return signal


def ldx(stock,mlen=60,glimit=3000,astart=60,aend=1000): #low down xcross 
    ''' 无增益
    '''
    pass

def tsvama2sbv(stock,fast,slow,follow=7):
    ''' svama慢线下叉快线，follow日后再上叉回来
        添加vfilter
    '''
    t = stock.transaction
    svap,v2i = stock.svap_ma_67_2

    ma_svapfast = ma(svap,fast)
    ma_svapslow = ma(svap,slow)
    trend_ma_svapfast = strend(ma_svapfast)
    trend_ma_svapslow = strend(ma_svapslow)

    cross_down = band(cross(ma_svapslow,ma_svapfast)<0,trend_ma_svapfast<0)    
    cross_up = band(cross(ma_svapslow,ma_svapfast)>0,trend_ma_svapfast>0)        
    
    sdown = transform(cross_down,v2i,len(t[VOLUME]))
    sup = transform(cross_up,v2i,len(t[VOLUME]))    
    
    sync_down_up = sfollow(sdown,sup,follow)
    
    linelog('%s:%s' % (tsvama2sbv.__name__,stock.code))

    vma_s = ma(t[VOLUME],13)
    vma_l = ma(t[VOLUME],30)

    vfilter = vma_s < vma_l

    ss = gand(bnot(sfollow(sync_down_up,stock.hup,10)),sfollow(sync_down_up,stock.hup,20))
    return gand(ss,stock.above,stock.t5,stock.magic,vfilter)


def hxudl(stock):
    ''' 恶劣
    '''
    t = stock.transaction
    linelog(stock.code)
    xatr = stock.atr * BASE / t[CLOSE]     

    ss = syntony(stock.hup,stock.hmxc,3)
    #ss = sfollow(stock.hup,stock.hmxc,3)

    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/5,t[VOLUME]>0,t[VOLUME]>vma*1/2)#,t[VOLUME]<vma*3/2)   #2/3    

    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)

    s=stock
    spos = gand(ma(stock.ref.transaction[CLOSE],250) > stock.ref.ma5,stock.ref.ma5>stock.ref.ma4,stock.ref.t4>0,stock.ref.ma1>stock.ref.ma2,stock.ref.ma1>stock.ref.ma3)
    #spos2 = gand(ma(t[CLOSE],250) > stock.ma5,stock.ma5>stock.ma4,stock.t4>0)    
    signal = gand(stock.hmxc,vfilter,spos,strend(stock.ma3)>0,xatr>45,xatr<60,stock.ma1>stock.ma2,stock.ma1>stock.ma3,s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g20<=8000,s.g5<s.g20,s.g20>=3000)
    return signal


def xud2(stock,xfunc=xc0s,astart=0):
    ''' 
    '''
    magnify = gand(stock.ma4_up,stock.mup_100)

    signal = s.mxru3(stock)
    signal = sfollow(signal,magnify,10)
    return signal

def mag(stock):
    '''
        只在大牛市中有意义,未继续检验
        0501-0909
        评估:总盈亏值=37642,交易次数=119        期望值=4051
                总盈亏率(1/1000)=37642,平均盈亏率(1/1000)=316,盈利交易率(1/1000)=781
                平均持仓时间=37,持仓效率(1/1000000)=8540
                赢利次数=93,赢利总值=39684
                亏损次数=26,亏损总值=2042
                平盘次数=0
                
        0807--0909
        评估:总盈亏值=4108,交易次数=26  期望值=1950
                总盈亏率(1/1000)=4108,平均盈亏率(1/1000)=158,盈利交易率(1/1000)=692
                平均持仓时间=38,持仓效率(1/1000000)=4157
                赢利次数=18,赢利总值=4760
                亏损次数=8,亏损总值=652
                平盘次数=0

    '''    
    s = stock
    t = stock.transaction    
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/2,svma>vma*2/3)
    xatr = stock.atr * BASE / t[CLOSE]     
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7)
    magnify = gand(stock.ma4_up,stock.mup_100)
    linelog(stock.code)
    magic = gand(s.g20 >= s.g120,s.g60 >= s.g120,s.g120 >= s.g250,s.g5<s.g20,s.g20<=8000)
    hma7 = ma(stock.hour,7)
    hma13 = ma(stock.hour,13)
    hma30 = ma(stock.hour,30)
    hs = hour2day(gand(stock.hour > hma7,gswing(hma7,hma13,hma30,5)<60))
    signal = gand(magnify,s.above,stock.t5,stock.t4,xatr>45,xatr<60,magic,vfilter,mcf<800,stock.ma1>stock.ma3,hs,stock.diff>stock.dea)
    return signal

def heff(stock):
    ''' 效果不平衡
        0501-0909
        评估:总盈亏值=35014,交易次数=178        期望值=2684
                总盈亏率(1/1000)=35014,平均盈亏率(1/1000)=196,盈利交易率(1/1000)=612
                平均持仓时间=32,持仓效率(1/1000000)=6125
                赢利次数=109,赢利总值=40100
                亏损次数=69,亏损总值=5086
                平盘次数=0
        0711-0909
        评估:总盈亏值=17918,交易次数=63 期望值=4437
                总盈亏率(1/1000)=17918,平均盈亏率(1/1000)=284,盈利交易率(1/1000)=809
                平均持仓时间=43,持仓效率(1/1000000)=6604
                赢利次数=51,赢利总值=18686
                亏损次数=12,亏损总值=768
                平盘次数=0

    '''
    linelog(stock.code)
    t = stock.transaction    
    ef = efficient_rate(stock.hour)
    zx = cached_zeros(len(stock.hour))
    efz = hour2day(gand(cross(zx,ef)>0,strend(ef)>0))
    vma = ma(t[VOLUME],30)
    svma = ma(t[VOLUME],3)
    vfilter = gand(svma<vma*3/4,t[VOLUME]<vma)
    cf = (t[OPEN]-t[LOW] + t[HIGH]-t[CLOSE])*1000 / (t[HIGH]-t[LOW])   #向下的动力  
    mcf = ma(cf,7) 

    refn = gand(stock.ref.ma0<stock.ref.ma1,stock.ref.ma1<stock.ref.ma2,bnot(stock.ref.t0),bnot(stock.ref.t1),bnot(stock.ref.t2))
    sup = gand(stock.ma0>stock.ma1,stock.ma1>stock.ma2,stock.t1,stock.t2)

    s1 = gand(efz,bor(bnot(refn),sup))
    s2 = sfollow(efz,bnot(refn),10)
    ss = bor(s1,s2)
    s = stock
    magic = gand(s.g20 >= s.g60,s.g60 >= s.g120,s.g120 >= s.g250,s.g5>s.g20,s.g20<=8000)
    xatr = stock.atr * BASE / t[CLOSE]     

    #signal = gand(ss,stock.above,stock.t5,stock.t4,magic,vfilter,mcf<1000)
    signal = gand(ss,stock.above,stock.t5,stock.t4,magic,vfilter,mcf<1000,xatr>40,stock.ma1>stock.ma3,stock.diff<stock.dea)
    return signal


def hmacd_a(stock):
    linelog(stock.code)
    t = stock.transaction    

    shour = stock.hour
    pdiff1,pdea1 = cmacd(stock.hour)
    pdiffd,pdead = cmacd(stock.hour,48,104,36)
    

    #signal = gand(cross(pdea1,pdiff1)>0,pdiffd>pdead,pdiffd>0,pdiff1>0)    #至少一日前还在下面

    msignal = gand(cross(cached_zeros(len(pdiff1)),pdiffd)>0,strend(pdiff1-pdea1)>3)

    #nsignal = gand(pdiff1<pdea1)

    signal = gand(hour2day(msignal))

    stock.hmacda = signal
    #signal = gand(signal,stock.t5,stock.t4)
    
    return signal

def hmacd_b(stock):
    linelog(stock.code)
    t = stock.transaction    

    asignal = stock.hmacda

    signal = gand(asignal)

    return signal
