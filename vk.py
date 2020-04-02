import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.answer import Answer
import json
import requests
from vk_api.upload import VkUpload

db_session.global_init("db/blogs.sqlite")
vk_session = vk_api.VkApi(
    token='f4a19a52663f6a229df74dee17a5a23e5d7f05cd4aabf1aefc00102492d7144c6b7707cb1a70de7b1b7ed')
start = "start"
fl = True
id_sp = []


def photo(user_id):
   pass


def dontknow(id):
    global fl
    vk = vk_session.get_api()
    vk.messages.send(user_id=id,
                     message='''
К такому сообщению я был не готов...🤔❄''',
                     random_id=random.randint(0, 2 ** 64))
    fl = False


def message_start(text, id):
    global start
    if start == "otvet":
        if text == "Да" or text == "да":
            vk = vk_session.get_api()
            vk.messages.send(user_id=id,
                             message='''
Для начала давай познакомимся! Как мне стоит к тебе обращаться? ☀''',
                             random_id=random.randint(0, 2 ** 64))
        elif text == "Нет" or text == "нет":
            vk = vk_session.get_api()
            vk.messages.send(user_id=id,
                             message='''
Очень жаль, приходи к нам еще!🌂''',
                             random_id=random.randint(0, 2 ** 64))
        else:
            dontknow(id)
    else:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id,
                         message='''
В каком городе ты проживаешь? ☂🏙''',
                         random_id=random.randint(0, 2 ** 64))


def registerbd(id_nach):
    global start
    session = db_session.create_session()
    vk = vk_session.get_api()
    vk.messages.send(user_id=id_nach,
                     message=f"Приятно познакомиться, {session.query(Answer).filter(Answer.id == id_nach).first().name}! "
                             f"Чуть позже я расскажу о погоде в городе"
                             f" {session.query(Answer).filter(Answer.id == id_nach).first().town} на сегодня😉🌦",
                     random_id=random.randint(0, 2 ** 64))
    photo(id_nach)


def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


keyboard = {
    "one_time": True,
    "buttons": [
        [
            get_button(label="Да", color="positive"),
            get_button(label="Нет", color="positive")
        ]
    ]
}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))


def main():
    global start
    global fl
    longpoll = VkBotLongPoll(vk_session, 193486299)
    for event in longpoll.listen():
        answer = Answer()
        if event.type == VkBotEventType.MESSAGE_NEW:
            session = db_session.create_session()
            id_nach = event.obj.message['from_id']
            if id_nach not in id_sp:
                id_sp.append(id_nach)
                answer.ans = "start"
                answer.id = event.obj.message['from_id']
                session.add(answer)
                session.commit()
                start = session.query(Answer).filter(
                    Answer.id == id_nach).first().ans
            else:
                start = session.query(Answer).filter(
                    Answer.id == id_nach).first().ans
            if start == "start":
                vk = vk_session.get_api()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='''Привет ☀

Добро пожаловать.
Я - Бот Погода.
Моя задача - помочь тебе узнать погоду на сегодня.
Начнём?🌦

Да/Нет''',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard)
                answer.ans = "otvet"
                session.commit()
            elif start == "otvet":
                fl = True
                message_start(event.obj.message['text'],
                              event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                print(answer)
                if fl:
                    answer.ans = "register"
                    session.commit()
            elif start == "register":
                message_start(event.obj.message['text'],
                              event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                answer.ans = "town"
                answer.name = event.obj.message['text']
                session.commit()
            elif start == "town":
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                answer.town = event.obj.message['text']
                session.commit()
                registerbd(event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                answer.ans = "...."
                session.commit()


if __name__ == '__main__':
    main()
