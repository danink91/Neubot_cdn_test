#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#
""" Performs whois"""

import subprocess
from twisted.internet import reactor
from twisted.internet import defer
import sys, os


def whois(ip_addr):
    """ Performs traceroute"""
    outer_deferred = defer.Deferred()
    def sched_periodic_():
        """ Schedule periodic task """
        reactor.callLater(3, periodic_impl_)

    def periodic_impl_():
        """ Periodically monitor subprocess (impl) """
        exitcode = proc.poll()
        if exitcode is not None:
            final_state_()
        else:
            sched_periodic_()

    def final_state_():
        """ Final state """
        if subprocess.PIPE:
            outer_deferred.callback(str(proc.communicate()[0]))

    with open(os.devnull, 'w') as devnull:
        proc = subprocess.Popen(["whois", "-h", "v4.whois.cymru.com", ip_addr],
                                stdout=subprocess.PIPE,
                                stderr=devnull)
    sched_periodic_()
    return outer_deferred

def main():
    """ Main function """
    def do_whois():
        """perf whois"""
        deferred = whois(sys.argv[1])
        def print_result(result):
            """ Print result of whois """
            print result
            reactor.stop()

        deferred.addCallback(print_result)

    reactor.callLater(0.0, do_whois)
    reactor.run()


if __name__ == "__main__":
    main()
