#!/usr/bin/python

"""This script is a test for CDN-test"""

from twisted.internet import reactor
import json
from twisted.names import client
from twisted.names import dns
import time
import datetime

TYPE_PTR = dns.PTR
TYPE_A = dns.A
TYPE_AAAA = dns.AAAA

class Answer(object):
    """This class is the complete answer"""

    def __init__(self, L, RL, server):
        times = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(times).strftime(
            '%Y-%m-%d %H:%M:%S')
        self.server = server
        self.lookup = L
        self.rlookup = RL

    def __str__(self):
        content = []
        content.append({
            "timestamp": str(self.timestamp),
            "server": str(self.server),

            "name": str(self.lookup.name),
            "type": getattr(self.lookup, "type"),
            "class": self.lookup.cls,
            "ttl": self.lookup.ttl,
            "auth": self.lookup.auth,
            "payload": {
                "address" : str(self.lookup.payload.dottedQuad()),
                "ttl": self.lookup.payload.ttl, },

            "nameR": str(self.rlookup.name),
            "typeR": getattr(self.rlookup, "type"),
            "classR": self.rlookup.cls,
            "ttlR": self.rlookup.ttl,
            "authR": self.rlookup.auth,
            "payloadR":{
                "nameR" : str(self.rlookup.payload.name),
                "ttlR": self.rlookup.payload.ttl, }
            })
        return json.dumps(content, indent=2)

class AnswersR(object):
    """This class is the list of Reverse Answers"""
    def __init__(self, ans, auth, additional):
        self.ans = ans
        self.auth = auth
        self.additional = additional
    def __str__(self):
        content = []
        for elem in self.ans:
            if elem.type == TYPE_PTR:
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

class AnswersL(object):
    """This class is the list of Lookup Answers"""

    def __init__(self, ans, auth, additional):
        self.ans = ans
        self.auth = auth
        self.additional = additional

    def __str__(self):
        content = []
        for elem in self.ans:
            if elem.type == TYPE_A or elem.type == TYPE_AAAA:
                content.append({
                    "name": str(elem.name),
                    "type": getattr(elem, "type"),
                    "class": elem.cls,
                    "ttl": elem.ttl,
                    "auth": elem.auth,
                    "payload": str(elem.payload),
                })
        return json.dumps(content, indent=2)

    def getaddressipv4(self):
        """This function returns the list of ipv4 of the lookup answers"""
        content = []
        for elem in self.ans:
            if elem.type == TYPE_A:
                content.append(str(elem.payload.dottedQuad()))
        return content

    def getaddressipv6(self):
        """This function returns the list of ipv4 of the lookup answers"""
        content = []
        for elem in self.ans:
            if elem.type == TYPE_AAAA:
                content.append(str(elem.payload.dottedQuad()))
        return content

def dotest():
    """main loop"""
    for server in DNSSERVERS:
        for host in HOSTNAMES:
            resolv(host, server)

def result(resrev, res, ipaddr, server):
    """This function builds the Answer and prints it to stdout"""
    res = AnswersL(res[0], res[1], res[2])
    res = res.ans
    ansrev = AnswersR(resrev[0], resrev[1], resrev[2])
    ansrev = ansrev.ans
    for elemrev in ansrev:
        for elem in res:
            if elem.type == TYPE_A and str(elem.payload.dottedQuad()) == ipaddr:
                answer = Answer(elem, elemrev, server)
                print answer
                return answer

def resolv(name, server):
    """This function performs the Lookup"""
    resolver = client.createResolver(servers=[(server, 53)])
    defer = resolver.lookupAddress(name=name)
    defer.addCallback(revresolv, server)

def revresolv(url, server):
    """This function performs the Reverse Lookup for each ip of
    lookup answer"""
    answerl = AnswersL(url[0], url[1], url[2])
    ipadd = answerl.getaddressipv4()
    for i in ipadd:
        rev_name = reversenamefromipaddress(address=i)
        defer = client.lookupPointer(rev_name)
        defer.addCallback(result, url, i, server)

def reversenamefromipaddress(address):
    """This function takes as input an address reverses it and
    concatenates .in-addr.arpa"""
    return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'

DNSSERVERS = ["8.8.8.8", "208.67.222.222"]
HOSTNAMES = ["i.dailymail.co.uk", "www.polito.it"]

for num in range(0, 5):
    reactor.callLater(5*num, dotest)

reactor.callLater(30, reactor.stop)
reactor.run()
