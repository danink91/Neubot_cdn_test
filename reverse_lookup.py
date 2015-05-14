import sys
import json
from twisted.internet import task
from twisted.names import client

class Answers(object):

    def __init__(self, orig):
        self.orig = orig

    def __str__(self):
        content = []
        for elem in self.orig:
            content.append({
                "name": str(elem.name),
                "type": getattr(elem, "type"),
                "class": elem.cls,
                "ttl": elem.ttl,
                "auth": elem.auth,
                "payload":[str(elem.payload.name),elem.payload.ttl,], 
            })
        return json.dumps(content, indent=2)


def reverseNameFromIPAddress(address):
    return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'

def printResult(result):
    answers=result

    for x in answers:
	    if x: 
	        a=Answers(x)
		print a

def main(reactor, address):
    d = client.lookupPointer(name=reverseNameFromIPAddress(address=address))
    d.addCallback(printResult)
    return d

task.react(main, sys.argv[1:])

