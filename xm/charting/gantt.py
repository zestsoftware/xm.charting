import calendar
from xml.dom import minidom
from datetime import date
from datetime import timedelta

ONEWEEK = timedelta(days=7)
ONEDAY = timedelta(days=1)
ONEMONTH = timedelta(days=28)
TWOMONTHS = timedelta(days=ONEMONTH.days*2)
THREEMONTHS = timedelta(days=ONEMONTH.days*3)


def total_days(d1, d2):
    if d1 > d2:
        d = d1 - d2
    else:
        d = d2 - d1

    return d.days


class HTMLGanttRenderer(object):

    now_factory = staticmethod(date.today)
    max_width = 700

    def __init__(self, duration_groups):
        self.duration_groups = duration_groups

    def render(self):
        impl = minidom.getDOMImplementation()
        self.doc = doc = impl.createDocument(None, "top", None)
        duration_groups = self.duration_groups

        self.table = table = doc.createElement('table')
        table.setAttribute('class', 'gantt-chart')
        table.setAttribute('cellspacing', '0')
        table.setAttribute('cellpadding', '0')

        thead = doc.createElement('thead')
        table.appendChild(thead)
        tr = doc.createElement('tr')
        tr.setAttribute('class', 'time-row')
        thead.appendChild(tr)

        th = doc.createElement('th')
        tr.appendChild(th)
        th.appendChild(doc.createTextNode(' '))

        earliest = self.now_factory()
        currentstartweek = earliest
        # find the monday of "this" week
        while calendar.weekday(currentstartweek.year, currentstartweek.month,
                               currentstartweek.day) != 0:
            currentstartweek -= ONEDAY

        # need to figure out some scaling by seeing how many items
        # and earliest/latest dates
        latest = earliest
        for duration_group in duration_groups:
            for duration in duration_group:
                if duration.startdate is not None and \
                       duration.startdate < earliest:
                    earliest = duration.startdate
                if duration.enddate is not None and duration.enddate > latest:
                    latest = duration.enddate

        # make sure the first day is the first monday before (or on) the
        # earliest date
        while calendar.weekday(earliest.year, earliest.month,
                               earliest.day) != 0:
            earliest -= ONEDAY
        # make sure the last day is the last sunday after (or on) the latest
        # date
        while calendar.weekday(latest.year, latest.month, latest.day) != 6:
            latest += ONEDAY

        if earliest < (currentstartweek - ONEMONTH):
            earliest = currentstartweek - ONEMONTH

        if latest > (currentstartweek + THREEMONTHS):
            latest = currentstartweek + THREEMONTHS

        self.earliest = earliest
        self.latest = latest

        days = total_days(earliest, latest)
        day_size = int(self.max_width / days) # how many pixels is one day?
        self.day_size = day_size

        th = doc.createElement('th')
        tr.appendChild(th)
        div = doc.createElement('div')
        th.appendChild(div)
        div.setAttribute('style', 'height: 2em; position: relative; ' + \
                                  'width: %ipx' % self.max_width)
        div.setAttribute('class', 'timeline')

        somedate = earliest
        weekwidth = day_size * 7
        totalwidth = 0
        while somedate < latest:
            weekdiv = doc.createElement('div')
            div.appendChild(weekdiv)
            weekdiv.setAttribute('class', 'week')
            w = weekwidth
            if totalwidth + w > self.max_width:
                w = self.max_width - totalwidth
            weekdiv.setAttribute('style',
                                 'overflow: hidden; height: 2em; ' + \
                                 'position: absolute; bottom: 0; ' + \
                                 'left: %ipx; width: %ipx'
                                 % (totalwidth, (w-5)))
            weekdiv.appendChild(doc.createTextNode(str(somedate)))
            somedate += ONEWEEK
            totalwidth += w

        self.tbody = tbody = self.tbody = doc.createElement('tbody')
        table.appendChild(tbody)

        self._generate_duration_rows()

        return table.toprettyxml('  ')

    def _generate_duration_rows(self):
        tr = None
        tbody = self.tbody
        doc = self.doc
        earliest = self.earliest
        latest = self.latest
        day_size = self.day_size

        for duration_group in self.duration_groups:
            tr = doc.createElement('tr')
            tbody.appendChild(tr)

            td = doc.createElement('td')
            tr.appendChild(td)
            td.appendChild(doc.createTextNode(duration_group.name))
            td.setAttribute('class', 'left-col')

            td = doc.createElement('td')
            tr.appendChild(td)
            td.setAttribute('class', 'duration-group-wrapper')

            div = doc.createElement('div')
            td.appendChild(div)
            div.setAttribute('style', 'width: %ipx' % self.max_width)
            div.setAttribute('class', 'duration-group')

            for duration in duration_group:
                durdiv = doc.createElement('div')
                div.appendChild(durdiv)
                durdiv.setAttribute('class', 'duration')

                start = duration.startdate
                if start is None or start < earliest:
                    start = earliest
                end = duration.enddate
                if end is None or end > latest:
                    end = latest

                days = total_days(earliest, start)
                pixels = int(days * day_size)
                if days > 0:
                    leading = doc.createElement('div')
                    durdiv.appendChild(leading)
                    leading.appendChild(doc.createTextNode('leading'))
                    leading.setAttribute('class', 'leading')
                    leading.setAttribute('style',
                                         'float: left; width: %ipx' % pixels)

                bar = doc.createElement('div')
                durdiv.appendChild(bar)
                bar.appendChild(doc.createTextNode(duration.name))
                c = 'bar'
                if duration.enddate is None or duration.startdate is None:
                    c += ' invalid-date'
                bar.setAttribute('class', c)
                days = total_days(start, end)
                pixels = int(days * day_size)
                bar.setAttribute('style', 'float: left; width: %ipx' % pixels)

                days = total_days(latest, end)
                pixels = int(days * day_size)
                if days > 0:
                    following = doc.createElement('div')
                    durdiv.appendChild(following)
                    following.appendChild(doc.createTextNode('following'))
                    following.setAttribute('class', 'following')
                    following.setAttribute('style',
                                           'float: left; width: %ipx' % pixels)

                br = doc.createElement('br')
                durdiv.appendChild(br)
                br.setAttribute('style', 'clear: both')

        # get last table row
        if tr is not None:
            tr.setAttribute('class', 'last')


class GanttChartBuilder(object):

    renderers = {'html': HTMLGanttRenderer}

    def __init__(self):
        self.duration_groups = []

    def generate(self, render_type):
        builder = self.renderers[render_type](self.duration_groups)
        return builder.render()

    def add_duration_group(self, d):
        self.duration_groups.append(d)


def generate_chart(duration_groups, render_type='html'):
    """Generate the HTML for a gantt chart."""

    builder = GanttChartBuilder()

    for duration_group in duration_groups:
        builder.add_duration_group(duration_group)

    return builder.generate(render_type)
