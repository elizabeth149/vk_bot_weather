import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.answer import Answer
import json
from vk_api.upload import VkUpload
import requests

db_session.global_init("db/blogs.sqlite")
vk_session = vk_api.VkApi(
    token='')
start = "start"
fl = True
git_z = 0
id_sp = []
ADDRES = 0
ADDRES2 = 0
pos1 = 0
pos2 = 0


def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_photo(vk, id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=random.randint(0, 2 ** 64),
        user_id=id,
        attachment=attachment
    )


def dontknow(id):
    global fl
    global git_z
    if git_z == 0:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id,
                         message='''
К такому сообщению я был не готов...🤔❄''',
                         random_id=random.randint(0, 2 ** 64))
        fl = False
    else:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id,
                         message='''
К такому сообщению я был не готов...🤔❄''',
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard_1)


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


def coordinates(geocoder_request, id_nach):
    global ADDRES
    global ADDRES2
    global pos1
    global pos2
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if len(json_response["response"]["GeoObjectCollection"][
                   "featureMember"]) != 0:
            toponym = \
                json_response["response"]["GeoObjectCollection"][
                    "featureMember"][
                    0][
                    "GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            ADDRES = float(toponym_coodrinates.split()[0])
            ADDRES2 = float(toponym_coodrinates.split()[1])
            pos1 = float(toponym_coodrinates.split()[0])
            pos2 = float(toponym_coodrinates.split()[1])
            sizze(id_nach)
            session = db_session.create_session()
            answer = session.query(Answer).filter(
                Answer.id == id_nach).first()
            answer.ans = "weather"
            session.commit()
        else:
            vk = vk_session.get_api()
            vk.messages.send(user_id=id_nach,
                             message='''Вашего города я не знаю☂🤷‍♀''',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=keyboard_1)
            session = db_session.create_session()
            answer = session.query(Answer).filter(
                Answer.id == id_nach).first()
            answer.ans = "change"
            session.commit()
    else:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id_nach,
                         message='''Вашего города я не знаю☂🤷‍♀''',
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard_1)
        session = db_session.create_session()
        answer = session.query(Answer).filter(
            Answer.id == id_nach).first()
        answer.ans = "change"
        session.commit()


def map(text, id_nach):
    coordinates(
        f"http://geocode-maps.yandex.ru/1.x/?apikey=APIKEY&geocode={text}&format=json",
        id_nach)


def sizze(id_nach):
    global ADDRES
    global ADDRES2
    sp = f"https://static-maps.yandex.ru/1.x/?ll={ADDRES},{ADDRES2}&spn=0.09,0.09&l=map&pt={pos1},{pos2},pm2rdl"
    response = requests.get(sp)
    map_file = "map.jpg"
    with open(map_file, "wb") as file:
        file.write(response.content)
    vk = vk_session.get_api()
    upload = VkUpload(vk)
    send_photo(vk, id_nach, *upload_photo(upload, map_file))


def registerbd(id_nach):
    global start
    global git_z
    if git_z == 0:
        session = db_session.create_session()
        vk = vk_session.get_api()
        vk.messages.send(user_id=id_nach,
                         message=f"Приятно познакомиться, {session.query(Answer).filter(Answer.id == id_nach).first().name}! "
                                 f"Ищу информацию о погоде в городе"
                                 f" {session.query(Answer).filter(Answer.id == id_nach).first().town} на сегодня...😉🌦",
                         random_id=random.randint(0, 2 ** 64))
    else:
        session = db_session.create_session()
        vk = vk_session.get_api()
        vk.messages.send(user_id=id_nach,
                         message=f"Ищу информацию о погоде в городе"
                                 f" {session.query(Answer).filter(Answer.id == id_nach).first().town} на сегодня...😉🌦",
                         random_id=random.randint(0, 2 ** 64))


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

keyboard_1 = {
    "one_time": True,
    "buttons": [
        [
            get_button(label="Изменить город", color="positive")
        ]
    ]
}

keyboard_1 = json.dumps(keyboard_1, ensure_ascii=False).encode('utf-8')
keyboard_1 = str(keyboard_1.decode('utf-8'))


def main():
    global start
    global fl
    global git_z
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
                map(session.query(Answer).filter(
                    Answer.id == id_nach).first().town,
                    event.obj.message['from_id'])
            elif start == "change":
                git_z = 1
                if event.obj.message['text'] == "Изменить город":
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='''
В каком городе ты проживаешь? ☂🏙''',
                                     random_id=random.randint(0, 2 ** 64))
                    answer = session.query(Answer).filter(
                        Answer.id == id_nach).first()
                    answer.ans = "town"
                    session.commit()
                else:
                    dontknow(event.obj.message['from_id'])


if __name__ == '__main__':
    main()
