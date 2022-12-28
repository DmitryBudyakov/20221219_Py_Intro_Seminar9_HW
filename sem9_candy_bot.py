import telebot
import bot_token
from random import randint


bot = telebot.TeleBot(bot_token.token, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # msg = 'Hello! I am bot. Nice to meet you!\nType /help for more info.'
    # bot.send_message(message.chat.id, msg)
    bot.reply_to(message, f"Hi, {message.from_user.first_name}!")


@bot.message_handler(commands=['help'])
def send_help_info(message):
    msg = 'Доступные команды:\n/start\n/help\n/remove\n/game'
    bot.send_message(message.chat.id, msg)
@bot.message_handler(commands=['remove'])
def remove_words_with_string(message):
    text_all = message.text.split()
    if len(text_all) < 2:
        answer = \
f'Usage: /remove text string\n\
It will remove words from "text" included "string"'
        bot.send_message(message.chat.id, answer)
    else:
        text_init = text_all[1:-1]
        # print(text_init)
        string = text_all[-1]   #'абв'
        # print(string)
        text_new = ' '.join([word for word in text_init if string not in word])
        # print(text_new)
        text_init_msg = f"Исходный текст:\n{' '.join(text_init)}"
        bot.send_message(message.chat.id, text_init_msg)
        text_new_msg = f'Текст после обработки:\n{text_new}'
        bot.send_message(message.chat.id, text_new_msg)
        removed_msg = f'Удалены слова, содержащие "{string}"'
        bot.send_message(message.chat.id, removed_msg)


def game_init(message):
    """ Инициализация параметров игры """
    global total_qty, turn, limit_up, limit_down, user_id
    total_qty = 117
    turn = get_turn()     # определение 1-го хода: 0 - player 1,  1 - player 2
    limit_up = 28
    limit_down = 1
    user_id = message.from_user.first_name  # имя пользователя
    # print(user_id)

def game_rules():
    """ Правила игры """
    rules = \
f'--- Игра с конфетами ---\n\
Правила игры:\n\
На столе лежит {total_qty} конфет. За один ход можно забрать не более чем {limit_up} конфет. \
Побеждает тот, кто сделает последний ход.'
    return rules

def get_turn() -> int:
    """ Жребий
    0 - Player 1
    1 - Player 2 (бот)
    """
    return randint(0, 1)


def player_name(turn):
    """ имя игрока """
    global user_id
    # player = 'User'
    player = user_id
    if turn == 1:
        player = 'Bot'
    return player


@bot.message_handler(commands=['game'])
def start_candy_game(message):
    global total_qty, turn, limit_up, limit_down
    game_init(message)          # начальные параметры
    rules_msg = game_rules()    # правила игры
    bot.send_message(message.chat.id, rules_msg)
    # turn = 1
    if turn == 1:               # ход бота
        player_turn_msg = f'Ходит {player_name(turn)}'
        bot.send_message(message.chat.id, player_turn_msg)
        bot_taken = bot_action(total_qty)
        total_qty -= bot_taken
        # print(f'{player_name(turn)}: {bot_taken} {total_qty}')
        if is_game_over(total_qty): # проверка окончания игры
            winner_msg = f'Игра окончена. Победил {player_name(turn)}'
            bot.send_message(message.chat.id, winner_msg)
        else:
            bot_taken_msg = taken_candy_msg(total_qty, bot_taken, player_name(turn))
            turn = 0    # смена хода
            player_turn_msg = f'\nХодит {player_name(turn)}'
            bot_msg = bot.send_message(message.chat.id, f'{bot_taken_msg}\n{player_turn_msg}')
            bot.register_next_step_handler(bot_msg, next_action)
    else:
        # ход игрока
        player_turn_msg = f'Ходит {player_name(turn)}'
        player_msg = bot.send_message(message.chat.id, player_turn_msg)  # сообщение о ходе игрока
        bot.register_next_step_handler(player_msg, next_action)
        
        
def next_action(message):
    global total_qty, turn, limit_up, limit_down
    player_took = int(message.text)
    if is_in_limit(player_took):
        total_qty -= player_took
        # print(player_took, total_qty, turn)
        # print(f'{player_name(turn)}: {player_took} {total_qty}')
        player_taken_msg = taken_candy_msg(total_qty, player_took, player_name(turn))
        bot.send_message(message.chat.id, player_taken_msg)
        if is_game_over(total_qty): # проверка окончания игры
            winner_msg = f'Игра окончена. Победил {player_name(turn)}'
            bot.send_message(message.chat.id, winner_msg)
        else:
            # ход бота
            turn = 1
            player_turn_msg = f'Ходит {player_name(turn)}'
            bot.send_message(message.chat.id, player_turn_msg)
            bot_taken = bot_action(total_qty)
            total_qty -= bot_taken
            # print(f'{player_name(turn)}: {bot_taken} {total_qty}')
            if is_game_over(total_qty): # проверка окончания игры
                winner_msg = f'Игра окончена. Победил {player_name(turn)}'
                bot.send_message(message.chat.id, winner_msg)
            else:
                bot_taken_msg = taken_candy_msg(total_qty, bot_taken, player_name(turn))
                turn = 0    # смена хода
                player_turn_msg = f'\nХодит {player_name(turn)}'
                bot_msg = bot.send_message(message.chat.id, f'{bot_taken_msg}\n{player_turn_msg}')
                bot.register_next_step_handler(bot_msg, next_action)
    else:
        # если игрок ввел число не в разрешенных пределах
        over_limit_msg = \
f'Ошибка ввода.\n\
Взять можно от {limit_down} до {limit_up} конфет и не больше оставшихся.\n\
\nПовторите ввод.'
        repeat_msg = bot.send_message(message.chat.id, over_limit_msg)
        bot.register_next_step_handler(repeat_msg, next_action)


def is_in_limit(taken_qty):
    """ проверка лимитов по условию задачи """
    global limit_up, limit_down, total_qty
    if limit_down <= taken_qty <= limit_up and taken_qty <= total_qty:
        return True


def bot_action(total_qty: int) -> int:
    """ действие бота """
    global limit_up, limit_down
    if total_qty <= limit_up:
        bot_took = total_qty
    else:
        bot_took = randint(limit_down, limit_up)
    return bot_took


def taken_candy_msg(total_qty, take_qty, player):
    """ сообщение о взятых конфетах """
    if total_qty <= 0:
        msg = \
f'{player} взял: {take_qty}\n\
Конфет не осталось.'
    else:
        msg = \
f'{player} взял: {take_qty}\n\
Осталось: {total_qty}'
    return msg

    
def is_game_over(total_qty):
    """ проверка окончания игры """
    if total_qty <= 0:
        return True


print('Bot is running ...')

bot.infinity_polling()
