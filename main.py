import datetime
import decimal
import httpimport
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from typing import Union
from enum import Enum, auto
from rich import print
from rich.table import Table

with httpimport.github_repo('vacanza', 'python-holidays', ref='master'):
    import holidays

DateLike = Union[datetime.datetime]
class HolidayType(Enum):
    HolidayInLaw = auto()
    Weekend = auto()

now = datetime.datetime.now()
IS_STUDENT = True  # 开启该设置，表示将寒暑假设为假期

winter_vacation_begin_time = datetime.datetime(now.year, 1, 15)
summer_vacation_begin_time = datetime.datetime(now.year, 7, 14)

# 自动更新当前时间
def update_now():
    global now
    now = datetime.datetime.now()

# 到某一天的天数（高精度）
def to(day: DateLike) -> decimal.Decimal:
    global now
    nowstamp = decimal.Decimal(now.timestamp())
    targetstamp = decimal.Decimal(day.timestamp())
    offsetstamp = targetstamp - nowstamp
    return offsetstamp / 86400

def main():
    cn_holidays = holidays.CountryHoliday('CN')
    law_holiday = []
    weekend_holiday = []
    
    tmp = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    while tmp <= datetime.datetime(now.year, 12, 31):
        tmp += datetime.timedelta(days=1)
        
        # 法定节假日
        if tmp in cn_holidays:
            law_holiday.append(tmp)
        
        # 周末
        if tmp.weekday() == 5 or tmp.weekday() == 6:
            weekend_holiday.append(tmp)
    del tmp
    
    law_holiday.sort()
    weekend_holiday.sort()
    
    # 最近的周末
    to_nearest_weekend = to(weekend_holiday[0])
    
    # 最近的法定节假日
    to_nearest_law_vacation = to(law_holiday[0])
    
    # 到寒假
    to_winter_vacation = to(winter_vacation_begin_time)
    
    # 到暑假
    to_summer_vacation = to(summer_vacation_begin_time)
    
    # 打印
    table = Table('类型', '距离')
    table.add_row('[green]最近的周末', f'{to_nearest_weekend:.5f} 天')
    table.add_row('[yellow]最近的法定节假日', f'{to_nearest_law_vacation:.5f} 天')
    table.add_row('[blue]到寒假', f'{to_winter_vacation:.5f} 天')
    table.add_row('[red]到暑假', f'{to_summer_vacation:.5f} 天')
    
    print(table)

if '__main__' == __name__:
    scheduler = BlockingScheduler()
    scheduler.add_job(update_now, 'interval', seconds=0.1)
    scheduler.add_job(main, 'interval', seconds=1)
    
    scheduler.start()