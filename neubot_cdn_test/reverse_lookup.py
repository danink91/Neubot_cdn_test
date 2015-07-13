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

    deferred = reverse_lookup(sys.argv[1])

    def print_result(result):
        print result
        reactor.stop()

    def print_error(err):
        print err
        reactor.stop()

    deferred.addCallbacks(print_result,print_error)
    reactor.run()

if __name__ == "__main__":
    main()
"""

from twisted.internet import defer
from twisted.names import client
from twisted.names import dns
from twisted.names import error
import json
import socket
import ipaddress_local


class ReverseAnswer(object):
    """This class is the list of Reverse Answers"""
    def __init__(self, result):
        self.result = result

    def __str__(self):
        content = self.dict_repr()
        return json.dumps(content, indent=2)

    def dict_repr(self):
        """Dictionary representation"""
        content = []
        for elem in self.result[0]:
            if elem.type == dns.PTR:
                content.append({
                    "name" : str(elem.name),
                    "type" : getattr(elem, "type"),
                    "class": elem.cls,
                    "ttl": elem.ttl,
                    "auth": elem.auth,
                    "payload":{
                        "name" : str(elem.payload.name),
                        "ttl": elem.payload.ttl, }
                })
        return content

class ReverseErrors(object):
    """This class is the list of Reverse Errors"""
    def __init__(self, result):
        self.message = result

    def __str__(self):
        content = self.dict_repr()
        return json.dumps(content, indent=2)

    def dict_repr(self):
        """Dictionary representation"""
        content = []
        content.append({
            "id" : str(self.message.value.message.id),
            "rCode" : str(self.message.value.message.rCode),
            "maxSize": str(self.message.value.message.maxSize),
            "answer": str(self.message.value.message.answer),
            "recDes": str(self.message.value.message.recDes),
            "recAv": str(self.message.value.message.recAv),
            "queries": str(self.message.value.message.queries),
            "authority": str(self.message.value.message.authority),
            "opCode": str(self.message.value.message.opCode),
            "ns": str(self.message.value.message.ns),
            "auth": str(self.message.value.message.auth),
        })
        return content

def reverse_ipv6(ipv6):

    """Return the reverse DNS pointer name for the IPv6 address.
    This implements the method described in RFC3596 2.5. """
    reverse_chars = ipaddress_local.ip_address(ipv6).exploded[::-1].replace(':', '')
    return '.'.join(reverse_chars) + '.ip6.arpa'

def reverse_ipv4(ipv4):

    """Return the reverse DNS pointer name for the IPv4 address.
    This implements the method described in RFC1035 3.5. """
    reverse_octets = str(ipv4).split('.')[::-1]
    return '.'.join(reverse_octets) + '.in-addr.arpa'

def getquery(address):
    """Takes as input an address and processes ipv4 and ipv6 for DNSquery"""
    try:
        socket.inet_aton(address)
        return reverse_ipv4(address)
    except socket.error:
        try:
            address = socket.inet_pton(socket.AF_INET6, address)
            return reverse_ipv6(address)
        except socket.error:
            return "IP not valid"

def reverse_ip_address(address):
    """This function takes as input an address gets the query"""
    query = getquery(address)
    return query

def reverse_lookup(address):
    """This function performs the Reverse Lookup for each ip of
    lookup answer"""
    outer_deferred = defer.Deferred()

    def wrap_result(result):
        """ Wrap result returned by Twisted """
        outer_deferred.callback(ReverseAnswer(result))

    def wrap_error(err):
        """ Wrap error returned by Twisted """
        outer_deferred.errback(ReverseErrors(err))

    rev_ip = reverse_ip_address(address=address)
    inner_deferred = client.lookupPointer(rev_ip)
    inner_deferred.addCallbacks(wrap_result, wrap_error)
    return outer_deferred

def main():
    """ Main function """
    from twisted.internet import reactor
    import sys
    deferred = reverse_lookup(sys.argv[1])

    def print_result(result):
        """ Print result of name lookup """
        print result
        reactor.stop()

    def print_error(err):
        """ Print err of name lookup """
        print err.value
        reactor.stop()

    deferred.addCallbacks(print_result, print_error)
    reactor.run()

if __name__ == "__main__":
    main()
