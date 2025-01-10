"""
Модуль с функциями для чтения и анализа языковых данных.
"""

import os
import Morphology
from bs4 import BeautifulSoup
from random import shuffle

def parse_table(table, test=False) -> Morphology.Paradigm | list[Morphology.WordForm] :
    """
    Анализ html-таблицы из Викисловаря. Логика полагается на разметку, которая принята в Викисловаре.
    Возвращает извлечённую из таблицы парадигму в нормальном режиме или 
    5% увиденных словоформ в режиме набора тестовой выборки. 
    """
    entries = []
    span_tag = table.find_all("span")
    for span in span_tag:
        gloss = ''
        if len(span['class']) > 1:
            gloss = span['class'][3].removesuffix('-form-of')
            lemma = span['class'][4].removeprefix('origin-')
            form = span.text.strip()
            entries.append(Morphology.WordForm(form, lemma, Morphology.Grammeme(gloss.split('|'))))
    
    if len(entries) > 0:
        if test:
            shuffle(entries)
            return entries[:len(entries) // 20]
        lex = Morphology.Lexeme(entries)
        par = lex.extract_paradigm()
    return par

def read_html(contents, test=False):
    """
    Чтение html-файла и поиск в нём латинской таблицы словоизменения в викисловарном формате.
    """
    soup = BeautifulSoup(contents, "html.parser")
    table_tags = soup.find_all("table", {"class": "roa-inflection-table"})
    table = 0
    for t in table_tags:
        span_tags = t.find_all('span')
        for span_tag in span_tags:
            if span_tag.has_attr('lang'):
                if span_tag['lang'] == 'la':
                    table = t
                    break
    if table != 0:
        return parse_table(table, test)
    else:
        print("Таблица глагола не найдена!")
        return None
    
def read_model(file):
    """
    Прочитать модель из текстового файла, куда её ранее экспортировали.
    """
    affixes = []
    with open (file, "r", encoding='utf8') as fin:
        lines = [line.rstrip() for line in fin]
        type_line = lines[0]
        stem_line = lines[1]
        lemma_line = lines[3]
        grammeme, form = lemma_line.split(' # ')
        name = type_line.split()[2]
        stems = stem_line.split(':')[1].split(', ')
        for line in lines[2:]:
            if ' # ' in line:
                grammeme, form = line.split(' # ')
                affixes.append(Morphology.Morpheme(form, grammeme))
    model = Morphology.Model(stems, affixes, name)
    return model

def directory_scan(sample_size: int):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    verbdir = dir_path + '\\Verbs'
    paradigms = []
    counter = 0
    directory = os.fsencode(verbdir)
    files = os.listdir(directory)
    shuffle(files)
    for file in files:
        if counter == sample_size:
            break
        filename = os.fsdecode(file)
        print(filename)
        with open(f'{verbdir}\\{filename}', encoding="utf8") as fin:
            table = read_html(fin)
        if table is not None:
            paradigms.append(table)
            counter += 1
    models = Morphology.create_models(paradigms)
    return models