"""
Модуль с классом для поиска наибольшей общей подпоследовательности в наборе строк.
"""

from numpy import zeros

class LcsFinder:
    def __init__(self):
        self.LCS = ''
        self.gap = False # контролирует, находимся ли мы в разрыве общей подпосл., чтобы поставить "_"

    def gap_on(self):
        if not self.gap:
            self.gap = True
            self.LCS += '_'
            
    def gap_off(self):
        self.gap = False

    def length(self, first, second):
        len1, len2 = len(first) + 1, len(second) + 1
        matrix = zeros((len1, len2))
        for i in range(len1-1):
            for j in range(len2-1):
                if first[i] == second[j]:
                    matrix[i+1,j+1] = matrix[i, j] + 1
                else:
                    matrix[i+1,j+1] = max(matrix[i+1, j], matrix[i, j+1])
        return matrix

    def backtrack(self, matrix, first, second, i, j):
        # print(i, first[i-1], j, second[j-1], self.gap)
        if i == 0 or j == 0:
            if i != j:
                self.gap_on()
            return ''
        elif first[i-1] == '_':
            self.gap_on()
            return self.backtrack(matrix, first, second, i-1, j)
        elif second[j-1] == '_':
            self.gap_on()
            return self.backtrack(matrix, first, second, i, j-1)
        elif first[i-1] == second[j-1]:
            self.gap_off()
            self.LCS += first[i-1]
            return self.backtrack(matrix, first, second, i-1, j-1) + first[i-1]
        elif matrix[i, j-1] > matrix[i-1, j]: # если слева больше, чем сверху
            self.gap_on()
            return self.backtrack(matrix, first, second, i, j-1) # иди влево
        self.gap_on()
        return self.backtrack(matrix, first, second, i-1, j) # иди вверх

    def pair_LCS(self, first, second):
        self.__init__()
        LCSmatrix = self.length(first, second)
        # print(LCSmatrix)
        self.backtrack(LCSmatrix, first, second, len(first), len(second))
        answer = self.LCS[::-1]
        self.LCS = ''
        return answer
    
    def reversed_LCS(self, first, second):
        return self.pair_LCS(first[::-1], second[::-1])[::-1]
    
    def compare_LCS(self, first, second):
        if first == second:
            return first
        len1, len2 = len(first) - first.count('_'), len(second) - second.count('_') 
        if len1 != len2:
            if len1 > len2:
                return first
            else:
                return second
        if first.count('_') < second.count('_'):
            return first
        if first.count('_') > second.count('_'):
            return second
        if second[-1] == '_' and first[-1] != '_':
            return second
        return first

    def multi_LCS(self, words: list[str]):
        if len(words) == 1:
            return words[0]
        else:
            lcs = self.pair_LCS(words[-2], words[-1])
            reversed_lcs = self.reversed_LCS(words[-2], words[-1])
            best_lcs = self.compare_LCS(lcs, reversed_lcs)
            new_words = words[:-2]
            new_words.append(best_lcs)
            return self.multi_LCS(new_words)