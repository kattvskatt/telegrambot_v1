from config import api_key, bot
from my_class import NASA
from telebot import types
import re
import datetime

@bot.message_handler(commands = ['help'])
def help_comand(message):
    bot.send_message(message.chat.id, f'(/start - начало работы бота);\n'
                                      f'(/help - помощь);\n'
                                      f'(При запуске бот требует ввести дату в заданном формате YYYY-MM-DD);\n' 
                                      f'(Если дата введена не корректно, Бот выведет сообщение.);\n'
                                      f'(Если дата введена корректно, Бот начнет запрос к API).\n'
                    ) 

@bot.message_handler(commands = ['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)
    button_asteroids = types.KeyboardButton('Прогноз астероидной погоды')
    button_apod = types.KeyboardButton("APOD")
    button_epic = types.KeyboardButton('EPIC')
    markup.add(button_asteroids)
    markup.add(button_apod, button_epic)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}! \n'
                     f'Нажми: \n<b>Прогноз астероидной погоды</b> для просмотра прогноза астероидной погоды \n' 
                     f'Нажми: \n<b>APOD (Astronomy Picture of the Day)</b> для получения астрономической картинки и ее описания \n'
                     f'Нажми: \n<b>EPIC (Earth Polychromatic Imaging Camera)</b> для получения снимка Земли, '
                     f'сделанного с помощью DSCOVR\'s Earth Polychromatic Imaging Camera (EPIC)',
                     reply_markup=markup,
                     parse_mode='html')
    gif_url = 'https://i.gifer.com/7gRp.gif'
    bot.send_animation(message.chat.id, animation=gif_url)
    # bot.register_next_step_handler(message, handle_button_click)

@bot.message_handler(commands = ['stop'])
def stop_command(message):
    bot.send_message(message.chat.id, "До встречи!")
    exit()

@bot.message_handler(content_types=['text'])
def handle_button_click(message):
    if message.text in ['Прогноз астероидной погоды', 'APOD', 'EPIC']:
        bot.send_message(message.chat.id, 'Для начала работы бота введите дату в формате "YYYY-MM-DD"')
        if message.text == 'Прогноз астероидной погоды':
            bot.register_next_step_handler(message, click_on_asteroids)
        elif message.text == 'APOD':
            bot.register_next_step_handler(message, click_on_apod)
        elif message.text == 'EPIC':
            bot.register_next_step_handler(message, click_on_epic)
    else:
        bot.reply_to(message, f'{message.chat.first_name}, не балуйся. Начни сначала!')
        return

def click_on_asteroids(message):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, message.text):
        start_date = message.text
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if start_date_obj.date() == datetime.datetime.now().date():
            end_date = start_date
        else:
            # end_date_obj = start_date_obj
            end_date_obj = start_date_obj + datetime.timedelta(days=1)
            end_date = end_date_obj.strftime('%Y-%m-%d')

        bot.send_message(message.chat.id, 'Дата введена верно.')
        bot.send_message(message.chat.id, f'Дата начала поиска {start_date}. Дата окончания поиска {end_date}.')

        nasa_asteroids = NASA(start_date=start_date, api_key=api_key, end_date=end_date)
        data = nasa_asteroids.get_asteroids()
        bot.send_message(message.chat.id,
                         f'В этот период замечено {data["element_count"]} объектов сближающихся с Землей.')

        data1 = nasa_asteroids.get_hazardous_asteroids()
        inf = ""
        for obgekt in data1:
            for key, value in obgekt.items():
                inf += f"{key}: {value}\n"
        bot.send_message(message.chat.id, f'Из них потенциально опасны: {len(data1)}')

        if end_date == start_date and len(data1) >= 1:
            bot.send_message(message.chat.id, f'ОПАСНОСТЬ МЕТИОРИТНОГО ДОЖДЯ, УКРОЙТЕСЬ В УБЕЖИЩЕ!!!!')
            gif_url3 = 'https://i.gifer.com/7BVP.gif'
            bot.send_animation(message.chat.id, animation=gif_url3)

        bot.send_message(message.chat.id, inf)
        gif_url2 = 'https://i.gifer.com/AG7C.gif'
        bot.send_animation(message.chat.id, animation=gif_url2)

    else:
        gif_url1 = 'https://i.gifer.com/VAyR.gif'
        bot.send_message(message.chat.id, 'ОШИБКА, ДАТА ВВЕДЕНА НЕ ПРАВИЛЬНО!!!')
        bot.send_animation(message.chat.id, animation=gif_url1)
        bot.send_message(message.chat.id, 'Попробуйте еще раз. Введите дату в формате "YYYY-MM-DD"')
        bot.register_next_step_handler(message, click_on_asteroids)


def click_on_apod(message):
    date = message.text
    if not re.match(r'\d{4}-\d{2}-\d{2}', date):
        bot.reply_to(message, 'Некорректный формат даты. Попробуйте еще раз. Введите дату в формате "YYYY-MM-DD"')
        bot.register_next_step_handler(message, click_on_apod)
    elif datetime.datetime.strptime(date, '%Y-%m-%d').date() > datetime.date.today() or date < '1995-06-16':
        bot.reply_to(message, 'Некорректная дата. Дата должна быть в пределах с 1995-06-16 по сегодня')
        bot.register_next_step_handler(message, click_on_apod)
    else:
        nasa_api = NASA(start_date=date, api_key=api_key)
        answer = nasa_api.get_apod()
        bot.send_photo(message.chat.id, photo=answer['url'])
        bot.send_message(message.chat.id, answer['explanation'])

def click_on_epic(message):
    date = message.text
    if not re.match(r'\d{4}-\d{2}-\d{2}', date):
        bot.reply_to(message, 'Некорректный формат даты. Попробуйте еще раз. Введите дату в формате "YYYY-MM-DD"')
        bot.register_next_step_handler(message, click_on_epic)
    elif datetime.datetime.strptime(date, '%Y-%m-%d').date() > datetime.date.today() or date < '2015-06-17':
        bot.reply_to(message, 'Некорректная дата. Дата должна быть в пределах с 2015-06-17 по сегодня')
        bot.register_next_step_handler(message, click_on_epic)
    else:
        nasa_api = NASA(start_date=date, api_key=api_key)
        answer = nasa_api.get_epic()
        if not answer:
            bot.send_message(message.chat.id, "Нет данных. Пожалуйста, начните сначала и выберите другую дату.")
        else:
            image_id = answer[0]['image']
            yyyymmdd = date.split('-')
            url_epic = f"https://epic.gsfc.nasa.gov/archive/natural/{yyyymmdd[0]}/{yyyymmdd[1]}/{yyyymmdd[2]}/png/{image_id}.png"
            bot.send_photo(message.chat.id, photo=url_epic)



@bot.message_handler(content_types=['photo', 'audio'])
def handle_other_mes(message):
    bot.reply_to(message, f'{message.chat.first_name}, не балуйся. Начни сначала!')


bot.polling(non_stop=True)