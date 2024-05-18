from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from datetime import datetime

TOKEN = ''

SELECT_ACTION, ADD_WORK_HOURS, GET_HOURS_BY_DAY, GET_HOURS_BY_MONTH, GET_HOURS_BY_PERIOD = range(5)

work_hours = {}


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Привет! Я бот для учета рабочих часов.\n'
        'Выберите действие:',
        reply_markup=ReplyKeyboardMarkup([['Добавить часы работы'],
                                          ['Получить часы работы по дню'],
                                          ['Получить часы работы по месяцу'],
                                          ['Получить часы работы за период']],
                                         one_time_keyboard=True)
    )
    return SELECT_ACTION


def add_work_hours(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Введите день, месяц, год и количество проработанных часов через пробел."
    )
    return ADD_WORK_HOURS


def process_add_work_hours(update: Update, context: CallbackContext) -> int:
    try:
        data = update.message.text.split()
        day, month, year, hours = map(int, data)
        date = datetime(year, month, day)
        date_str = date.strftime("%Y-%m-%d")

        if date_str not in work_hours:
            work_hours[date_str] = hours
        else:
            work_hours[date_str] += hours

        update.message.reply_text("Часы работы успешно добавлены.")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

    return SELECT_ACTION


def get_hours_by_day(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Введите день, месяц и год через пробел."
    )
    return GET_HOURS_BY_DAY


def process_get_hours_by_day(update: Update, context: CallbackContext) -> int:
    try:
        data = update.message.text.split()
        day, month, year = map(int, data)
        date_str = f"{year}-{month:02d}-{day:02d}"
        hours = work_hours.get(date_str, 0)

        update.message.reply_text(f"Часы работы в указанный день: {hours}")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

    return SELECT_ACTION


def get_hours_by_month(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Введите месяц и год через пробел."
    )
    return GET_HOURS_BY_MONTH


def process_get_hours_by_month(update: Update, context: CallbackContext) -> int:
    try:
        data = update.message.text.split()
        month, year = map(int, data)
        total_hours = 0
        for date_str, hours in work_hours.items():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date.month == month and date.year == year:
                total_hours += hours

        update.message.reply_text(f"Часы работы в указанный месяц: {total_hours}")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

    return SELECT_ACTION


def get_hours_by_period(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Введите начальную и конечную дату в формате день месяц год через пробел, разделяя даты запятой."
    )
    return GET_HOURS_BY_PERIOD


def process_get_hours_by_period(update: Update, context: CallbackContext) -> int:
    try:
        data = update.message.text.split(',')
        start_date_str, end_date_str = data
        start_day, start_month, start_year = map(int, start_date_str.split())
        end_day, end_month, end_year = map(int, end_date_str.split())

        start_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)

        total_hours = 0
        for date_str, hours in work_hours.items():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= date <= end_date:
                total_hours += hours

        update.message.reply_text(f"Часы работы за указанный период: {total_hours}")
    except Exception as e:
        update.message.reply_text(f"Ошибка: {e}")

    return SELECT_ACTION


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Действие отменено.', reply_markup=ReplyKeyboardRemove()
    )
    return SELECT_ACTION


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_ACTION: [
                MessageHandler(Filters.regex('^Добавить часы работы$'), add_work_hours),
                MessageHandler(Filters.regex('^Получить часы работы по дню$'), get_hours_by_day),
                MessageHandler(Filters.regex('^Получить часы работы по месяцу$'), get_hours_by_month),
                MessageHandler(Filters.regex('^Получить часы работы за период$'), get_hours_by_period),
                MessageHandler(Filters.text & ~(Filters.regex('^Добавить часы работы$') | Filters.regex(
                    '^Получить часы работы по дню$') | Filters.regex(
                    '^Получить часы работы по месяцу$') | Filters.regex(
                    '^Получить часы работы за период$')), cancel),
            ],
            ADD_WORK_HOURS: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), process_add_work_hours)],
            GET_HOURS_BY_DAY: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')),
                                              process_get_hours_by_day)],
            GET_HOURS_BY_MONTH: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')),
                                                process_get_hours_by_month)],
            GET_HOURS_BY_PERIOD: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')),
                                                 process_get_hours_by_period)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
