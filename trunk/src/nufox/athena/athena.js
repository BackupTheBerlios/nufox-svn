
var nevow_baseURL = this.location.toString();
var nevow_queryParamIndex = nevow_baseURL.indexOf('?');

if (nevow_queryParamIndex != -1) {
    nevow_baseURL = nevow_baseURL.substring(0, nevow_queryParamIndex);
}

if (nevow_baseURL.charAt(nevow_baseURL.length - 1) != '/') {
    nevow_baseURL += '/';
}

nevow_baseURL += 'transport';

function nevow_constructActionURL(action, arguments) {
    var argumentQueryArgument = serializeJSON(arguments);
    return (nevow_baseURL
            + '?action='
            + encodeURIComponent(action)
            + '&args='
            + encodeURIComponent(argumentQueryArgument));
}

var nevow_remoteCallCount = 0;
var nevow_remoteCalls = {};
var nevow_outstandingTransports = 0;
var nevow_responseDispatchTable = new Object();

nevow_responseDispatchTable['text/xml'] = function(d, content) {
    d.callback(TEH_XML_PARSER(content));
}

nevow_responseDispatchTable['text/json'] = function(d, content) {
    d.callback(content);
}

function nevow_XMLHttpRequestReady(req) {
    nevow_outstandingTransports--;

    /* The response's content is a JSON-encoded 3-array of
     * [Response-Id, Request-Id, Content-Type, Content].  If this is a
     * response to a previous request, responseId will not
     * be null.  If this is a server-initiated request,
     * requestId will not be null.
     */

    var responseParts = evalJSON(req.responseText);

    var responseId = responseParts[0];
    var requestId = responseParts[1];

    if (requestId != null) {
        /* alert('Got a response to a request'); */

        var contentType = responseParts[2];
        var contentBody = responseParts[3];

        var d = nevow_remoteCalls[requestId];
        var handler = nevow_responseDispatchTable[contentType];
        delete nevow_remoteCalls[requestId];

        if (handler != null) {
            handler(d, contentBody);
        } else {
            /* alert("Unknown content-type: " + contentType); */
            d.errback(new Error("Unhandled content type: " + contentType));
        }

    } else if (responseId != null) {
        /* alert('Server initiated request'); */

        var contentBody = responseParts[2];

        var objectId = contentBody[0];
        var methodName = contentBody[1];
        var methodArgs = contentBody[2];

        /*
        var resultD = nevow_localObjectTable[objectId].dispatch(methodName, methodArgs);
        resultD.addCallbacks(nevow_respondToRequest
        */

        /* alert('Invoking ' + new String(methodName) + ' with arguments ' + new String(methodArgs)); */
        var result = eval(methodName).apply(null, methodArgs);

        /* if it quacks like a duck ...
           this sucks!!!  */
        var isDeferred = (
            result.addCallback != undefined &&
            result.addErrback != undefined);

        if (isDeferred) {
            result.addCallback(function(result){
                nevow_respondToRemote(responseId, result);
            });
        } else {
            nevow_respondToRemote(responseId, result);
        }

    } else {
        /* Protocol error */
        alert("Protocol error");
    }

    /* Client code has had a chance to run now, in response to
     * receiving the result.  If it issued a new request, we've got an
     * output channel already.  If it didn't, though, we might not
     * have one.  In that case, issue a no-op to the server so it can
     * send us things if it needs to. */
    if (nevow_outstandingTransports == 0) {
        nevow_sendNoOp();
    }
}

function nevow_XMLHttpRequestFail(req) {
    nevow_outstandingTransports--;

    if (nevow_outstandingTransports == 0) {
        nevow_sendNoOp();
    }
}

function nevow_prepareRemoteAction(actionType, args) {
    var url = nevow_constructActionURL(actionType, args);
    var req = MochiKit.Async.getXMLHttpRequest();
    req.open('GET', url, true);
    nevow_outstandingTransports++;
    /* alert("Setting livepage id " + new String(nevow_livepageId)); */
    req.setRequestHeader('Livepage-Id', nevow_livepageId);
    return req;
}

function nevow_respondToRemote(requestID, args) {
    var req = nevow_prepareRemoteAction('respond', [args]);
    req.setRequestHeader('Response-Id', requestID);
    MochiKit.Async.sendXMLHttpRequest(req).addCallbacks(nevow_XMLHttpRequestReady, nevow_XMLHttpRequestFail);
}

function nevow_sendNoOp() {
    var req = nevow_prepareRemoteAction('noop', []);
    MochiKit.Async.sendXMLHttpRequest(req).addCallbacks(nevow_XMLHttpRequestReady, nevow_XMLHttpRequestFail);
}

function nevow_callRemote(methodName, args) {
    var resultDeferred = new MochiKit.Async.Deferred();
    var req = nevow_prepareRemoteAction('call', MochiKit.Base.extend([methodName], args));
    var requestId = 'c2s' + nevow_remoteCallCount;

    nevow_remoteCallCount++;
    nevow_remoteCalls[requestId] = resultDeferred;
    req.setRequestHeader('Request-Id', requestId);

    MochiKit.Async.sendXMLHttpRequest(req).addCallbacks(nevow_XMLHttpRequestReady,
                                                        nevow_XMLHttpRequestFail)

    return resultDeferred;
}

var server = {
    /* Backwards compatibility API - you really want callRemote */
    handle: function(handlerName /*, ... */ ) {
        var args = [handlerName];
        for (var idx = 1; idx < arguments.length; idx++) {
            args.push(arguments[idx]);
        }
        nevow_callRemote('handle', args).addCallback(eval);
    },

    /* Invoke a method on the server.  Return a Deferred that fires
     * when the method completes. */
    callRemote: function(methodName /*, ... */) {
        var args = [];
        for (var idx = 1; idx < arguments.length; idx++) {
            args.push(arguments[idx]);
        }
        return nevow_callRemote(methodName, args);
    }
};
