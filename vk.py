import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.answer import Answer

db_session.global_init("db/blogs.sqlite")
vk_session = vk_api.VkApi(
    token='f4a19a52663f6a229df74dee17a5a23e5d7f05cd4aabf1aefc00102492d7144c6b7707cb1a70de7b1b7ed')
start = "start"
answer = Answer()
id_sp = []


def dontknow(id):
    vk = vk_session.get_api()
    vk.messages.send(user_id=id,
                     message='''
К такому сообщению я был не готов...🤔❄''',
                     random_id=random.randint(0, 2 ** 64))


def message_start(text, id):
    global start
    global answer
    if start == "otvet":
        if text == "Да":
            vk = vk_session.get_api()
            vk.messages.send(user_id=id,
                             message='''
Для начала давай познакомимся! Как мне стоит к тебе обращаться? ☀''',
                             random_id=random.randint(0, 2 ** 64))
        elif text == "Нет":
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



def registerbd(text, id):
    global start
    vk = vk_session.get_api()
    vk.messages.send(user_id=id,
                     message=f"Приятно познакомиться, {answer.name}! "
                             f"Чуть позже я расскажу о погоде в городе"
                             f" {answer.town} на сегодня😉🌦",
                     random_id=random.randint(0, 2 ** 64))


def main():
    global start
    global answer
    longpoll = VkBotLongPoll(vk_session, 193486299)
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            session = db_session.create_session()
            id_nach = event.obj.message['from_id']
            if id_nach not in id_sp:
                id_sp.append(id_nach)
                answer.ans = "start"
                answer.id = event.obj.message['from_id']
                session.add(answer)
                session.commit()
                start = answer.ans
            else:
                start = answer.ans
            if start == "start":
                vk = vk_session.get_api()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='''Привет ☀

Добро пожаловать.
Я - Бот Погода.
Моя задача - помочь тебе узнать погоду на сегодня.
Начнём?🌦

Да/Нет''',
                                 random_id=random.randint(0, 2 ** 64))
                answer = session.query(Answer).filter(Answer.id == id_nach).first()
                answer.ans = "otvet"
                session.commit()
            elif start == "otvet":
                message_start(event.obj.message['text'],
                              event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
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
                registerbd(event.obj.message['text'], event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                answer.ans = "...."
                session.commit()


if __name__ == '__main__':
    main()
