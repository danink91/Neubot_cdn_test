#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Performs lookup of DNS names """


from twisted.internet import defer
from twisted.names import client
from twisted.names import dns
import json
import logging
import socket

class LookupAnswer(object):
    """ Wrapper for Twisted lookup answer """

    def __init__(self, result):
        self.ans = result[0]
        self.auth = result[1]
        self.additional = result[2]


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
        content = []
        for elem in self.ans:
            logging.debug("__str__: elem %s", elem)
            if elem.type in (dns.A, dns.AAAA):
                content.append({
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
        return json.dumps(content, indent=2)

    def join_ipv4_ipv6(self, ipv6):
        """Join result ipv4 and ip6"""
        for ip6 in ipv6.ans:
            self.ans.append(ip6)
        return self

    def _get_ipvx_addresses(self, expected):
        """ Internal function to get addresses """
        content = []
        for elem in self.ans:
            if elem.type == expected:
                content.append(self._address_to_string(elem))
        return content

    def get_ipv4_addresses(self):
        """ Returns the list of ipv4 of the lookup answer """
        return self._get_ipvx_addresses(dns.A)

    def get_ipv6_addresses(self):
        """ Returns the list of ipv4 of the lookup answer """
        return self._get_ipvx_addresses(dns.AAAA)

def lookup(server, name):
    """ This function performs the lookup """
    outer_deferred = defer.Deferred()
    def wrap_result(result):
        """ Wrap result returned by Twisted """
        in_deferred = defer.Deferred()
        def wrap_res(res):
            """ Wrap result returned by Twisted """
            outer_deferred.callback(result.join_ipv4_ipv6(res))
        in_deferred = lookup_name6(server, name)
        in_deferred.addCallback(wrap_res)

    inner_deferred = lookup_name(server, name)
    inner_deferred.addCallback(wrap_result)
    return outer_deferred

def lookup_name(server, name):
    """ This function performs the lookup """
    resolver = client.createResolver(servers=[(server, 53)])
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    inner_deferred = resolver.lookupAddress(name=name)
    inner_deferred.addCallback(wrap_result)
    return outer_deferred

def lookup_name6(server, name):
    """ This function performs the lookup """
    resolver = client.createResolver(servers=[(server, 53)])
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    inner_deferred = resolver.lookupIPV6Address(name=name)
    inner_deferred.addCallback(wrap_result)
    return outer_deferred

def main():
    """ Main function """
    from twisted.internet import reactor
    import sys
    deferred = lookup("8.8.8.8", sys.argv[1])
    def print_result(result):
        """ Print result of name lookup """
        print result
        print result.get_ipv4_addresses()
        print result.get_ipv6_addresses()
        reactor.stop()

    deferred.addCallback(print_result)
    reactor.run()

if __name__ == "__main__":
    main()
