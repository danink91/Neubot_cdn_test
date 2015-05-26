#!/usr/bin/python
"""This script is a test for CDN-test"""
from twisted.internet import reactor
import json
from twisted.names import client
import time
import datetime

TYPEPTR = 12
TYPEA = 1
TYPEAAAA = 28
class Answer(object):
    """This class is the complete answer"""
    def __init__(self, L, RL, dns):
        times = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(times).strftime('%Y-%m-%d %H:%M:%S')
        self.dns = dns
        self.lookup = L
        self.rlookup = RL
    def __str__(self):
        content = []
        content.append({
            "timestamp": str(self.timestamp),
            "dns": str(self.dns),

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
            if elem.type == TYPEPTR:
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
            if elem.type == TYPEA or elem.type == TYPEAAAA:
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
            if elem.type == TYPEA:
                content.append(str(elem.payload.dottedQuad()))
        return content

    def getaddressipv6(self):
        """This function returns the list of ipv4 of the lookup answers"""
        content = []
        for elem in self.ans:
            if elem.type == TYPEAAAA:
                content.append(str(elem.payload.dottedQuad()))
        return content

class Functions(object):
    """This class contains all function used for the test"""
    def __init__(self):
        self._results = []

    def dotest(self):
        """main loop"""
        for dns in DNSSERVERS:
            for host in HOSTNAMES:
                self.resolv(host, dns)

    def result(self, resrev, res, ipaddr, dns):
        """This function given build the Answer and prints it to stdout"""
        res = AnswersL(res[0], res[1], res[2])
        res = res.ans
        ansrev = AnswersR(resrev[0], resrev[1], resrev[2])
        ansrev = ansrev.ans
        for elemrev in ansrev:
            for elem in res:
                if elem.type == TYPEA and str(elem.payload.dottedQuad()) == ipaddr:
                    answer = Answer(elem, elemrev, dns)
                    print answer
                    return answer

    def resolv(self, name, dns):
        """This function performs the Lookup"""
        resolver = client.createResolver(servers=[(dns, 53)])
        defer = resolver.lookupAddress(name=name)
        defer.addCallback(self.revresolv, dns)
    def revresolv(self, url, dns):
        """This function performs the Reverse Lookup for each ip of
        lookup answer"""
        answerl = AnswersL(url[0], url[1], url[2])
        ipadd = answerl.getaddressipv4()
        for i in ipadd:
            rev_name = reversenamefromipaddress(address=i)
            defer = client.lookupPointer(rev_name)
            defer.addCallback(self.result, url, i, dns)
    def run(self):
        """reactor run"""
        reactor.run()

def reversenamefromipaddress(address):
    """This function takes as input an address reverses it and
    concatenates .in-addr.arpa"""
    return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'

DNSSERVERS = ["8.8.8.8", "208.67.222.222"]
HOSTNAMES = ["i.dailymail.co.uk", "www.polito.it"]
test = Functions()
for num in range(0, 5):
    reactor.callLater(5*num, test.dotest)

reactor.callLater(30, reactor.stop)
test.run()
