from classes import Token, TokenTable
from classification import classify
from funcs import can_be_in_word, can_be_in_number, number_is_correct, check_anagrams, is_substring, is_pointer


errors = {}

type_entered = False
operator_entered = False

def tokenize(text: str):

    tokens = []
    currect_line = 1
    wait_for_token_start = True
    awaited_type = None
    previous_type = None
    previous_token = None
    skip = False
    comment_type = None
    plain_pick = False
    symbol_pick = False
    current_token = ""
    in_process_of_commenting = False
   # datatype_defined = False
    #current_datatype = ""

    def deal_with_token(token, token_type, line):
        if len(token) > 0 and token != ' ':
            tokens.append([token, token_type, line])

    for index, ch in enumerate(text):

        # commenting
        if skip:
            if comment_type == 'one-line':
                if ch != '\n':
                    continue
                else:
                    skip = False
                    comment_type = None
                    continue
            elif comment_type == 'multi-line':
                if ch == '*' and index < len(text) -1 and text[index+1] == '/':
                    comment_type = None
                    skip = False
                    continue
            else:
                print("WHY SKIPPING?")

        # almost commenting
        elif in_process_of_commenting and not skip:
            if comment_type is not None:
                skip = True
            else:
                in_process_of_commenting = False
        # text literals
        elif plain_pick:
            if ch != '"' or ch == '"' and text[index-1] == '\\':
                current_token += str(ch)
            else:
                current_token += str(ch)
                plain_pick = False
                tokens.append([current_token, "const char *", currect_line])
                # awaited_type = None
                current_token = ""
                # wait_for_token_start = True
        elif symbol_pick:
            if ch != '\'' or ch == '\'' and text[index-1] == '\\':
                current_token += str(ch)
            else:
                current_token += str(ch)
                symbol_pick = False
                tokens.append([current_token, "symbol", currect_line])
                # awaited_type = None
                if len(current_token) > 4 or len(current_token) < 3 or len(current_token) == 4 and current_token[1] != '\\':
                    errors[len(errors)] = f"Error: inappropriate format of symbol: {current_token}."
                current_token = ""
                #wait_for_token_start = True

        # normal code analysis
        else:

            if ch == '#':
                if index < len(text)-1 and text[index+1].isalpha():
                    awaited_type = 'directive'
                else:
                    awaited_type = 'operator'
                current_token = "" + ch
                wait_for_token_start = False

            elif ch == '-' or ch == '+':
                if awaited_type == 'number':
                    # check mantissa or start new operator
                    if current_token[len(current_token)-1].lower() == 'e' and index<len(text)-1 and text[index+1].isdigit():
                        current_token += str(ch)
                    else:
                        deal_with_token(current_token, awaited_type, currect_line)
                        awaited_type = 'operator'
                        current_token = "" + str(ch)
                elif awaited_type == 'operator':
                    # - is a part of an operator or start of a number
                    if current_token[len(current_token)-1] == '=':
                        if index<len(text)-1 and text[index+1].isdigit():
                            deal_with_token(current_token, awaited_type, currect_line)
                            awaited_type = 'number'
                            current_token = "" + str(ch)
                        else:
                            deal_with_token(current_token, awaited_type,currect_line)
                            awaited_type = 'operator'
                            current_token = "" + str(ch)
                    else:
                        current_token += str(ch)
                elif awaited_type is None:
                    if previous_type == 'operator':
                        if index < len(text) - 1 and text[index + 1].isdigit():
                            awaited_type = 'number'
                        else:
                            awaited_type = 'operator'
                        current_token = "" + str(ch)
                    else:
                        awaited_type = 'operator'
                        current_token = "" + str(ch)
                    wait_for_token_start = False
                else:
                    deal_with_token(current_token, awaited_type,currect_line)
                    awaited_type = 'operator'
                    current_token = "" + str(ch)

            elif ch == '.' and awaited_type=='number':
                # float
                current_token += str(ch)

            elif ch == "'":
                wait_for_token_start = False
                current_token += str(ch)
                symbol_pick = True
                continue

            elif ch == '"':
                wait_for_token_start = False
                current_token += str(ch)
                plain_pick = True
                continue

            elif '0' <= ch <= '9':
                # normal separation so it's number
                if wait_for_token_start:
                    awaited_type = 'number'
                    current_token = str(ch)
                    wait_for_token_start = False
                else:
                    # digit is a part of kw or variable name or number
                    if awaited_type == 'key-or-name' or awaited_type == 'number':
                        current_token += str(ch)
                    # there was no space after operator and still a new number
                    else:
                        deal_with_token(current_token, awaited_type,currect_line)
                        current_token = "" + str(ch)
                        awaited_type = 'number'
                continue

            elif can_be_in_word(ch):
                # type or keyword or variable
                if wait_for_token_start:
                    if awaited_type == 'operator' and ch.isalpha():
                        deal_with_token(current_token, awaited_type,currect_line)
                    awaited_type = 'key-or-name'
                    current_token = "" + ch
                    wait_for_token_start = False

                else:

                    # continue token forming
                    if awaited_type == 'key-or-name' or awaited_type == 'directive' or awaited_type == 'number':
                        current_token += ch
                    # start new token
                    else:
                        deal_with_token(current_token, awaited_type,currect_line)
                        current_token = "" + ch
                        awaited_type = 'key-or-name'
                continue

            # comments
            elif ch == '/' and index < len(text) - 1 and text[index+1] == '/':
                comment_type = 'one-line'
                in_process_of_commenting = True
                deal_with_token(current_token, awaited_type,currect_line)
                current_token = ""
                awaited_type = None
                continue
            elif ch == '/' and index < len(text) - 1 and text[index+1] == '*':
                comment_type = 'multi-line'
                in_process_of_commenting = True
                deal_with_token(current_token, awaited_type,currect_line)
                current_token = ""
                awaited_type = None
                continue

            # human friendly design to end token
            elif ch == ' ' or ch == '\t' or ch == '\n':
                if ch == '\n':
                    currect_line+=1
                deal_with_token(current_token, awaited_type,currect_line)
                current_token = ""
                awaited_type = None
                continue

            # delimiters
            elif ch == ';':
                deal_with_token(current_token, awaited_type, currect_line)
                current_token = ';'
                awaited_type = 'delimiter'
                current_datatype = ""
                #deal_with_token(current_token, awaited_type);
                wait_for_token_start = True


            else:

                scobes = ['(', ')', '[', ']', '{', '}']
                # continue build operator
                if awaited_type == 'operator' and ch not in scobes and current_token not in scobes:
                    current_token += ch

                # start new operator
                else:

                    if ch == '*' and previous_type == 'data-type':
                        previous_token = previous_token + ch
                        #current_datatype = previous_token
                        current_token = "*"
                        awaited_type = 'key-or-name'
                    else:
                        deal_with_token(current_token, awaited_type,currect_line)
                        awaited_type = 'operator'
                        current_token = ch
    return tokens

'''
files = ['code1.txt']
file = open(files[0], 'r')

the_text = file.read()

tokens = tokenize(the_text)

table = classify(tokens)

itog_tokens = table.get_values()

for i, tok in enumerate(itog_tokens):
    print(f"{i+1}.\t\t{tok.name}:\t\t{tok.ttype}\t\tline: {tok.line}")

'''
