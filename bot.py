import datetime
import urllib.parse

import telebot
from telebot import apihelper

import app
import config

apihelper.proxy = {
    'http': config.http_proxy,
    'https': config.https_proxy
}

user_urls = {}
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.send_message(message.chat.id, 'Привет. Напиши номер своей группы.')


@bot.message_handler(commands=['schedule'])
def handle_start_help(message):
    url = user_urls.get(message.chat.id)
    if url == None:
        bot.send_message(message.chat.id, 'Напиши номер своей группы.')
    else:
        add_msg = message.text.replace('/schedule ', '')

        if add_msg.lower() == 'завтра':
            date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

            params = {'date': date}
            url_parts = list(urllib.parse.urlparse(url))
            query = dict(urllib.parse.parse_qsl(url_parts[4]))
            query.update(params)
            url_parts[4] = urllib.parse.urlencode(query)
            url = urllib.parse.urlunparse(url_parts)

        schedule = app.get_all_lessons_day(url)
        msg = ''
        msg += f'*{schedule["header"]}*'
        msg += '\n\n'
        for les in schedule['lessons']:
            msg += f'*{les["time"]}* {les["name"]} '
            if les["lecture"] is not None:
                msg += f'_{les["lecture"]}_'
            msg += '\n'
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(regexp="^[МБСАИмбсаи]\d{2}-[\w\d]\d{2}$")
def get_group_num(message):
    bot.send_message(message.chat.id, f'Отлично, сейчас найдем твою группу {message.text}')
    url = app.get_group_url(message.text)
    if url is None:
        bot.send_message(message.chat.id, f'К сожалению твой номер группы не найден {message.text}')
    else:
        user_urls[message.chat.id] = url
        bot.send_message(message.chat.id, f'Отлично. Запроси расписание /schedule')


@bot.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, 'Пока такое не обрабатываю. Введите номер группы или посмотртите расписание '
                                      '/schedule')


if __name__ == '__main__':
    bot.polling(none_stop=True)
