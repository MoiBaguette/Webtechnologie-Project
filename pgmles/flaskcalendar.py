import random
from calendar import Calendar as Month
from datetime import datetime

lessons = ['Python van Cr', 'C van Hg', 'Python van Kr',
           None, None, None, None, None, None]


class Calendar:
    weekdays = list(enumerate(['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']))
    rows = []

    def __init__(self):
        today = datetime.today()

        m = Month()
        for days in m.monthdayscalendar(today.year, today.month):
            self.rows.append([(i, d, (random.choice(lessons) if d != 0 and i != 6 else None))
                              for i, d in enumerate(days)])

        print(self.rows)
