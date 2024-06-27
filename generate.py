import datetime
import json
import pathlib
import random
import shutil
import sys
from typing import List

import holidays
from bs4 import BeautifulSoup
from rich import print
from rich.console import Console

console = Console()
cn_holidays = holidays.CountryHoliday('CN', years=datetime.datetime.now().year)

hitokoto: List[str] = json.loads(
    pathlib.Path('./hitokoto.json').read_text('utf-8'))
template_file = pathlib.Path('./template.svg')
template = BeautifulSoup(template_file.read_text('utf-8'), 'xml')

begin_day = datetime.date.today()
summer_holiday = datetime.date(2024, 7, 20)

WEEKDAY_TO_STR = [
    '星期一',
    '星期二',
    '星期三',
    '星期四',
    '星期五',
    '星期六',
    '星期日',
]

shutil.rmtree('./generated', ignore_errors=True)
pathlib.Path('./generated').mkdir(exist_ok=True, parents=True)


def get_hitokoto(max_length: int):
    while True:
        s = random.choice(hitokoto)

        if s['hitokoto'].__len__() > max_length:
            continue
        else:
            return s['hitokoto']

# 获取“宜”


def get_good_things_to_do(date: datetime.date) -> str:
    things = []

    # 月末固定事件
    if date.day >= 20:
        things.append('学习')

    weekend_random_events = ['打篮球', '跑步', '和同学打游戏', '睡觉']
    workday_random_events = ['刷题', '学点别的', '网购练习册']
    if date.weekday() == 5 or date.weekday() == 6:
        things.append(random.choice(weekend_random_events))
    else:
        things.append(random.choice(workday_random_events))

    return '、'.join(things)

# 获取“忌”


def get_bad_things_to_do(date: datetime.date) -> str:
    things = []

    # 月末固定事件
    if date.day >= 20:
        things.append('啥都不干')

    things.extend(list(set(random.choices(
        ['吃喝玩乐', '浪费时间', '网购练习册以外的物品', '买新东西'],
        k=random.randint(1, 4)
    ))))

    return '、'.join(things)


today = begin_day
while today <= summer_holiday:
    # 固定随机种子
    # random.seed(today.year * today.month * today.day)
    print(today)

    calendar_today_file = pathlib.Path(
        './generated').joinpath(today.__str__() + '.svg')
    calendar_today = template

    calendar_today.select_one(
        '#_图层_1 > text:nth-child(7) > tspan.cls-9 > tspan').string = get_hitokoto(15)  # 一言

    # 日期
    calendar_today.select_one(
        '#_图层_1 > text:nth-child(2) > tspan.cls-13 > tspan').string = f'{today.month}月'
    calendar_today.select_one(
        '#_图层_1 > text:nth-child(2) > tspan.cls-11 > tspan').string = f'{today.day:0>2d}'
    calendar_today.select_one(
        '#_图层_1 > text.cls-6 > tspan').string = WEEKDAY_TO_STR[today.weekday()]

    # 距离 XX 的日期
    holidays_from_now = sorted(list(cn_holidays.items()), key=lambda x: x[0])
    holidays_from_now = [x[0] for x in holidays_from_now if x[0] >= today]

    calendar_today.select_one(
        '#_图层_1 > text.cls-2 > tspan:nth-child(3)').string = f'{(summer_holiday - today).days:0>3d}天'  # 到暑假
    calendar_today.select_one(
        '#_图层_1 > text.cls-4 > tspan.cls-12').string = f'{(holidays_from_now[0] - today).days}天'  # 到节假日

    # 宜、忌
    calendar_today.select_one(
        '#_图层_1 > text.cls-3 > tspan:nth-child(1)').string = f'宜：{get_bad_things_to_do(today)}'
    calendar_today.select_one(
        '#_图层_1 > text.cls-3 > tspan:nth-child(2)').string = f'忌：{get_good_things_to_do(today)}'

    calendar_today_file.write_text(calendar_today.__str__(), 'utf-8')
    today += datetime.timedelta(days=1)

# 生成html
pathlib.Path('./generated/generated.html').write_text("<body>{}</body>".format(
    '\n'.join([
        f'<img src="{x.absolute()}" style="height: 100vh;">'
        for x in pathlib.Path('./generated').iterdir()
        if x.suffix == '.svg'
    ])
), 'utf-8')
