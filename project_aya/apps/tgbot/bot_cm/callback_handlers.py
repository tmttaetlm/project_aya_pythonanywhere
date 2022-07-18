from datetime import datetime, timezone, timedelta
from django.utils import timezone
from main.models import User, Vacancy, Message, Info, Specialisation
from .keyboards import keyboard
from .functions import registration_customer, registration_specialist, search_master, not_confirmed_users, not_confirmed_ads, check_and_delete_msg, confirm_ads

def callback(bot, callback_message):
    admin = User.objects.filter(role='Админ')
    bot_user = User.objects.get(chat_id=callback_message.from_user.id)
    messages = Message.objects.filter(clue = 'bot_msgs')

    if len(admin) == 0: admin_id = 248598993
    else: admin_id = admin[0].chat_id

    # User callbacks
    if callback_message.data == 'start_accept':
        check_and_delete_msg(bot, callback_message.from_user.id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(callback_message.from_user.id, 'Выберите кто Вы:', reply_markup = keyboard('who_you_are'))
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.step = 0
        bot_user.save()
        return
    if callback_message.data == 'customer':
        bot_user.step = 1
        bot_user.save()
        registration_customer(bot, callback_message)
        return
    if callback_message.data == 'specialist':
        bot_user.step = 1
        bot_user.save()
        registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('city_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_city', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_city':
            bot_user.city = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Город изменён.', reply_markup = keyboard('edit_customer_account') if bot_user.role == 'Заказчик' else keyboard('edit_specialist_account'))
        elif bot_user.mode.rfind('one_click_vacancy_') >= 0:
            _vacancy = Vacancy.objects.get(id=bot_user.mode[bot_user.mode.rfind('_')+1:len(bot_user.mode)])
            _vacancy.city = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
            _vacancy.save()
            check_and_delete_msg(bot, callback_message.from_user.id, bot_user.msg_id, bot_user.msg_time)
            res = bot.send_message(callback_message.from_user.id, messages[2].text.replace('br', '\n'))
            bot_user.msg_id = None
            bot_user.msg_time = None
            bot_user.step = None
            bot_user.mode = None
            bot_user.save()
            admin_msg_text = 'Пользователь'+((' @'+bot_user.user) if bot_user.user != None else '')+' (Имя: '+bot_user.name+' ID: '+str(bot_user.chat_id)+') создал объявление!'
            admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\n\nГород, куда опубликовать: '+_vacancy.city+'\nТекст:\n'+_vacancy.text
            res = bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
            admin[0].msg_id = res.id
            admin[0].msg_time = timezone.now()
            admin[0].save()
        else:
            if bot_user.role == 'Заказчик':
                bot_user.step = 4
                bot_user.save()
                registration_customer(bot, callback_message)
            elif bot_user.role == 'Исполнитель':
                bot_user.step = 4
                bot_user.save()
                registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('exp_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_exp', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_experience':
            bot_user.experience = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Опыт работы изменен.', reply_markup = keyboard('edit_specialist_account'))
        else:
            bot_user.step = 5
            bot_user.save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data.find('spec_') >= 0:
        if bot_user.mode == 'search':
            Info.objects.create(clue='sp_spec', text=callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)])
            search_master(bot, callback_message)
        elif bot_user.mode == 'edit_specialisation':
            spec = Specialisation.objects.get(clue=callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)])
            bot_user.speciality = spec.clue
            bot_user.mode = None
            bot_user.save()
            bot.send_message(callback_message.from_user.id, 'Специализация изменена.', reply_markup = keyboard('edit_specialist_account'))
        else:
            bot_user.step = 6
            bot_user.save()
            registration_specialist(bot, callback_message)
        return
    if callback_message.data == 'skip_photo':
        bot_user.step = 7
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_portfolio':
        bot_user.step = 8
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data == 'skip_description':
        bot_user.step = 9
        bot_user.save()
        registration_specialist(bot, callback_message, 1)
        return
    if callback_message.data.find('confirm_text') >= 0:
        check_and_delete_msg(bot, callback_message.from_user.id, bot_user.msg_id, bot_user.msg_time)
        res = bot.send_message(callback_message.from_user.id, 'Ваше объявление выйдет в ближайшее время!\nКофе☕️, Чай🍃, Воду? :)')
        bot_user.msg_id = res.id
        bot_user.msg_time = timezone.now()
        bot_user.save()
        _vacancy = Vacancy.objects.order_by('-id').first()
        admin_msg_text = 'Пользователь'+((' @'+bot_user.user) if bot_user.user != None else '')+' (Имя: '+bot_user.name+' ID: '+str(bot_user.chat_id)+') создал объявление!'
        admin_msg_text += '\n\nID вакансии: '+str(_vacancy.id)+'\nОписание:\n'+_vacancy.text
        bot.send_message(admin_id, admin_msg_text, reply_markup = keyboard('approve_vacancy', {'vacancy': _vacancy.id}))
    if callback_message.data.find('reject_text') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        check_and_delete_msg(bot, callback_message.from_user.id, bot_user.msg_id, bot_user.msg_time)
        bot.send_message(callback_message.from_user.id, '🚫 Вы удалили объявление. Вы можете подать его повторно.')
    #######################
    # Admin callbacks
    if callback_message.data.find('confirm_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        tmp_user = User.objects.get(chat_id=user_id)
        check_and_delete_msg(bot, user_id, tmp_user.msg_id, tmp_user.msg_time)
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        tmp_user.mode = None
        tmp_user.step = None
        tmp_user.save()
        bot.send_message(user_id, '✅ Администрация подтвердила Ваш аккаунт!', reply_markup = keyboard('customer') if tmp_user.role == 'Заказчик' else keyboard('specialist'))
        bot.send_message(admin_id, 'Аккаунт пользователя'+((' @'+tmp_user.user) if tmp_user.user != None else '')+'(Имя: '+tmp_user.name+' ID: '+user_id+') подтверждён')
        return
    if callback_message.data.find('reject_user') >= 0:
        user_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        tmp_user = User.objects.get(chat_id=user_id)
        check_and_delete_msg(bot, user_id, tmp_user.msg_id, tmp_user.msg_time)
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        tmp_user.delete()
        bot.send_message(user_id, '🚫 Администрация отклонила Ваш аккаунт! Попробуйте зарегистрироваться заново.')
        bot.send_message(admin_id, 'Аккаунт пользователя'+((' @'+tmp_user.user) if tmp_user.user != None else '')+'(Имя: '+tmp_user.name+' ID: '+user_id+') отклонён')
        return
    if callback_message.data.startswith('to_bot'):
        confirm_ads(bot, admin_id, admin, 'to_bot', callback_message)
        return
    if callback_message.data.startswith('to_channel'):
        confirm_ads(bot, admin_id, admin, 'to_channel', callback_message)
        return
    if callback_message.data.startswith('to_everywhere'):
        confirm_ads(bot, admin_id, admin, 'to_everywhere', callback_message)
        return
    if callback_message.data.find('reject_vacancy') >= 0:
        vacancy_id = callback_message.data[callback_message.data.rfind('_')+1:len(callback_message.data)]
        _vacancy = Vacancy.objects.get(id=vacancy_id)
        bot_user = User.objects.get(chat_id=_vacancy.chat_id)
        check_and_delete_msg(bot, _vacancy.chat_id, bot_user.msg_id, bot_user.msg_time)
        bot.send_message(_vacancy.chat_id, '🚫 Администрация удалила Ваше объявление с ID '+str(vacancy_id))
        bot.send_message(admin_id, 'Вы отклонили объявление с ID '+vacancy_id)
        vac = Vacancy.objects.get(id=vacancy_id)
        vac.delete()
        return
    if callback_message.data == 'send_now':
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        admin[0].msg_id = res.id
        admin[0].msg_time = timezone.now()
        admin[0].mode = 'send_now'
        admin[0].save()
        return
    if callback_message.data == 'send_on_time':
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        res = bot.send_message(admin_id, 'Отправьте текст сообщения для отправки')
        admin[0].msg_id = res.id
        admin[0].msg_time = timezone.now()
        admin[0].mode = 'send_on_time'
        admin[0].step = 1
        admin[0].save()
        Message.objects.create(clue='on_time_msg')
        return
    if callback_message.data.startswith('next_') or callback_message.data.startswith('prev_'):
        num = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
        if num != '-': not_confirmed_users(bot, num)
        return
    if callback_message.data.startswith('vnext_') or callback_message.data.startswith('vprev_'):
        num = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
        if num != '-': not_confirmed_ads(bot, num)
        return
    if callback_message.data.startswith('word_'):
        word = callback_message.data[callback_message.data.index('_')+1:len(callback_message.data)]
        if word == 'add':
            bot.edit_message_text(chat_id=admin_id, message_id=admin[0].msg_id, text='Отправьте слово-раздражитель для бота')
            admin[0].mode = 'add_word'
            admin[0].step = 1
            admin[0].save()
        return
    if callback_message.data.startswith('confirm_redirect_'):
        msg_id = callback_message.data[callback_message.data.rfind('_')+1:callback_message.data.find('|')]
        chat_id = callback_message.data[callback_message.data.find('|')+1:len(callback_message.data)]
        msg = callback_message.message.text.replace('Автор', '<b>Автор</b>')
        msg = msg.replace('Текст', '<b>Текст</b>')
        service_msg = 'Не удалось отправить сообщение следующим пользователям:'
        users = User.objects.filter(role='Исполнитель', mode=None)
        for user in users:
            try:
                bot.send_message(user.chat_id, msg, parse_mode='HTML')
            except:
                service_msg += '\n'+str(user.chat_id)+' | '+('@'+user.user if user.user is not None else '+'+user.phone)
        bot.send_message(chat_id, '✅ '+messages[3].text, reply_to_message_id=msg_id)
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        bot.send_message(admin_id, 'Вы отправили исполнителям сообщение с объявлением, пересылаемое с канала в бота.')
        if service_msg != 'Не удалось отправить сообщение следующим пользователям:':
            bot.send_message(248598993, service_msg)
        return
    if callback_message.data.startswith('reject_redirect_'):
        msg_id = callback_message.data[callback_message.data.rfind('_')+1:callback_message.data.find('|')]
        chat_id = callback_message.data[callback_message.data.find('|')+1:len(callback_message.data)]
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        bot.send_message(admin_id, 'Вы отклонили сообщение с объявлением, пересылаемое с канала в бота.')
        bot.send_message(chat_id, messages[6].text, reply_to_message_id=msg_id)
        return
    if callback_message.data.startswith('autoredirect'):
        autoredirect = Info.objects.get(clue='autoredirect_msg')
        mode = callback_message.data[callback_message.data.find('_')+1:len(callback_message.data)]
        if mode == 'on':
            autoredirect.text = '1'
            msg = 'Автопересылка объявлении включена.'
        elif mode == 'off':
            autoredirect.text = '0'
            msg = 'Автопересылка объявлении отключена.'
        autoredirect.save()
        check_and_delete_msg(bot, admin_id, admin[0].msg_id, admin[0].msg_time)
        bot.send_message(admin_id, msg)
    if callback_message.data.startswith('yes_it_is_ads'):
        msg_id = callback_message.data[callback_message.data.rfind('_')+1:callback_message.data.find('|')]
        chat_id = callback_message.data[callback_message.data.find('|')+1:len(callback_message.data)]
        msg = f'Пересылка сообщения с объявлением. \n'
        msg += '\n<b>Чат:</b> '+callback_message.message.chat.title
        if callback_message.message.chat.username is not None:
            msg += '\n<b>Ссылка на чат:</b> @'+callback_message.message.chat.username
        msg += '\n<b>Автор:</b> '+('@'+callback_message.message.reply_to_message.from_user.username if callback_message.message.reply_to_message.from_user.username is not None else callback_message.message.reply_to_message.from_user.first_name)
        msg += '\n<b>Текст:</b>\n' + callback_message.message.reply_to_message.text
        res = bot.send_message(admin_id, msg, reply_markup = keyboard('approve_redirect', {'msg': msg_id, 'chat': chat_id}), parse_mode='HTML')
        admin[0].msg_id = res.id
        admin[0].msg_time = timezone.now()
        admin[0].save()
        utc_time = datetime.fromtimestamp(callback_message.message.date, timezone.utc)
        local_time = utc_time.astimezone()
        check_and_delete_msg(bot, callback_message.message.chat.id, callback_message.message.id, local_time)
        bot.send_message(callback_message.message.chat.id, messages[4].text, reply_to_message_id=msg_id)
    if callback_message.data == 'no_it_is_not_ads':
        utc_time = datetime.fromtimestamp(callback_message.message.date, timezone.utc)
        local_time = utc_time.astimezone()
        check_and_delete_msg(bot, callback_message.message.chat.id, callback_message.message.id, local_time)
        bot.send_message(callback_message.message.chat.id, 'Простите за беспокойство.')
    ################
    #bot.answer_callback_message_query(callback_message.id)
