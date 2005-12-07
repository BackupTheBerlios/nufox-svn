# From http://www.python.org/peps/pep-0309.html


class partial(object):

    def __init__(*args, **kw):
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)

    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)
