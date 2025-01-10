"""
Загрузка преобразователя из файла latest_FST.pkl для проверки слов, вводимых пользователем по одному.
"""

import pickle
from Morphology import demacronize, remacronize

with open('latest_FST.pkl', 'rb') as inp:
    word = pickle.load(inp)

print("Введите что-нибудь похожее на форму латинского глагола.")
print("Долгие гласные нужно писать:")
print("\tлибо с макронами — ō, ē")
print("\tлибо с дефисами после гласных — o-, e-")
print("\tно не просто как o, e.")

while True:
    verb = demacronize(input("Мой глагол: "))
    [print(remacronize(x)) for x in word.apply(verb)]
