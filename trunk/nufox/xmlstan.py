from nevow.stan import Tag
from nevow import flat
from nevow.flat import flatstan

class xmlns:
    def __init__(self, uri):
        self.uri = uri
flat.registerFlattener(lambda orig, ctx: orig.uri, xmlns)

class NSTag(Tag):

    def __call__(self, **kw):
        for k,v in kw.items():
            if isinstance(v, xmlns):
                self.attributes['xmlns:'+k] = v.uri
                del kw[k]
        return Tag.__call__(self, **kw)

flat.registerFlattener(flatstan.TagSerializer, NSTag)

class TagNamespace(object):

    def __init__(self, namespace, nsKey=None, validTags=[]):
        self._namespace = namespace
        if nsKey:
            self._nsKey = nsKey
        else:
            self._nsKey = namespace[0]
        self._validTags = validTags

    def _makeTagName(self, name):
        return "%s:%s" % (self._nsKey, name)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            if len(self._validTags) > 0 and name not in self._validTags:
                raise KeyError(
                    "%s is not a valid tag in the %s namespace." % (name, 
                    self._namespace))
            return NSTag(self._makeTagName(name))

class PrimaryNamespace(TagNamespace):
    
    def _makeTagName(self, name):
        return name

if __name__ == '__main__':
    from nevow.flat.ten import flatten
    h = PrimaryNamespace('html')
    x = TagNamespace('xforms')
    
    b = h.html(x=xmlns("http://www.w3.org/2002/xforms"), 
               h=xmlns("http://www.w3.org/2002/06/xhtml2"))[
            h.head[
                x.model(schema="foo.xsd")
            ]
        ]
    print flatten(a)
