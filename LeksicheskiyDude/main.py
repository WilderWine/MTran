from classes import Token, TokenTable
from collectios import datatypes, datatypes_pieces, keywords, dividers, operators, directives, delimiters
from funcs import can_be_in_word, can_be_in_number, number_is_correct, check_anagrams, is_substring, is_pointer
const_datatypes = ["const "+datatype for datatype in datatypes]
const_datatypes.remove("const const")

type_entered = False
operator_entered = False

tt = TokenTable()
errors = {}
tokens = []

def tokenize(text: str):
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
    datatype_defined = False
    current_datatype = ""

    def deal_with_token(token, token_type):

        nonlocal wait_for_token_start
        nonlocal previous_token
        nonlocal previous_type
        nonlocal datatype_defined
        nonlocal current_datatype
        if token == "":
            return
        '''if token_type == 'number':
            if not number_is_correct(token):
                errors[len(errors)] = f"Error: Wrong number format: {token}"
            #if not tt.check_token_in_table(token):
            tt.add_token(Token(token, 'number'))
            previous_token = token
            previous_type = token_type
        elif token_type == 'operator':
            if token not in operators:
                errors[len(errors)] = f"Error: Unknown operator {token}"
            #if not tt.check_token_in_table(token):
            tt.add_token(Token(token, 'operator'))
            previous_token = token
            previous_type = token_type
        
        elif token_type == 'delimiter':
            if token == ",":
                previous_token = ","
                previous_type = 'delimiter'
            elif token == ";":
                #if not tt.check_token_in_table(token):
                tt.add_token(Token(token, 'delimiter'))
                previous_token = ";"
                previous_type = 'delimiter'
                datatype_defined = False
                current_datatype = None
       
        elif token_type == 'directive':
            if token not in directives:
                errors[len(errors)] = f"Error: Unknown directive {token}"
            #if not tt.check_token_in_table(token):
            tt.add_token(Token(token, 'operator'))
            previous_token = token
            previous_type = token_type
            pass'''
        # group other into data types, keywords, etc.
        else:
            if token in keywords:
                #if not tt.check_token_in_table(token):
                tt.add_token(Token(token, 'keyword'))
                if previous_type == 'data-type':
                    errors[len(errors)] = f"Error: name {token} matches keyword"
                    previous_type = 'variable'
                else:
                    previous_type = 'keyword'
                previous_token = token

            elif token in datatypes:
                if previous_type == 'data-type':
                    current_datatype = current_datatype+" " + token
                    previous_token = token
                else:
                    datatype_defined = True
                    previous_type = 'data-type'
                    current_datatype = token
                    previous_token = token
                    tt.add_token(Token(token, 'datadype'))


        '''elif tt.check_token_in_table(token):
                if previous_type == 'data-type':
                    errors[len(errors)] = f"Error: variable {token} is already declared"
                previous_token = token
                previous_type = 'variable'
        '''

        #else:
        if previous_token == "class":
            previous_token = token
            previous_type+ = 'data-type'
            datatypes.append(token)
            tt.add_token(Token(token, 'class-name'))
        elif previous_token == "struct":
            previous_token = token
            previous_type = 'data-type'
            datatypes.append(token)
            tt.add_token(Token(token, 'structure-name'))
        elif previous_token == "union":
            previous_token = token
            previous_type = 'data-type'
            datatypes.append(token)
            tt.add_token(Token(token, 'union-name'))
        elif previous_token == "enum":
            previous_token = token
            previous_type = 'data-type'
            datatypes.append(token)
            tt.add_token(Token(token, 'enum-name'))
        elif previous_token == ";" or previous_type is None:
            solution_found = False
            for dt in datatypes:
                if check_anagrams(token, dt):
                    errors[len(errors)] = f"Error: Unknown token {token}. Did you mean {dt}?"
                    solution_found = True
                    previous_type = 'data-type'
                    previous_token = token
                    current_datatype = token
                    break
            if not solution_found:
                for kw in keywords:
                    if check_anagrams(token, kw):
                        errors[len(errors)] = f"Error: Unknown token {token}. Did you mean {kw}?"
                        solution_found = True
                        previous_type = 'keyword'
                        previous_token = token
                        break
            if not solution_found:
                for dt in datatypes:
                    if is_substring(token, dt) or is_substring(dt,token):
                        errors[len(errors)] = f"Error: Unknown token {token}. Did you mean {dt}?"
                        solution_found = True
                        break
            if not solution_found:
                for kw in keywords:
                    if is_substring(token, kw) or is_substring(kw,token):
                        errors[len(errors)] = f"Error: Unknown token {token}. Did you mean {kw}?"
                        solution_found = True
                        break

            if not solution_found:
                errors[len(errors)] = f"Error: Undeclared variable {token}."
        elif previous_token in datatypes or previous_type == 'data-type' or previous_token == ',':
            if current_datatype not in datatypes and current_datatype not in const_datatypes:
                is_ptr = False
                for dt in datatypes:
                    if is_pointer(current_datatype, dt):
                        is_ptr = True
                        previous_type = 'variable'
                        break
                if not is_ptr:
                    previous_type = 'variable'
                    errors[len(errors)] = f"Error: Unknown datatype {token} ({current_datatype})"
            tt.add_token(Token(token, current_datatype))
            previous_token = token

        _i, _tok = tt.get_token_by_name(token)
        if _tok is not None:
            tt.table[_i].lines.add(currect_line)
        wait_for_token_start = True

        if len(token) > 0 and token != ' ':
            tokens.append(token)

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
                #if not tt.check_token_in_table(current_token):
                tt.add_token(Token(current_token, "const char *"))
                # awaited_type = None
                current_token = ""
                # wait_for_token_start = True
        elif symbol_pick:
            if ch != '\'' or ch == '\'' and text[index-1] == '\\':
                current_token += str(ch)
            else:
                current_token += str(ch)
                symbol_pick = False
                #if not tt.check_token_in_table(current_token):
                tt.add_token(Token(current_token, "symbol"))
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
                        deal_with_token(current_token, awaited_type)
                        awaited_type = 'operator'
                        current_token = "" + str(ch)
                elif awaited_type == 'operator':
                    # - is a part of an operator or start of a number
                    if current_token[len(current_token)-1] == '=':
                        if index<len(text)-1 and text[index+1].isdigit():
                            deal_with_token(current_token, awaited_type)
                            awaited_type = 'number'
                            current_token = "" + str(ch)
                        else:
                            deal_with_token(current_token, awaited_type)
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
                    deal_with_token(current_token, awaited_type)
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
                        deal_with_token(current_token, awaited_type)
                        current_token = "" + str(ch)
                        awaited_type = 'number'
                continue

            elif can_be_in_word(ch):
                # type or keyword or variable
                if wait_for_token_start:
                    if awaited_type == 'operator' and ch.isalpha():
                        deal_with_token(current_token, awaited_type)
                    awaited_type = 'key-or-name'
                    current_token = "" + ch
                    wait_for_token_start = False

                else:

                    # continue token forming
                    if awaited_type == 'key-or-name' or awaited_type == 'directive' or awaited_type == 'number':
                        current_token += ch
                    # start new token
                    else:
                        deal_with_token(current_token, awaited_type)
                        current_token = "" + ch
                        awaited_type = 'key-or-name'
                continue

            # comments
            elif ch == '/' and index < len(text) - 1 and text[index+1] == '/':
                comment_type = 'one-line'
                in_process_of_commenting = True
                deal_with_token(current_token, awaited_type)
                current_token = ""
                awaited_type = None
                continue
            elif ch == '/' and index < len(text) - 1 and text[index+1] == '*':
                comment_type = 'multi-line'
                in_process_of_commenting = True
                deal_with_token(current_token, awaited_type)
                current_token = ""
                awaited_type = None
                continue

            # human friendly design to end token
            elif ch == ' ' or ch == '\t' or ch == '\n':
                if ch == '\n':
                    currect_line+=1
                deal_with_token(current_token, awaited_type)
                current_token = ""
                awaited_type = None
                continue

            # delimiters
            elif ch == ';':
                deal_with_token(current_token, awaited_type);
                current_token = ';'
                awaited_type = 'delimiter'
                current_datatype = ""
                deal_with_token(current_token, awaited_type);
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
                        current_datatype = previous_token
                        current_token = "*"
                        awaited_type = 'key-or-name'
                    else:
                        deal_with_token(current_token, awaited_type)
                        awaited_type = 'operator'
                        current_token = ch


files = ['code1.txt']
file = open(files[0], 'r')

the_text = file.read()

tokenize(the_text)

tt.print_tokens()

print(tokens)

for key in errors.keys():
    print(f"{key + 1}.  {errors[key]}")
