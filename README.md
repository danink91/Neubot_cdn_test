# CDN test location

CODE STRUCTURE:

1.main.py: main program 2 nested for cycle(for all dns server->for all hostname):
          -resolve name
          -reverselookup (find the CNAME)
          -traceroute
          -whois
          
2.gethost.py: (e.g. gethost.py www.google.it 8.8.8.8) given an address(string) as argument resolves the name and a server dns as second arg.

3.reverse_lookup.py: (e.g. reverse_lookup.py 8.8.8.8) given an address(dot form) as argument retrieves the cname

NB: Still buggy. Tested only on linux.
TODO: catch exception for example when the server does not answer or for example answer with an IPv6
