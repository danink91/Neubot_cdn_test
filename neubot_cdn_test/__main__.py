#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Main of the CDN test module """

from twisted.internet import reactor
import lookup_name, reverse_lookup, traceroute, whois, \
              task_runner

import getopt
import logging
import pprint
import sys
import time


def op_reverse4(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    server, address, runner = args
    runner.results[server]["ReverseA"].setdefault(address, {})
    deferred = reverse_lookup.reverse_lookup(address)
    def print_result(result):
        """ Print result of name revlookup """
        runner.results[server]["ReverseA"][address] = result.dict_repr()
        runner.decrease_counter()

    def print_error(err):
        """ Print err of name revlookup """
        runner.results[server]["ReverseA"][address] = err.value.dict_repr()
        runner.decrease_counter()

    deferred.addCallbacks(print_result, print_error)


def op_reverse6(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    server, address, runner = args
    runner.results[server]["ReverseAAAA"].setdefault(address, {})
    deferred = reverse_lookup.reverse_lookup(address)
    def print_result(result):
        """ Print result of name revlookup """
        runner.results[server]["ReverseAAAA"][address] = result.dict_repr()
        runner.decrease_counter()

    def print_error(err):
        """ Print err of name revlookup """
        runner.results[server]["ReverseAAAA"][address] = err.value.dict_repr()
        runner.decrease_counter()

    deferred.addCallbacks(print_result, print_error)


def op_resolve4(*args):
    """ Resolve @{name} to A using @{server} and store the
        result in the @{destination} dictionary """
    # TODO: move here code to carefully access dictionaries?
    server, name, runner = args
    if server != "<default>":
        deferred = lookup_name.lookup_name4(name, server=server)
    else:
        deferred = lookup_name.lookup_name4(name)

    def print_result(result):
        """ Print result of name lookup """
        if name == "whoami.akamai.net":
            runner.results["default_nameserver"] = result.dict_repr()
            runner.decrease_counter()
        elif name == "myip.opendns.com":
            runner.results["ip_client"] = result.dict_repr()
            runner.decrease_counter()
        else:
            runner.results[server]["A"].setdefault(name, {})
            runner.results[server]["A"][name] = result.dict_repr()
            runner.decrease_counter()
            for address in result.get_ipv4_addresses():
                runner.add_operation(op_reverse4, (server, address, runner))
                if not address in runner.results["traceroute"]:
                    runner.add_operation(op_traceroute, (address, runner))

    def print_error(err):
        """ Print result of name lookup """
        runner.results[server]["A"].setdefault(name, {})
        runner.results[server]["A"][name] = err.value.dict_repr()
        runner.decrease_counter()

    deferred.addCallbacks(print_result, print_error)


def op_resolve6(*args):
    """ Resolve @{name} to AAAA using @{server} and store the
        result in the @{destination} dictionary """
    server, name, runner = args
    if server != "<default>":
        deferred = lookup_name.lookup_name6(name, server=server)
    else:
        deferred = lookup_name.lookup_name6(name)

    def print_result(result):
        """ Print result of name lookup """
        runner.results[server]["AAAA"].setdefault(name, {})
        runner.results[server]["AAAA"][name] = result.dict_repr()
        runner.decrease_counter()
        for address in result.get_ipv6_addresses():
            runner.add_operation(op_reverse6, (server, address, runner))
            if not address in runner.results["traceroute"]:
                runner.add_operation(op_traceroute, (address, runner))

    def print_error(err):
        """ Print result of name lookup """
        runner.results[server]["AAAA"].setdefault(name, {})
        runner.results[server]["AAAA"][name] = err.value.dict_repr()
        runner.decrease_counter()

    deferred.addCallbacks(print_result, print_error)



def op_traceroute(*args):
    """Performs traceroute"""
    address, runner = args
    runner.results.setdefault("traceroute", {})
    runner.results["traceroute"].setdefault(address, {})
    deferred = traceroute.tracert(address)
    def print_result(result):
        """ Print result of traceroute """
        runner.results["traceroute"][address] = result
        runner.decrease_counter()
        runner.add_operation(op_whois, (address, runner))

    deferred.addCallback(print_result)


def op_whois(*args):
    """Performs whois"""
    address, runner = args
    runner.results.setdefault("whois", {})
    runner.results["whois"].setdefault(address, {})
    deferred = whois.whois(address)
    def print_result(result):
        """ Print result of whois """
        runner.results["whois"][address] = result
        runner.decrease_counter()

    deferred.addCallback(print_result)

def op_initialize(arg, workdir):
    """Init task_runner"""
    runner = arg

    with open(workdir + "/Input/hostnames") as f:
        HOSTNAMES = f.read().splitlines()

    with open(workdir + "/Input/dnsservers") as f:
	    DNSSERVERS = f.read().splitlines()

    for server in DNSSERVERS:
        runner.dns_servers.append(server)
    for name in HOSTNAMES:
        runner.names.append(name)
    runner.results.setdefault("default_nameserver", "")
    runner.results.setdefault("ip_client", "")
    runner.results.setdefault("traceroute", {})
    runner.results.setdefault("whois", {})
    for server in runner.dns_servers:
        for name in runner.names:
            runner.results.setdefault(server, {})
            runner.results[server].setdefault("A", {})
            runner.results[server].setdefault("AAAA", {})
            runner.results[server].setdefault("ReverseA", {})
            runner.results[server].setdefault("ReverseAAAA", {})


def main():
    """ Main function """
    workdir = "."
    start_time = time.time()
    print "test running..."
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "d:v")
    except getopt.error:
        sys.exit("usage: neubot_cdn_test [-d workdir] [-v]")
    if arguments:
        sys.exit("usage: neubot_cdn_test [-d workdir] [-v]")
    for name, value in options:
        if name == "-d":
            workdir = value
        elif name == "-v":
            logging.getLogger().setLevel(logging.DEBUG)

    import pickle
    runner = task_runner.TaskRunner()

    op_initialize(runner, workdir)
    
    runner.add_operation(op_resolve4, ("<default>", "whoami.akamai.net", runner))
    runner.add_operation(op_resolve4, ("208.67.222.222", "myip.opendns.com", runner))

    for server in runner.dns_servers:
        for name in runner.names:
            runner.add_operation(op_resolve4, (server, name, runner))
            runner.add_operation(op_resolve6, (server, name, runner))

    reactor.callLater(0, runner.execute)
    reactor.run()
    namef ="data"+time.strftime("%Y-%m-%d--%H:%M:%S")
    wfile = open(workdir + '/Output/'+namef+'.txt', 'w')
    pprint.pprint(runner.__dict__, wfile)
    namef =namef+".pkl"
    with open(workdir + '/Output/'+namef, 'wb') as output:
        pickle.dump(runner, output, pickle.HIGHEST_PROTOCOL)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
