from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import smtplib
import re
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

TOKEN = os.getenv("TG_ACCESS_TOKEN")
EMAIL, MESSAGE = range(2)

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это бот для уведомлений. Введите email, на который нужно отправить письмо:")
    return EMAIL

# Обработчик ввода email
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if validate_email(email):
        context.user_data['email'] = email
        await update.message.reply_text("Введите текст сообщения:")
        return MESSAGE
    else:
        await update.message.reply_text("Некорректный email. Попробуйте снова.")
        return EMAIL

# Обработчик ввода сообщения
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    recipient_email = context.user_data['email']
    sender_email = "mishasender@yandex.ru"
    sender_password = "bdtpdnsvzwiozjuk"

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Уведомление"
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        with smtplib.SMTP('smtp.yandex.ru', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)  # Отправка MIME-сообщения
        await update.message.reply_text("Сообщение успешно отправлено! :)")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке: {e}")
    return ConversationHandler.END

# Обработчик отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def main():
    print('Программа запущена')
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
    print('Программа завершила свою работу')

if __name__ == '__main__':
    main()
