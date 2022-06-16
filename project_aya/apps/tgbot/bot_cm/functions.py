from django.db.models import Q
from django.conf import settings
from telebot import types
from datetime import datetime
from main.models import User, Vacancy, Info, Specialisation
from .keyboards import keyboard

def not_confirmed_users(bot, num, data=None, first_call=False):
    admin = User.objects.filter(role='Админ')
    if len(admin) == 0:
        admin_id = 248598993
        admin = User.objects.filter(chat_id=admin_id)
    else: admin_id = admin[0].chat_id
    users = User.objects.exclude(role='Админ').filter(Q(mode='registration'), Q(step=4)|Q(step=9)).order_by('-id')
    phone = '+'+str(users[int(num)-1].phone) if str(users[int(num)-1].phone) != '-' else '-'
    msg = f'Неподтвержденный пользователь {num}/{len(users)}:\n'
    msg += '\n\n<b>ID</b> ' + str(users[int(num)-1].chat_id)
    msg += '\n<b>Имя:</b> ' + users[int(num)-1].name
    msg += '\n<b>Роль:</b> '+users[int(num)-1].role
    msg += '\n<b>Номер телефона:</b> ' + phone
    msg += '\n<b>Город:</b> ' + users[int(num)-1].city
    msg += '\n<b>Дата регистрации:</b> '+users[int(num)-1].registration_date.strftime('%d.%m.%Y %H:%M:%S')
    if first_call:
        res = bot.send_message(admin_id, msg, reply_markup = keyboard('postapprove_user', {'user': users[int(num)-1].chat_id, 'next': (int(num)+1) if int(num) < len(users) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')
        admin[0].msg_id = res.id
        admin[0].save()
    else:
        bot.edit_message_text(chat_id=admin_id, message_id=admin[0].msg_id, text=msg, reply_markup = keyboard('postapprove_user', {'user': users[int(num)-1].chat_id, 'next': (int(num)+1) if int(num) < len(users) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')

def create_one_click_vacancy(bot, data):
    v = Vacancy.objects.create(chat_id=data.from_user.id, msg_id=data.id, text=data.text, date=datetime.now())
    text = 'Ваше объявление:\n\n'
    text += data.text+'\n\n'
    text += 'Выберите в группу какого города хотите опубликовать:'
    res = bot.send_message(data.from_user.id, text, reply_markup = keyboard('cities'))
    bot_user = User.objects.get(chat_id=data.from_user.id)
    bot_user.msg_id = res.id
    bot_user.mode = bot_user.mode + '_' + str(v.id)
    bot_user.save()

def search_master(bot, data):
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if bot_user.mode == 'search' and bot_user.step == 1:
        res = bot.send_message(data.from_user.id, 'Укажите специальность:', reply_markup = keyboard('speciality'))
        bot_user.msg_id = res.id
        bot_user.step = 2
        bot_user.save()
        return
    if bot_user.mode == 'search' and bot_user.step == 2:
        bot.edit_message_text(chat_id=data.from_user.id, message_id=bot_user.msg_id, text='Укажите опыт работы:', reply_markup = keyboard('experience'))
        bot_user.step = 3
        bot_user.save()
        return
    if bot_user.mode == 'search' and bot_user.step == 3:
        bot.edit_message_text(chat_id=data.from_user.id, message_id=bot_user.msg_id, text='Укажите город из списка:', reply_markup = keyboard('cities'))
        bot_user.step = 4
        bot_user.save()
        return
    if bot_user.mode == 'search' and bot_user.step == 4:
        bot_user.step = None
        bot_user.mode = None
        bot_user.save()
        sp_city = Info.objects.get(clue='sp_city')
        sp_exp = Info.objects.get(clue='sp_exp')
        sp_spec = Info.objects.get(clue='sp_spec')
        result = User.objects.filter(city=sp_city.text, experience=sp_exp.text, speciality=sp_spec.text, role='Исполнитель').order_by('-registration_date')[:10]
        if len(result) > 0:
            msg = 'Специалисты, соответствующие вашим критериям поиска:\n\n'
            for row in result:
                can_chat = ('\nНаписать в телеграм: @'+row.user) if row.user != None else ''
                msg += 'Имя: '+row.name+'\nНомер телефона: '+row.phone+'\nСсылка на портфолио: '+row.portfolio_url+can_chat+'\n\n'
        else:
            msg = 'Специалисты, соответствующие вашим критериям не найдены\n\n'
        bot.edit_message_text(chat_id=data.from_user.id, message_id=bot_user.msg_id, text=msg)
        sp_city.delete()
        sp_exp.delete()
        sp_spec.delete()
        return
    return

def registration_customer(bot, data):
    admin = User.objects.filter(role="Админ")
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if bot_user.mode != 'registration': return
    if bot_user.step == 1:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Заказчик'
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 2:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '☺️ Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == '➡️ Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.save()
        return
    if bot_user.step == 3:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '🏙 Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 4:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        phone = '+'+str(bot_user.phone) if str(bot_user.phone) != '-' else '-'
        msg = 'Пользователь'+((' @'+bot_user.user) if bot_user.user != None else '')+' завершил регистрацию!'
        msg += '\n\n<b>ID</b> ' + str(bot_user.chat_id)
        msg += '\n<b>Имя:</b> ' + bot_user.name
        msg += '\n<b>Роль:</b> '+bot_user.role
        msg += '\n<b>Номер телефона:</b> ' + phone
        msg += '\n<b>Город:</b> ' + bot_user.city
        res = bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': bot_user.chat_id}), parse_mode='HTML')
        admin[0].msg_id = res.id
        admin[0].save()
        return

def registration_specialist (bot, data, skip = 0):
    admin = User.objects.filter(role="Админ")
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if bot_user.mode != 'registration': return
    if bot_user.step == 1:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Исполнитель'
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 2:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == '➡️ Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.save()
        return
    if bot_user.step == 3:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 4:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 5:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Укажите специальность', reply_markup = keyboard('speciality'))
        bot_user.experience = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 6:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_photo'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Загрузите вашу фотография', reply_markup = t_keyboard)
        bot_user.speciality = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.save()
        return
    if bot_user.step == 7:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_portfolio'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Отправьте ссылку на портфолио', reply_markup = t_keyboard)
        if skip:
            bot_user.photo_url = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            file = bot.get_file(data.photo[-1].file_id)
            downloaded_file = bot.download_file(file.file_path)
            with open(settings.STATIC_ROOT+'/img/user_photos/'+str(bot_user.chat_id)+'.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
                bot_user.photo_url = data.photo[-1].file_id
            bot_user.msg_id = res.id
            bot_user.save()
        return
    if bot_user.step == 8:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_description'))
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Раскажите немного о себе', reply_markup = t_keyboard)
        if skip:
            bot_user.portfolio_url = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            bot_user.portfolio_url = data.text
            bot_user.msg_id = res.id
            bot_user.save()
        return
    if bot_user.step == 9:
        bot.delete_message(chat_id, bot_user.msg_id)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        if skip:
            bot_user.description = '-'
            bot_user.msg_id = res.id
            bot_user.save()
        else:
            bot_user.description = data.text
            bot_user.msg_id = res.id
            bot_user.save()
        phone = '+'+str(bot_user.phone) if str(bot_user.phone) != '-' else '-'
        msg = 'Пользователь'+((' @'+bot_user.user) if bot_user.user != None else '')+' завершил регистрацию!'
        msg += '\n\n<b>ID:</b> ' + str(bot_user.chat_id)
        msg += '\n<b>Имя:</b> ' + bot_user.name
        msg += '\n<b>Номер телефона:</b> ' + phone
        msg += '\n<b>Город:</b> ' + bot_user.city
        spec = Specialisation.objects.get(clue=bot_user.speciality)
        msg += '\n<b>Специализация:</b> ' + spec.name
        if bot_user.experience == 'less-one':
            experience = 'Менее года'
        elif bot_user.experience == 'one-three':
            experience = '1-3 года'
        elif bot_user.experience == 'more-three':
            experience = 'Более 3 лет'
        msg += '\n<b>Опыт работы:</b> ' + experience
        msg += '\n<b>Ссылка на портфолио:</b> ' + str(bot_user.portfolio_url)
        msg += '\n<b>О себе:</b> ' + bot_user.description
        if bot_user.photo_url == '-':
            res = bot.send_message(admin_id, msg, reply_markup = keyboard('approve_user', {'user': bot_user.chat_id}), parse_mode="HTML")
        else:
            res = bot.send_photo(admin_id, bot_user.photo_url, reply_markup = keyboard('approve_user', {'user': bot_user.chat_id}), caption = msg, parse_mode="HTML")
        admin[0].msg_id = res.id
        admin[0].save()
        return
