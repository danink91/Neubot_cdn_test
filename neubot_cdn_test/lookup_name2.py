#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Performs reverse lookup of an address """

from twisted.names import error
from twisted.internet import defer
from twisted.names import client
from twisted.names import dns
import json
import socket

class LookupAnswer(object):
    """ Wrapper for Twisted lookup answer """

    def __init__(self, result):
        if hasattr(result, 'index'):
            if hasattr(result[0][0], 'type'):
                self.result = result
                self.errmessage = []
                self.erradditional = []
        else:
            if hasattr(result.value.message, 'rCode') and hasattr(result, 'getErrorMessage'):
                if result.value.message.rCode == dns.ENAME:
                    self.errmessage = []
                    self.errmessage.append(result)
                    self.result = []
                    self.erradditional = []
                else:
                    self.erradditional = []
                    self.erradditional.append(result)
                    self.result = []
                    self.errmessage = []
            else:
                self.erradditional = []
                self.erradditional.append(result)
                self.result = []
                self.errmessage = []

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
        for element in self.result:
            for elem in element:
                if hasattr(elem, 'type'):
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
        for elem in self.errmessage:
            if hasattr(elem.value.message, 'rCode'):
                if elem.value.message.rCode == dns.ENAME:
                    content.append({
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
        for elem in self.erradditional:
            content.append({"error" : str(elem.value),})

        return json.dumps(content, indent=2)

    def join_result(self, elem_to_add):
        """Join results"""
        for err_mess in elem_to_add.errmessage:
            self.errmessage.append(err_mess)
        for err_add in elem_to_add.erradditional:
            self.erradditional.append(err_add)
        for element in elem_to_add.result:
            for elem in element:
                self.result[0].append(elem)

        return self

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


def lookup_name4(server, name, factory=client.createResolver):
    """ This function performs the lookup for ipv4 """
    resolver = factory(servers=[(server, 53)])
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    def wrap_error(err):
        """ Wrap error returned by Twisted """
        outer_deferred.errback(LookupAnswer(err))

    inner_deferred = resolver.lookupAddress(name=name)
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def lookup_name6(server, name, factory=client.createResolver):
    """ This function performs the lookup for ipv6 """
    resolver = factory(servers=[(server, 53)])
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(LookupAnswer(result))

    def wrap_error(err):
        """ Wrap error returned by Twisted """
        outer_deferred.errback(LookupAnswer(err))

    inner_deferred = resolver.lookupIPV6Address(name=name)
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def lookup_name(server, name, factory=client.createResolver):
    """ This function performs the lookup """
    outer_deferred = defer.Deferred()
    def wrap_result(result):
        """ Wrap result returned by Twisted """
        in_deferred = defer.Deferred()

        def wrap_res(res):
            """ Wrap result returned by Twisted """
            outer_deferred.callback(result.join_result(res))

        def wrap_err(err_ipv6):
            """ Wrap err_ipv6 returned by Twisted """
            outer_deferred.errback(result.join_result(err_ipv6.value))

        in_deferred = lookup_name6(server, name, factory)
        in_deferred.addCallbacks(wrap_res, wrap_err)

    def wrap_error(err_ipv4):
        """ Wrap err_ipv4 returned by Twisted """
        in_deferred = defer.Deferred()
        def wrap_res(res):
            """ Wrap result returned by Twisted """
            outer_deferred.callback(err_ipv4.value.join_result(LookupAnswer(res)))

        def wrap_err(err_ipv6):
            """ Wrap err_ipv6 returned by Twisted """
            outer_deferred.errback(err_ipv4.value.join_result(err_ipv6.value))

        in_deferred = lookup_name6(server, name, factory)
        in_deferred.addCallbacks(wrap_res, wrap_err)

    inner_deferred = lookup_name4(server, name, factory)
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def main():
    """ Main function """
    from twisted.internet import reactor
    import sys
    #TEST connectivity
    deferred = lookup_name("8.8.8.8", sys.argv[1])
    def print_result(result):
        """ Print result of name lookup """
        print result
        reactor.stop()

    def print_error(err):
        """ Print error of name lookup """
        print err.value
        if reactor.running:
            reactor.stop()



    deferred.addCallbacks(print_result, print_error)
    reactor.run()


if __name__ == "__main__":
    main()