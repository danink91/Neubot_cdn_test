from twisted.internet import reactor
import lookup_name,reverse_lookup, traceroute, whois
import pprint

class State(object):

    # TODO: do the iterator the Pythonic way

    def __init__(self):
        self.names = []
        self.dns_servers = []
        self.results = {}
        self._code = []

    def get_next_operations(self):
        """ Return some operations to run next """
        # TODO: use deque for efficiency
        retval = self._code[:1]
        self._code = self._code[1:]
        return retval

    def no_more_operations(self):
        return len(self._code) == 0

    def add_operation(self, function, args):
        self._code.append((function, args))

def execute(state):
    """ Execture operations using reactor """
    # Note: this could also be a method of State
    if not state.no_more_operations():
        reactor.callLater(4, execute, state)
        for func, args in state.get_next_operations():
            reactor.callLater(0, func, *args)
    else:
        reactor.stop()

def op_reverse4(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    server, address, state = args
    state.results.setdefault(server, {})
    state.results[server].setdefault("ReverseA", {})
    deferred = reverse_lookup.reverse_lookup(address)
    def print_result(result):
        """ Print result of name lookup """
        state.results[server]["ReverseA"][address] = result.dict_repr()
        state.add_operation(op_traceroute, (address, state))
        state.add_operation(op_whois, (address, state))

    def print_error(err):
        """ Print err of name lookup """
        state.results[server]["ReverseA"][address] = err.value.dict_repr()

    deferred.addCallbacks(print_result, print_error)
    print server, address, state

def op_reverse6(*args):
    """ Reverse resolve A @{address} using @{server} and store the
        result in the @{destination} dictionary """
    server, address, state = args
    state.results.setdefault(server, {})
    state.results[server].setdefault("ReverseAAAA", {})
    deferred = reverse_lookup.reverse_lookup(address)
    def print_result(result):
        """ Print result of name lookup """
        state.results[server]["ReverseAAAA"][address] = result.dict_repr()
        state.add_operation(op_traceroute, (address, state))
        state.add_operation(op_whois, (address, state))

    def print_error(err):
        """ Print err of name lookup """
        state.results[server]["ReverseAAAA"][address] = err.value.dict_repr()

    deferred.addCallbacks(print_result, print_error)
    print server, address, state

def op_resolve4(*args):
    """ Resolve @{name} to A using @{server} and store the
        result in the @{destination} dictionary """
    # TODO: move here code to carefully access dictionaries?
    server, name, state = args
    if server != "<default>":
        deferred = lookup_name.lookup_name4(name, server=server)
    else:
        deferred = lookup_name.lookup_name4(name)

    def print_result(result):
        state.results[server]["A"][name] = result.dict_repr()
        for address in result.get_ipv4_addresses():
            state.add_operation(op_reverse4, (server, address, state))    

    def print_error(err):
        state.results[server]["A"][name] = err.value.dict_repr()

    deferred.addCallbacks(print_result,print_error)
    print server, name, state

def op_resolve6(*args):
    """ Resolve @{name} to AAAA using @{server} and store the
        result in the @{destination} dictionary """
    server, name, state = args 
    if server != "<default>":
        deferred = lookup_name.lookup_name6(name, server=server)
    else:
        deferred = lookup_name.lookup_name6(name)

    def print_result(result):
        state.results[server]["AAAA"][name] = result.dict_repr()
        for address in result.get_ipv6_addresses():
            state.add_operation(op_reverse6, (server, address, state))

    def print_error(err):
        state.results[server]["A"][name] = err.value.dict_repr()

    deferred.addCallbacks(print_result,print_error)

    print server, name, state

def op_traceroute(*args):
    address, state = args
    state.results.setdefault("traceroute", {})
    state.results["traceroute"].setdefault(address, {})
    deferred = traceroute.tracert(address)
    def print_result(result):
        """ Print result of name lookup """
        state.results["traceroute"][address] = result

    deferred.addCallback(print_result)

def op_whois(*args):
    address, state = args
    state.results.setdefault("whois", {})
    state.results["whois"].setdefault(address, {})
    deferred = whois.whois(address)
    def print_result(result):
        """ Print result of name lookup """
        state.results["whois"][address] = result

    deferred.addCallback(print_result)

def main():
    state = State()
   
    DNSSERVERS=["8.8.8.8","208.67.222.222","<default>"]
    HOSTNAMES=["www.facebook.com", "www.google.com"]
    for server in DNSSERVERS:
        state.dns_servers.append(server)
    for name in HOSTNAMES:
        state.names.append(name)

    # TODO: this "paragraph" could be op_initialize
    for server in state.dns_servers:
        for name in state.names:
            state.results.setdefault(server, {})
            state.results[server].setdefault("A", {})
            state.add_operation(op_resolve4, (server, name, state))
            state.results.setdefault(server, {})
            state.results[server].setdefault("AAAA", {})
            state.add_operation(op_resolve6, (server, name, state))

       
    reactor.callLater(0, execute, state)
    reactor.run()

    pprint.pprint(state.__dict__)

if __name__ == "__main__":
    main()
