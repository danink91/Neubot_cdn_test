from twisted.internet import reactor
import sys
import json
from twisted.names import client
from twisted.internet import task,defer
import socket
import twisted.names.dns
import time
import datetime

class Answer(object):

    def __init__(self, L,RL,dns):
        ts = time.time()
        self.timestamp=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.dns=dns        
        self.L = L
        self.RL=RL
        
    def __str__(self):
        content = []
        content.append({
                         "timestamp": str(self.timestamp),
                         "dns": str(self.dns),
                         
                         "name": str(self.L.name),
                         "type": getattr(self.L, "type"),
                         "class": self.L.cls,
                         "ttl": self.L.ttl,
                         "auth": self.L.auth,
                         "payload": {"address" : str(self.L.payload.dottedQuad()),"ttl": self.L.payload.ttl, },
		          
	                     "nameR": str(self.RL.name),
	                     "typeR": getattr(self.RL, "type"),
	                     "classR": self.RL.cls,
	                     "ttlR": self.RL.ttl,
	                     "authR": self.RL.auth,
	                     "payloadR":{"nameR" : str(self.RL.payload.name),"ttlR": self.RL.payload.ttl, }
		        })
        return json.dumps(content, indent=2)

class AnswersR(object):

    def __init__(self, ans,auth,additional):
        self.ans = ans
        self.auth=auth
        self.additional=additional
    def __str__(self):
        content = []
        for elem in self.ans:
	    if elem.type==12:
	        content.append({
	             "name": str(elem.name),
	             "type": getattr(elem, "type"),
	             "class": elem.cls,
	             "ttl": elem.ttl,
	             "auth": elem.auth,
	             "payload":{"name" : str(elem.payload.name),"ttl": elem.payload.ttl, }
		})
        return json.dumps(content, indent=2)

class AnswersL(object):

    def __init__(self, ans,auth,additional):
        self.ans = ans
        self.auth=auth
        self.additional=additional

    def __str__(self):
        content = []
        for elem in self.ans:
            if elem.type==1:
                content.append({
	                     "name": str(elem.name),
	                     "type": getattr(elem, "type"),
	                     "class": elem.cls,
	                     "ttl": elem.ttl,
	                     "auth": elem.auth,
	                     "payload": str(elem.payload),
		        })
        return json.dumps(content, indent=2)
    
    def __repr__(self):
        return 'MyClass #%d' % (self.id,)

    def getAddressIPv4(self):
        content=[]
        for elem in self.ans:
            if elem.type==1:
                content.append( str(elem.payload.dottedQuad()))
        return content
    def getAddressIPv6(self,orig):
        content=[]
        for elem in self.ans:
            if elem.type==1:
	            content.append( str(socket.inet_ntop(AF_INET6, elem.payload.address)))
        return content
    
    
        
        
class Getter(object):

    def __init__(self):
        self._sequence = 0
        self._results = []
        self._errors = []

    def Result(self,resrev, res,ip,dns):
        
        res=AnswersL(res[0],res[1],res[2])
        res=res.ans
        ansrev=AnswersR(resrev[0],resrev[1],resrev[2])
        ansrev=ansrev.ans
        for elemrev in ansrev:
            for elem in res: 
                
                if elem.type==1 and str(elem.payload.dottedQuad())==ip:
                    x=Answer(elem,elemrev,dns)
                    return x
     
    
    def Resolv(self, name,dns):
        resolver = client.createResolver(servers=[(dns, 53)])
        d = resolver.lookupAddress(name=name)
        d.addCallback(self.revResolv,dns)
        
        

    def revResolv(self, url,dns):
        
        x=AnswersL(url[0],url[1],url[2])
        IP=x.getAddressIPv4()
        for i in IP:
            rev_name=reverseNameFromIPAddress(address=i)
            d = client.lookupPointer(rev_name)
            d.addCallback(self.Result,url,i,dns)
            d.addCallbacks(self._on_success, self._on_error)
            d.addCallback(self._on_finish)
            self._sequence += 1
        
        

    def _on_finish(self, *narg):
        self._sequence -= 1
        if not self._sequence:
            reactor.stop()

    _on_success = lambda self, res: self._results.append(res) 
    _on_error = lambda self, err: self._errors.append(err)

    def run(self):
        reactor.run()
        return self._results, self._errors


def reverseNameFromIPAddress(address):
    return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'




dnsservers=["8.8.8.8","208.67.222.222"]
hostnames=["i.dailymail.co.uk", "www.polito.it","www.facebook.com"]



g = Getter()
for dns in dnsservers:
            for host in hostnames:
                g.Resolv(host,dns)


results,errors=g.run()
for x in results:
        print x

