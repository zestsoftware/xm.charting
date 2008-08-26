from xm.charting import interfaces
from zope import interface


class DurationGroup(object):
    interface.implements(interfaces.IDurationGroup)

    def __init__(self, name):
        self.name = name
        self._iterations = []

    def __iter__(self):
        return iter(self._iterations)

    def __len__(self):
        return len(self._iterations)


class Duration(object):
    interface.implements(interfaces.IDuration)

    def __init__(self, name, start, end):
        self.name = name
        self.startdate = start
        self.enddate = end
