"""nufox.widget base classes."""

import louie

from twisted.internet.defer import Deferred

from nufox.defer import defgen, dlist, wait
from nufox.widget import signal
from nufox.widget.signal import Signal
from nufox import xul
from nufox.xul import xulns


class Widget(xul.XULWidgetTemplate):
    """Base class for all `nufox.widget` classes.

    Some basic tenets are described below.


    General Naming
    ==============

    When possible, a class will retain the name of the primary XUL tag
    that it is based upon.  This provides familiarity when
    cross-referencing with general XUL documentation.

    Class names are in CamelCase, and method names are in mixedCase.
    This keeps method names in-line with Nevow and Twisted coding
    styles.


    Properties
    ==========

    A property is a combination of a getter (and optionally, a setter)
    method with a common base name.  Both getter and setter methods
    return a deferred that calls back with the property value.

    Getter methods are named the same as the property in mixedCase.
    For instance, to get the ``title`` property from a widget ``w``::

        def gotTitle(title):
            print title
        w.title().addCallback(gotTitle)

    Setter methods start with ``set``, followed by the name of the
    property in CamelCase. For instance, to set the ``title`` property
    of a widget ``w``::

        def wasSet(title):
            print u'title was set to', title
        w.setTitle(u'something').addCallback(wasSet)

    In general, a class will have properties for most or all of the
    attributes of the primary XUL tag that it is based upon.

    Python property decorators are not used, as property setter
    methods operate asynchronously and thus return deferreds.


    Server-side Events
    ==================

    `nufox.widget` aims to hide the details of typical
    client-to-server event handling, choosing instead to expose events
    on the server side via the following mechanism.

    Signals
    -------

    Signals are defined as subclasses of `nufox.widget.base.Signal`,
    and are used to identify the details of types of signals
    dispatched by a widget. Signals are named using mixedCase rather
    than CamelCase, despite that they are classes. For instance, a
    button widget might have the following signal defined::

        class TextBox(Widget):

            class changed(Signal):
                '''The text has changed.'''
                args = ('text', ) # Argument names, for documentation.

    Dispatching
    -----------

    To dispatch an event, widgets use their ``dispatch`` method,
    specifying the signal and optional arguments.  For instance, the
    button widget above might have this ``oncommand`` handler::

        def handle_onchange(self, text):
            self.dispatch(self.changed, text)

    Listening
    ---------

    To listen for events from a particular widget, call the
    dispatching widget's ``connect`` method, specifying the signal to
    watch for and a callable.  The naming convention for callables
    that are methods is ``on_``, then optionally a name of a contained
    widget followed by ``_``, then the name of the signal. For
    instance, here is how a widget that contains an instance of
    ``TextBox`` above could handle the ``changed`` signal::

        def setup(self):
            # ...
            tb = self.textBox = TextBox(...)
            tb.connect(tb.changed, self.on_textBox_changed)
            # ...

        def on_textBox_changed(self, text):
            print 'textBox was changed.'

    Disconnecting
    -------------

    To reverse the operation of ``connect``, use ``disconnect``.  For
    example, to disconnect the connection made in the listening
    example above, do this::

        tb.disconnect(tb.changed, self.on_textBox_changed)
            

    Client-to-Server Events
    =======================

    When using `nufox.widget`, you typically will not have to worry
    about the lower-level details of common client-to-server events.

    When an event is fired on the client side that is connected to an
    event handler in the widget instance, the handler will be named
    starting with ``handle_``, then optionally a name of a contained
    widget followed by ``_``, then the lowercase name of the
    client-side event.  For instance, here is how ``onclick`` would be
    handled for an XUL node ``okButton``::

        def setup(self):
            # ...
            b = self.okButton = xul.Button(...)
            b.addHandler('oncommand', self.handle_okButton_oncommand)
            # ...

        def handle_okButton_oncommand(self):
            print 'okButton was clicked.'


    Other Methods
    =============

    Methods that return information about a widget always return
    deferreds.

    Methods that act upon a widget on the remote side always return
    deferreds.
    """

    # Override these in subclasses.
    tag = None
    namespace = xulns
    xmlNamespaces = []
    
    def __init__(self, **kwargs):
        self.__receivers = []
        self.preInit(kwargs)
        xul.XULWidgetTemplate.__init__(self, **kwargs)
        # Set all remaining kwargs-based attributes using set/get.
        kwargs = self.kwargs
        for key in kwargs.keys():
            if key != 'id':
                self.set(key, kwargs[key])
        self.setup()

    def preInit(self, kwargs):
        """Override this if necessary to manipulate kwargs in
        subclasses during instantiation."""

    def setup(self):
        """Override this if necessary to manipulate widget during
        instantiation."""

    def close(self):
        """Close this widget, and dispatch a signal about its closure
        once the operation has completed."""
        return super(Widget, self).close().addCallback(self._after_close)
        
    def _after_close(self, result):
        self.dispatch(signal.closed)
        return result

    def connect(self, signal, receiver):
        """Connect the sending of ``signal`` by this widget to
        ``receiver``."""
        louie.connect(receiver, signal, self)
        self.__receivers.append((receiver, signal))

    def disconnect(self, signal, receiver):
        """Reverse of ``connect``."""
        louie.disconnect(receiver, signal, self)
        self.__receivers.remove((receiver, signal))

    @defgen
    def dispatch(self, signal, *args):
        """Dispatch ``signal`` with optional ``args`` to listeners.

        Returns a deferred that calls back with a list of
        (receiver, result) tuples after all receivers have finished.
        """
        receiver_results = louie.send_minimal(signal, self, *args)
        results = []
        for receiver, result in receiver_results:
            if isinstance(result, Deferred):
                result = wait(result)
                yield result
                result = result.getResult()
            results.append((receiver, result))
        yield results

    def getTag(self):
        t = getattr(self.namespace, self.tag)
        return t(*self.xmlNamespaces, **self.kwargs)

    def get(self, attr):
        fn = getattr(self, 'preGet_%s' % attr, None)
        if callable(fn):
            attr = fn()
        d = super(Widget, self).get(attr)
        fn = getattr(self, 'postGet_%s' % attr, None)
        if callable(fn):
            d.addCallback(fn)
        return d

    def set(self, attr, value):
        fn = getattr(self, 'preSet_%s' % attr, None)
        if callable(fn):
            attr, value = fn(value)
        d = super(Widget, self).set(attr, value)
        fn = getattr(self, 'postSet_%s' % attr, None)
        if callable(fn):
            def returnValue(result):
                fn(value)
                return result
            d.addCallback(returnValue)
        return d
