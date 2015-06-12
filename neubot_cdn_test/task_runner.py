#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Task runner """

import logging

from twisted.internet import reactor

LOG = logging.getLogger("TaskRunner")

class TaskRunner(object):
    """ Runs tasks composing the test """
    # TODO: do the iterator the Pythonic way

    def __init__(self):
        """init class"""
        self.names = []
        self.dns_servers = []
        self.results = {}
        self._code = []
        self.counter = 0
        self.maxcounter = 10

    def get_next_operations(self):
        """ Return some operations to run next """
        # TODO: use deque for efficiency
        print "active: ", self.counter
        avail = min(self.maxcounter-self.counter, len(self._code))
        retval = self._code[:avail]
        self._code = self._code[avail:]
        self.counter = self.counter+avail

        return retval

    def decrease_counter(self):
        """decrease counter"""
        self.counter = self.counter-1

    def no_more_operations(self):
        """check if there are no more operation"""
        return len(self._code) == 0

    def add_operation(self, func, args):
        """Add an operation in _code"""
        LOG.info("Add task: %s, %s", func, args)
        self._code.append((func, args))

    def execute(self):
        """ Execute operations using reactor """
        LOG.info("=== Executing tasks ===")
        if not self.no_more_operations():
            reactor.callLater(1, self.execute)
            for func, args in self.get_next_operations():
                LOG.info("Execute task: %s, %s", func, args)
                reactor.callLater(0, func, *args)
        else:
            print "no more operation,but counter = ", self.counter
            if self.counter > 0:
                reactor.callLater(1, self.execute)
            else:
                reactor.stop()
