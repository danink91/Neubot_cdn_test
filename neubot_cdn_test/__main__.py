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
import time, json


def op_reverse4(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    address, runner = args
    def do_revlookup():
        """do the rev lookup"""
        deferred = reverse_lookup.reverse_lookup(address)
        def print_result(result):
            """ Print result of name revlookup """
            runner.results["reverse"].setdefault(address, {})
            runner.results["reverse"][address] = result.dict_repr()
            runner.decrease_counter()

        def print_error(err):
            """ Print err of name revlookup """
            runner.results["reverse"].setdefault(address, {})
            runner.results["reverse"][address] = err.value.dict_repr()
            runner.decrease_counter()

        deferred.addCallbacks(print_result, print_error)

    reactor.callLater(0.0, do_revlookup)


def op_reverse6(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    address, runner = args
    def do_revlookup():
        """do the rev lookup"""
        deferred = reverse_lookup.reverse_lookup(address)
        def print_result(result):
            """ Print result of name revlookup """
            runner.results["reverse"].setdefault(address, {})
            runner.results["reverse"][address] = result.dict_repr()
            runner.decrease_counter()

        def print_error(err):
            """ Print err of name revlookup """
            runner.results["reverse"].setdefault(address, {})
            runner.results["reverse"][address] = err.value.dict_repr()
            runner.decrease_counter()

        deferred.addCallbacks(print_result, print_error)

    reactor.callLater(0.0, do_revlookup)


def op_resolve4(*args):
    """ Resolve @{name} to A using @{server} and store the
        result in the @{destination} dictionary """
    # TODO: move here code to carefully access dictionaries?
    server, name, runner = args

    def do_lookup():
        """Perform the lookup"""
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
                    if not address in runner.results["reverse"]:
                        runner.add_operation(op_reverse4, (address, runner))
                    if not address in runner.results["traceroute"]:
                        runner.add_operation(op_traceroute, (address, runner))
                    if not address in runner.results["whois"]:
                        runner.add_operation(op_whois, (address, runner))

        def print_error(err):
            """ Print result of name lookup """
            runner.results[server]["A"].setdefault(name, {})
            runner.results[server]["A"][name] = err.value.dict_repr()
            runner.decrease_counter()

        deferred.addCallbacks(print_result, print_error)

    reactor.callLater(0.0, do_lookup)


def op_resolve6(*args):
    """ Resolve @{name} to AAAA using @{server} and store the
        result in the @{destination} dictionary """
    server, name, runner = args
    def do_lookup():
        """Perform the lookup"""
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
                if not address in runner.results["reverse"]:
                    runner.add_operation(op_reverse6, (address, runner))
                if not address in runner.results["traceroute"]:
                    runner.add_operation(op_traceroute, (address, runner))
                if not address in runner.results["whois"]:
                    runner.add_operation(op_whois, (address, runner))

        def print_error(err):
            """ Print result of name lookup """
            runner.results[server]["AAAA"].setdefault(name, {})
            runner.results[server]["AAAA"][name] = err.value.dict_repr()
            runner.decrease_counter()

        deferred.addCallbacks(print_result, print_error)

    reactor.callLater(0.0, do_lookup)


def op_traceroute(*args):
    """Performs traceroute"""
    address, runner = args
    def do_trace():
        """perf traceroute"""
        deferred = traceroute.tracert(address)
        def print_result(result):
            """ Print result of traceroute """
            runner.results["traceroute"].setdefault(address, {})
            runner.results["traceroute"][address] = result
            runner.decrease_counter()

        deferred.addCallback(print_result)

    reactor.callLater(0.0, do_trace)


def op_whois(*args):
    """Performs whois"""
    address, runner = args
    def do_whois():
        """perf whois"""
        deferred = whois.whois(address)
        def print_result(result):
            """ Print result of whois """
            runner.results["whois"].setdefault(address, {})
            runner.results["whois"][address] = result
            runner.decrease_counter()

        deferred.addCallback(print_result)

    reactor.callLater(0.0, do_whois)


def op_initialize(arg, workdir):
    """Init task_runner"""
    runner = arg

    with open(workdir + "/Input/hostnames") as fhost:
        hostnames = fhost.read().splitlines()

    with open(workdir + "/Input/dnsservers") as fserver:
        dnsservers = fserver.read().splitlines()

    for server in dnsservers:
        runner.dns_servers.append(server)
    for name in hostnames:
        runner.names.append(name)
    runner.results.setdefault("default_nameserver", "")
    runner.results.setdefault("ip_client", "")
    runner.results.setdefault("traceroute", {})
    runner.results.setdefault("reverse", {})
    runner.results.setdefault("whois", {})
    for server in runner.dns_servers:
        for name in runner.names:
            runner.results.setdefault(server, {})
            runner.results[server].setdefault("A", {})
            runner.results[server].setdefault("AAAA", {})


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
    namef = "data"+time.strftime("%Y-%m-%d--%H:%M:%S")
    #pprint
    pfile = open(workdir + '/Output/'+namef+'.txt', 'w')
    pprint.pprint(runner.__dict__, pfile)
    pfile.close()
    #json
    wfile = open(workdir + '/Output/'+namef+'.dat', 'w')
    json.dump(runner.results, wfile, indent=2)
    wfile.close()
    #pkl
    ppfile = open(workdir + '/Output/'+namef+'.pkl', 'wb')
    pickle.dump(runner, ppfile, pickle.HIGHEST_PROTOCOL)
    ppfile.close()
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
