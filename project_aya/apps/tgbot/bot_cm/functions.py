from django.db.models import Q
from django.conf import settings
from telebot import types
from datetime import timedelta
from django.utils import timezone
from main.models import User, Vacancy, Info, Specialisation
from .keyboards import keyboard

def not_confirmed_ads(bot, num, data=None, first_call=False):
    admin = User.objects.filter(role='Админ')
    if len(admin) == 0:
        admin_id = 248598993
        admin = User.objects.filter(chat_id=admin_id)
    else:
        admin_id = admin[0].chat_id
    _vacancy = Vacancy.objects.filter(confirmed=None).order_by('-id')
    author = User.objects.get(chat_id=_vacancy[int(num)-1].chat_id)
    postapprove_msg = Info.objects.get(clue='postapprove_ads_msg_id')
    if len(_vacancy) > 0:
        msg = f'Неподтвержденное объявление {num}/{len(_vacancy)}:'
        msg += '\n\n<b>ID вакансии:</b> '+str(_vacancy[int(num)-1].id)
        msg += '\n<b>Дата создания:</b> '+_vacancy[int(num)-1].date.strftime('%d.%m.%Y %H:%M:%S')
        msg += '\n<b>Город, куда опубликовать:</b> '+(_vacancy[int(num)-1].city if _vacancy[int(num)-1].city is not None else 'НЕ УКАЗАН')
        msg += '\n<b>Текст:</b>\n'+_vacancy[int(num)-1].text
        msg += '\n<b>Автор:</b> ' + author.name
        msg += '\n<b>ID автора:</b> ' + str(author.chat_id)
        if str(author.phone) != '-': msg += '\n<b>Номер телефона:</b> ' + '+'+str(author.phone)
        if author.user is not None: msg += '\n<b>Telegram:</b> @' + author.user
        if first_call:
            res = bot.send_message(admin_id, msg, reply_markup = keyboard('postapprove_vacancy', {'vacancy': _vacancy[int(num)-1].id, 'next': (int(num)+1) if int(num) < len(_vacancy) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')
            postapprove_msg.text = res.id
            postapprove_msg.save()
        else:
            bot.edit_message_text(chat_id=admin_id, message_id=postapprove_msg.text, text=msg, reply_markup = keyboard('postapprove_vacancy', {'vacancy': _vacancy[int(num)-1].id, 'next': (int(num)+1) if int(num) < len(_vacancy) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')
    else:
        bot.send_message(admin_id, 'Неподтвержденных объявлений не найдено.')

def not_confirmed_users(bot, num, data=None, first_call=False):
    admin = User.objects.filter(role='Админ')
    postapprove_msg = Info.objects.get(clue='postapprove_users_msg_id')
    if len(admin) == 0:
        admin_id = 248598993
        admin = User.objects.filter(chat_id=admin_id)
    else: admin_id = admin[0].chat_id
    users = User.objects.exclude(role='Админ').filter(Q(mode='registration'), Q(step=4)|Q(step=9)).order_by('-id')
    if len(users) > 0:
        phone = '+'+str(users[int(num)-1].phone) if str(users[int(num)-1].phone) != '-' else '-'
        msg = f'Неподтвержденный пользователь {num}/{len(users)}:'
        msg += '\n\n<b>ID:</b> ' + str(users[int(num)-1].chat_id)
        msg += '\n<b>Имя:</b> ' + users[int(num)-1].name
        msg += '\n<b>Роль:</b> '+users[int(num)-1].role
        msg += '\n<b>Номер телефона:</b> ' + phone
        msg += '\n<b>Город:</b> ' + users[int(num)-1].city
        if users[int(num)-1].role == 'Исполнитель':
            spec = Specialisation.objects.get(clue=users[int(num)-1].speciality)
            msg += '\n<b>Специализация:</b> ' + spec.name
            if users[int(num)-1].experience == 'less-one':
                experience = 'Менее года'
            elif users[int(num)-1].experience == 'one-three':
                experience = '1-3 года'
            elif users[int(num)-1].experience == 'more-three':
                experience = 'Более 3 лет'
            msg += '\n<b>Опыт работы:</b> ' + experience
            msg += '\n<b>Ссылка на портфолио:</b> ' + str(users[int(num)-1].portfolio_url)
            msg += '\n<b>О себе:</b> ' + users[int(num)-1].description
        msg += '\n<b>Дата регистрации:</b> '+users[int(num)-1].registration_date.strftime('%d.%m.%Y %H:%M:%S')
        if first_call:
            res = bot.send_message(admin_id, msg, reply_markup = keyboard('postapprove_user', {'user': users[int(num)-1].chat_id, 'next': (int(num)+1) if int(num) < len(users) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')
            postapprove_msg.text = res.id
            admin[0].save()
        else:
            bot.edit_message_text(chat_id=admin_id, message_id=postapprove_msg.text, text=msg, reply_markup = keyboard('postapprove_user', {'user': users[int(num)-1].chat_id, 'next': (int(num)+1) if int(num) < len(users) else '-', 'prev': (int(num)-1) if int(num) > 1 else '-'}), parse_mode='HTML')
    else:
        bot.send_message(admin_id, 'Неподтвержденных пользователей не найдено.')

def create_one_click_vacancy(bot, data):
    v = Vacancy.objects.create(chat_id=data.from_user.id, msg_id=data.id, text=data.text, date=timezone.now())
    text = 'Ваше объявление:\n\n'
    text += data.text+'\n\n'
    text += 'Выберите в группу какого города хотите опубликовать:'
    res = bot.send_message(data.from_user.id, text, reply_markup = keyboard('cities'))
    bot_user = User.objects.get(chat_id=data.from_user.id)
    bot_user.msg_id = res.id
    bot_user.msg_time = timezone.now()
    bot_user.mode = bot_user.mode + '_' + str(v.id)
    bot_user.save()

def search_master(bot, data):
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if bot_user.mode == 'search' and bot_user.step == 1:
        res = bot.send_message(data.from_user.id, 'Укажите специальность:', reply_markup = keyboard('speciality'))
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
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
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Заказчик'
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 2:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, '☺️ Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == '➡️ Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.msg_time = timezone.now()
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.msg_time = timezone.now()
                bot_user.save()
        return
    if bot_user.step == 3:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, '🏙 Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 4:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
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
        admin[0].msg_time = timezone.now()
        admin[0].save()
        return

def registration_specialist(bot, data, skip = 0):
    admin = User.objects.filter(role="Админ")
    bot_user = User.objects.get(chat_id=data.from_user.id)
    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id
    chat_id = data.from_user.id

    if bot_user.mode != 'registration': return
    if bot_user.step == 1:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, '📱 Отправьте Ваш номер телефон (необязательно)', reply_markup = keyboard('phone_request'))
        bot_user.role = 'Исполнитель'
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 2:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Как к Вам обращаться?', reply_markup = keyboard('remove_keyboard'))
        if data.text == '➡️ Пропустить':
            bot_user.phone = '-'
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        else:
            if data.contact is None:
                bot_user.msg_id = res.id
                bot_user.msg_time = timezone.now()
                bot_user.save()
            else:
                bot_user.phone = data.contact.phone_number
                bot_user.msg_id = res.id
                bot_user.msg_time = timezone.now()
                bot_user.save()
        return
    if bot_user.step == 3:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Ваш город?', reply_markup = keyboard('cities'))
        bot_user.name = data.text
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 4:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Укажите опыт работы', reply_markup = keyboard('experience'))
        bot_user.city = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 5:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Укажите специальность', reply_markup = keyboard('speciality'))
        bot_user.experience = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 6:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_photo'))
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Загрузите вашу фотография', reply_markup = t_keyboard)
        bot_user.speciality = data.data[data.data.index('_')+1:len(data.data)]
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        return
    if bot_user.step == 7:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_portfolio'))
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Отправьте ссылку на портфолио', reply_markup = t_keyboard)
        if skip:
            bot_user.photo_url = '-'
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        else:
            file = bot.get_file(data.photo[-1].file_id)
            downloaded_file = bot.download_file(file.file_path)
            with open(settings.STATIC_ROOT+'/img/user_photos/'+str(bot_user.chat_id)+'.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
                bot_user.photo_url = data.photo[-1].file_id
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        return
    if bot_user.step == 8:
        t_keyboard = types.InlineKeyboardMarkup()
        t_keyboard.add(types.InlineKeyboardButton('➡️ Пропустить', callback_data = 'skip_description'))
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Раскажите немного о себе', reply_markup = t_keyboard)
        if skip:
            bot_user.portfolio_url = '-'
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        else:
            bot_user.portfolio_url = data.text
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        return
    if bot_user.step == 9:
        check_and_delete_msg(bot, chat_id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(chat_id, 'Поздравляю с успешной регистрацией! После подтверждения администратором Вы сможете использовать функционал бота!')
        if skip:
            bot_user.description = '-'
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
            bot_user.save()
        else:
            bot_user.description = data.text
            bot_user.msg_id = res.id
            bot_user.msg_time = timezone.now()
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
        admin[0].msg_time = timezone.now()
        admin[0].save()
        return

def check_and_delete_msg(bot, chat_id, msg_id, msg_time):
    if msg_id is not None:
        if msg_time > timezone.now() - timedelta(days=3):
            try:
                bot.delete_message(chat_id, msg_id)
                msg_id = None
                msg_time = None
            except:
                bot.send_message(248598993, 'Попытка удаления сообщения '+str(msg_id)+' в чате '+str(chat_id)+' неудачна')

def confirm_ads(bot, admin_id, admin, mode, callback_message, postfactum):
    vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
    _vacancy = Vacancy.objects.get(id=vacancy_id)
    author = User.objects.get(chat_id=_vacancy.chat_id)
    service_msg = ''
    if _vacancy.text == '':
        service_msg += 'В вакансии c ID '+vacancy_id+' текст описания пустой!\n'
    if _vacancy.city is None:
        service_msg += 'В вакансии c ID '+vacancy_id+' не указан город!\n'
    if author.user is None:
        service_msg += 'Не указано имя пользователя в Telegram. Для связи будет указан номер телефона.\n'
    else:
        phone = '+'+str(author.phone) if str(author.phone) != '-' else '-'
    if mode == 'to_bot':
        users = User.objects.filter(city=_vacancy.city, role='Исполнитель')
        for usr in users:
            msg_text = '⭕️ <b>Новый Заказ</b>\n\n'
            msg_text += '▫️ <b>Описание:</b>\n'+_vacancy.text+'\n'
            msg_text += '👤 <b>Имя заказчика:</b> '+author.name+'\n'
            if _vacancy.city is not None:
                msg_text += '👤 <b>Город:</b> '+_vacancy.city+'\n'
            if author.user is not None:
                msg_text += '📨 <b>Написать автору:</b> '+author.user+'\n'
            else:
                phone = '+'+str(author.phone) if str(author.phone) != '-' else '-'
                msg_text += '📱 <b>Номер телефона:</b> '+phone+'\n'
            try:
                res = bot.send_message(usr.chat_id, msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': usr.user}), parse_mode='HTML')
            except:
                continue
                #bot.send_message(admin_id, f'Не удалось отправить сообщение пользователю @{usr.user} (ID: {usr.chat_id}, Имя: {usr.name})')
        check_and_delete_msg(bot, _vacancy.chat_id, author.msg_id, author.msg_time)
        bot.send_message(_vacancy.chat_id, '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id+'. Объявление разослано всем зарегистрированным исполнителям')
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        if postfactum:
            admin_msg = 'Вы подтвердили и отправили пользователям бота объявление с ID '+vacancy_id+'\n\nОбъявление было отправлено из списка с неподтвержденными объявлениями.'
        else:
            admin_msg = 'Вы подтвердили и отправили пользователям бота объявление с ID '+vacancy_id
        if service_msg != '':
            admin_msg += '\n\nСервисные сообщения:\n'+service_msg
        bot.send_message(admin_id, admin_msg)
    if mode == 'to_channel':
        msg_text = '⭕️ Новый Заказ\n\n'
        msg_text += '▫️ Описание:\n'+_vacancy.text+'\n\n'
        msg_text += '👤 Имя заказчика: '+author.name+'\n'
        if author.user is not None:
            msg_text += '📨 Написать автору: '+author.user+'\n'
        else:
            phone = '+'+str(author.phone) if str(author.phone) != '-' else '-'
            msg_text += '📱 Номер телефона: '+phone+'\n'
        groups = {
            'Неважно': '@kazakhstan_jumys',
            'Almaty': '@almaty_jumys',
            'Nur-Sultan': '@astana_jumys',
            'Shymkent': '@shymkent_job',
            'Kyzylorda': '@qyzylorda_job',
            'Karagandy': '@karagandy_job',
            'Taraz': '@taraz_job',
            'Aktau': '@aktau_jumys',
            'Atyrau': '@atyrau_job',
            'Aktobe': '@jobaktobe',
            'Oral': '@oral_job',
            'Petropavl': '@petropavl_job',
            'Pavlodar': '@job_pavlodar',
            'Kostanay': '@kostanay_job',
            'Oskemen': '@oskemen_job',
            'Semey': '@semey_job',
            'Taldykorgan': '@taldykorgan_jumys',
            'Zhezkazgan': '@jezkazgan_jumys'
        }
        #bot.send_message('@tmttae', msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
        res = bot.send_message(groups.get('Неважно'), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
        user_msg = '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id+'. Объявление размещено в общую группу.'
        admin_msg = 'Вы подтвердили и отправили в канал объявление с ID '+vacancy_id+'. Объявление размещено в общую группу.'
        if _vacancy.city is not None:
            res = bot.send_message(groups.get(_vacancy.city), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
            user_msg = '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id+'. Объявление размещено в общую группу и в группу, указанного вами города.'
            admin_msg = 'Вы подтвердили и отправили в канал объявление с ID '+vacancy_id+'. Объявление размещено в общую группу и в группу, указанного города.'
        else:
            service_msg += 'Объявление будет отправлено только в общую группу.\n'
        check_and_delete_msg(bot, _vacancy.chat_id, author.msg_id, author.msg_time)
        bot.send_message(_vacancy.chat_id, user_msg)
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        if postfactum:
            admin_msg += '\n\nОбъявление было отправлено из списка с неподтвержденными объявлениями.'
        if service_msg != '':
            admin_msg += '\n\nСервисные сообщения:\n'+service_msg
        bot.send_message(admin_id, admin_msg)
        _vacancy.msg_id = res.id
    if mode == 'to_everywhere':
        users = User.objects.filter(city=_vacancy.city, role='Исполнитель')
        for usr in users:
            msg_text = '⭕️ <b>Новый Заказ</b>\n\n'
            msg_text += '▫️ <b>Описание:</b>\n'+_vacancy.text+'\n'
            msg_text += '👤 <b>Имя заказчика:</b> '+author.name+'\n'
            if _vacancy.city is not None:
                msg_text += '👤 <b>Город:</b> '+_vacancy.city+'\n'
            if author.user is not None:
                msg_text += '📨 <b>Написать автору:</b> '+author.user+'\n'
            else:
                phone = '+'+str(author.phone) if str(author.phone) != '-' else '-'
                msg_text += '📱 <b>Номер телефона:</b> '+phone+'\n'
            try:
                res = bot.send_message(usr.chat_id, msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': usr.user}), parse_mode='HTML')
            except:
                continue
                #bot.send_message(admin_id, f'Не удалось отправить сообщение пользователю @{usr.user} (ID: {usr.chat_id}, Имя: {usr.name})')
        msg_text = '⭕️ Новый Заказ\n\n'
        msg_text += '▫️ Описание:\n'+_vacancy.text+'\n\n'
        msg_text += '👤 Имя заказчика: '+author.name+'\n'
        if author.user is not None:
            msg_text += '📨 Написать автору: '+author.user+'\n'
        else:
            phone = '+'+str(author.phone) if str(author.phone) != '-' else '-'
            msg_text += '📱 Номер телефона: '+phone+'\n'
        groups = {
            'Неважно': '@kazakhstan_jumys',
            'Almaty': '@almaty_jumys',
            'Nur-Sultan': '@astana_jumys',
            'Shymkent': '@shymkent_job',
            'Kyzylorda': '@qyzylorda_job',
            'Karagandy': '@karagandy_job',
            'Taraz': '@taraz_job',
            'Aktau': '@aktau_jumys',
            'Atyrau': '@atyrau_job',
            'Aktobe': '@jobaktobe',
            'Oral': '@oral_job',
            'Petropavl': '@petropavl_job',
            'Pavlodar': '@job_pavlodar',
            'Kostanay': '@kostanay_job',
            'Oskemen': '@oskemen_job',
            'Semey': '@semey_job',
            'Taldykorgan': '@taldykorgan_jumys',
            'Zhezkazgan': '@jezkazgan_jumys'
        }
        #bot.send_message('@tmttae', msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
        res = bot.send_message(groups.get('Неважно'), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
        check_and_delete_msg(bot, _vacancy.chat_id, author.msg_id, author.msg_time)
        bot.send_message(_vacancy.chat_id, '✅ Администрация подтвердила Ваше объявление с ID '+vacancy_id)
        admin_msg = 'Вы подтвердили объявление с ID '+vacancy_id+'. \nОбъявление разослано всем зарегистрированным исполнителям.\n'
        if _vacancy.city is not None:
            res = bot.send_message(groups.get(_vacancy.city), msg_text, reply_markup = keyboard('vacancy_to_bot', {'username': author.user}))
            admin_msg += 'Объявление размещено в общую группу и в группу, указанного города.\n'
        else:
            admin_msg += 'Объявление размещено в общую группу.\n'
        if postfactum:
            admin_msg += '\nОбъявление было отправлено из списка с неподтвержденными объявлениями.'
        if service_msg != '':
            admin_msg += '\n\nСервисные сообщения:\n'+service_msg
        bot.send_message(admin_id, admin_msg)
    _vacancy.confirmed = 1
    _vacancy.save()
    not_confirmed_ads(bot, 1)
