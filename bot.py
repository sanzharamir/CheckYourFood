import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging
from io import BytesIO
from google.cloud import vision, translate_v2 as translate
from google.cloud.vision import types

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot_token = os.environ['TOKEN']
target = "en"

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()

upd = Updater(token=bot_token, use_context=True)
dp = upd.dispatcher 

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    print(context, context.args)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def choose(update, context):
	global target
	target = context.args[0]
	context.bot.send_message(chat_id=update.effective_chat.id, text="You have chosen " + target)

def list_languages(update, context):
    results = translate_client.get_languages()
    langauges = ""
    for language in results:
        langauges += u'{name} ({language})\n'.format(**language)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target langauge\n" + langauges)

def images(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="I have recieved an image. Translating in process...")

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

	context.bot.send_message(chat_id=update.effective_chat.id, text=u'Text: {}\n'.format(result['input'])) 
	context.bot.send_message(chat_id=update.effective_chat.id, text=u'Detected source language: {}\n'.format(result['detectedSourceLanguage']))
	context.bot.send_message(chat_id=update.effective_chat.id, text=u'Translation: {}\n'.format(result['translatedText'])) 

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

start_handler = CommandHandler('start', start)
caps_handler = CommandHandler('caps', caps)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
choose_handler = CommandHandler('choose', choose)
list_handler = CommandHandler('list', list_languages)
image_handler = MessageHandler(Filters.photo | Filters.document.image, images)
unknown_handler = MessageHandler(Filters.command, unknown)

dp.add_handler(start_handler)
dp.add_handler(echo_handler)
dp.add_handler(caps_handler)
dp.add_handler(choose_handler)
dp.add_handler(list_handler)
dp.add_handler(image_handler)
dp.add_handler(unknown_handler)

upd.start_polling()
upd.idle()
