"""
Основные обработчики событий чат-бота.
Чтение квест-данных в формате json.
"""
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters
import json

import db_session
from users import User

# import users
TOKEN = ''

# with open("data/script.json", encoding='UTF8', mode="r") as f:
#     script = json.load(f)

with open("data/forks.json", encoding='UTF8', mode="r") as f:
    states = json.load(f)


# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
def start(update, context):

    auth(update, context)

    context.user_data["cur"] = "0"
    state(update, context)


# создание записи для пользователя в базе данных
def auth(update, context):
    user = User()
    user.name = update.message.chat.id
    # print(update.message.from_user)
    user.amount = 0

    # создать запись для пользователя
    if db_sess.query(User).filter(User.name == update.message.chat.id).count() == 0:
        db_sess.add(user)
    db_sess.commit()


# информация о квест-боте
def help(update, context):
    update.message.reply_text(states["0"]["text"] +
        '\n\nНажмите /start для прохождения квеста с начала или /next '
        'чтобы продолжить прохождение с того момента, на котором вы остановились.'
    )


# функция для остановки квест-бота
def stop(update, context):
    update.message.reply_text('Очень жаль, что вам надоело.\n'
                              'Можем поиграть в следующий раз')
    context.user_data["cur"] = "0"


# основной обработчик квест-бота -
# обрабатывает ответ пользователя на основе текущего состояния,
# прочитанного из файла состояний на json
def state(update, context):
    # текущее состояние из контекста пользователя
    cur = context.user_data["cur"]

    answer = update.message.text

    # это был ответ на квиз
    if "quiz" in states[cur]:
        # работа с картой, увеличить масштаб
        if answer == "<Увеличить масштаб>":
            # кнопки
            if states[cur]["buttons"]:
                reply_keyboard = [[states[cur]["buttons"][i]] for i in range(len(states[cur]["buttons"]) - 1)]
                markup = ReplyKeyboardMarkup(reply_keyboard,
                                             one_time_keyboard=False,
                                             resize_keyboard=True)
                # картинка и текст
                context.bot.send_photo(update.message.chat.id,
                                       photo=states[cur]["link"] + '&z=17',
                                       caption=states[cur]["text"],
                                       reply_markup=markup)
                return

        # был дан правильный ответ
        if answer == states[cur]["quiz"]:
            # работа с базой
            user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
            if answer == "Потратить":
                # обнулить счет
                user.amount = 0
            else:
                # увеличим личный счет пользователя
                user.amount += 100
            db_sess.commit()

            update.message.reply_text(states[cur]["reply_yes"])
        else:
            update.message.reply_text(states[cur]["reply_no"])

    # определяем состояние для перехода
    if states[cur]["connection"] and len(states[cur]["buttons"]) > 0 or cur == "finish":

        for i in range(len(states[cur]["buttons"])):
            if states[cur]["buttons"][i] == answer:
                # переход в другое состояние
                cur = states[cur]["connection"][i]
                break

        text = states[cur]["text"]

        # обработка последнего состояния
        if cur == "finish":

            if states[cur]["animation"]:
                context.bot.send_animation(update.message.chat.id,
                                       animation=open(states[cur]["animation"], 'rb'),
                                       caption=text,
                                       reply_markup=ReplyKeyboardRemove())
            else:
                update.message.reply_text(text,
                                          reply_markup=ReplyKeyboardRemove())
            return

        # обработка состояния для работы с базой (счет пользователя)
        if cur == "amount":
            user = db_sess.query(User).filter(User.name == update.message.chat.id).first()
            print(user.amount)
            if user.amount == 0:
                text = "У вас на счету 0 руб. Попробуйте правильно ответить на вопросы в следующий раз"
                reply_keyboard = [["дальше"]]
                markup = ReplyKeyboardMarkup(reply_keyboard,
                                             one_time_keyboard=False,
                                             resize_keyboard=True)
                update.message.reply_text(text,
                                          reply_markup=markup)
                context.user_data["cur"] = "finish"
                return
            else:
                text = states[cur]["text"] + str(user.amount) + ' руб.'

        # кнопки
        markup = ReplyKeyboardRemove()
        if states[cur]["buttons"]:
            reply_keyboard = [[states[cur]["buttons"][i]] for i in range(len(states[cur]["buttons"]))]
            markup = ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=False,
                                         resize_keyboard=True)

        # печать текста и/или картинки
        if states[cur]["image"] != "":
            # картинка и текст
            context.bot.send_photo(update.message.chat.id,
                                   photo=open(states[cur]["image"], 'rb'),
                                   caption=text,
                                   reply_markup=markup)
        elif states[cur]["link"] != "":
            # картинка-линк и текст
            context.bot.send_photo(update.message.chat.id,
                                   photo=states[cur]["link"] + '&z=13',
                                   caption=text,
                                   reply_markup=markup)
        else:
            # только текст
            update.message.reply_text(text,
                                      reply_markup=markup)

        # сохранение текущего состояния в контекст пользователя
        context.user_data["cur"] = cur

    else:
        update.message.reply_text(states[cur]["text"],
                                  reply_markup=ReplyKeyboardRemove())


def main():
    # объект updater
    """
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://ip:port',  # Адрес прокси сервера
        # Опционально, если требуется аутентификация:
        # 'urllib3_proxy_kwargs': {
        #     'assert_hostname': 'False',
        #     'cert_reqs': 'CERT_NONE'
        #     'username': 'user',
        #     'password': 'password'
        # }
    }

    updater = Updater(TOKEN, use_context=True,
                      request_kwargs=REQUEST_KWARGS)
    """
    updater = Updater(TOKEN, use_context=True)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Первым параметром конструктора CommandHandler я
    # вляется название команды.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("next", state))
    dp.add_handler(CommandHandler("stop", stop))

    # Регистрируем обработчик в диспетчере.
    text_handler = MessageHandler(Filters.text & ~Filters.command, state)
    dp.add_handler(text_handler)

    # цикл приема и обработки сообщений.
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    db_session.global_init("db/quest.db")
    db_sess = db_session.create_session()
    main()
