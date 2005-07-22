from nevow import rend, loaders, inevow, tags as T
from nufox import xmlstan

class XULStanPage(rend.Page):
    """I use xmlstan directly in a nevowish way to render some XUL."""
    
    X = xmlstan.PrimaryNamespace('xul')
    docFactory = loaders.stan([
        T.xml("""<?xml version="1.0"?><?xml-stylesheet href="chrome://global/skin/" type="text/css"?>"""),
        X.window(id="xul-window", title="My Example", 
            orient="horizontal",
            xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul",
            n=xmlstan.xmlns("http://nevow.com/ns/nevow/0.1")) [
            X.vbox(flex="1")[
                X.description(render=T.directive("desc")),
            ]
        ]])

    def render_desc(self, ctx, data):
        return ctx.tag["This message is from a render_ method"]

    def beforeRender(self, ctx):
        inevow.IRequest(ctx).setHeader("Content-Type", 
            "application/vnd.mozilla.xul+xml; charset=UTF-8")

example = XULStanPage()
