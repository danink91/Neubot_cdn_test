#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Performs reverse lookup of an address

Example usage:

from twisted.internet import reactor
import sys
def main():

    deferred = lookup_name("8.8.8.8", sys.argv[1])
    def print_result(result):
        print result
        reactor.stop()

    def print_error(err):
        x=LookupErrors(err)
        outer_deferred.callback(x)

    deferred.addCallbacks(print_result,print_error)
    reactor.run()

if __name__ == "__main__":
    main()
"""

from twisted.names import error
from twisted.internet import defer
from twisted.names import client
from twisted.names import dns
import json
import socket
import time


class LookupAnswer(object):
    """ Wrapper for Twisted lookup answer """

    def __init__(self, result):
        self.result = result

    @staticmethod
    def _address_to_string(elem):
        """ Map address to string depending on type """
        if elem.type == dns.A:
            return socket.inet_ntop(socket.AF_INET, elem.payload.address)
        elif elem.type == dns.AAAA:
            return socket.inet_ntop(socket.AF_INET6, elem.payload.address)
        else:
            raise RuntimeError

    def __str__(self):
        content = self.dict_repr()
        return json.dumps(content, indent=2)

    def dict_repr(self):
        """Dictionary representation"""
        content = []
        for elem in self.result[0]:
            if hasattr(elem, 'type'):
                if elem.type in (dns.A, dns.AAAA):
                    content.append({
                        "utime": int(time.time()),
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": str(elem.name),
                        "type": getattr(elem, "type"),
                        "class": elem.cls,
                        "ttl": elem.ttl,
                        "auth": elem.auth,
                        "payload": {
                            "address" : self._address_to_string(elem),
                            "ttl": elem.payload.ttl,
                        },
                    })
        return content

    def _get_ipvx_addresses(self, expected):
        """ Internal function to get addresses """
        content = []
        for elem in self.result[0]:
            if elem.type == expected:
                content.append(self._address_to_string(elem))
        return content

    def get_ipv4_addresses(self):
        """ Returns the list of ipv4 of the lookup answer """
        return self._get_ipvx_addresses(dns.A)

    def get_ipv6_addresses(self):
        """ Returns the list of ipv4 of the lookup answer """
        return self._get_ipvx_addresses(dns.AAAA)

class LookupErrors(object):
    """This class is the list of Lookup Error"""
    def __init__(self, result):
        self.message = []
        self.message.append(result)

    def __str__(self):
        content = self.dict_repr()
        return json.dumps(content, indent=2)

    def dict_repr(self):
        """Dictionary representation"""
        content = []
        for elem in self.message:
            if hasattr(elem.value.message, 'rCode'):
                if elem.value.message.rCode == dns.ENAME:
                    content.append({
                        "utime": int(time.time()),
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "id" : str(elem.value.message.id),
                        "rCode" : str(elem.value.message.rCode),
                        "maxSize": str(elem.value.message.maxSize),
                        "answer": str(elem.value.message.answer),
                        "recDes": str(elem.value.message.recDes),
                        "recAv": str(elem.value.message.recAv),
                        "queries": str(elem.value.message.queries),
                        "authority": str(elem.value.message.authority),
                        "opCode": str(elem.value.message.opCode),
                        "ns": str(elem.value.message.ns),
                        "auth": str(elem.value.message.auth),
                    })
                else:
                    content.append({"error" : str(elem.value),})
            else:
                content.append({"error" : str(elem.value),})
        return content

def lookup_name4(name, server=None):
    """ This function performs the lookup for ipv4 """
    if server != None:
        resolver = client.Resolver(servers=[(server, 53)])
    else:
        resolver = client.createResolver()
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    def wrap_error(err):
        """ Wrap error returned by Twisted """
        outer_deferred.errback(LookupErrors(err))

    inner_deferred = resolver.lookupAddress(name=name, timeout=[2,5])
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def lookup_name6(name, server=None):
    """ This function performs the lookup for ipv6 """
    if server != None:
        resolver = client.Resolver(servers=[(server, 53)])
    else:
        resolver = client.createResolver()
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    def wrap_error(err):
        """ Wrap error returned by Twisted """
        outer_deferred.errback(LookupErrors(err))

    inner_deferred = resolver.lookupIPV6Address(name=name, timeout=[2,5])
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def main():
    """ Main function """
    from twisted.internet import reactor
    import sys
    def do_lookup():
        deferred = lookup_name4(sys.argv[1], server="208.67.222.222")
        #deferred = lookup_name6(sys.argv[1], server="8.8.8.8")
        def print_result(result):
            """ Print result of name lookup """
            print result
            reactor.stop()

        def print_error(err):
            """ Print error of name lookup """
            print err.value
            reactor.stop()

        deferred.addCallbacks(print_result, print_error)
    
    reactor.callLater(0.0, do_lookup)
    reactor.run()

if __name__ == "__main__":
    main()
