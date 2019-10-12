#!/usr/bin/python
from tkinter import *
from tkinter import filedialog
import os
import threading

import primes

KEY_LENGTH = 1024
THREADS = 4
BYTES_FOR_BLOCK_SIZE = 2
key_lines = None
key_type = "none"


def change_state(state):
    state_label["text"] = state
    return


def euclid_alg(e, fi):
    u = (e, 1)
    v = (fi, 0)
    while v[0] != 0:
        q = u[0] // v[0]
        t = (u[0] % v[0], u[1] - q * v[1])
        u = v
        v = t
    if u[0] != 1:
        return 0
    return u[1] % fi


def save_key(e, n, d):
    for i in ('public.key', 'private.key'):
        with open(i, "w") as key_file:
            key_file.write(str(e) + "\n")
            key_file.write(str(n) + "\n")
            if i == 'private.key':
                key_file.write(str(d))
    return


def generate_key():
    lock_all()
    change_state(u"Генерируется ключ")
    primes.get_prime_list()
    process_label["text"] = "1/2"
    p = primes.generate_prime_threads(KEY_LENGTH, THREADS)
    process_label["text"] = "2/2"
    q = primes.generate_prime_threads(KEY_LENGTH, THREADS)
    if p == -1 | q == -1:
        change_state(u"Ошибка генерации ключа")
        unlock_all()
        return
    n = p * q
    fi = (p-1) * (q - 1)
    e = 65537
    d = euclid_alg(e, fi)
    if d == 0:
        print(u"Что-то пошло не так")
    save_key(e, n, d)
    change_state(u"Ключ сгенерирован")
    process_label["text"] = ""
    unlock_all()
    return


def regenerate_key():
    with open("public.key", "w") as pub_key:
        a = pub_key.readline()
        b = pub_key.readline()
        pub_key.writelines(a)
        pub_key.writelines(b)
    change_state(u"Регененирован открытый ключ")
    return


def open_key_files():
    global key_lines
    global key_type
    if os.path.exists("private.key"):
        key_file = open("private.key")
        change_state(u"Открыт приватный ключ\nДоступно шифрование и дешифровка")
        regen_button["state"] = NORMAL
        encrypt_button["state"] = NORMAL
        decrypt_button["state"] = NORMAL
        key_lines = key_file.readlines()
        key_type = "priv"
    elif os.path.exists("public.key"):
        key_file = open("public.key")
        change_state(u"Открыт публичный ключ\nДоступно только шифрование")
        encrypt_button["state"] = NORMAL
        key_lines = key_file.readlines()
        key_type = "pub"
    else:
        change_state(u"Ключ не найден.\nОн должен лежать в папке с программой\nи называться public.key или private.key")
    return


def convert_to_int(block):
    number_string = "f"
    # Каждое число в хексе будет начинаться с одной цифры f, чтобы не потерять ведущие нули
    for letter in block:
        hex_letter = hex(letter)[2:4]
        if len(hex_letter) != 2:  # Добавляем ведущие нули
            hex_letter = "0" + hex_letter
        number_string += hex_letter
    try:
        number_int = int(number_string, 16)
    except ValueError:
        return -1
    return number_int


def convert_from_int(number_int):
    hex_block = hex(number_int)[3:]
    # отбрасываем 0xf (f - символ для защиты от потери нулей)
    if hex_block[-1:] == "L":  # в конце может оказаться символ L от слова "лонг", видимо. Убираем
        hex_block = hex_block[:-1]
    out_array = []
    for i in range(0, int(len(hex_block)/2)):
        letter_int = hex_block[i*2] + hex_block[i*2+1]
        out_array.append(int(letter_int, 16))
    return bytes(out_array)


def encrypt():
    global key_lines
    lock_all()
    change_state(u"Шифрование")
    in_file = filedialog.askopenfile(mode='rb')
    out_file_name = in_file.name + '.rsa'
    out_file = open(out_file_name, 'wb')
    size_of_block = int(int(key_lines[1]).bit_length() / 16)
    file_len = os.stat(in_file.name).st_size
    blocks = file_len / size_of_block
    i = 1
    while True:
        percent = min(round(i/blocks * 100), 100)
        # В небольших файлах на последнем шаге процент может стать больше 100.
        # В этом случае указываем 100
        process_label["text"] = str(percent) + "%"
        i += 1
        # root.update()
        block = in_file.read(size_of_block)
        if len(block) == 0:
            change_state(u"Шифрование окончено")
            in_file.close()
            out_file.close()
            break
        block_int = convert_to_int(block)
        if block_int > int(key_lines[1]):
            print(u"Странно")
        crypto = pow(block_int, int(key_lines[0]), int(key_lines[1]))
        # возводим число_строку в степень E по модулю N
        out_file.write(bytes(str(crypto) + '\n', "UTF-8"))
    unlock_all()


def decrypt():
    global key_lines
    lock_all()
    in_file = filedialog.askopenfile(mode='rb')
    change_state(u"Дешифрование")
    out_file_name = in_file.name + '.nonrsa'
    out_file = open(out_file_name, 'wb')
    blocks = sum(1 for line in open(in_file.name))  # считаем количество строк в файле
    i = 1
    while True:
        percent = min(round(i/blocks * 100), 100)
        # В небольших файлах на последнем шаге процент может стать больше 100.
        # В этом случае указываем 100
        process_label["text"] = str(percent) + "%"
        i += 1
        # root.update()
        input_str = in_file.readline()
        if len(input_str) == 0:
            in_file.close()
            out_file.close()
            change_state(u"Дешифрование окончено")
            break
        input_int = int(input_str)
        if input_int > int(key_lines[1]):
            print(u"Странно")
        output_int = pow(input_int, int(key_lines[2]), int(key_lines[1]))
        # строка в степени D по модулю N
        output_str = convert_from_int(output_int)
        out_file.write(output_str)
    unlock_all()


def unlock_all():
    generate_button["state"] = NORMAL
    open_button["state"] = NORMAL
    if key_type == "pub":
        encrypt_button["state"] = NORMAL
    if key_type == "priv":
        encrypt_button["state"] = NORMAL
        regen_button["state"] = NORMAL
        decrypt_button["state"] = NORMAL


def lock_all():
    generate_button["state"] = DISABLED
    open_button["state"] = DISABLED
    encrypt_button["state"] = DISABLED
    regen_button["state"] = DISABLED
    decrypt_button["state"] = DISABLED


def enc():
    t = threading.Thread(target=encrypt)
    t.start()


def dec():
    t = threading.Thread(target=decrypt)
    t.start()


def gen():
    t = threading.Thread(target=generate_key)
    t.start()

root = Tk()

generate_button = Button(text=u"Сгенгерировать ключи", command=gen, state=NORMAL)
open_button = Button(text=u"Открыть ключи", command=open_key_files)
regen_button = Button(text=u"Создать открытый ключ", command=regenerate_key, state=DISABLED)
encrypt_button = Button(text=u"Зашифровать...", command=enc, state=DISABLED)
decrypt_button = Button(text=u"Дешифровать...", command=dec, state=DISABLED)
state_label = Label(text=u"Состояние")
process_label = Label(text=u"Процесс")

generate_button.grid(row=0, column=0)
open_button.grid(row=1, column=0)
regen_button.grid(row=2, column=0)
encrypt_button.grid(row=1, column=1)
decrypt_button.grid(row=2, column=1)
state_label.grid(row=3, column=0)
process_label.grid(row=3, column=1)

root.mainloop()
