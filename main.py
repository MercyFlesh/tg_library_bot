import time
import re
import telebot
from telebot.apihelper import edit_message_reply_markup
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from help_db import DBHelper
from config import *

bot = telebot.TeleBot(token)

######################
# GENERATE KEYBOARDS #
######################

def get_topics_keyboard(state_button=4):
    with DBHelper() as db:
        topics = db.get_post_topics()
    
    keyboard = InlineKeyboardMarkup()

    for i in range(state_button - 4, state_button):
        if i < len(topics):
            keyboard.add(InlineKeyboardButton(text=topics[i], callback_data=f'topic_{topics[i]}'))
        else:
            break

    button_next = InlineKeyboardButton(text="»", callback_data="next")
    button_prev = InlineKeyboardButton(text="«", callback_data="prev")
    if state_button == 4 and state_button < len(topics):
        keyboard.add(button_next)
    elif state_button > 4 and state_button < len(topics):
        keyboard.add(button_prev, button_next)
    elif state_button > 4:
        keyboard.add(button_prev)
    
    return keyboard


def get_topic_links_keyboard(len_links, state_link=0):
    keyboard = InlineKeyboardMarkup()
    
    button_next = InlineKeyboardButton(text="»", callback_data="next_link")
    button_prev = InlineKeyboardButton(text="«", callback_data="prev_link")
    button_topics = InlineKeyboardButton(text="выбрать другую тему", callback_data="alt_topic")
    
    if state_link == 0 and state_link < len_links:
        keyboard.add(button_next)
    elif state_link > 0 and state_link < len_links:
        keyboard.add(button_prev, button_next)
    elif state_link > 0 and state_link == len_links:
        keyboard.add(button_prev)
    keyboard.add(button_topics)

    return keyboard


######################
######################
######################

@bot.message_handler(commands=['start'])
def start(message):
    text = ('Привет! Это бот с катологом статей канала [hello world](https://t.me/hw_code), '
        'разделенным по темам для удобного поиска нужного материала.\n\n'
        '_Чтобы выбрать нужную тему нажмите_ /topics')
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, text, parse_mode='Markdown')
    
    with DBHelper() as db:
        db.add_user(message.chat.id)


############################
# TOPICS CALLBACK HENDLERS #
############################

@bot.message_handler(commands=['topics'])
def get_topics_hendler(message):
    keyboard = get_topics_keyboard()
    text = "Выберите тему:"

    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
    
    with DBHelper() as db:
        db.set_user_state_links(message.chat.id, 0) #nulling position on links


def get_topics(message):
    keyboard = get_topics_keyboard()
    text = "Выберите тему:"

    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, text=text, reply_markup=keyboard)
    
    with DBHelper() as db:
        db.set_user_state_links(message.chat.id, 0)




@bot.callback_query_handler(func=lambda call: call.data in ['next', 'prev'])
def call_next_listTopics(call):
    if call.data == 'next':
        with DBHelper() as db:
            state = db.get_user_state_topics(call.from_user.id)
            db.set_user_state_topics(call.from_user.id, state + 4)
        keyboard = get_topics_keyboard(state + 4)
    else:
        with DBHelper() as db:
            state = db.get_user_state_topics(call.from_user.id)
            db.set_user_state_topics(call.from_user.id, state - 4)
        keyboard = get_topics_keyboard(state - 4)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboard)


###########################
# LINKS CALLBACK HENDLERS #
###########################

@bot.callback_query_handler(func=lambda call: call.data in re.findall(r'topic_[\w\s]+', call.data))
def call_next_listTopic_links(call):
    enter_topic = re.match(r'topic_([\w\s]+)', call.data)
    with DBHelper() as db:
        links = db.get_topic_links(enter_topic.group(1))
        db.set_user_state_topics(call.from_user.id, 4) #4 - inital state user in topics list
        db.update_user_enter_topic(call.from_user.id, enter_topic.group(1)) 

    keyboard = get_topic_links_keyboard(len(links) - 1)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, links[0], reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['prev_link', 'next_link'])
def call_next_link(call):    
    if call.data == 'prev_link':
        with DBHelper() as db:
            state = db.get_user_state_links(call.from_user.id)
            enter_topic = db.get_user_enter_topic(call.from_user.id)
            links = db.get_topic_links(enter_topic)
            db.set_user_state_links(call.from_user.id, state - 1)
            state -= 1
    else:
        with DBHelper() as db:
            state = db.get_user_state_links(call.from_user.id)
            enter_topic = db.get_user_enter_topic(call.from_user.id)
            links = db.get_topic_links(enter_topic)
            db.set_user_state_links(call.from_user.id, state + 1)
            state += 1

    keyboard = get_topic_links_keyboard(len(links) - 1, state)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=links[state], reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'alt_topic')
def call_topics_list(call):
    #bot.register_next_step_handler(call.message, get_topics)
    keyboard = get_topics_keyboard()
    text = "Выберите тему:"

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)
    
    with DBHelper() as db:
        db.set_user_state_links(call.message.chat.id, 0)
  

#################
# ADMINS FUNCKS #
#################
regex_link = 'https:\/\/[a-zA-Z0-9а-я\-]+.[a-zA-Zа-я]?[a-zA-Zа-я]?\/[@a-zA-Z0-9\-\/\_]*'
regex_topic = '[а-яА-Яa-zA-Z\s]+'

@bot.message_handler(content_types=['text'],
                    func=lambda message: message.chat.id in admin_id and
                    message.text.split(' ')[0] == 'set')
def set_link(message):
    
    res = re.match(rf'(set\s{regex_link}\s{regex_topic})', message.text)
    if res is not None and res.group(0) == message.text:
        result = re.findall(rf'set\s({regex_link})\s({regex_topic})', message.text)
        post_link = result[0][0]
        post_topic = result[0][1]
        with DBHelper() as db:
            res = db.set_post(post_link, post_topic)
        bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, 'Incorrect format request')


@bot.message_handler(content_types=['text'],
                    func=lambda message: message.chat.id in admin_id and
                    message.text.split(' ')[0] == 'update_link') 
def update_link(message):
    res = re.match(rf'(update_link\s{regex_link}\s{regex_link})', message.text)
    if res is not None and res.group(0) == message.text:
        post_link = message.text.split(' ')[1]
        new_link = message.text.split(' ')[2]
        with DBHelper() as db:
            res = db.update_post_link(post_link, new_link)
        bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, 'Incorrect format request')

@bot.message_handler(content_types=['text'],
                    func=lambda message: message.chat.id in admin_id and
                    message.text.split(' ')[0] == 'update_topic')
def update_topic(message):
    res = re.match(rf'(update_topic\s{regex_link}\s{regex_topic}\s{regex_topic})', message.text)
    if res is not None and res.group(0) == message.text:
        result = re.findall(rf'update_topic\s({regex_link})\s({regex_topic})\s({regex_topic})', message.text)
        post_link = result[0][0]
        old_topic = result[0][1]
        new_topic = result[0][2]

        with DBHelper() as db:
            res = db.update_post_topic(post_link, old_topic, new_topic)
        bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, 'Incorrect format request')


@bot.message_handler(content_types=['text'],
                    func=lambda message: message.chat.id in admin_id and
                    message.text.split(' ')[0] == 'delete')
def delete_link(message):
    res = re.match(rf'(delete\s{regex_link})', message.text)
    if res is not None and res.group(0) == message.text:
        res = re.search(rf'delete\s({regex_link})', message.text)
        with DBHelper() as db:
            del_res = db.del_post_link(res.group(1))
        bot.send_message(message.chat.id, del_res)


#################
#################
#################

def main():
    bot.infinity_polling(True)

if __name__ == "__main__":
    main()
