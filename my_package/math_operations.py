
# Задание 1
def main():
    s = 'hello'
    result = {}
    for i in s:
        result[i] = result.get(i, 0) + 1
    print(result)
main()

# Задание 2

def merge_dictionaries():
    d1 = {1: 150, 'b': 'Hello ', 3: 100}
    d2 = {1: 150, 'b': 'world', 3: 100}
    d = d1.copy()
    for i, p in d2.items():
        d[i] = d.get(i, 0) + p
    print(d)

merge_dictionaries()

# 3 Задание

def max1():
    d = {'BMW': 100, 'Vesta': 1292, 'Granta': 210000, 'Ferrari': 88}
    res = max(d, key=d.get)
    print(res)
max1()

# 4 Задание

def inversion():
    dictionary = {'попью': 'какавы', 'поем': 'бананы', 'вышел': 'грека'}
    inv_dictionary = {v: k for k, v in dictionary.items()}
    print(inv_dictionary)
inversion()

# 5 Задание

def sorted1():
    sample_dict = {'Мушкетеры': 3, 'Том и Джери': 2, 'Шаурма': 1, 'Иванушки Интернешенел': 4}

    sorted_dict = {}
    for key in sorted(sample_dict, key=sample_dict.get):
        sorted_dict[key] = sample_dict[key]

    print(sorted_dict)

sorted1()


# 6 Задание

def del1():
    d = {'Гранта': 106, 'Веста': 108, 'Приора': 95}

    for k, v in list(d.items()):
        if v == 95:
            d.pop(k)


    print(d)
del1()

# 7 Задание

def group1():
    text1 = "Welcome to the club body"
    res = {}

    for w in text1.split():
        res.setdefault(w[0], []).append(w)

    print(res)



group1()

# 8 Задание

def are_anagrams(str1, str2):
    return sorted(str1) == sorted(str2)
print(are_anagrams('listen','silent'))