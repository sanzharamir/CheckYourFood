import os
import logging
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from google.cloud import vision, translate_v2 as translate
from google.cloud.vision import types

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

PORT = int(os.environ.get('PORT', 5000))
bot_token = os.environ['TOKEN']
app_name = os.environ['MY_APP']

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()
target = "en"

upd = Updater(token=bot_token, use_context=True)
dp = upd.dispatcher 


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, to start, set the language you wish me to translate to by sending /choose + 'code of the langauge'.\n" + "To see all langauges with codes use /list.\n" + "Then just send a me a picture of contents.\n" + "For example, to choose English, type '/choose en'")

def list_languages(update, context):
    results = translate_client.get_languages()
    langauges = ""
    for language in results:
        langauges += u'{name} ({language})\n'.format(**language)
    context.bot.send_message(chat_id=update.effective_chat.id, text=langauges)

def choose(update, context):
    global target
    target = context.args[0]
    languages = translate_client.get_languages()
    target_language = ""
    for language in languages:
        if language["language"] == target:
            target_language = language["name"]
    if target_language == "":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Language has not been found. Try again!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have chosen " + target_language + ".\n" + "Now, send me a picture.")

def images(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I have recieved an image. Please, wait a second.")

    if update.message.photo:
        photo = update.message.photo[-1].file_id
    elif update.message.document:
        photo = update.message.document.file_id
    else:
        return

    file = context.bot.get_file(photo)
    f = BytesIO(file.download_as_bytearray())

    response = vision_client.text_detection(image=f)
    description = response.text_annotations[0].description
    result = translate_client.translate(description, target_language=target)

    context.bot.send_message(chat_id=update.effective_chat.id, text=u'Original Text:\n {}\n'.format(result['input'])) 
    context.bot.send_message(chat_id=update.effective_chat.id, text=u'Translated Text:\n {}\n'.format(result['translatedText'])) 

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

start_handler = CommandHandler('start', start)
choose_handler = CommandHandler('choose', choose)
list_handler = CommandHandler('list', list_languages)
image_handler = MessageHandler(Filters.photo | Filters.document.image, images)
unknown_handler = MessageHandler(Filters.command, unknown)

dp.add_handler(start_handler)
dp.add_handler(choose_handler)
dp.add_handler(list_handler)
dp.add_handler(image_handler)
dp.add_handler(unknown_handler)

upd.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=bot_token)
upd.bot.setWebhook("MY_APP" + bot_token)
upd.idle()
import os
import logging
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from google.cloud import vision, translate_v2 as translate
from google.cloud.vision import types

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

PORT = int(os.environ.get('PORT', 5000))
bot_token = os.environ['TOKEN']

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()
target = "en"

upd = Updater(token=bot_token, use_context=True)
dp = upd.dispatcher 


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, to start, set the language you wish me to translate to by sending /choose + 'code of the langauge'.\n" + "To see all langauges with codes use /list.\n" + "Then just send a me a picture of contents.\n" + "For example, to choose English, type '/choose en'")

def list_languages(update, context):
    results = translate_client.get_languages()
    langauges = ""
    for language in results:
        langauges += u'{name} ({language})\n'.format(**language)
    context.bot.send_message(chat_id=update.effective_chat.id, text=langauges)

def choose(update, context):
    global target
    target = context.args[0]
    languages = translate_client.get_languages()
    target_language = ""
    for language in languages:
        if language["language"] == target:
            target_language = language["name"]
    if target_language == "":
        context.bot.send_message(chat_id=update.effective_chat.id, text="Language has not been found. Try again!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have chosen " + target_language + ".\n" + "Now, send me a picture.")

def images(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I have recieved an image. Please, wait a second.")

    if update.message.photo:
        photo = update.message.photo[-1].file_id
    elif update.message.document:
        photo = update.message.document.file_id
    else:
        return

    file = context.bot.get_file(photo)
    f = BytesIO(file.download_as_bytearray())

    response = vision_client.text_detection(image=f)
    description = response.text_annotations[0].description
    result = translate_client.translate(description, target_language=target)

    context.bot.send_message(chat_id=update.effective_chat.id, text=u'Original Text:\n {}\n'.format(result['input'])) 
    context.bot.send_message(chat_id=update.effective_chat.id, text=u'Translated Text:\n {}\n'.format(result['translatedText'])) 

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

start_handler = CommandHandler('start', start)
choose_handler = CommandHandler('choose', choose)
list_handler = CommandHandler('list', list_languages)
image_handler = MessageHandler(Filters.photo | Filters.document.image, images)
unknown_handler = MessageHandler(Filters.command, unknown)

dp.add_handler(start_handler)
dp.add_handler(choose_handler)
dp.add_handler(list_handler)
dp.add_handler(image_handler)
dp.add_handler(unknown_handler)

upd.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=bot_token)
upd.bot.setWebhook(app_name + bot_token)
upd.idle()
