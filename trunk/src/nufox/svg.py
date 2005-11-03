"""This module provides SVG support in the Nufox style.
see http://www.w3.org/TR/SVG for a description, use of this
module will require clients using firefox 1.5 +."""

import xmlstan
from xul import GenericWidget

svgns = xmlstan.TagNamespace('svg', 'http://www.w3.org/2000/svg')
xlinkns = xmlstan.TagNamespace('xlink', 'http://www.w3.org/1999/xlink')

class SVGWidgetTemplate(GenericWidget):
    def __init__(self, **kwargs):
        if kwargs.has_key('id'):
            GenericWidget.__init__(self, kwargs['id'])
        else:
            GenericWidget.__init__(self)
        kwargs.update({'id':self.id})
        self.kwargs = kwargs

    def getTag(self):
        self.kwargs.update(dict([(k,v[1]) for k,v in self.handlers.items()]))
        #XXX We need a better way to support attributes with a - in them..
        for k,v in self.kwargs.items():
            if k.find('_') != -1:
                del self.kwargs[k]
                self.kwargs[k.replace('_','-')] = v
        return getattr(svgns, self.tag)(**self.kwargs)

bigListOSvgTags = ['a', 'altGlyph', 'altGlyphDef', 'altGlyphItem', 'animate',
'animateColor', 'animateMotion', 'animateTransform', 'circle', 'clipPath',
'color-profile', 'cursor', 'definition-src', 'defs', 'desc', 'ellipse',
'feBlend', 'feColorMatrix', 'feComponentTransfer', 'feComposite',
'feConvolveMatrix', 'feDiffuseLighting', 'feDisplacementMap', 'feDistantLight',
'feFlood', 'feFuncA', 'feFuncB', 'feFuncG', 'feFuncR', 'feGaussianBlur',
'feImage', 'feMerge', 'feMergeNode', 'feMorphology', 'feOffset',
'fePointLight', 'feSpecularLighting', 'feSpotLight', 'feTile', 'feTurbulence',
'filter', 'font', 'font-face', 'font-face-format', 'font-face-name',
'font-face-src', 'font-face-uri', 'foreignObject', 'g', 'glyph', 'glyphRef',
'hkern', 'image', 'line', 'linearGradient', 'marker', 'mask', 'metadata',
'missing-glyph', 'mpath', 'path', 'pattern', 'polygon', 'polyline',
'radialGradient', 'rect', 'script', 'set', 'stop', 'style', 'svg', 'switch',
'symbol', 'text', 'textPath', 'title', 'tref', 'tspan', 'use', 'view', 'vkern']

gl = globals()

for t in bigListOSvgTags:
    if t not in gl.keys():
        gl[t] = type(t, (SVGWidgetTemplate,), {'tag' : t.lower()})
