from telebot import types
from datetime import datetime
from main.models import User, Message, Vacancy, Specialisation
from .keyboards import keyboard
from .functions import search_master, not_confirmed_users

def control(bot, message):
    admin = User.objects.filter(role='Админ')
    bot_user = User.objects.get(chat_id=message.from_user.id)
    messages = Message.objects.filter(clue='bot_msgs')
    if len(admin) == 0:
        admin_id = 248598993
        admin = User.objects.filter(chat_id=admin_id)
    else: admin_id = admin[0].chat_id

    # Меню администратора
    if message.text == '👤 Пользователи':
        users = User.objects.exclude(role='Админ').exclude(mode='registration').order_by('-registration_date')[:10]
        msg = 'Последние 10 зарегистрировавщихся пользователей:\n\n'
        for user in users:
            can_chat = ('\nНаписать в телеграм: @'+user.user) if user.user != None else ''
            msg += 'Имя: '+user.name+'\nНомер телефона: '+user.phone+'\nГород: '+user.city+'\nДата регистрации: '+user.registration_date.strftime('%d.%m.%Y %H:%M:%S')+can_chat+'\n'
            msg += '------------------------------------------------------------\n'
        bot.send_message(admin_id, msg)
    if message.text == '📄 Объявления':
        vacancies = Vacancy.objects.order_by('-date')[:10]
        msg = 'Последние 10 опубликованных объявлений:\n\n'
        for vacancy in vacancies:
            author = User.objects.get(chat_id = vacancy.chat_id)
            can_chat = ('\nНаписать в телеграм: @'+author.user) if author.user != None else ''
            msg += 'Дата публикации: '+vacancy.date.strftime('%d.%m.%Y %H:%M:%S')+'\nТекст: '+vacancy.text+'\nАвтор: '+author.name+can_chat+'\n'
            msg += '------------------------------------------------------------\n'
        bot.send_message(admin_id, msg)
    if message.text == '📑 Неподтвержденные пользователи':
        not_confirmed_users(bot, 1, first_call=True)
    if message.text == '💬 Опубликовать сообщение':
        res = bot.send_message(admin_id, 'Как вы хотите отправить сообщение боту?', reply_markup = keyboard('send_to_bot'))
        admin[0].msg_id = res.id
        admin[0].save()
    # Сторона заказчика
    if message.text == '⚡️ Разместить вакансию в 1 клик':
        bot_user.mode = 'one_click_vacancy'
        bot_user.save()
        bot.send_message(message.from_user.id, messages[1].text.replace('br', '\n'))
        return
    if message.text == '🔎 Поиск специалиста':
        bot_user.mode = 'search'
        bot_user.step = 1
        bot_user.save()
        search_master(bot, message)
        return
    # Общие функции
    if message.text == '📇 Мой аккаунт':
        bot.send_message(message.from_user.id, 'Мой аккаунт', reply_markup = keyboard('my_account'))
    if message.text == '🗂 Посмотреть аккаунт':
        if bot_user.role == 'Заказчик':
            msg = 'Моё резюме:\n'
            msg += '\n*Имя:* ' + bot_user.name
            msg += '\n*Город:* ' + bot_user.city
            msg += '\n*Номер телефона:* +' + bot_user.phone
            bot.send_message(message.from_user.id, msg, parse_mode="Markdown")
        else:
            msg = 'Моё резюме:\n'
            msg += '\n*Имя:* ' + bot_user.name
            msg += '\n*Город:* ' + bot_user.city
            msg += '\n*Номер телефона:* +' + bot_user.phone
            spec = Specialisation.objects.get(clue=bot_user.speciality)
            msg += '\n*Специализация:* ' + spec.name
            if bot_user.experience == 'less-one':
                experience = 'Менее года'
            elif bot_user.experience == 'one-three':
                experience = '1-3 года'
            elif bot_user.experience == 'more-three':
                experience = 'Более 3 лет'
            msg += '\n*Опыт работы:* ' + experience
            msg += '\n*Ссылка на портфолио:* ' + bot_user.portfolio_url
            msg += '\n*О себе:* ' + bot_user.description
            if bot_user.photo_url == '-':
                bot.send_message(message.from_user.id, msg, parse_mode="Markdown")
            else:
                bot.send_photo(message.from_user.id, bot_user.photo_url, caption = msg, parse_mode="Markdown")
    if message.text == '📝 Редактировать аккаунт':
        bot_user.mode = 'edit_account'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Редактирование аккаунта', reply_markup = keyboard('edit_customer_account') if bot_user.role == 'Заказчик' else keyboard('edit_specialist_account'))
    if message.text == '📨 Написать админу':
        bot.send_message(message.from_user.id, 'Аккаунт администратора @'+admin[0].user+'\nВы можете напрямую написать ему.')
    if message.text == '📰 Купить рекламу в боте':
        bot.send_message(message.from_user.id, 'Для размещения рекламы напишите @'+admin[0].user)
    if message.text == '🔙 Назад':
        bot_user.mode = None
        bot_user.save()
        bot.send_message(message.from_user.id, 'Главное меню', reply_markup = keyboard('customer') if bot_user.role == 'Заказчик' else keyboard('specialist'))
    # Редактирование профиля общее
    if message.text == '✅ Изменить имя':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        msg = '*Текущее имя:* ' + bot_user.name + '\n\nОтправьте новое имя.'
        bot_user.mode = 'edit_name'
        bot_user.save()
        bot.send_message(message.from_user.id, msg, reply_markup = kb, parse_mode='Markdown')
    if message.text == '🏢 Изменить город':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        msg = '*Текущий город:* ' + bot_user.city + '\n\nВыберите город из списка.'
        bot.send_message(message.from_user.id, '*Текущий город:* ' + bot_user.city, reply_markup = kb, parse_mode='Markdown')
        bot_user.mode = 'edit_city'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Выберите город из списка.', reply_markup = keyboard('cities'))
    if message.text == '📱 Изменить номер телефона':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('📱 Отправить новый номер телефона', request_contact = True))
        kb.add(types.KeyboardButton('❌ Отмена'))
        msg = '*Текущий номер телефона:* +' + bot_user.phone + '\n\nОтправьте новый номер телефона или воспользуйтесь кнопкой ниже.'
        bot_user.mode = 'edit_phone'
        bot_user.save()
        bot.send_message(message.from_user.id, msg, reply_markup = kb, parse_mode='Markdown')
    if message.text == '🚮 Удалить мой аккаунт':
        if admin_id == message.from_user.id:
            bot.send_message(message.from_user.id, 'Удаление аккаунта невозможно, так как вы являетесь администратором бота. Удаление администратора бота влечёт за собой отрицательные последствия в работе бота.')
        else:
            person = User.objects.get(chat_id=message.from_user.id)
            person.delete()
            bot.send_message(message.from_user.id, 'Рады были с вами поработать. Всего хорошего!\n\nЧтобы зарегистрироваться повторно отправьте боту команду /start', reply_markup = keyboard('remove_keyboard'))
    # Редактирование профиля заказчика
    if message.text == '😕 Я не Заказчик':
        bot_user.role = None
        bot_user.name = None
        bot_user.phone = None
        bot_user.city = None
        bot_user.mode = 'registration'
        bot_user.step = 1
        bot_user.save()
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('who_you_are'))
        bot_user.msg_id = res.id
        bot_user.save()
    # Редактирование профиля исполнителя
    if message.text == '🧰 Изменить специализацию':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        spec = Specialisation.objects.get(clue=bot_user.speciality)
        bot.send_message(message.from_user.id, '*Текущая специализация:* ' + spec.name, reply_markup = kb, parse_mode='Markdown')
        bot_user.mode = 'edit_specialisation'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Выберите специализацию.', reply_markup = keyboard('speciality'))
    if message.text == '🗃 Изменить опыт работы':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        if bot_user.experience == 'less-one':
            experience = 'Менее года'
        elif bot_user.experience == 'one-three':
            experience = '1-3 года'
        elif bot_user.experience == 'more-three':
            experience = 'Более 3 лет'
        bot.send_message(message.from_user.id, '*Текущий опыт работы:* ' + experience, reply_markup = kb, parse_mode='Markdown')
        bot_user.mode = 'edit_experience'
        bot_user.save()
        bot.send_message(message.from_user.id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
    if message.text == '📂 Изменить ссылку портфолио':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        msg = '*Текущая ссылка на портфолио:* ' + bot_user.portfolio_url + '\n\nОтправьте ссылку на портфолио.'
        bot_user.mode = 'edit_portfolio'
        bot_user.save()
        bot.send_message(message.from_user.id, msg, reply_markup = kb, parse_mode='Markdown')
    if message.text == '📷 Изменить фото':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        bot_user.mode = 'edit_photo'
        bot_user.save()
        if bot_user.photo_url == '-':
            bot.send_message(message.from_user.id, '*Текущее фото профиля:* ' + bot_user.photo_url + '\n\nОтправьте новое фото.', reply_markup = kb, parse_mode='Markdown')
        else:
            bot.send_photo(message.from_user.id, bot_user.photo_url, caption = '*Текущее фото профиля:* ⬆️\n\nОтправьте новое фото.', reply_markup = kb, parse_mode="Markdown")
    if message.text == '✌ Изменить описание о себе':
        kb = types.ReplyKeyboardMarkup(resize_keyboard = True)
        kb.add(types.KeyboardButton('❌ Отмена'))
        msg = '*Текущее описание о себе:* ' + bot_user.description + '\n\nНапишите пару слов о себе.'
        bot_user.mode = 'edit_description'
        bot_user.save()
        bot.send_message(message.from_user.id, msg, reply_markup = kb, parse_mode='Markdown')
    if message.text == '😕 Я не Специалист':
        bot_user.role = None
        bot_user.name = None
        bot_user.phone = None
        bot_user.city = None
        bot_user.experience = None
        bot_user.speciality = None
        bot_user.photo_url = None
        bot_user.portfolio_url = None
        bot_user.description = None
        bot_user.mode = 'registration'
        bot_user.step = 1
        bot_user.save()
        res = bot.send_message(message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('who_you_are'))
        bot_user.msg_id = res.id
        bot_user.save()
