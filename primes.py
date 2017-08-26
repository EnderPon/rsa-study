# Набор функций для генерации простых чисел заданной длины.
import random

global_primes_list = []      # хранение списка простых чисел
CHECK_STEPS = 100            # раундов для проверки Ферма
ERATO_PRIMES = 1000          # до какого протого числа делать решето


def write_to_file():
    file = open("primes.txt", "w")
    file.write(str(ERATO_PRIMES) + "\n")
    file.writelines(str(global_primes_list))
    file.close()


def read_from_file():
    global global_primes_list
    out = []
    file = open("primes.txt", "r")
    n = file.readlines()[1]
    f = n[1:-1].split(", ")
    for i in f:
        out.append(int(i))
    global_primes_list = out


def get_prime_list():
    try:
        primes_file = open("primes.txt", "r")
        primes_in_file = primes_file.readlines()[0]
        primes_file.close()
    except(IOError, IndexError):
        print(u"Файл с простыми не найден, создаем")
        eratosthenes()
        write_to_file()
        return
    if int(primes_in_file) != ERATO_PRIMES:
        print(u"Файл найден, но чисел не столько сколько надо")
        eratosthenes()
        write_to_file()
        return
    read_from_file()


def eratosthenes():
    primes = []
    multiples = []
    for i in range(2, ERATO_PRIMES+1):
        if i not in multiples:
            primes.append(i)
            multiples.extend(range(i*i, ERATO_PRIMES+1, i))
    global global_primes_list
    global_primes_list = primes
    print(global_primes_list)


def check_with_primes(number):
    for prime in global_primes_list:
        if number % prime == 0:
            print(u"+", end='', flush=True)
            return False
    return True


def test_fermat(number):
    for i in range(CHECK_STEPS):
        a = random.randint(2, number)
        if pow(a, number-1, number) != 1:
            print(u"-", end='', flush=True)
            return False
    return True


def generate_prime(length):
    cycles = 1000000
    for i in range(cycles):
        n = random.randint(2 ** (length-1), 2 ** length)
        if check_with_primes(n) is True and test_fermat(n) is True:
            print("\n")
            # print(u"Вышло.")
            # print(n)
            # print(u"................")
            return n
    print(u"Не вышло.")
    return -1


def generate_prime_range(start, stop):
    cycles = 1000000
    for i in range(cycles):
        n = random.randint(start, stop)
        if check_with_primes(n) is True and test_fermat(n) is True:
            print("\n", flush=True)
            return n
