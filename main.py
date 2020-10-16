import telebot
import cherrypy
import configparser, logging
import db_creator

#logging cocnfig
logging.basicConfig(filename='bot.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

config = configparser.ConfigParser()
config.read('config.cfg')
WEBHOOK_HOST = config.get('Settings', 'WEBHOOK_HOST')
WEBHOOK_PORT = config.getint('Settings', 'WEBHOOK_PORT')  # 443, 80, 88 or 8443 (port should be oppened!)
WEBHOOK_LISTEN = config.get('Settings',
                            'WEBHOOK_LISTEN')  
WEBHOOK_SSL_CERT = config.get('Settings', 'WEBHOOK_SSL_CERT')  
WEBHOOK_SSL_PRIV = config.get('Settings', 'WEBHOOK_SSL_PRIV')  
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.get('Settings', 'token'))
bot = telebot.TeleBot(config.get('Settings', 'token'))

# WebhookServer
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

# /reset reset all progress
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    db = db_creator.SQLighter(config.get('Settings', 'db_name'))
    db.delete_user_data(str(message.chat.id))
    bot.send_message(message.chat.id, "All progress has been dropped")
    db.close()

@bot.message_handler(commands=["next"])
def cmd_reset(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add("/next")
    markup.add("/reset")
    db = db_creator.SQLighter(config.get('Settings', 'db_name'))
    for number_of_the_question in db.check_user_state(str(message.chat.id)):
        if int(number_of_the_question) == 312:
            db.change_state(1, str(message.chat.id))
        else:
            for question in db.get_question(number_of_the_question):
                bot.send_message(message.chat.id, question, reply_markup=markup)
            new_number_of_the_question = int(number_of_the_question) + 1
            db.change_state(new_number_of_the_question, str(message.chat.id))
    db.close()


 # RUN!
if __name__ == "__main__":
    # Initial dialog
    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        db = db_creator.SQLighter(config.get('Settings', 'db_name'))
        check_state_result = db.check_user_state(str(message.chat.id))
        if check_state_result:
            db.close()
            logging.info(f'The next user {message.chat.id} logged in')
        else:
            bot.send_message(message.chat.id, "Hello! I am Rather game bot. Send /next for startning the game /reset - delete all created progress")
            db_creator.SQLighter(config.get('Settings', 'db_name')).add_new_user(str(message.chat.id))
            logging.info(f'The next user {message.chat.id} has been registered')
            db.close()

    # Take out webhook!
    bot.remove_webhook()
    # Place webhook!
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))
    
    # Settings of the server CherryPy
    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
