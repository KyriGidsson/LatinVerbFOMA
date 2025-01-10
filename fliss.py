"""
Find Logic In String Set (FLISS) — поиск регулярного выражения, описывающего набор строк.
"""

def find_regex(strings: list[str], threshold=0.05):
    p = fliss(strings)
    if p > threshold:
        p1, prefix = trimming_fliss(strings, 'p', threshold)
        p2, suffix = trimming_fliss(strings, 's', threshold)
        return min(p1, p2), prefix + '.' + suffix
    else:
        return p, union(strings)

def trimming_fliss(strings: list[str], mode: str, threshold=0.05):
    p = 1
    while p > threshold and max(strings) != '':
        max_len = max([len(x) for x in strings])
        if mode == 'p':
            strings = [x[:max_len-1]for x in strings]
        elif mode == 's':
            strings = [x[:-max_len:-1][::-1]for x in strings]
        else:
            raise Exception("Error: no such mode for fliss")
        p = fliss(strings)
    return p, union(strings)

def fliss(strings: list[str]):
    seen = set(strings)
    p_unseen = (1 - 1 / (len(seen) + 1) ) ** len(strings)
    return p_unseen

def union(strings: list[str]):
    uniques = set(strings)
    if len(uniques) == 0:
        return ''
    elif len(uniques) == 1:
        return strings[0]
    else:
        return f'({'|'.join(uniques)})'