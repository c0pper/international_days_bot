import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import time, date, datetime
import pytz
import json

TELE_TOKEN = os.environ.get('TELE_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

tz_Rome = pytz.timezone('Europe/Rome')


def check_job_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    else:
        return True


def get_next_int_day() -> str:
    with open("db.json", "r", encoding="utf8") as db:
        data = json.load(db)
        giorni = sorted(data.keys(), key=lambda g: datetime.strptime(g, '%d %B'))
        
        next_int_day = None
        for g in giorni:
            datetime_object = datetime.strptime(g, '%d %B')
            day, month = datetime_object.day, datetime_object.month
            year_month_day_obj = date(date.today().year, month, day)
            if year_month_day_obj > date.today():
                next_int_day = year_month_day_obj
                break
        
        # If no date is found, wrap around to the start of the next year
        if next_int_day is None:
            first_day = giorni[0]
            datetime_object = datetime.strptime(first_day, '%d %B')
            day, month = datetime_object.day, datetime_object.month
            next_int_day = date(date.today().year + 1, month, day)
        
    return next_int_day.strftime("%d/%m/%Y")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    target_dates = []
    with open("db.json", "r", encoding="utf8") as db:
        data = json.load(db)
        giorni = data.keys()
        print(giorni)
        for g in giorni:
            datetime_object = datetime.strptime(g, '%d %B')
            day, month = datetime_object.day, datetime_object.month
            target_date = date(date.today().year, month, day)
            target_dates.append(target_date)

    print("today", date.today(), "\n")
    for d in target_dates:
        if date.today() == d:
            datetime_object = datetime.fromisoformat(str(date.today()))
            if os.name == "nt":
                data_formattata = datetime_object.strftime('%#d %B')
            else:
                data_formattata = datetime_object.strftime('%-d %B')
            print("data formattata", data_formattata)
            # print(data[data_formattata])


    chat_id = update.effective_message.chat_id
    next_int_day = get_next_int_day()
    if check_job_exists(str(chat_id), context):
        text = f"Prossima giornata mondiale: {next_int_day}"
        await update.effective_message.reply_text(text)
    else:
        context.job_queue.run_daily(get_global_day, time(hour=7, tzinfo=tz_Rome), days=(0, 1, 2, 3, 4, 5, 6),
                                    name=str(chat_id), chat_id=chat_id)

        text = f"Bot avviato. Prossima giornata mondiale: {next_int_day}"
        await update.effective_message.reply_text(text)


async def get_global_day(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    target_dates = []
    with open("db.json", "r", encoding="utf8") as db:
        data = json.load(db)
        giorni = data.keys()
        print(giorni)
        for g in giorni:
            datetime_object = datetime.strptime(g, '%d %B')
            day, month = datetime_object.day, datetime_object.month
            target_date = date(date.today().year, month, day)
            target_dates.append(target_date)

    for d in target_dates:
        if date.today() == d:
            datetime_object = datetime.fromisoformat(str(date.today()))
            if os.name == "nt":
                data_formattata = datetime_object.strftime('%#d %B')
            else:
                data_formattata = datetime_object.strftime('%-d %B')
            print(data_formattata)

            text = f"Felice {' e '.join(data[data_formattata])}  :)"
            await context.bot.send_message(job.chat_id, text=text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELE_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()