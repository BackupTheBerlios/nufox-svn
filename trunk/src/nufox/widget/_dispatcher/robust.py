"""Module implementing error-catching version of send (sendRobust)."""

from nufox.widget._dispatcher.dispatcher import (
    Any, Anonymous, liveReceivers, getAllReceivers)
from nufox.widget._dispatcher.robustapply import robustApply


def sendRobust(signal=Any, sender=Anonymous, *arguments, **named):
    """Send signal from sender to all connected receivers catching errors

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

    Return a list of tuple pairs [(receiver, response), ... ]

    If any receiver raises an error (specifically, any subclass of
    Exception), the error instance is returned as the result for that
    receiver.
    """
    # Call each receiver with whatever arguments it can accept.
    # Return a list of tuple pairs [(receiver, response), ... ].
    responses = []
    for receiver in liveReceivers(getAllReceivers(sender, signal)):
        try:
            response = robustApply(
                receiver,
                signal=signal,
                sender=sender,
                *arguments,
                **named
                )
        except Exception, err:
            responses.append((receiver, err))
        else:
            responses.append((receiver, response))
    return responses
