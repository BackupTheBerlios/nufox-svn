"""Multiple-producer-multiple-consumer signal-dispatching.

dispatcher is the core of the PyDispatcher system, providing the
primary API and the core logic for the system.

Module attributes of note:

  Any:

    Singleton used to signal either 'Any Sender' or 'Any Signal'.  See
    documentation of the _Any class.

  Anonymous:

    Singleton used to signal 'Anonymous Sender'.  See documentation of
    the _Anonymous class.

Internal attributes:

  WEAKREF_TYPES:

    Tuple of types/classes which represent weak references to
    receivers, and thus must be dereferenced on retrieval to retrieve
    the callable object
        
  connections:

    { senderkey (id) : { signal : [receivers...] } }
    
  senders:

    { senderkey (id) : weakref(sender) }

    Used for cleaning up sender references on sender deletion
        
  sendersBack:

    { receiverkey (id) : [senderkey (id)...] }

    Used for cleaning up receiver references on receiver deletion.
"""


import os
import weakref

from nufox.widget._dispatcher import saferef, robustapply, errors


# Support for statistics.

connects = 0
disconnects = 0
sends = 0

def printStats():
    print ('\n'
           'PyDispatcher connects: %i\n'
           'PyDispatcher disconnects: %i\n'
           'PyDispatcher sends: %i\n'
           '\n') % (connects, disconnects, sends)

if 'PYDISPATCH_STATS' in os.environ:
    import atexit
    atexit.register(printStats)


class _Parameter:
    """Used to represent default parameter values."""
    
    def __repr__(self):
        return self.__class__.__name__


class _Any(_Parameter):
    """Singleton used to signal either 'Any Sender' or 'Any Signal'.

    The Any object can be used with connect, disconnect, send, or
    sendExact to signal that the parameter given Any should react to
    all senders/signals, not just a particular sender/signal.
    """
Any = _Any()


class _Anonymous(_Parameter):
    """Singleton used to signal 'Anonymous Sender'

    The Anonymous object is used to signal that the sender of a
    message is not specified (as distinct from being 'any sender').
    Registering callbacks for Anonymous will only receive messages
    sent without senders.  Sending with anonymous will only send
    messages to those receivers registered for Any or Anonymous.

    Note: The default sender for connect is Any, while the default
    sender for send is Anonymous.  This has the effect that if you do
    not specify any senders in either function then all messages are
    routed as though there was a single sender (Anonymous) being used
    everywhere.
    """
Anonymous = _Anonymous()


WEAKREF_TYPES = (weakref.ReferenceType, saferef.BoundMethodWeakref)


connections = {}
senders = {}
sendersBack = {}
plugins = []

def reset():
    """Reset the state of PyDispatcher.

    Useful during unit testing.  Should be avoided otherwise.
    """
    global connections, senders, sendersBack, plugins
    connections = {}
    senders = {}
    sendersBack = {}
    plugins = []


def connect(receiver, signal=Any, sender=Any, weak=True):
    """Connect receiver to sender for signal

    receiver:

      A callable Python object which is to receive
      messages/signals/events.  Receivers must be hashable objects.

      If weak is True, then receiver must be weak-referencable (more
      precisely saferef.safeRef() must be able to create a reference
      to the receiver).
    
      Receivers are fairly flexible in their specification, as the
      machinery in the robustApply module takes care of most of the
      details regarding figuring out appropriate subsets of the sent
      arguments to apply to a given receiver.

      Note: If receiver is itself a weak reference (a callable), it
      will be de-referenced by the system's machinery, so *generally*
      weak references are not suitable as receivers, though some use
      might be found for the facility whereby a higher-level library
      passes in pre-weakrefed receiver references.

    signal:

      The signal to which the receiver should respond.
    
      If Any, receiver will receive any signal from the indicated
      sender (which might also be Any, but is not necessarily Any).
        
      Otherwise must be a hashable Python object other than None
      (DispatcherError raised on None).
        
    sender:

      The sender to which the receiver should respond.
    
      If Any, receiver will receive the indicated signals from any
      sender.
        
      If Anonymous, receiver will only receive indicated signals from
      send/sendExact which do not specify a sender, or specify
      Anonymous explicitly as the sender.

      Otherwise can be any python object.
        
    weak:

      Whether to use weak references to the receiver.
      
      By default, the module will attempt to use weak references to
      the receiver objects.  If this parameter is false, then strong
      references will be used.

    Returns None, may raise DispatcherTypeError.
    """
    if signal is None:
        raise errors.DispatcherTypeError(
            'Signal cannot be None (receiver=%r sender=%r)'%( receiver,sender)
            )
    if weak:
        receiver = saferef.safeRef(receiver, onDelete=_removeReceiver)
    senderkey = id(sender)
    if connections.has_key(senderkey):
        signals = connections[senderkey]
    else:
        connections[senderkey] = signals = {}
    # Keep track of senders for cleanup.
    # Is Anonymous something we want to clean up?
    if sender not in (None, Anonymous, Any):
        def remove(object, senderkey=senderkey):
            _removeSender(senderkey=senderkey)
        # Skip objects that can not be weakly referenced, which means
        # they won't be automatically cleaned up, but that's too bad.
        try:
            weakSender = weakref.ref(sender, remove)
            senders[senderkey] = weakSender
        except:
            pass
        
    receiverID = id(receiver)
    # get current set, remove any current references to
    # this receiver in the set, including back-references
    if signals.has_key(signal):
        receivers = signals[signal]
        _removeOldBackRefs(senderkey, signal, receiver, receivers)
    else:
        receivers = signals[signal] = []
    try:
        current = sendersBack.get(receiverID)
        if current is None:
            sendersBack[receiverID] = current = []
        if senderkey not in current:
            current.append(senderkey)
    except:
        pass

    receivers.append(receiver)

    # Update stats.
    global connects
    connects += 1


def disconnect(receiver, signal=Any, sender=Any, weak=True):
    """Disconnect receiver from sender for signal

    receiver: The registered receiver to disconnect.
    
    signal: The registered signal to disconnect.
    
    sender: The registered sender to disconnect.
    
    weak: The weakref state to disconnect.

    disconnect reverses the process of connect, the semantics for the
    individual elements are logically equivalent to a tuple of
    (receiver, signal, sender, weak) used as a key to be deleted from
    the internal routing tables.  (The actual process is slightly more
    complex but the semantics are basically the same).

    Note: Using disconnect is not required to cleanup routing when an
    object is deleted, the framework will remove routes for deleted
    objects automatically.  It's only necessary to disconnect if you
    want to stop routing to a live object.
        
    Returns None, may raise DispatcherTypeError or DispatcherKeyError.
    """
    if signal is None:
        raise errors.DispatcherTypeError(
            'Signal cannot be None (receiver=%r sender=%r)'%( receiver,sender)
            )
    if weak:
        receiver = saferef.safeRef(receiver)
    senderkey = id(sender)
    try:
        signals = connections[senderkey]
        receivers = signals[signal]
    except KeyError:
        raise errors.DispatcherKeyError(
            'No receivers found for signal %r from sender %r' 
            % (signal, sender)
            )
    try:
        # also removes from receivers
        _removeOldBackRefs(senderkey, signal, receiver, receivers)
    except ValueError:
        raise errors.DispatcherKeyError(
            'No connection to receiver %s for signal %s from sender %s'
            % (receiver, signal, sender)
            )
    _cleanupConnections(senderkey, signal)

    # Update stats.
    global disconnects
    disconnects += 1


def getReceivers(sender=Any, signal=Any):
    """Get list of receivers from global tables.

    This utility function allows you to retrieve the raw list of
    receivers from the connections table for the given sender and
    signal pair.

    Note: There is no guarantee that this is the actual list stored in
    the connections table, so the value should be treated as a simple
    iterable/truth value rather than, for instance a list to which you
    might append new records.

    Normally you would use liveReceivers(getReceivers(...)) to
    retrieve the actual receiver objects as an iterable object.
    """
    try:
        return connections[id(sender)][signal]
    except KeyError:
        return []


def liveReceivers(receivers):
    """Filter sequence of receivers to get resolved, live receivers.

    This is a generator which will iterate over the passed sequence,
    checking for weak references and resolving them, then returning
    all live receivers.
    """
    for receiver in receivers:
        if isinstance(receiver, WEAKREF_TYPES):
            # Dereference the weak reference.
            receiver = receiver()
        if receiver is not None:
            # Check installed plugins to make sure this receiver is
            # live.
            live = True
            for plugin in plugins:
                if not plugin.is_live(receiver):
                    live = False
                    break
            if live:
                yield receiver
            

def getAllReceivers(sender=Any, signal=Any):
    """Get list of all receivers from global tables.

    This gets all receivers which should receive the given signal from
    sender, each receiver should be produced only once by the
    resulting generator.
    """
    receivers = {}
    for set in (
        # Get receivers that receive *this* signal from *this* sender.
        getReceivers(sender, signal),
        # Add receivers that receive *any* signal from *this* sender.
        getReceivers(sender, Any),
        # Add receivers that receive *this* signal from *any* sender.
        getReceivers(Any, signal),
        # Add receivers that receive *any* signal from *any* sender.
        getReceivers(Any, Any),
        ):
        for receiver in set:
            if receiver: # filter out dead instance-method weakrefs
                try:
                    if not receivers.has_key(receiver):
                        receivers[receiver] = 1
                        yield receiver
                except TypeError:
                    # dead weakrefs raise TypeError on hash...
                    pass


def send(signal=Any, sender=Anonymous, *arguments, **named):
    """Send signal from sender to all connected receivers.
    
    signal:

      (Hashable) signal value, see connect for details

    sender:

      The sender of the signal.
    
      If Any, only receivers registered for Any will receive the
      message.

      If Anonymous, only receivers registered to receive messages from
      Anonymous or Any will receive the message.

      Otherwise can be any Python object (normally one registered with
      a connect if you actually want something to occur).

    arguments:

      Positional arguments which will be passed to *all*
      receivers. Note that this may raise TypeErrors if the receivers
      do not allow the particular arguments.  Note also that arguments
      are applied before named arguments, so they should be used with
      care.

    named:

      Named arguments which will be filtered according to the
      parameters of the receivers to only provide those acceptable to
      the receiver.

    Return a list of tuple pairs [(receiver, response), ...]

    If any receiver raises an error, the error propagates back through
    send, terminating the dispatch loop, so it is quite possible to
    not have all receivers called if a raises an error.
    """
    # Call each receiver with whatever arguments it can accept.
    # Return a list of tuple pairs [(receiver, response), ... ].
    responses = []
    for receiver in liveReceivers(getAllReceivers(sender, signal)):
        # Wrap receiver using installed plugins.
        original = receiver
        for plugin in plugins:
            receiver = plugin.wrap_receiver(receiver)
        response = robustapply.robustApply(
            receiver, original,
            signal=signal,
            sender=sender,
            *arguments,
            **named
            )
        responses.append((receiver, response))

    # Update stats.
    global sends
    sends += 1
    
    return responses


def sendExact(signal=Any, sender=Anonymous, *arguments, **named):
    """Send signal only to receivers registered for exact message.

    sendExact allows for avoiding Any/Anonymous registered handlers,
    sending only to those receivers explicitly registered for a
    particular signal on a particular sender.
    """
    responses = []
    for receiver in liveReceivers(getReceivers(sender, signal)):
        # Wrap receiver using installed plugins.
        original = receiver
        for plugin in plugins:
            receiver = plugin.wrap_receiver(receiver)
        response = robustapply.robustApply(
            receiver, original,
            signal=signal,
            sender=sender,
            *arguments,
            **named
            )
        responses.append((receiver, response))
    return responses
    

class Plugin(object):
    """Base class for PyDispatcher plugins.

    Plugins are used to extend or alter the behavior of PyDispatcher
    in a uniform way without having to modify the PyDispatcher code
    itself.

    Common plugins are available in the `plugin` module.
    """

    def is_live(self, receiver):
        """Return True if the receiver is still live.

        Only called for receivers who have already been determined to
        be live by default PyDispatcher semantics.
        """
        return True

    def wrap_receiver(self, receiver):
        """Return a callable that passes arguments to the receiver.

        Useful when you want to change the behavior of all receivers.
        """
        return receiver


def _removeReceiver(receiver):
    """Remove receiver from connections."""
    if not sendersBack:
        # During module cleanup the mapping will be replaced with None.
        return False
    backKey = id(receiver)
    for senderkey in sendersBack.get(backKey, ()):
        try:
            signals = connections[senderkey].keys()
        except KeyError:
            pass
        else:
            for signal in signals:
                try:
                    receivers = connections[senderkey][signal]
                except KeyError:
                    pass
                else:
                    try:
                        receivers.remove(receiver)
                    except Exception:
                        pass
                _cleanupConnections(senderkey, signal)
    try:
        del sendersBack[backKey]
    except KeyError:
        pass

            
def _cleanupConnections(senderkey, signal):
    """Delete empty signals for senderkey. Delete senderkey if empty."""
    try:
        receivers = connections[senderkey][signal]
    except:
        pass
    else:
        if not receivers:
            # No more connected receivers. Therefore, remove the signal.
            try:
                signals = connections[senderkey]
            except KeyError:
                pass
            else:
                del signals[signal]
                if not signals:
                    # No more signal connections. Therefore, remove the sender.
                    _removeSender(senderkey)


def _removeSender(senderkey):
    """Remove senderkey from connections."""
    _removeBackrefs(senderkey)
    try:
        del connections[senderkey]
    except KeyError:
        pass
    # Senderkey will only be in senders dictionary if sender 
    # could be weakly referenced.
    try:
        del senders[senderkey]
    except:
        pass


def _removeBackrefs(senderkey):
    """Remove all back-references to this senderkey."""
    try:
        signals = connections[senderkey]
    except KeyError:
        signals = None
    else:
        items = signals.items()
        def allReceivers():
            for signal, set in items:
                for item in set:
                    yield item
        for receiver in allReceivers():
            _killBackref(receiver, senderkey)


def _removeOldBackRefs(senderkey, signal, receiver, receivers):
    """Kill old sendersBack references from receiver.

    This guards against multiple registration of the same receiver for
    a given signal and sender leaking memory as old back reference
    records build up.

    Also removes old receiver instance from receivers.
    """
    try:
        index = receivers.index(receiver)
        # need to scan back references here and remove senderkey
    except ValueError:
        return False
    else:
        oldReceiver = receivers[index]
        del receivers[index]
        found = 0
        signals = connections.get(signal)
        if signals is not None:
            for sig, recs in connections.get(signal, {}).iteritems():
                if sig != signal:
                    for rec in recs:
                        if rec is oldReceiver:
                            found = 1
                            break
        if not found:
            _killBackref(oldReceiver, senderkey)
            return True
        return False
        
        
def _killBackref(receiver, senderkey):
    """Do actual removal of back reference from receiver to senderkey."""
    receiverkey = id(receiver)
    set = sendersBack.get(receiverkey, ())
    while senderkey in set:
        try:
            set.remove(senderkey)
        except:
            break
    if not set:
        try:
            del sendersBack[receiverkey]
        except KeyError:
            pass
    return True

    
