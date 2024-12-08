from actions.actions import *
from util import default_callback_handler

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

app.add_handler(CallbackQueryHandler(default_callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.run_polling()
