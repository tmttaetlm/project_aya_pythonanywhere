from telebot import types

def keyboard(type, params = {}):
    if type == 'start':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Согласен', callback_data = 'start_accept'))
    if type == 'customer':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('⚡️ Разместить вакансию в 1 клик'))
        keyboard.add(types.KeyboardButton('🔎 Поиск специалиста'))
        keyboard.add(types.KeyboardButton('📇 Мой аккаунт'))
        keyboard.add(types.KeyboardButton('📨 Написать админу'))
        keyboard.add(types.KeyboardButton('📰 Купить рекламу в боте'))
    if type == 'specialist':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('📇 Мой аккаунт'))
        keyboard.add(types.KeyboardButton('📨 Написать админу'))
        keyboard.add(types.KeyboardButton('📰 Купить рекламу в боте'))
    if type == 'admin':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('👤 Пользователи'))
        keyboard.add(types.KeyboardButton('📄 Объявления'))
        keyboard.add(types.KeyboardButton('👔 Неподтвержденные пользователи'))
        keyboard.add(types.KeyboardButton('📑 Неподтвержденные объявления'))
        keyboard.add(types.KeyboardButton('💬 Опубликовать сообщение'))
        keyboard.add(types.KeyboardButton('🈲 Слова-раздражители для бота'))
        keyboard.add(types.KeyboardButton('⤴️ Автопересылка объявлении'))
    if type == 'send_to_bot':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🚀 Моментально', callback_data = 'send_now'))
        keyboard.add(types.InlineKeyboardButton('🕐 В запланированное время (разово)', callback_data = 'send_on_time'))
    if type == 'phone_request':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton(text = '📱 Отправить номер телефона', request_contact = True))
        keyboard.add(types.KeyboardButton(text = '➡️ Пропустить'))
    if type == 'cities':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Неважно', callback_data = 'city_Неважно'),types.InlineKeyboardButton('Almaty', callback_data = 'city_Almaty'),types.InlineKeyboardButton('Nur-Sultan', callback_data = 'city_Nur-Sultan'))
        keyboard.row(types.InlineKeyboardButton('Shymkent', callback_data = 'city_Shymkent'),types.InlineKeyboardButton('Kyzylorda', callback_data = 'city_Kyzylorda'),types.InlineKeyboardButton('Karagandy', callback_data = 'city_Karagandy'))
        keyboard.row(types.InlineKeyboardButton('Taraz', callback_data = 'city_Taraz'),types.InlineKeyboardButton('Aktau', callback_data = 'city_Aktau'),types.InlineKeyboardButton('Atyrau', callback_data = 'city_Atyrau'))
        keyboard.row(types.InlineKeyboardButton('Aktobe', callback_data = 'city_Aktobe'),types.InlineKeyboardButton('Oral', callback_data = 'city_Oral'),types.InlineKeyboardButton('Petropavl', callback_data = 'city_Petropavl'))
        keyboard.row(types.InlineKeyboardButton('Palvodar', callback_data = 'city_Pavlodar'),types.InlineKeyboardButton('Kostanay', callback_data = 'city_Kostanay'),types.InlineKeyboardButton('Oskemen', callback_data = 'city_Oskemen'))
        keyboard.row(types.InlineKeyboardButton('Semey', callback_data = 'city_Semey'),types.InlineKeyboardButton('Taldykorgan', callback_data = 'city_Taldykorgan'),types.InlineKeyboardButton('Zhezkazgan', callback_data = 'city_Zhezkazgan'))
    if type == 'experience':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Менее года', callback_data = 'exp_less-one'))
        keyboard.add(types.InlineKeyboardButton('1-3 года', callback_data = 'exp_one-three'))
        keyboard.add(types.InlineKeyboardButton('Более 3 лет', callback_data = 'exp_more-three'))
    if type == 'speciality':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('SMM продвижение', callback_data = 'spec_SMM'), types.InlineKeyboardButton('Дизайн', callback_data = 'spec_design'))
        keyboard.add(types.InlineKeyboardButton('Модель', callback_data = 'spec_model'), types.InlineKeyboardButton('SEO оптимизация', callback_data = 'spec_SEO'))
        keyboard.add(types.InlineKeyboardButton('Маркетолог', callback_data = 'spec_marketolog'), types.InlineKeyboardButton('CRM', callback_data = 'spec_CRM'))
        keyboard.add(types.InlineKeyboardButton('Контекстная реклама', callback_data = 'spec_contextads'), types.InlineKeyboardButton('Таргетированная реклама', callback_data = 'spec_targetads'))
        keyboard.add(types.InlineKeyboardButton('Разработка сайта (конструкторы)', callback_data = 'spec_sites'), types.InlineKeyboardButton('Разработка чат-бота', callback_data = 'spec_bots'))
        keyboard.add(types.InlineKeyboardButton('Видеосъемка', callback_data = 'spec_vidoe'), types.InlineKeyboardButton('Фотосъемка', callback_data = 'spec_photo'))
        keyboard.add(types.InlineKeyboardButton('Продажи', callback_data = 'spec_sells'), types.InlineKeyboardButton('Копирайтинг/Перевод', callback_data = 'spec_translate'))
        keyboard.add(types.InlineKeyboardButton('Продюссер', callback_data = 'spec_producer'), types.InlineKeyboardButton('Сторисмейкер', callback_data = 'spec_storiesmaker'))
        keyboard.add(types.InlineKeyboardButton('Другое', callback_data = 'spec_other'))
    if type == 'approve_user':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_user_'+str(params['user'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_user_'+str(params['user'])))
    if type == 'postapprove_user':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('<< Предыдущий', callback_data = 'prev_'+str(params['prev'])), types.InlineKeyboardButton('>> Следующий', callback_data = 'next_'+str(params['next'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_user_'+str(params['user'])), types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_user_'+str(params['user'])))
    if type == 'approve_vacancy':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить в канал', callback_data = 'to_channel_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить внутрь бота', callback_data = 'to_bot_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить в канал и внутрь бота', callback_data = 'to_everywhere'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_vacancy_'+str(params['vacancy'])))
    if type == 'postapprove_vacancy':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('<< Предыдущий', callback_data = 'vprev_'+str(params['prev'])), types.InlineKeyboardButton('>> Следующий', callback_data = 'vnext_'+str(params['next'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить в канал', callback_data = 'to_channel_postfactum_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить внутрь бота', callback_data = 'to_bot_postfactum_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить и отправить в канал и внутрь бота', callback_data = 'to_everywhere_postfactum_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Отклонить', callback_data = 'reject_vacancy_'+str(params['vacancy'])))
    if type == 'approve_redirect':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_redirect_'+str(params['msg'])+'|'+str(params['chat'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Удалить', callback_data = 'reject_redirect_'+str(params['msg'])+'|'+str(params['chat'])))
    if type == 'approve_text':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm_text_'+str(params['vacancy'])))
        keyboard.add(types.InlineKeyboardButton('🚫 Удалить', callback_data = 'reject_text_'+str(params['vacancy'])))
    if type == 'who_you_are':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('🍊 Исполнитель', callback_data = 'specialist'))
        keyboard.add(types.InlineKeyboardButton('🍒 Заказчик', callback_data = 'customer'))
    if type == 'vacancy_to_bot':
        keyboard = types.InlineKeyboardMarkup()
        if params['username'] is not None:
            keyboard.add(types.InlineKeyboardButton('➡️ Написать заказчику', url = 'https://t.me/'+params['username']))
        keyboard.add(types.InlineKeyboardButton('➡️ Разместить свой заказ', url = 'https://t.me/aya_cyberbot'))
    if type == 'edit_customer_account':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('✅ Изменить имя'))
        keyboard.add(types.KeyboardButton('🏢 Изменить город'))
        keyboard.add(types.KeyboardButton('📱 Изменить номер телефона'))
        keyboard.add(types.KeyboardButton('🚮 Удалить мой аккаунт'))
        keyboard.add(types.KeyboardButton('😕 Я не Заказчик'))
        keyboard.add(types.KeyboardButton('🔙 Назад'))
    if type == 'edit_specialist_account':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('✅ Изменить имя'))
        keyboard.add(types.KeyboardButton('🏢 Изменить город'))
        keyboard.add(types.KeyboardButton('📱 Изменить номер телефона'))
        keyboard.add(types.KeyboardButton('🧰 Изменить специализацию'))
        keyboard.add(types.KeyboardButton('🗃 Изменить опыт работы'))
        keyboard.add(types.KeyboardButton('📂 Изменить ссылку портфолио'))
        keyboard.add(types.KeyboardButton('📷 Изменить фото'))
        keyboard.add(types.KeyboardButton('✌ Изменить описание о себе'))
        keyboard.add(types.KeyboardButton('🚮 Удалить мой аккаунт'))
        keyboard.add(types.KeyboardButton('😕 Я не Специалист'))
        keyboard.add(types.KeyboardButton('🔙 Назад'))
    if type == 'my_account':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        keyboard.add(types.KeyboardButton('🗂 Посмотреть аккаунт'))
        keyboard.add(types.KeyboardButton('📝 Редактировать аккаунт'))
        keyboard.add(types.KeyboardButton('🔙 Назад'))
    if type == 'chat_to_user':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('📨 '+params['button'], url = 'https://t.me/'+params['username']))
    if type == 'ads_question':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Да', callback_data = 'yes_it_is_ads_'+str(params['msg'])+'|'+str(params['chat'])), types.InlineKeyboardButton('Нет', callback_data = 'no_it_is_not_ads'))
    if type == 'remove_keyboard':
        keyboard = types.ReplyKeyboardRemove()

    return keyboard
