"""A stan with namespaces
"""      

from nevow import flat
from nevow.flat import flatstan
from nevow.stan import Tag, Proto


class NSProto(Proto):
    
    def __call__(self, *args, **kw):
        return NSTag(self)(*args, **kw)


class NSTag(Tag):
    
    def __call__(self, *args, **kw):
        for a in args:
            if isinstance(a, PrimaryNamespace):
                self.attributes['xmlns'] = a.uri
            elif isinstance(a, TagNamespace):
                self.attributes['xmlns:'+a.namespace] = a.uri
                
        for k,v in kw.items():
            if isinstance(v, PrimaryNamespace):
                self.attributes['xmlns'] = v.uri
            elif isinstance(v, TagNamespace):
                self.attributes['xmlns:'+k] = v.uri
                v.namespace = k
                del kw[k]
                
        return Tag.__call__(self, **kw)


class TagGenerator(object):
    tagFactory = Proto
    
    def __init__(self, singletons=[], validTags=[], tags={}):
        self.validTags = validTags
        
        if not isinstance(singletons, (tuple, list)):
            self.singletons = (singletons,)
        else:
            self.singletons = singletons

        flatstan.allowSingleton += tuple([self.makeTagName(x)
                                          for x in self.singletons])

        self.tags = tags
        
        self.validTags.extend(self.tags.keys())
        
    def makeTagName(self, name):
        return name

    def __getattr__(self, name):
        if name in self.tags:
            return self.tags[name]
        
        if len(self.validTags) > 0 and name not in self.validTags:
            raise KeyError(
                "%s is not a valid tag in the %s namespace."
                % (name, self.namespace))
        return self.tagFactory(self.makeTagName(name))
    

class TagNamespace(TagGenerator):
    
    tagFactory = NSProto
    
    def __init__(self, namespace, uri, *args, **kwargs):
        self.namespace = namespace
        self.uri = uri

        TagGenerator.__init__(self, *args, **kwargs)

    def makeTagName(self, name):
        return "%s:%s" % (self.namespace, name)

flat.registerFlattener(lambda orig, ctx: orig.uri, TagNamespace)


class PrimaryNamespace(TagNamespace):
    
    tagFactory = NSProto

    def makeTagName(self, name):
        return name

        
if __name__ == '__main__':
    from nevow.flat.ten import flatten

    h = PrimaryNamespace(
        'html', "http://www.w3.org/2002/06/xhtml2",
        singletons=('model', 'key'))
    x = TagNamespace(
        'xforms', "http://www.w3.org/2002/xforms",
        singletons=('model', 'key'))
    
    a = h.html(x, h)[
            h.head[
                x.model(schema="foo.xsd")['Not a singleton'],
                x.key(modifier='control', _key='c'),
                h.key(modifier='control', _key='c')
            ]
        ]

    print flatten(a)

    print "-" * 20

    b = h.html(x=x)[
            h.head[
                x.model
            ]
        ]
    
    print flatten(b)
