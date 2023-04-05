"""
Úlohy pro cvičení 3
"""

OFFSET = 5

def factorize(n: int):
    """
    Funkce rozloží číslo na prvočísla
    """
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def queen(m: int, n: int, x: int, y: int):
    """
    Vykreslí hrací plochu dámy o velikosti m * n, a dámu na souřadnicích x, y
    """
    for column in range(m):
        for row in range(n):
            if column == x and row == y:
                print("D", end=" ")
            elif column == x or row == y:
                print("*", end=" ")
            elif abs(column - x) == abs(row - y):
                print("*", end=" ")

            else:
                print(".", end=" ")

        print()

def censor_number(limit, censored):
    """
    Funkce cenzurující čísla v posloupnosti.
    """
    for i in range(limit + 1):
        if str(i).find(str(censored)) > -1:
            print("".join(["*"] * len(str(i))))
        else:
            print(str(i).replace(str(censored), "*"))


def text_analysis(path: str):
    """
    Funkce rádoby analyzující text
    """
    file = open(path, "r", encoding="utf-8-sig")
    content = file.readlines()

    letters = {}
    words = {}

    for line in content:
        line_letters = list(line.replace(" ", ""))
        line_words = list(line.split(" "))
        for line_word in line_words:
            if line_word not in words:
                words[line_word] = 0
            words[line_word] += 1

        for line_letter in line_letters:
            if line_letter not in letters:
                letters[line_letter] = 0
            letters[line_letter] += 1

    return (letters, words)


def get_words(n, m, data):
    """
    Funkce vytahá n slov s nejmenší délkou m
    """
    words_with_minimal_length = list(filter(lambda k: len(k[0]) >= m, data.items()))
    sorted_words = sorted(words_with_minimal_length, key=lambda x: x[1], reverse=True)

    print(sorted_words[:n])

def cypher(input_path, output_path):
    """
    Funkce pro zašifrování vstupního souboru
    """
    input_file = open(input_path, "r", encoding="utf-8-sig")
    output_file = open(output_path, "+a", encoding="utf-8-sig")

    content = input_file.readlines()

    for line in content:
        #cyphered.append([ord(x) + OFFSET for x in line])
        output_file.write("".join([chr(ord(x) + OFFSET) for x in line]))

    return None

def decypher(input_path, output_path):
    """
    Funkce pro dešifrování vstupního souboru
    """
    input_file = open(input_path, "r", encoding="utf-8-sig")
    output_file = open(output_path, "+a", encoding="utf-8-sig")

    content = input_file.readlines()

    for line in content:
        output_file.write("".join([chr(ord(x) - OFFSET) for x in line]))

    return None

if __name__ == "__main__":
    print(factorize(10))
    queen(20, 20, 10, 13)
    censor_number(10, 1)
    tupl = text_analysis("./data_03.txt")
    get_words(5, 10, tupl[1])
    cypher("./data_03.txt", "./cyphered.txt")
    decypher("./cyphered.txt", "./uncyphered.txt")
