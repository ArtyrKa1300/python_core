import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, CallbackContext, \
    MessageHandler, filters, ConversationHandler

from credentials import ChatGPT_TOKEN, BOT_TOKEN
from gpt import ChatGptService
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, send_text_buttons)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",filemode="a",
    format="%(asctime)s %(levelname)s %(message)s"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Start")
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'translate': 'Переводчик',
        'recommend': 'Рекомендации по фильмам, книгам и музыке'
    })


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Random")
    await send_image(update, context, 'random')
    prompt = load_prompt('random')
    answer = await chat_gpt.send_question(prompt_text=prompt, message_text='')
    logging.info(f"Answer from gpt in random: {answer}")
    await send_text_buttons(update, context, answer, {
        'random_more': 'Хочу еще факт',
        'stop': 'Закончить'
    })


async def gpt(update: Update, context: CallbackContext):
    logging.info("User selected Gpt")
    context.user_data['mode'] = 'gpt'
    chat_gpt.set_prompt(load_prompt('gpt'))
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Talk")
    context.user_data['mode'] = 'talk'
    text = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, text, buttons={
        'talk_cobain': 'Курт Кобейн',
        'talk_hawking': 'Стивен Хокинг',
        'talk_nietzsche': 'Фридрих Ницше',
        'talk_queen': 'Елизавета II',
        'talk_tolkien': 'Джон Толкиен'
    })


async def talk_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Talk_buttons")
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    greet = await chat_gpt.add_message('Поздоровайся со мной')
    await send_image(update, context, data)
    await send_text(update, context, greet)


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Translate")
    context.user_data['mode'] = 'translate'
    text = load_message('translate')
    await send_image(update, context, 'translate')
    await send_text_buttons(update, context, text, buttons={
        'translate_eng': 'Английский',
        'translate_ger': 'Немецкий',
        'translate_random': 'Определи язык и переведи'
    })


async def translate_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Translate Buttons")
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    await send_text(update, context, "Введи текст, плз")


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Recommend")
    context.user_data['mode'] = 'recommend'
    context.user_data['not'] = []
    text = load_message('recommend')
    await send_image(update, context, 'recommend')
    await send_text_buttons(update, context, text, buttons={
        'recommend_film': 'Фильм',
        'recommend_book': 'Книгу',
        'recommend_music': 'Музыку'
    })


async def recommend_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected recommend buttons")
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    await send_text(update, context, "Введи желаемый жанр")


async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected change lang")
    await update.callback_query.answer()
    await translate(update, context)


async def change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected change recommend")
    await update.callback_query.answer()
    await recommend(update, context)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Stop")
    await update.callback_query.answer()
    await start(update, context)


async def random_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await random(update, context)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Start gpt dialog")
    request = update.message.text
    message = await send_text(update, context, 'Думаю над ответом')
    answer = await chat_gpt.add_message(request)

    await message.delete()
    await send_text_buttons(update, context, answer, buttons={'stop': 'Завершить'})


async def translate_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Start translate dialog")
    request = update.message.text
    logging.info(f"User string need translate: {request}")
    message = await send_text(update, context, 'Думаю над ответом')
    answer = await chat_gpt.add_message(request)
    logging.info(f"Translate: {answer}")
    await message.delete()
    await send_text_buttons(update, context, answer, buttons={'change_lang': "Сменить язык", 'stop': 'Завершить'})


async def recommend_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Start recommend dialog")
    request = update.message.text
    logging.info(f"User need recommend: {request}")
    message = await send_text(update, context, 'Думаю над ответом')
    answer = await chat_gpt.add_message(request)
    logging.info(f"Recommend from gpt: {answer}")
    context.user_data['not'] += answer
    await message.delete()
    await send_text_buttons(update, context, answer, buttons={'change': "Не нравится", 'stop': 'Закончить'})


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match context.user_data['mode']:
        case 'main':
            await start(update, context)
        case 'gpt':
            await gpt_dialog(update, context)
        case 'talk':
            await gpt_dialog(update, context)
        case 'translate':
            await translate_dialog(update, context)
        case 'recommend':
            await recommend_dialog(update, context)


chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('translate', translate))
app.add_handler(CommandHandler('recommend', recommend))

app.add_handler(CallbackQueryHandler(translate_button, pattern='^translate_.*'))
app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(stop, pattern='stop'))
app.add_handler(CallbackQueryHandler(change_lang, pattern='change_lang'))
app.add_handler(CallbackQueryHandler(change, pattern='change'))
app.add_handler(CallbackQueryHandler(recommend_button, pattern='^recommend_*'))
app.add_handler(CallbackQueryHandler(random_button, pattern='^random_*'))


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User selected Quiz")
    context.user_data['mode'] = 'quiz'
    context.user_data['score'] = 0
    chat_gpt.set_prompt(load_prompt('quiz'))
    await send_text_buttons(update, context, 'Выберите тему', buttons={
        'quiz_prog': 'Программирование',
        'quiz_math': 'Математика',
        'quiz_biology': 'Биология'
    })
    return THEME


async def quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Start quiz_theme")
    await update.callback_query.answer()
    question = await chat_gpt.add_message(update.callback_query.data)
    await send_text(update, context, question)
    return ANSWER


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Start quiz_answer")
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    logging.info(f"Quiz answer: {answer}")
    if answer == 'Правильно!':
        context.user_data['score'] = context.user_data.get('score', 0) + 1
    await send_text_buttons(update, context, answer + '\n\nВаш счет: ' + str(
        context.user_data['score']), {
        'quiz_more': 'Еще вопрос',
        'quiz_change': 'Выбрать другую тему',
        'stop': 'Завершить'
    })
    return CHOOSE_AFTER


async def quiz_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == 'quiz_more':
        return await quiz_theme(update, context)
    else:
        await update.callback_query.answer()
        return await quiz(update, context)


THEME, CHOOSE, ANSWER, CHOOSE_AFTER = range(4)

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler('quiz', quiz)],
    states={
        THEME: [CallbackQueryHandler(quiz_theme, pattern='^quiz_.*')],
        CHOOSE: [CallbackQueryHandler(quiz_theme, pattern='quiz_more'),
                 CallbackQueryHandler(quiz, pattern='quiz_change')],
        ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer)],
        CHOOSE_AFTER: [CallbackQueryHandler(quiz_choose, pattern='^quiz_.*')]
    },
    fallbacks=[CommandHandler('stop', stop)]
))

app.add_handler(CallbackQueryHandler(default_callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.run_polling()
