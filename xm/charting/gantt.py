from xml.dom import minidom
from datetime import date


def total_days(d1, d2):
    if d1 > d2:
        d = d1 - d2
    else:
        d = d2 - d1

    return d.days


class GanttChartBuilder(object):

    now_factory = staticmethod(date.today)
    max_width = 600

    def __init__(self):
        self.duration_groups = []

    def generate(self):
        impl = minidom.getDOMImplementation()
        doc = impl.createDocument(None, "top", None)

        table = doc.createElement('table')
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

        # need to figure out some scaling by seeing how many items
        # and earliest/latest dates

        earliest = self.now_factory()
        latest = earliest
        for duration_group in self.duration_groups:
            for duration in duration_group:
                if duration.startdate < earliest:
                    earliest = duration.startdate
                if duration.enddate > latest:
                    latest = duration.enddate

        days = total_days(earliest, latest)
        day_size = int(self.max_width / days) # how many pixels is one day?

        th = doc.createElement('th')
        tr.appendChild(th)
        div = doc.createElement('div')
        th.appendChild(div)
        div.setAttribute('style', 'width: %ipx' % self.max_width)
        div.setAttribute('class', 'timeline')

        tbody = self.tbody = doc.createElement('tbody')
        table.appendChild(tbody)

        tr = None
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

                days = total_days(earliest, duration.startdate)
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
                bar.setAttribute('class', 'bar')
                days = total_days(duration.startdate, duration.enddate)
                pixels = int(days * day_size)
                bar.setAttribute('style', 'float: left; width: %ipx' % pixels)

                days = total_days(latest, duration.enddate)
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

        return table.toprettyxml('  ')

    def add_duration_group(self, d):
        self.duration_groups.append(d)


def generate_chart(duration_groups):
    """Generate the HTML for a gantt chart."""

    builder = GanttChartBuilder()

    for duration_group in duration_groups:
        builder.add_duration_group(duration_group)

    return builder.generate()
