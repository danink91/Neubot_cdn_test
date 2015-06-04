import lookup_name, reverse_lookup, traceroute
from twisted.names import dns
from twisted.internet import reactor
import sys
import socket

def main():

    deferred = lookup_name.lookup_name("8.8.8.8", sys.argv[1])
    def print_result(result):
        for i in result.result[0]:
            if i.type == dns.A:
                print socket.inet_ntop(socket.AF_INET, i.payload.address)
                ipv4 = socket.inet_ntop(socket.AF_INET, i.payload.address)
                d=reverse_lookup.reverse_lookup(ipv4)
                def print_result(result):
                    print result
                    deferred = traceroute.tracert(ipv4)
                    def print_result(result):
                        """ Print result of name lookup """
                        print result

                    deferred.addCallback(print_result)

                def print_error(err):
                    print err

                d.addCallbacks(print_result,print_error)
            elif i.type == dns.AAAA:
                ipv6 = socket.inet_ntop(socket.AF_INET6, i.payload.address)   
                print socket.inet_ntop(socket.AF_INET6, i.payload.address)            
                d=reverse_lookup.reverse_lookup(ipv6)
                def print_result(result):
                    print result
                           

    def print_error(err):
        print err.value




    deferred.addCallbacks(print_result,print_error)

    reactor.run()
if __name__ == "__main__":
    main()


