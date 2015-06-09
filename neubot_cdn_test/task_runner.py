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

    def get_next_operations(self):
        """ Return some operations to run next """
        # TODO: use deque for efficiency
        retval = self._code[:4]
        self._code = self._code[4:]
        return retval

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
            reactor.callLater(1, self.execute)  # XXX
            for func, args in self.get_next_operations():
                LOG.info("Execute task: %s, %s", func, args)
                reactor.callLater(0, func, *args)
        else:
            pass #reactor.stop()  # FIXME
