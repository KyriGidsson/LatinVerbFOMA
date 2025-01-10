"""
Классы морфологических единиц разных уровней, от набора признаков морфемы до модели спряжения.
"""

from fliss import find_regex

class Grammeme:
    """
    Набор грамматических признаков. Используется в определении морфем.
    У корневых морфем граммема состоит только из признака None.
    """
    def __init__(self, features: list[str]):
        if features:
            self.features = tuple(features)
        else:
            self.features = tuple(['None'])
    
    def __repr__(self) -> str:
        return '|'.join(self.features)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.features == other.features
        return False
    
    def __hash__(self):
        return hash(self.__repr__())
    
    def __sub__(self, other):
        return Grammeme([x for x in self.features if x not in other.features])
    
    def __and__(self, other):
        return Grammeme([x for x in self.features if x in other.features])
    
class WordForm:
    """
    Словоформа — то, как выглядит слово в конкретной грамматической роли. Тройка вида:
        форма,\n
        исходная форма (лемма),\n 
        грамматическая роль (граммема).
    """
    def __init__(self, form: str, lemma: str, grammeme: Grammeme):
        self.form = form
        self.lemma = lemma
        self.grammeme = grammeme
    
    def __repr__(self) -> str:
        return f'{remacronize(self.form)}\t{self.lemma}[{self.grammeme}]'
    
    def find_affix(self, stem: str):
        """
        Суть такова: имея словоформу типа "песок" и основу типа "пес_к_", мы едем по обеим и
        сравниваем символы, создав предварительно пустой список. Если символы совпадают, мы ничего не делаем, 
        просто едем дальше по обеим строкам. В нашем случае мы так проезжаем первые три символа, "пес". 
        Потом мы натыкаемся на "о" в словоформе и _ в основе. Значит, в словоформе мы ближайшее время будем 
        иметь дело с аффиксом. Добавляем в список пустую строку и едем в основе на следующий символ, с которым 
        будем сравнивать символы в словоформе, начиная с нынешнего. В нашем случае сравниваем "о" и "к", 
        получаем несовпадение и, соответственно, пишем "о" в последний аффикс в списке и едем дальше в словоформе. 
        Сравниваем "к" и "к" — совпадение! Значит, аффикс кончился. Кладём в список новый пустой элемент. 
        Теперь у нас в списке готовый аффикс "о" и пустая строка. Едем дальше по обеим строкам. Видим в основе 
        прочерк — значит, сейчас будет ещё один аффикс! Добавляем пустую строку в список. Пытаемся поехать дальше 
        по основе, но основа кончилась. Значит, мы выходим из этого цикла и дописываем в последний элемент списка всё, 
        что осталось в словоформе — а там ничего и не осталось. По итогу имеем список ["о", ""], который 
        и является искомым аффиксом. 
        Для сравнения, если бы мы работали со строками "пески" и "пес_к_", у нас бы получился список ["", "и"].
        Для строк "gesungen" и "_s_ng_" — ["ge", "u", "en"], для "sang" и "_s_ng_" — ["", "a", ""]
        """
        fullForm = self.form
        affix_form = []
        stem_pos = 0
        full_pos = 0
        while stem_pos < len(stem): # Едем по основе и полной форме, пока основа не кончится
            if stem[stem_pos] == '_': # Если попали на прочерк в основе, 
                affix_form.append("") # кладём в список пустую строку
                stem_pos += 1 # и едем по основе дальше
            else:
                if stem[stem_pos] == fullForm[full_pos]: # Если попали на общий символ в основе и полной форме,
                    stem_pos += 1 # едем дальше по обеим строкам
                    full_pos += 1
                else: # Если символы разнятся,
                    affix_form[-1] += fullForm[full_pos] # дописываем текущий символ словоформы в последний аффикс
                    full_pos += 1 # и едем дальше по словоформе
        for i in range(full_pos, len(fullForm)): # Дописываем в последний аффикс хвост словоформы, когда основа кончилась
            affix_form[-1] += fullForm[i]
        return Morpheme('_'.join(affix_form), self.grammeme)

class Lexeme:
    """
    Набор всех форм одного и того же слова. Формы — объекты типа WordForm, словоформы. 
    Создаётся из списка словоформ. У словоформ ожидается одна и та же лемма, иначе бросается исключение.
    """
    def __init__(self, wordforms: list[WordForm]):
        self.forms = wordforms
        self.lemma = wordforms[0].lemma
        for w in self.forms:
            if w.lemma != self.lemma:
                raise Exception(f"Wordform with alien lemma {w.lemma} detected while creating lexeme {self.lemma}!")
            w.form = demacronize(w.form)

    def extract_paradigm(self):
        from LCS import LcsFinder
        LCSFinder = LcsFinder()
        stem = LCSFinder.multi_LCS([x.form for x in self.forms])
        affixes = []
        for form in self.forms:
            affix = form.find_affix(stem)
            affixes.append(affix)
        return Paradigm(stem, affixes, self.lemma)

class Morpheme:
    """
    Морфема. Пара "форма / граммема". В основном используется для хранения словоизменительных аффиксов.
    То, что основы тоже отнесены к этому классу (с признаком isroot) — всё, что осталось
    от попыток выделять аффиксы несколько иначе, чем они выделяются в итоге.
    """
    def __init__(self, form: str, grammeme: Grammeme, isroot=False) -> None:
        self.form = form
        self.grammeme = grammeme
        self.isroot = isroot

    def __repr__(self) -> str:
        return f"{self.grammeme}: {self.form}"
    
    def __str__(self) -> str:
        if self.isroot:
            if self.grammeme.features[0] == "None":
                return f'{self.form}'
            else:
                return f'{self.form}={self.grammeme}'
        else:
            return f'{self.form} # {self.grammeme}'
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.form == other.form) and (self.grammeme == other.grammeme)
        return False
    
    def __hash__(self):
        return hash(self.grammeme)

class Paradigm:
    """Выделенная из лексемы основа и набор всех её словоизменительных аффиксов. """

    def __init__(self, stem: str, affixes: list[Morpheme], lemma: str = "") -> None:
        common = affixes[0].grammeme
        for i in range(1, len(affixes)):
            common &= affixes[i].grammeme
        local_affixes = [Morpheme(a.form, a.grammeme - common, a.isroot) for a in affixes]

        self.stem = Morpheme(form=stem, grammeme=common, isroot=True)
        self.affixes = local_affixes
        self.lemma_affix = affixes[0]
        self.lemma = lemma
        self.parts = len([x for x in stem.split("_") if x != ""])
        self.count = len(self.affixes)

    def __eq__(self, other):
        selfaf = set(self.affixes)
        otheraf = set(other.affixes)
        result = selfaf.issubset(otheraf) or otheraf.issubset(selfaf)
        return result
    
    def __repr__(self) -> str:
        affixes = '\n'.join([x.__str__() for x in self.affixes])
        return f"{self.stem} \n{affixes}"

class Model:
    """Модель словоизменения, полученная по итогу обработки парадигм."""

    def __init__(self, stems: list[Morpheme], affixes: list[Morpheme], name: str):
        self.stems = stems
        self.affixes = affixes
        self.name = name
        self.lemma = affixes[0]
        self.parts = len([x for x in self.stems[0].form.split("_") if x != ""]) 
        # ↑ by design у всех основ в модели одинаковая разрывность, так что можно проверить только первую
        self.openness = [0] * self.parts
        self.expressions = [''] * self.parts
        for i in range(self.parts):
            part_list = [stem.form.split("_")[i] for stem in self.stems]
            self.openness[i], self.expressions[i] = find_regex(part_list)
    
    @property
    def power(self): return len(self.stems)

    @property
    def size(self): return len(self.affixes)
    
    def __str__(self) -> str:
        stats = ''
        for p, regex in zip(self.openness, self.expressions):
            stats += f'{p}: {regex}\n'
        return f"{self.name}: {len(self.stems)} stems\nVariables:\n{stats}"

    def add_stem(self, stem: str):
        self.stems.append(stem)
    
    def compare_stem_parts(self):
        for i in range(self.parts):
            part_list = [stem.split("_")[i] for stem in self.stems]
            self.openness[i], self.expressions[i] = find_regex(part_list)

    def export(self, folder):
        with open(folder + '\\' + self.stems[0] + '[{}]'.format(len(self.stems)) + ".txt", "w", encoding="utf8") as fout: 
            fout.write('Paradigm type "{}":\n'.format(self.name))
            fout.write('Stems: ' + ', '.join(self.stems) + '\n\n')
            [fout.write(a.grammeme + ' # ' + a.form + '\n') for a in self.affixes]

def create_models(paradigms: list[Paradigm]):
    """
    Обобщить список парадигм до моделей спряжения.
    Суть такова: создаётся пустой список, куда мы будем складывать модели, и ещё один, куда мы будем
    складывать номера парадигм, для которых мы уже нашли модель. Бежим по списку парадигм.
    Для каждой свежевзятой парадигмы проверяем, есть ли её номер в списке обработанных. Убедившись, что 
    его там нет, создаём под неё новую модель, копируя туда аффиксы этой парадигмы
    и кладя её основу в список основ модели. Затем смотрим на все парадигмы в списке после нынешней и
    сравниваем их с нынешней, если их номеров нет в списке виденных. Если нашли совпадение, 
    добавляем в текущую модель новую основу, а в список виденных — новый номер.
    Добравшись до конца списка парадигм, кладём модель в список и берёмся за следующую парадигму.
    """
    models = []
    seen = []
    for i in range(len(paradigms)):
        if i not in seen:
            stems = [paradigms[i].stem]
            for j in range(i + 1, len(paradigms)):
                if j not in seen:
                    if paradigms[i] == paradigms[j]:
                        stems.append(paradigms[j].stem)
                        seen.append(j)
            models.append(Model(stems, paradigms[i].affixes, paradigms[i].lemma))
    return models

def demacronize(word: str):
    word = word.replace('ā', 'a-').replace('ē', 'e-').replace('ī', 'i-')
    word = word.replace('ō', 'o-').replace('ū', 'u-').replace('ȳ', 'y-')
    return word

def remacronize(word: str):
    word = word.replace('a-', 'ā').replace('e-', 'ē').replace('i-', 'ī')
    word = word.replace('o-', 'ō').replace('u-', 'ū').replace('y-', 'ȳ')
    return word