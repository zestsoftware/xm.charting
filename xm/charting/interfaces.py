from zope import interface
from zope import schema


class IDurationGroup(interface.Interface):
    name = schema.TextLine(title=u'Name')

    def __iter__():
        """Return iterations."""

    def __len__():
        """Return number of durations"""


class IDuration(interface.Interface):
    name = schema.TextLine(title=u'Name')
    startdate = schema.Date(title=u'Start Date')
    enddate = schema.Date(title=u'End Date')
