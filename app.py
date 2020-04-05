import urllib.parse

import requests as req
from bs4 import BeautifulSoup

base_url = 'https://home.mephi.ru'
shedule_urls = [
    'https://home.mephi.ru/study_groups?level=0&organization_id=1&term_id=9',
    'https://home.mephi.ru/study_groups?level=1&organization_id=1&term_id=9'
    'https://home.mephi.ru/study_groups?level=2&organization_id=1&term_id=9',
    'https://home.mephi.ru/study_groups?level=3&organization_id=1&term_id=9'
    'https://home.mephi.ru/study_groups?level=4&organization_id=1&term_id=9',
]


def get_group_url(group_num):
    for url in shedule_urls:
        resp = req.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        for i in soup.find_all('a', attrs={'class': 'list-group-item'}):
            if i.text[:-1].lower() == group_num.lower():
                ret_url = urllib.parse.urljoin(base_url, i['href'])
                ret_url = urllib.parse.urljoin(ret_url, 'day')
                return ret_url
    return None


def get_all_lessons_day(url):
    schedule = {}
    resp = req.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')

    if soup.body.find('div', id='wrapper').find('div', id='page-content-wrapper').div.contents[13].text == 'Занятий не найдено':
        schedule['header'] = 'Занятий не найдено'
        schedule['lessons'] = []
        return schedule

    schedule_block = soup.body.find('div', id='wrapper').find('div', id='page-content-wrapper').div.find_all('div', attrs={'id': '', 'class': ''})[1]

    schedule['header'] = schedule_block.h3.contents[2][1:-1]
    schedule['lessons'] = []

    lessons = [i for i in schedule_block.div.children if i.name is not None]

    for les in lessons:
        lesson_dict = {}
        lesson_dict['time'] = les.find('div', attrs={'class': 'lesson-time'}).text.replace(' ', '').replace(' ', '')
        lesson_dict['name'] = les.find('div', attrs={'class': 'lesson-lessons'}).div.div.contents[6][1:-1]
        lecture = les.find('div', attrs={'class': 'lesson-lessons'}).div.div.find('span', attrs={'class': 'text-nowrap'})
        if lecture is None:
            lesson_dict['lecture'] = None
        else:
            lesson_dict['lecture'] = lecture.a.text.replace(' ', ' ')

        schedule['lessons'].append(lesson_dict)

    return schedule


if __name__ == '__main__':
    print(get_group_url('А16-211'))
    print(get_all_lessons_day('https://home.mephi.ru/study_groups/6655/day?date=2020-04-06'))
