from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import Updater, MessageHandler, Filters
import json

# import users

TOKEN = '5104628293:AAEn4SO-8-phjdqLj_M9U0E0EaeiZxHnQsU'

# with open("data/script.json", encoding='UTF8', mode="r") as f:
#     script = json.load(f)

with open("data/forks.json", encoding='UTF8', mode="r") as f:
    states = json.load(f)


# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.
def start(update, context):
    help(update, context)
    context.user_data["cur"] = "0"
    state(update, context)


def help(update, context):
    update.message.reply_text(
        'Это квест-бот по роману Ф. М. Достоевского \"Преступление и наказание\". '
        'Вы играете за Родиона Раскольникова и принимаете решения от его лица.\n'
        'Нажмите /start для прохождения квеста с начала или /next '
        'чтобы продолжить прохождение с того момента, на котором вы остановились.\n'
        'Нажмите /stop, если вам надоело играть.'
    )


def stop(update, context):
    update.message.reply_text('Очень жаль, что вам надоело.\n'
                              'Можем поиграть в следующий раз')
    context.user_data["cur"] = "0"



def state(update, context):
    cur = context.user_data["cur"]

    answer = update.message.text

    # это был ответ на квиз
    if "quiz" in states[cur]:
        # был дан правильный ответ
        if answer == states[cur]["quiz"]:
            # увеличим личный счет
            update.message.reply_text(states[cur]["reply_yes"])
        else:
            update.message.reply_text(states[cur]["reply_no"])

    if states[cur]["connection"]:
        for i in range(len(states[cur]["buttons"])):
            if states[cur]["buttons"][i] == answer:
                # переход в другое состояние
                cur = states[cur]["connection"][i]
                break

        # кнопки
        reply_keyboard = [[states[cur]["buttons"][i]] for i in range(len(states[cur]["buttons"]))]
        markup = ReplyKeyboardMarkup(reply_keyboard,
                                     one_time_keyboard=True,
                                     resize_keyboard=True)

        # печать текста и/или картинки
        if states[cur]["image"] != "":
            # картинка и текст
            context.bot.send_photo(update.message.chat.id,
                                   photo=open(states[cur]["image"], 'rb'),
                                   caption=states[cur]["text"],
                                   reply_markup=markup)
        elif states[cur]["link"] != "":
            # картинка и текст
            context.bot.send_photo(update.message.chat.id,
                                   photo=states[cur]["link"],
                                   caption=states[cur]["text"],
                                   reply_markup=markup)
        else:
            # только текст
            update.message.reply_text(states[cur]["text"],
                                      reply_markup=markup)

        # сохранение текущего состояния в контекст пользователя
        context.user_data["cur"] = cur

    else:
        update.message.reply_text(states[cur]["text"])


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
    dp.add_handler(CommandHandler("next", stop))

    # Регистрируем обработчик в диспетчере.
    text_handler = MessageHandler(Filters.text & ~Filters.command, state)
    dp.add_handler(text_handler)

    # цикл приема и обработки сообщений.
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
