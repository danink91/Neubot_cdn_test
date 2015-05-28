#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Performs reverse lookup of an address """



from twisted.internet import defer

from twisted.names import client
from twisted.names import dns

import json
import logging
import socket

class ReverseAnswer(object):
    """This class is the list of Reverse Answers"""
    def __init__(self,result):
        self.ans = result[0]
        self.auth = result[1]
        self.additional = result[2]
    def __str__(self):
        content = []
        for elem in self.ans:
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
        return json.dumps(content, indent=2)

def getquery(address):
    """Takes as input an address and processes ipv4 and ipv6 for DNSquery"""
    try:
        socket.inet_aton(address)
        return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'
    except socket.error:

        try:
            address =socket.inet_pton(socket.AF_INET6, address).encode('hex')
            s=""    
            for i in address:
                s=s+"."+i
            return s[::-1]+'ip6.arpa'
        except socket.error:
            print "error"
            return "error"
    

def reverse_ip_address(address):
    """This function takes as input an address gets the query"""
    query=getquery(address)
    return query  
    
    
    

def reverse_lookup(address):
    """This function performs the Reverse Lookup for each ip of
    lookup answer"""
    outer_deferred = defer.Deferred()
    def wrap_result(result):
        """ Wrap result returned by Twisted """
        logging.debug("wrap_result: %s", result)
        outer_deferred.callback(ReverseAnswer(result))

    rev_ip = reverse_ip_address(address=address)
    inner_deferred = client.lookupPointer(rev_ip)
    inner_deferred.addCallback(wrap_result)
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

    deferred.addCallback(print_result)
    reactor.run()

if __name__ == "__main__":
    main()
