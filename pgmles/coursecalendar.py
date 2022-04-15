import random
from calendar import Calendar as Month
from datetime import datetime

lesson_names = [ 'Python', 'C', 'C++', 'Java', 'JavaScript', None, None, None, None, None, None, None, None ]

lessons = [ None ] * 31


class Calendar:
    weekdays = enumerate(['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo'])
    nextlesson = ''
    rows = []

    def __init__(self):
        today = datetime.today()

        m = Month()

        for day in m.itermonthdays(today.year, today.month):
            if day != 0:
                lessons[day] = random.choice(lesson_names)

        for day, lesson in enumerate(lessons[today.day:]):
            if lesson is not None:
                self.nextlesson = lesson
                break

        for days in m.monthdayscalendar(today.year, today.month):
            self.rows.append([(i, d, lessons[d]) for i, d in enumerate(days)])

#        print(self.rows)
