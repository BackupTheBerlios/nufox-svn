"""A stan with namespaces
"""   

from nevow.stan import Tag
from nevow import flat
from nevow.flat import flatstan

class NSTag(Tag):

    def __call__(self, *args, **kw):
        for a in args:
            if isinstance(a, PrimaryNamespace):
                self.attributes['xmlns'] = a.uri
            elif isinstance(a, TagNamespace):
                self.attributes['xmlns:'+a.namespace] = a.uri
                
        for k,v in kw.items():
            if isinstance(v, TagNamespace):
                self.attributes['xmlns:'+k] = v.uri
                v.namespace = k
                del kw[k]
        return Tag.__call__(self, **kw)

flat.registerFlattener(flatstan.TagSerializer, NSTag)

class TagNamespace(object):

    def __init__(self, namespace, uri, validTags=[]):
        self.namespace = namespace
        self._validTags = validTags
        self.uri = uri

    def _makeTagName(self, name):
        return "%s:%s" % (self.namespace, name)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            if len(self._validTags) > 0 and name not in self._validTags:
                raise KeyError(
                    "%s is not a valid tag in the %s namespace." % (name, 
                    self.namespace))
            return NSTag(self._makeTagName(name))

flat.registerFlattener(lambda orig, ctx: orig.uri, TagNamespace)

class PrimaryNamespace(TagNamespace):    
    def _makeTagName(self, name):
        return name

if __name__ == '__main__':
    from nevow.flat.ten import flatten
    h = PrimaryNamespace('html', "http://www.w3.org/2002/06/xhtml2")
    x = TagNamespace('xforms', "http://www.w3.org/2002/xforms")
    
    a = h.html(x, h)[
            h.head[
                x.model(schema="foo.xsd")
            ]
        ]
    print flatten(a)
