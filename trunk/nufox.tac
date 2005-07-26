import os
from nevow import rend, loaders, tags as T

class Examples(rend.Page):

    docFactory = loaders.stan(
        T.html[
            T.head[T.title["NuFox Examples"]],
            T.body[
                T.invisible(data=T.directive('examples'), render=rend.sequence)[
                    T.div(pattern='item', render=T.directive('example'))
                ]
            ]
        ]
    )

    def __init__(self):
        rend.Page.__init__(self)
        l = []
        for mod in os.listdir('examples'):
            if mod == '__init__.py' or not mod.endswith('py'):
                continue
            imp = "from examples.%s import example" % (mod[:-3],)
            print "IMP", imp
            exec(imp)
            self.putChild(mod[:-3], example)
            l.append(mod[:-3])
        self.examples = l
        
    def data_examples(self, ctx, data):
        return self.examples

    def render_example(self, ctx, data):
        return ctx.tag[T.a(href='#',
            onclick='window.open("%s","%s","chrome,centerscreen,resizable, width=400,height=400");'%(
                data,data))[data]]

from twisted.application import internet, service
from nevow import appserver


application = service.Application('xulstan')
webServer = internet.TCPServer(8080, appserver.NevowSite(Examples()))
webServer.setServiceParent(application)


