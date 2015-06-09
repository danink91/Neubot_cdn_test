#
# This file is part of Neubot CDN test.
#
# Neubot CDN test is free software. See AUTHORS and LICENSE for
# more information on the copying conditions.
#

""" Task runner """

from twisted.internet import reactor

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

    def add_operation(self, function, args):
        """Add an operation in _code"""
        self._code.append((function, args))

    def execute(self):
        """ Execture operations using reactor """
        # Note: this could also be a method of TaskRunner
        if not self.no_more_operations():
            reactor.callLater(4, self.execute)
            for func, args in self.get_next_operations():
                reactor.callLater(0, func, *args)
        else:
            reactor.stop()
