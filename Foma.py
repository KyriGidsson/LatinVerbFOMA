"""
Ключевой модуль. Запускает сканирование папки с html-таблицами глаголов, выделяет из них модели спряжения
и создаёт на их основе конечный морфологический преобразователь, который затем сохраняется в файл latest_FST.
"""
from pyfoma import FST
from Morphology import Model
from parse import directory_scan
import os
import pickle

define = {}
dir_path = os.path.dirname(os.path.realpath(__file__))
verbdir = dir_path + '\\Verbs'
verbs = [x for x in os.listdir(verbdir)]

def from_model(model: Model):
    vars = model.expressions
    lemma = model.lemma.form.split('_')
    affixes = model.affixes
    for af in affixes:
        s = ''
        gram, form = af.grammeme, af.form.split('_')
        for i in range(len(vars)):
            s += vars[i]
            if not form[i]:
                form[i] = r"''"
            if not lemma[i]:
                lemma[i] = r"''"
            if len(vars) - i != 1:
                if form[i] != lemma[i]:
                    s += f"({form[i]}:{lemma[i]})"
                else:
                    s += f"{lemma[i]}"
            else:
                s += f"({form[i]}):({lemma[i]}'\t{gram}')"
        s = s.replace('-', r'\-')
        s = s.strip('.')
        yield(s)

def define_affix():
    while True:
        size = input('Введите желаемый размер обучающей выборки: ')
        if size == "max":
            models = directory_scan(len(verbs))
            break
        elif int(size) > 0 and int(size) <= len(verbs):
            models = directory_scan(int(size))
            break
        else:
            print(f'Неверный размер; введите целое число от 1 до {len(verbs)}')
    total_conjug = FST()
    for model in models:
        conjug = FST()
        for regex in from_model(model):
            conjug |= FST.re(regex)
            conjug = conjug.epsilon_remove().determinize().minimize()
        total_conjug |= conjug
        total_conjug = total_conjug.epsilon_remove().determinize().minimize()
        print(f"Состояний: {len(total_conjug)}...")
    return total_conjug

define['vowel'] = FST.re(r"[aeouiy]\-?")
define['cons'] = FST.re("[a-z] - $vowel", define)
define['letter'] = FST.re("$cons | $vowel", define)
define['affix'] = define_affix()
fsm = FST.re('$letter+ $affix', define)
print(f"FST готов, состояний: {len(fsm)}")

with open('latest_FST.pkl', 'wb') as outp:
    pickle.dump(fsm, outp, pickle.HIGHEST_PROTOCOL)
