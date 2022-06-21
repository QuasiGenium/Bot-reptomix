from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler
from flask import Flask
from flask_restful import Api
from data import db_session
from data.users import User
from telegram import ReplyKeyboardMarkup
from parser import parse_types, all_of_type, sort_between_prices
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kkkk'
api = Api(app, catch_all_404s=True)
TOKEN = open('token.txt', 'r').readline()


def new_user(telegram_id):
    user = User()
    user.telegram_id = telegram_id
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


def change_user(telegram_id, typ='', mi=0):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    try:
        user.type = typ if typ else user.type
        user.min_price = mi if mi else user.min_price
        db_sess.add(user)
        db_sess.commit()
        return True
    except Exception as e:
        print(e)
        return False


def start(update, context):
    chat = update.effective_chat
    if not db_session.create_session().query(User).filter(User.telegram_id == chat.id).first():
        new_user(chat.id)
    reply_keyboard = [['/filter', '/help']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Привет я бот сайта https://reptomix.com/ \n"
        "Используй команду /filter для поиска по фильтрам", reply_markup=markup)


def help_(update, context):
    update.message.reply_text(
        "Для для поиска по фильтрам используй команду /filter, "
        "после чего отвечайте на вопросы. Бот выдаст все товары по выбранным вами категориям.")


def filt(update, context):
    chat = update.effective_chat
    js = parse_types()
    a, b = js['type'].keys(), js['subtype'].keys()
    a = '\n'.join(a)
    b = '\n'.join(b)
    update.message.reply_text(
        f"Какой тип желаемого товара?\nКатегории:\n{a}\nПодкатегории:\n{b}"
        f"\n(Чтобы сбросить запрос напишите команду /stop )")
    return 1


def first_response(update, context):
    chat = update.effective_chat
    type_ = update.message.text.strip()
    js = parse_types()
    if type_.lower() in list(map(lambda x: x.lower(), js['type'].keys())) or type_.lower() in\
            list(map(lambda x: x.lower(), js['subtype'].keys())):
        change_user(chat.id, typ=type_)
        a = min(list(map(lambda x: x['price'], all_of_type(type_, js))))
        update.message.reply_text(
            f"Какая минимиальная желаемая вами стоимость? (Самый дешёвый среди выбранной категории - {a})")
        return 2
    else:
        update.message.reply_text("Неверно введены данные\n"
                                  "Какой тип желаемого товара?")
        return 1


def second_response(update, context):
    chat = update.effective_chat
    min_ = update.message.text.strip()
    try:
        change_user(chat.id, mi=int(min_))
    except Exception as e:
        print(e)
        update.message.reply_text("Неверно введены данные\n"
                                  "Какая максимальная желаемая вами стоимость?")
        return 2
    a = max(list(map(lambda x: x['price'],
                     all_of_type(db_session.create_session().query(User).filter(User.telegram_id
                                                                                ==
                                                                                chat.id).first().type, parse_types()))))
    update.message.reply_text(f"Какая максимальная желаемая вами стоимость?"
                              f" (Самый дорогой среди выбранной категории - {a})")
    return 3


def third_response(update, context):
    chat = update.effective_chat
    max_ = update.message.text.strip()
    try:
        max_ = int(max_)
    except Exception as e:
        print(e)
        update.message.reply_text("Неверно введены данные\n"
                                  "Какая максимальная желаемая вами стоимость?")
        return 3
    user = db_session.create_session().query(User).filter(User.telegram_id == chat.id).first()
    ba = sort_between_prices(all_of_type(user.type), user.min_price, max_)
    if ba:
        update.message.reply_text(ba)
    else:
        update.message.reply_text('К сожалению по вашему запросу ничего не найдено🙁.'
                                  ' Попробуйте ещё раз по команде /filter')
    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text("Запрос по фильтрам отменён.")
    return ConversationHandler.END


def main():
    db_session.global_init("db/users.db")
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('filter', filt)],
        states={

            1: [MessageHandler(Filters.text & ~Filters.command, first_response)],

            2: [MessageHandler(Filters.text & ~Filters.command, second_response)],

            3: [MessageHandler(Filters.text & ~Filters.command, third_response)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
