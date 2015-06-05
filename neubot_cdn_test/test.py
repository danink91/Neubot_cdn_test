import lookup_name, reverse_lookup, traceroute
from twisted.names import dns
from twisted.internet import reactor
import sys
import socket
import json

class Results(object):
    """ Wrapper for Result """

    def __init__(self, names, dnsservers):
        self.input = names
        self.dns_servers= dnsservers
        self.output = []

    def __str__(self):
        content = []
        content.append({"input" : self.input,
                        "dns_servers" : self.dns_servers,
                        "output" : {
                            "default_nameserver" : self.output[0],
                            self.dns_servers[0] : { },##FIXME
                            self.dns_servers[1] : { },
                            "traceroute" : {},
                            "whois" : {},
                        },
                    })
        return json.dumps(content, indent=2)
        
    def add_default_dns(self, result):
        self.output.append(result[0])

    
DNSSERVERS=["8.8.8.8","208.67.222.222"]
HOSTNAMES=["i.dailymail.co.uk", "www.polito.it","www.facebook.com"]
def main():
    x=Results(HOSTNAMES, DNSSERVERS)
    deferred = lookup_name.lookup_name4("whoami.akamai.net", server="8.8.8.8")
    def print_result(result):
        x.add_default_dns(result.get_ipv4_addresses())
        print x
        

    def print_error(err):
        print err.value

    deferred.addCallbacks(print_result,print_error)
    reactor.run()
if __name__ == "__main__":
    main()


