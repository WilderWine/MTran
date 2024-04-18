import regex


def can_be_in_number(ch):
    if 'a' < ch.lower() < 'f' or ch == 'x' or ch == '.' or ch == '-':
        return True
    return False


def can_be_in_word(ch):
    if 'a' <= ch.lower() <= 'z' or '0' < ch < '9' or ch == '_':
        return True
    return False


def number_is_correct(number):
    binary = r"[+-]?0b[01]+(.[01]+)?"
    hhex = r"[+-]?0x[0-9a-fA-F]+(.[0-9a-fA-F]+)?"
    ooct = r"[+-]?0[0-7]+(.[0-7]+)?"
    dec = r"[+-]?[1-9][0-9]*(.[0-9]+)?"
    dec_mantissa = r"[1-9][0-9]*[eE][+-]?[0-9]+"

    if regex.fullmatch(binary, number):
        return True, 'binary'
    elif regex.fullmatch(hhex, number):
        return True, 'hexadecimal'
    elif regex.fullmatch(ooct, number):
        return True, 'octal'
    elif regex.fullmatch(dec, number) or regex.fullmatch(dec_mantissa, number) or number == '0':
        return True, 'decimal'
    return False, None


def is_ptr(operator: str):
    ptr = r"\*+"
    if regex.fullmatch(ptr, operator):
        return True
    return False


def check_anagrams(str1, str2):
    if len(str1) != len(str2):
        return False
    sorted_str1 = sorted(str1)
    sorted_str2 = sorted(str2)
    if sorted_str1 == sorted_str2:
        return True
    else:
        return False


def is_substring(str1, str2):
    if str1 in str2:
        return True
    else:
        return False


def is_pointer(suspicious, datatype):
    if is_substring(datatype, suspicious):
        remain = suspicious.replace(datatype, "")
        if regex.fullmatch(r"\*+", remain):
            return True
    return False
