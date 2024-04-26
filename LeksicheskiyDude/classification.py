from collectios import  (datatypes, datatypes_pieces, operators, math_operators, logic_operators, compare_operators,
                         comment_operators, bitwise_operators, math_funcs, stand_funcs, dividers, parenthesis,
                         delimiters, keywords, directives, libraries, classes, spsymbols, containers)
const_datatypes = ["const "+datatype for datatype in datatypes]
const_datatypes.remove("const const")
from funcs import number_is_correct, is_ptr
from classes import Token, TokenTable

tt = TokenTable()
errors = {}

user_funcs=[]
methods=[]
userdatatypes=[]


def classify(token_stream):
    tt = TokenTable()
    errors = {}

    user_funcs = []
    methods = []
    variables = []
    declaring_array = False


    area_stack = ['global']
    need_main_area = False
    in_procces_of_datatyping = False # true starting from first td part detected until ; symbol
    current_datatype = ""
    current_datasubtype = ""
    previous_type = ""
    previous_token = ""
    current_area = "global" # global, class, function, funcparams, main
    previous_area = ""
    funcname = ""
    classname = ""
    for i in range(len(token_stream)):
        token = token_stream[i]
        if token[1] == 'delimiter':
            if token[0] == ',':
                previous_token = ","
                previous_type = 'delimiter'
                current_datasubtype = current_datatype
                tt.add_token(Token(',', 'comma', token[2]))
                current_datasubtype = ""
            elif token[0] == ';':
                previous_token = ";"
                previous_type = 'eoc'
                current_datatype = ""
                current_datasubtype = ""
                tt.add_token(Token(';', 'eoc', token[2]))
        elif token[1] == 'directive':
            if token not in directives:
                errors[len(errors)] = f"Error: Unknown directive {token[0]}"
            tt.add_token(Token(token[0], 'directive', token[2]))
            previous_token = token[0]
            previous_type = token[1]
        elif token[1] == 'number':
            res, ss = number_is_correct(token[0])
            if not res:
                errors[len(errors)] = f"Error: Wrong number format: {token[0]}"
                exit()
            tt.add_token(Token(token[0], f'number, {ss}', token[2]))

            previous_token = token[0]
            previous_type = token[1]
        elif token[1] == 'operator':
            if token[0] not in operators and not is_ptr(token[0]):
                errors[len(errors)] = f"Error: Unknown operator {token[0]}"
            if token[0] == '=':
                tt.add_token(Token('=', 'assign', token[2]))
            elif token[0] == '*' or is_ptr(token[0]):
                if in_procces_of_datatyping and previous_token == ',' or previous_token in datatypes:
                    if is_ptr(previous_token):
                        current_datasubtype += token[0]
                        continue
                    else:
                        current_datasubtype = current_datatype + token[0]
                    continue
                elif previous_token == '?' or previous_token == '=' or previous_token == ';' or previous_token in parenthesis:
                    tt.add_token(Token(token[0], "operator, dereferencing", token[2]))
                elif token[0] == '*':
                    tt.add_token(Token(token[0], "operator, arithmetic", token[2]))
                else:
                    errors[len(errors)] = f"Error: Wrong use of pointers: {token[0]}"
            elif token[0] == '?':
                tt.add_token(Token(token[0], "operator, ternary", token[2]))
            elif token[0] in math_operators:
                tt.add_token(Token(token[0], "operator, arithmetic", token[2]))
            elif token[0] in parenthesis:

                if token[0] == '(':
                    if previous_type == 'function':
                        area_stack.append('fparams')
                        tt.add_token(Token('@fparams@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    else:
                        area_stack.append('other')
                        tt.add_token(Token(f"@other, {previous_token}@", 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    previous_area = current_area
                elif token[0] == ')' or token[0] == '}':
                    previous_area = area_stack.pop()
                    tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    tt.add_token(Token('@end@', 'area', token[2]))
                elif token[0] == '{':
                    if previous_token == ']' or previous_token == '=':
                        area_stack.append('block')
                        tt.add_token(Token('@block@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    elif previous_type == 'class-name':
                        area_stack.append('class')
                        tt.add_token(Token('@class@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    elif previous_type == 'struct-name':
                        area_stack.append('struct')
                        tt.add_token(Token('@struct@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    elif previous_type == 'union-name':
                        area_stack.append('union')
                        tt.add_token(Token('@union@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    elif previous_type == 'enum-name':
                        area_stack.append('enum')
                        tt.add_token(Token('@enum@', 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    elif previous_area == 'fparams' and previous_token == ')':
                        if need_main_area:
                            need_main_area = False
                            area_stack.append('main')
                            tt.add_token(Token('@main@', 'area', token[2]))
                            tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                        else:
                            area_stack.append('function')
                            tt.add_token(Token('@function@', 'area', token[2]))
                            tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    else:
                        area_stack.append('other')
                        tt.add_token(Token(f"@other, {previous_token}@", 'area', token[2]))
                        tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                    previous_area = current_area
                elif token[0] == '[':
                    sqsctype: str
                    if declaring_array:
                        sqsctype = "operator, parenthesis, array-declare"
                    else:
                        sqsctype = "operator, parenthesis, indexing"
                    tt.add_token(Token(token[0], sqsctype, token[2]))
                elif token[0] == ']':

                    if not (declaring_array and i < len(token_stream)- 1 and token_stream[i+1][0] == '['):
                        declaring_array = False
                    tt.add_token(Token(token[0], "operator, parenthesis", token[2]))
                if(len(area_stack) > 0):
                    current_area = area_stack[len(area_stack) -1]

            elif token[0] in logic_operators:
                tt.add_token(Token(token[0], "operator, logic", token[2]))
            elif token[0] in bitwise_operators:
                tt.add_token(Token(token[0], "operator, bitwise", token[2]))
            elif token[0] in compare_operators:
                tt.add_token(Token(token[0], "operator, compare", token[2]))
            elif token[0] in spsymbols:
                tt.add_token(Token(token[0], "operator, special", token[2]))
            else:
                tt.add_token(Token(token[0], "operator, other", token[2]))
            previous_token = token[0]
            previous_type = token[1]
        elif token[1] == 'const char *':
            tt.add_token(Token(token[0], "string", token[2]))
        elif token[1] == 'symbol':
            tt.add_token(Token(token[0], "char", token[2]))
        elif token[1] == 'key-or-name':

            if token[0] in libraries:
                tt.add_token(Token(token[0], "library", token[2]))
                previous_token = token[0]
                previous_type = 'library'
            elif token[0] in keywords or token in stand_funcs:
                if token[0] in stand_funcs:
                    if token[0] == 'main':
                        #print("I NEED MAIN")
                        need_main_area = True
                    tt.add_token(Token(token[0], "function, standart", token[2]))
                    previous_token = token[0]
                    previous_type = 'function'
                else:
                    tt.add_token(Token(token[0], "keyword", token[2]))
                    previous_token = token[0]
                    previous_type = 'keyword'
            elif token[0] in datatypes and not (i != len(token_stream)-1 and token_stream[i+1][0] == '('):
                if previous_type == 'data-type':
                    current_datatype = current_datatype + " " + token[0]
                    previous_token = current_datatype
                else:
                    previous_type = 'data-type'
                    current_datatype = token[0]
                    previous_token = token[0]
                if i != (len(token_stream) - 1) and token_stream[i + 1][0] not in datatypes:
                    tt.add_token(Token(current_datatype, 'datadype', token[2]))
            elif previous_token == "class":
                previous_token = token[0]
                previous_type = 'class-name'
                classname=token[0]
                datatypes.append(token[0])
                tt.add_token(Token(token[0], 'class-name', token[2]))
            elif previous_token == "struct":
                previous_token = token[0]
                previous_type = 'struct-name'
                classname = token[0]
                datatypes.append(token[0])
                tt.add_token(Token(token[0], 'structure-name', token[2]))
            elif previous_token == "union":
                previous_token = token[0]
                previous_type = 'union-name'
                datatypes.append(token[0])
                tt.add_token(Token(token[0], 'union-name', token[2]))
            elif previous_token == "enum":
                previous_token = token[0]
                previous_type = 'enum-name'
                datatypes.append(token[0])
                tt.add_token(Token(token[0], 'enum-name', token[2]))
            # function, method, etc.
            elif i != (len(token_stream) - 1) and token_stream[i + 1][0] == '(':
                if current_area == 'class':
                # constrctor
                    if (previous_type == 'eoc' or previous_type == 'operator') and token[0] in datatypes:
                        #print('constructor detected')
                        if previous_token == '~':
                            tt.add_token(Token(token[0], f"destructor", token[2]))
                        else:
                            tt.add_token(Token(token[0], f"constructor", token[2]))
                        previous_token = token[0]
                        previous_type = 'function'
                    # method of class
                    if previous_token in datatypes and previous_type != 'function':
                        rettype = current_datatype
                        if current_datasubtype != "":
                            rettype = current_datasubtype
                        tt.add_token(Token(token[0], f"method, {classname}, {rettype}", token[2]))
                        methods.append(token[0])
                        previous_token = token[0]
                        previous_type = 'function'
                        methods.append([token[0], classname])
                # standart
                elif token[0] in stand_funcs and token[0] not in user_funcs and previous_token not in datatypes:
                    tt.add_token(Token(token[0], f"function, standart", token[2]))
                    previous_token = token[0]
                    previous_type = 'function'
                # user-defined
                else:
                    rettype = current_datatype
                    if current_area == 'global' and previous_type == 'data-type':

                        if current_datasubtype != "":
                            rettype = current_datasubtype
                        user_funcs.append(token[0])
                        tt.add_token(Token(token[0], f"function, user, {rettype}", token[2]))
                        previous_token = token[0]
                        previous_type = 'function'
                    else:
                        if current_datasubtype != "":
                            rettype = current_datasubtype
                        if token[0] in datatypes:
                            if previous_token == '~':
                                tt.add_token(Token(token[0], f"destructor", token[2]))
                            else:
                                tt.add_token(Token(token[0], f"constructor", token[2]))
                        elif token[0] in [met[0] for met in methods] and previous_token in ['.', ',']:
                            clas = ""
                            for meth in methods:
                                if token[0] == meth[0]:
                                    clas = meth[1]

                            tt.add_token(Token(token[0], f"method, {clas}, {rettype}", token[2]))
                        else:
                            tt.add_token(Token(token[0], f"function, user, {rettype}", token[2]))
                        previous_token = token[0]
                        previous_type = 'function'
                        if token[0] not in user_funcs:
                            errors[len(errors)] = f"Error: Unknown function {token[0]}"
            # array or indexing
            elif i != (len(token_stream) - 1) and token_stream[i + 1][0] == '[':
                # array initialization
                if previous_token in datatypes:
                    vartype = current_datatype
                    if current_datasubtype != "":
                        vartype = current_datasubtype
                    tt.add_token(Token(token[0], f"array, {vartype}, declare", token[2]))
                    declaring_array = True
                else:
                    ind, tock = tt.get_token_by_name(token[0])
                    vartype = 'array, unknown'
                    if tock is not None:
                        vartype = tock.ttype
                        last_comma_index = vartype.rfind(",")
                        vartype = vartype[:last_comma_index]
                        vartype = f"{vartype}, use"
                    tt.add_token(Token(token[0], vartype, token[2]))
            # variable or poor thing that will be seen as variable
            else:
                if previous_token in datatypes or previous_token == ',' and current_datatype != "":
                    vartype = current_datatype
                    if current_datasubtype != "":
                        vartype = current_datasubtype
                    tt.add_token(Token(token[0], f"variable, {vartype}, declare", token[2]))
                else:
                    #print(f"strange thing: {token[0]}")
                    ind, tock = tt.get_token_by_name(token[0])
                    #print(f"found in tt: {tock.ttype}")
                    vartype = 'variable, unknown'
                    if tock is not None:
                        vartype = tock.ttype
                        last_comma_index = vartype.rfind(",")
                        vartype = vartype[:last_comma_index]
                    tt.add_token(Token(token[0], f"{vartype}, use", token[2]))
    print(errors)
    #tt.print_tokens()
    return tt