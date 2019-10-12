# Набор функций для генерации простых чисел заданной длины.
import random
import multiprocessing
import math

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
            #print(u"+", end='', flush=True)
            return False
    return True


def test_fermat(number):
    for i in range(CHECK_STEPS):
        a = random.randint(2, number)
        if pow(a, number-1, number) != 1:
            #print(u"-", end='', flush=True)
            return False
    return True

# def generate_prime_threads(len, threads):


def generate_prime(length, cycles=1000000):
    for i in range(cycles):
        n = random.randint(2 ** (length-1), 2 ** length)
        if check_with_primes(n) is True and test_fermat(n) is True:
            # print("\n")
            # print(u"Вышло.")
            # print(n)
            # print(u"................")
            return n
    # print(u"Не вышло.")
    return -1


def generate_prime_threads(length, threads_c):
    q = multiprocessing.Queue()
    a_stop_event = multiprocessing.Event()

    def generate_key_thread(length):
        while not a_stop_event.is_set():
            a = generate_prime(length, 1)
            if a > 0:
                q.put(a)
                return

    q.empty()
    a_stop_event.clear()
    threads = [multiprocessing.Process(target=generate_key_thread, args=(length,)) for i in range(threads_c)]
    for th in threads:
        th.start()
    result = q.get()
    a_stop_event.set()
    for th in threads:
        th.join()
    print("")
    pretty_print_prime(length, result)
    return result


def generate_prime_range(start, stop):
    cycles = 1000000
    for i in range(cycles):
        n = random.randint(start, stop)
        if check_with_primes(n) is True and test_fermat(n) is True:
            print("\n", flush=True)
            return n


def pretty_print_prime(length, number):
    side = math.sqrt(length)
    if not side.is_integer():
        return
    side = int(side/2)
    encoded = encodeN(number, 16)
    print("+" + "-"*side + "+")
    for i in range(side):
        print("|" + encoded[i*side:(i+1)*side] + "|")
    print("+" + "-"*int(side) + "+")



def encodeN(n,N,D="1234567890ABCDEF"):
    return (encodeN(n//N,N)+D[n%N]).lstrip("0") if n>0 else "0"
