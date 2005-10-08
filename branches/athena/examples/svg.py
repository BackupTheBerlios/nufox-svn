from nufox import xul, svg

warning = """
SVG support is a very new thing in both nufox and mozilla, for this example 
to work you will need to be running one of the firefox 1.5 betas 
(deer park 2 is the current one). The nufox svg API is a first-pass proof of 
concept, it will probably undergo a large amount of change in the near future.
"""
formations = {'pyramid' : [(0,50),(70,150),(-70, 150)],
              'vline' : [(0,150),(150,150),(300, 150)],
              'hline' : [(150,0),(150,150),(150, 300)],
             }

class Example(xul.XULPage):

    def __init__(self):
        self.window = xul.Window(svg.svgns, height=400, width=400, 
                                 title="SVG Example")
        vbx = xul.VBox(flex=1)
        pb = xul.Button(label="Pyramid")
        pb.addHandler('oncommand', self.pyramidPushed)
        hb = xul.Button(label="Horazontal Line")
        hb.addHandler('oncommand', self.hlinePushed)
        vb = xul.Button(label="Vertical Line")
        vb.addHandler('oncommand', self.vlinePushed)
        vbx.append(xul.TextBox(value=warning, readonly='true', rows=5, multiline='true'),pb,hb,vb)
        
        #SVG stuff:
        svgDisplay = svg.svg()
        group = svg.g(stroke='black', fill_opacity="0.7", stroke_width="0.1cm") 
        self.c1 = svg.circle(cx='6cm', cy='2cm', r='100', fill='red',
                        transform="translate(0,0)") 
        self.c2 = svg.circle(cx='6cm', cy='2cm', r='100', fill='blue',
                        transform="translate(0,0)") 
        self.c3 = svg.circle(cx='6cm', cy='2cm', r='100', fill='green',
                        transform="translate(0,0)") 
        svgDisplay.append(svg.text(x="250", y="55", 
                                   font_size='55').append("This is SVG!"),
                          group.append(self.c1,self.c2,self.c3))
        
        self.window.append(vbx.append(svgDisplay))

    def pyramidPushed(self):
        self.rearrange(formations['pyramid'])

    def hlinePushed(self):
        self.rearrange(formations['hline'])
        
    def vlinePushed(self):
        self.rearrange(formations['vline'])
     
    def rearrange(self, formation):
        self.c1.setAttr('transform',"translate%s" % (formation[0],))
        self.c2.setAttr('transform',"translate%s" % (formation[1],))
        self.c3.setAttr('transform',"translate%s" % (formation[2],))
