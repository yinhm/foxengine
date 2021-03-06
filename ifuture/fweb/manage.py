# -*- coding: utf-8 -*-

import os.path
import web
from wolfox.fengine.ifuture.ibase import *
import wolfox.fengine.ifuture.dynamic as dynamic
import wolfox.fengine.ifuture.ifuncs as ifuncs
import wolfox.fengine.ifuture.ifuncs2 as ifuncs2
import wolfox.fengine.ifuture.ifuncs1a as ifuncs1a
import wolfox.fengine.ifuture.ifuncs2a as ifuncs2a
import wolfox.fengine.ifuture.xfuncs as xfuncs
import wolfox.fengine.ifuture.xfuncs2 as xfuncs2
import wolfox.fengine.ifuture.ufuncs as ufuncs


#必须写绝对路径名，否则在apache中相对路径的起始是site-packages/web
path_name = os.path.dirname(__file__)
#path_name = 'D:/work/applications/gcode/wolfox/fengine/ifuture/web'
render = web.template.render(path_name)


urls = (
  '/last', 'LastUpdateX',
  '/last/(.*)','LastUpdateX',
  '/lastx2', 'LastUpdateX2',
  '/lastx2/(.*)','LastUpdateX2',
  '/lastx1', 'LastUpdateX1',
  '/lastx1/(.*)','LastUpdateX1',
  '/lastn', 'LastUpdateN',
  '/lastn/(.*)','LastUpdateN',
  '/last1', 'LastUpdate1',
  '/last1/(.*)','LastUpdate1',
  '/last2', 'LastUpdate2',
  '/last2/(.*)','LastUpdate2',
  '/last3', 'LastUpdate3',
  '/last3/(.*)','LastUpdate3',
  '/indices','Indices', 
  '/indices/(.*)','Indices',   
)

application = web.application(urls, globals()).wsgifunc()

class LastUpdateX:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.uget(ufuncs.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)

class LastUpdateX2:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(xfuncs2.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)


class LastUpdateX1:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(xfuncs.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)

class LastUpdateN:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(ifuncs2.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)


class LastUpdate1:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(ifuncs.xxx4,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)


class LastUpdate2:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(ifuncs1a.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)

class LastUpdate3:
    def GET(self,priority=2500):
        try:
            priority = int(priority)    #除默认外，传入的是字符串
        except:
            return u'优先级请输入合法的数字，您输入的是:%s' % priority
        fname,sif,xactions = dynamic.whget(ifuncs2a.xxx2,priority=priority)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        #print priority
        return render.last(fname,lasttime,xactions)

class Indices:
    def GET(self,length=2000):
        try:
            length = int(length)    #除默认外，传入的是字符串
        except:
            return u'覆盖长度请输入合法的数字，您输入的是:%s' % length
        fname,sif = dynamic.fget(ifuncs1a.xxx)
        #return "name=%s,lastupdate=%s:%s" % (fname,sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        lasttime = "%s-%s" % (sif.transaction[IDATE][-1],sif.transaction[ITIME][-1])
        indices = zip(sif.date  #这里的次序必须与模板中的次序一致
                    ,sif.time
                    ,sif.s30
                    ,sif.xatr
                    ,sif.mxatr
                    ,sif.xatr30x
                    ,sif.mxatr30x
                    ,sif.xtrend
                    ,sif.dma
                    ,sif.sdma
                    ,sif.xstate
        )
        #print priority
        return render.indices(fname,lasttime,indices[:-length:-1])


if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
