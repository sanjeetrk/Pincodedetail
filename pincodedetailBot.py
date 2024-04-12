import time
import telebot
from telebot import types
import requests  # Import the requests library

bot = telebot.TeleBot('BOT_TOKEN')

user_pincode = {}  # Dictionary to store each user's selected pincode

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Please enter a pincode.")


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back_handler(call):
    # callback_handler()
    user_id = call.from_user.id
    pincode = user_pincode.get(user_id)

    url = f"https://api.postalpincode.in/pincode/{pincode}"

    response = requests.get(url)
    data = response.json()

    if data[0]['Status'] == 'Success':
        post_offices = data[0]['PostOffice']

        markup = types.InlineKeyboardMarkup()
        for idx, office in enumerate(post_offices, start=1):
            button = types.InlineKeyboardButton(text=office['Name'], callback_data=f"{user_id}:{idx}")
            markup.add(button)

        bot.send_message(user_id, "Select a Post Office to get details:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_pincode(message):
    user_id = message.from_user.id
    pincode = message.text.strip()
    url = f"https://api.postalpincode.in/pincode/{pincode}"

    response = requests.get(url)
    data = response.json()

    if data[0]['Status'] == 'Success':
        post_offices = data[0]['PostOffice']

        markup = types.InlineKeyboardMarkup(row_width=2)  # Set the number of buttons in a row to 2

        buttons = []  # List to store buttons for each row
        for idx, office in enumerate(post_offices, start=1):
            button = types.InlineKeyboardButton(text=office['Name'], callback_data=f"{user_id}:{idx}")
            buttons.append(button)

            # When two buttons are collected, add them to the markup and clear the list
            if len(buttons) == 2:
                markup.add(*buttons)
                buttons.clear()

        # If there are remaining buttons in the list, add them to the last row
        if buttons:
            markup.add(*buttons)

        user_pincode[user_id] = pincode  # Store user's selected pincode

        reply = "Select a Post Office to get details:"
        bot.send_message(user_id, reply, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        user_id, index = call.data.split(":")
    except ValueError:
        # bot.send_message(call.chat.id,'Click back or send other Pin code')
        bot.reply_to(call.message, 'Click back or send other pincode')
        return
    user_id = int(user_id)
    index = int(index) - 1  # Adjust for 0-based indexing

    pincode = user_pincode.get(user_id)

    url = f"https://api.postalpincode.in/pincode/{pincode}"

    response = requests.get(url)
    data = response.json()

    if data[0]['Status'] == 'Success':
        post_offices = data[0]['PostOffice']

        if 0 <= index < len(post_offices):
            selected_office = post_offices[index]
            markup = types.InlineKeyboardMarkup(row_width=2)  # Set the number of buttons in a row
            for key, value in selected_office.items():
                key_button = types.InlineKeyboardButton(str(key), callback_data=f"{user_id}:key:{index}")
                value_button = types.InlineKeyboardButton(str(value), callback_data=f"{user_id}:value:{index}")
                markup.add(key_button, value_button)

            markup.add(types.InlineKeyboardButton("Back", callback_data="back"))
 #           bot.answer_callback_query(call.id, text="You clicked on a button!")
            bot.send_message(user_id, "Details:", reply_markup=markup)



#bot.polling()
while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(5)
