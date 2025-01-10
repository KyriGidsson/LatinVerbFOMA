"""
Сбор проверочной выборки словоформ из html-таблиц и проверка на них преобразователя,
загруженного из файла latest_FST.pkl. Успешным срабатыванием преобразователя считается
наличие реальной пары "лемма + граммема" среди пар в его выдаче. Наличие "лишних" пар в выдаче
не берётся во внимание ввиду невозможности их отсеять из-за синкретизма в латинской морфологии.
Отдельно ведётся учёт полууспешных срабатываний, когда в выдаче есть искомая граммема, но неверно определена лемма.
"""

import os
import pickle
from random import shuffle
from parse import read_html
from Morphology import demacronize, remacronize, WordForm

def collect_sample(sample_size) -> list[WordForm]:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    verbdir = dir_path + '\\Verbs'
    directory = os.fsencode(verbdir)
    files = os.listdir(directory)
    counter = 0
    shuffle(files)
    sample = []
    for file in files:
        if counter == sample_size:
            break
        filename = os.fsdecode(file)
        print(filename)
        with open(f'{verbdir}\\{filename}', encoding="utf8") as fin:
            [sample.append(x) for x in read_html(fin, test=True)]
        counter += 1
    return sample

with open('latest_FST.pkl', 'rb') as inp:
    word = pickle.load(inp)

dir_path = os.path.dirname(os.path.realpath(__file__))
directory = os.fsencode(dir_path + '\\Verbs')
verbs = os.listdir(directory)

while True:
    size = input('Введите желаемый размер проверочной выборки: ')
    if size == "max":
        sample = collect_sample(len(verbs))
        break
    elif int(size) > 0 and int(size) <= len(verbs):
        sample = collect_sample(int(size))
        break
    else:
        print(f'Неверный размер; введите целое число от 1 до {len(verbs)}')

good = 0
semigood = 0
for s in sample:
    verb = demacronize(s.form)
    grammeme = s.grammeme.__repr__()
    lemma = s.lemma
    answers = []
    grams = set()
    for x in word.apply(verb):
        form, gram = x.split("\t")
        grams.add(gram.strip())
        answers.append((remacronize(form).strip(), gram.strip()))
    if (lemma, grammeme) in answers:
        good += 1
    else:
        print(s)
        print("-"*10)
        [print(a) for a in answers]
        print()
        if grammeme in grams:
            semigood += 1

print(f"Точность с учётом выявления леммы: {good / len(sample)}\nБез учёта леммы: {(good + semigood) / len(sample)}")
