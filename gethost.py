
import sys

from twisted.names import client, error
from twisted.internet.task import react
from twisted.python import usage



class Options(usage.Options):
    synopsis = 'Usage: gethostbyname.py HOSTNAME SERVERDNS'

    def parseArgs(self, hostname, dns):
        self['hostname'] = hostname
	self['dns'] = dns


def printResult(address, hostname):
    """
    Print the IP address or an error message if an IP address was not
    found.
    """
    if address:
        sys.stdout.write(address + '\n')
    else:
        sys.stderr.write(
            'ERROR: No IP addresses found for name %r\n' % (hostname,))



def printError(failure, hostname):
    """
    Print a friendly error message if the hostname could not be
    resolved.
    """
    failure.trap(error.DNSNameError)
    sys.stderr.write('ERROR: hostname not found %r\n' % (hostname,))



def main(reactor, *argv):
    options = Options()
    try:
        options.parseOptions(argv)
    except usage.UsageError as errortext:
        sys.stderr.write(str(options) + '\n')
        sys.stderr.write('ERROR: %s\n' % (errortext,))
        raise SystemExit(1)

    hostname = options['hostname']
    dns=options['dns']
    resolver = client.createResolver(servers=[(dns, 53)])
    d = resolver.getHostByName(hostname)
    d.addCallback(printResult, hostname)
    d.addErrback(printError, hostname)
    return d



if __name__ == '__main__':
    react(main, sys.argv[1:])

