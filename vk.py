import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from data import db_session
from data.answer import Answer
import json
from vk_api.upload import VkUpload
import requests
import password as settings

token = settings.MYSQL_TOKEN
apikey = settings.MYSQL_APIKEY
db_session.global_init("db/blogs.sqlite")
vk_session = vk_api.VkApi(
    token=token)
start = "start"
fl = True
fl_1 = False
townfl = True
git_z = 0
id_sp = []
ADDRES = 0
ADDRES2 = 0
pos1 = 0
pos2 = 0


class Weather:
    def __init__(self):
        pass

    def find_w(self, find, id):
        global git_z
        try:
            a = find["weather"][0]["description"]
            b = round(float(find["main"]["temp"]) - 273)  # темп
            b_1 = round(float(find["main"]["feels_like"]) - 273)
            c = find["main"]["humidity"]  # влажность
            d = round(float(
                find["main"][
                    "pressure"]) * 0.00750063755419211 * 100)  # давление
            return a, b, b_1, c, d
        except KeyError:
            if git_z != 2:
                vk = vk_session.get_api()
                vk.messages.send(user_id=id,
                                 message='''Погода в вашем городе не найдена, 
попробуйте изменить данные☂''',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard_1)
            session = db_session.create_session()
            answer = session.query(Answer).filter(
                Answer.id == id).first()
            answer.ans = "change"
            session.commit()
            return None

    def weather(self, id):
        session = db_session.create_session()
        answer = session.query(Answer).filter(
            Answer.id == id).first()
        if townfl:
            try:
                find = requests.get(
                    f'http://api.openweathermap.org/'
                    f'data/2.5/weather?q={answer.town}'
                    f'&appid=e1c74a6cdc0612198a312535515c63b3&lang=RU').json()
                return self.find_w(find, id)
            except ConnectionResetError:
                vk = vk_session.get_api()
                vk.messages.send(user_id=id,
                                 message='''Сервер временно недоступен, 
попробуйте повторить попытку позже''',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard_1)
                session = db_session.create_session()
                answer = session.query(Answer).filter(
                    Answer.id == id).first()
                answer.ans = "weather"
                session.commit()
                return 1
        else:
            try:
                find = requests.get(
                    f'http://api.openweathermap.org/'
                    f'data/2.5/weather?q={answer.another_town}'
                    f'&appid=e1c74a6cdc0612198a312535515c63b3&lang=RU').json()
                return self.find_w(find, id)
            except ConnectionResetError:
                vk = vk_session.get_api()
                vk.messages.send(user_id=id,
                                 message='''Сервер временно недоступен, 
попробуйте повторить попытку позже''',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard_1)
                session = db_session.create_session()
                answer = session.query(Answer).filter(
                    Answer.id == id).first()
                answer.ans = "weather"
                session.commit()
                return 1


def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


class Photo:
    def __init__(self):
        pass

    def send_photo(self, vk, id, owner_id, photo_id, access_key):
        w = Weather()
        global townfl
        session = db_session.create_session()
        answer = session.query(Answer).filter(
            Answer.id == id).first()
        weather = w.weather(id)
        if weather is not None and weather != 1:
            a, b, b_1, c, d = w.weather(id)
            attachment = f'photo{owner_id}_{photo_id}_{access_key}'
            if townfl:
                town = answer.town
            else:
                town = answer.another_town
            vk.messages.send(
                random_id=random.randint(0, 2 ** 64),
                user_id=id,
                message=f'Погода в настоящее время в городе {town}🌦:\n'
                        f'Сейчас {a}\n'
                        f'Температура🌡: {b}℃, ощущается {b_1}℃\n'
                        f'Влажность воздуха: {c}%\n'
                        f'Давление: {d}мм.рт.ст.\n',
                attachment=attachment,
                keyboard=keyboard_2
            )
        elif weather == 1:
            vk.messages.send(
                random_id=random.randint(0, 2 ** 64),
                user_id=id,
                keyboard=keyboard_2
            )
        else:
            if git_z == 2:
                vk.messages.send(
                    random_id=random.randint(0, 2 ** 64),
                    user_id=id,
                    message=f'Погода в данном городе не найдена,'
                            f' попробуйте выбрать другой город🌡',
                    keyboard=keyboard_1
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
    elif git_z == 1:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id,
                         message='''
К такому сообщению я был не готов...🤔❄''',
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard_1)
    else:
        vk = vk_session.get_api()
        vk.messages.send(user_id=id,
                         message='''
К такому сообщению я был не готов...🤔❄''',
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard_2)


def message_start(text, id):
    global start
    global fl_1
    if start == "otvet":
        if text == "Да" or text == "да":
            fl_2 = True
            vk = vk_session.get_api()
            vk.messages.send(user_id=id,
                             message='''
Для начала давай познакомимся! Как мне стоит к тебе обращаться? ☀''',
                             random_id=random.randint(0, 2 ** 64))
            fl_1 = True
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
            if answer.ans != "change":
                answer.ans = "weather"
                session.commit()
        else:
            vk = vk_session.get_api()
            vk.messages.send(user_id=id_nach,
                             message='''Ваш город не найден, 
попробуйте изменить данные☂''',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=keyboard_1)
            session = db_session.create_session()
            answer = session.query(Answer).filter(
                Answer.id == id_nach).first()
            answer.ans = "change"
            session.commit()


def map(text, id_nach):
    global apikey
    coordinates(
        f"http://geocode-maps.yandex.ru/1.x/?apikey={apikey}"
        f"&geocode={text}&format=json",
        id_nach)


def sizze(id_nach):  # выдаем погоду
    global ADDRES
    global ADDRES2
    global townfl
    s = Photo()
    sp = f"https://static-maps.yandex.ru/1.x/?ll={ADDRES},{ADDRES2}" \
         f"&spn=0.09,0.09&l=map&pt={pos1},{pos2},pm2rdl"
    response = requests.get(sp)
    map_file = "map.jpg"
    with open(map_file, "wb") as file:
        file.write(response.content)
    vk = vk_session.get_api()
    upload = VkUpload(vk)
    s.send_photo(vk, id_nach, *upload_photo(upload, map_file))
    townfl = True


class Register:
    def __init__(self):
        pass

    def registerbd(self, id_nach):
        global start
        global git_z
        if git_z == 0:
            session = db_session.create_session()
            vk = vk_session.get_api()
            vk.messages.send(user_id=id_nach,
                             message=f"Приятно познакомиться, "
                                     f"{session.query(Answer).filter(Answer.id == id_nach).first().name}! "
                                     f"Ищу информацию о погоде в городе"
                                     f" {session.query(Answer).filter(Answer.id == id_nach).first().town} "
                                     f"на сегодня...😉🌦",
                             random_id=random.randint(0, 2 ** 64))
        else:
            if townfl:
                session = db_session.create_session()
                vk = vk_session.get_api()
                vk.messages.send(user_id=id_nach,
                                 message=f"Ищу информацию о погоде в городе"
                                         f" {session.query(Answer).filter(Answer.id == id_nach).first().town} "
                                         f"на сегодня...😉🌦",
                                 random_id=random.randint(0, 2 ** 64))
            else:
                session = db_session.create_session()
                vk = vk_session.get_api()
                vk.messages.send(user_id=id_nach,
                                 message=f"Ищу информацию о погоде в городе"
                                         f" {session.query(Answer).filter(Answer.id == id_nach).first().another_town} "
                                         f"на сегодня...😉🌦",
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
keyboard_2 = {
    "one_time": True,
    "buttons": [
        [
            get_button(label="Другой город", color="positive"),
            get_button(label="Погода в моем городе", color="positive")
        ]
    ]
}

keyboard_2 = json.dumps(keyboard_2, ensure_ascii=False).encode('utf-8')
keyboard_2 = str(keyboard_2.decode('utf-8'))


def main():
    global start
    global fl
    global git_z
    global fl_1
    global townfl
    r = Register()
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
            elif event.obj.message['text'] == "Начать":
                answer.ans = "start"
                answer.id = event.obj.message['from_id']
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
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                answer.ans = "otvet"
                session.commit()
            elif start == "otvet":
                fl = True
                fl_1 = False
                message_start(event.obj.message['text'],
                              event.obj.message['from_id'])
                answer = session.query(Answer).filter(
                    Answer.id == id_nach).first()
                if fl:
                    if fl_1:
                        answer.ans = "register"
                        session.commit()
                    else:
                        answer.ans = "start"
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
                if git_z != 2:
                    answer.town = event.obj.message['text']
                    session.commit()
                    r.registerbd(event.obj.message['from_id'])
                    map(session.query(Answer).filter(
                        Answer.id == id_nach).first().town,
                        event.obj.message['from_id'])
                else:
                    answer.another_town = event.obj.message['text']
                    session.commit()
                    r.registerbd(event.obj.message['from_id'])
                    if townfl:
                        map(session.query(Answer).filter(
                            Answer.id == id_nach).first().town,
                            event.obj.message['from_id'])
                    else:
                        map(session.query(Answer).filter(
                            Answer.id == id_nach).first().another_town,
                            event.obj.message['from_id'])

            elif start == "change":
                if event.obj.message['text'] == "Изменить город":
                    if git_z == 0 or git_z == 1:
                        git_z = 1
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
                        townfl = False
                        vk = vk_session.get_api()
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message='''
В каком городе ты бы хотел узнать погоду? ☂🏙''',
                                         random_id=random.randint(0, 2 ** 64))
                        answer = session.query(Answer).filter(
                            Answer.id == id_nach).first()
                        answer.ans = "town"
                        session.commit()
                else:
                    dontknow(event.obj.message['from_id'])
            elif start == "weather":
                git_z = 2
                if event.obj.message['text'] == "Другой город":
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message='''
В каком городе ты бы хотел узнать погоду? ☂🏙''',
                                     random_id=random.randint(0, 2 ** 64))
                    answer = session.query(Answer).filter(
                        Answer.id == id_nach).first()
                    answer.ans = "town"
                    session.commit()
                    townfl = False
                elif event.obj.message['text'] == "Погода в моем городе":
                    r.registerbd(event.obj.message['from_id'])
                    map(session.query(Answer).filter(
                        Answer.id == id_nach).first().town,
                        event.obj.message['from_id'])
                else:
                    dontknow(event.obj.message['from_id'])


if __name__ == '__main__':
    main()
