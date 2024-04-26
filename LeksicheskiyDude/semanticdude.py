import re
word = r'[_a-zA-Z][_a-zA-Z0-9]*'
#import token

from collectios import  (datatypes, datatypes_pieces, operators, math_operators, logic_operators, compare_operators,
                         comment_operators, bitwise_operators, math_funcs, stand_funcs, dividers, parenthesis,
                         delimiters, keywords, directives, libraries, classes, spsymbols, containers, stds)
const_datatypes = ["const "+datatype for datatype in datatypes]
const_datatypes.remove("const const")
#from funcs import number_is_correct, is_ptr
#ffrom tokenization import tokenize
#from classification import classify


from syntaxdude import *

files = ['code1.txt']
file = open(files[0], 'r')
the_text = file.read()
tokens = tokenize(the_text)
table = classify(tokens)
itog_tokens = table.get_values()
root, namespaces = tree_profound_rooting(itog_tokens)


'''def check_children(tree_root: Node):
    print(f"{tree_root.name}, {tree_root.ntype}")
    for node in tree_root.children:
        check_children(node)
    if len(tree_root.children) == 0:
        print("my vetka ended")
        curnode = tree_root
        while curnode.name!="program":
            curnode = curnode.parent
        print("my roots found")
    return


check_children(root)'''

user_functions = []
methods = []
arrays = []


def check_semantic_errors(node: Node):
    current_function = ''

    # checking function and methods redeclaration
    # same name and different arguments can exist
    # same name and same arguments - not
    if node.ntype == 'function-user-declare':
        current_function += node.name
        param_node = None
        for subnode in node.children:
            if subnode.ntype == 'function-parameters':
                param_node = subnode
        if param_node == None:
            print(f"ERROR: cannot detect function {current_function} arguments!")
            exit()
        for child in subnode.children:
            if child.ntype == 'declare':
                current_function += f" {child.datatype}"
        if current_function in user_functions:
            print(f"ERROR: user's function {current_function} already exists!")
            exit()
        user_functions.append(current_function)
        current_function = ""

    # check methods' re-declaration
    if isinstance(node.ntype, str) and node.ntype.startswith('method-') and node.ntype.endswith('-declare') or node.ntype == 'constructor-declare':
        classname: str
        if node.ntype == 'constructor-declare':
            classname = node.name
            current_function += f"{classname}"
        else:
            classname = [tok for tok in node.ntype.split('-')][1]
            current_function += f"{classname} {node.name}"
        for subnode in node.children:
            if subnode.ntype == 'function-parameters':
                param_node = subnode
        if param_node == None:
            print(f"ERROR: cannot detect method(constructor) {current_function} arguments!")
            exit()
        for child in subnode.children:
            if child.ntype == 'declare':
                current_function += f" {child.datatype}"
        if current_function in user_functions:
            print(f"ERROR: method(constructor) {current_function} already exists!")
            exit()
        methods.append(current_function)
        current_function = ""

    # check symbol
    if isinstance(node.ntype, str) and 'char' in node.ntype:
            pure_symbol = node.name[1:-1]
            if not ((len(pure_symbol) == 1) or (len(pure_symbol) == 2 and pure_symbol[0] == '\\')):
                print(f"ERROR: Wrong char value: {node.name}")

    # check char when it's number
    if isinstance(node.datatype, str) and 'char' in node.datatype:
        decimal_value = 0
        for subnode  in node.children:
            if subnode.ntype == 'assign':
                for subsubnode in subnode.children:
                    if subsubnode.ntype == 'decimal':
                        decimal_value = int(subsubnode.name)
                    elif subsubnode.ntype == 'binary':
                        decimal_value = int(subsubnode.name, 2)
                    elif subsubnode.ntype == 'hexadecimal':
                        decimal_value = int(subsubnode.name, 16)
                    elif subsubnode.ntype == 'octal':
                        decimal_value = int(subsubnode.name, 8)

        if 'unsigned' in node.datatype:
            if abs(int(decimal_value)) > 255:
                print(f"ERROR: Wrong unsigned char value: {node.name}, {decimal_value}")
        else:
            if decimal_value > 125:
                print(f"ERROR: Wrong char value: {node.name}, {decimal_value}")

    # check variable re-declarations
    if node.ntype == 'declare' or node.ntype == 'declare-array':
        variable_name = node.name
        node.marked = True

        ancestor = node
        while True:
            ancestor = ancestor.parent
            for sibling in node.parent.children:
                if (not sibling.marked) and sibling.ntype in ['declare', 'array-declare']:
                    if sibling.name == variable_name:
                        print(f"ERROR: variable with name {variable_name} already exists")
                        exit()
            if ancestor.ntype == 'root':
                node.marked = False
                break
        node.marked = False

    # define if coloning object exists and is suitable
    if node.ntype == 'operator-colon':
        # namespace detected during lab3, so check what coloning
        coloning_object = ''
        coloning_object_type = ''
        namespace = ''
        if node.parent.ntype != 'namespace':
            node.marked = True
            for i, sibling in enumerate(node.parent.children):
                if sibling.ntype == 'user-namespace' and i < len(node.parent.children)-1 and node.parent.children[i+1].marked:
                    namespace = sibling.name
                elif i > 0 and node.parent.children[i-1].marked:
                    coloning_object_type = sibling.ntype
                    coloning_object = sibling.name
            if coloning_object_type not in ['variable', 'array', f"method-{namespace}-call", f"constructor-{namespace}-call"]:
                print(f"ERROR: Wrong usage of colon: {namespace}::{coloning_object}")
                exit()
            elif coloning_object_type in ['variable', 'array']:
                class_node = node
                while class_node.ntype != 'root':
                    class_node = class_node.parent
                for bigchild in class_node.children:
                    if bigchild.ntype == 'class' and bigchild.name == namespace:
                        class_node = bigchild
                        break
                if class_node.ntype == 'root':
                    print(f"ERROR: could not find namespace: {namespace}")
                    exit()

                # variables can be ONLY public's children of a class
                found = False
                #print(f"finding {coloning_object} in {namespace}")
                for child in class_node.children:
                    if child.ntype =='class-body':
                        for grand_child in child.children:
                            if grand_child.ntype == 'access-modification' and grand_child.name == 'public':
                                for _node in grand_child.children:
                                    if _node.name == 'static':
                                        for potential in _node.children:
                                            if potential.ntype == 'declare' and potential.name == coloning_object:
                                                #print("FINALLY I FOUND U")
                                                found = True
                if not found:
                    print(f"ERROR: static variable {coloning_object} not found in class {namespace}")

    # . and ->
    if node.ntype == 'dot' or node.name == '->':
        variable_name = ''
        variable_type = ''
        node.marked = True
        for i, child in enumerate(node.parent.children):
            if child.marked:
                if i > 0 and child.parent.children[i-1].ntype == 'variable':
                    variable_name = node.parent.children[i-1].name
                else:
                    print("ERROR: Wrong usage of ->/. !")
                    node.marked = False
                    exit()
        node.marked = False
        ancestor = node
        while True:
            ancestor = ancestor.parent
            for sibling in node.parent.children:
                if sibling.ntype in ['declare', 'array-declare']:
                    if sibling.name == variable_name:
                        variable_type = sibling.datatype

            if ancestor.ntype == 'root':
                node.marked = False
                break

        temptype = variable_type.replace("*", "")
        #print(f"ff{temptype in namespaces} '{variable_type}'")
        if variable_name == '' or variable_type == '' or temptype not in namespaces:
            print("ERROR: wrong usage of ->/.!")

        if '*' not in variable_type and node.name == '->':
            print(f"ERROR: (->) variable {variable_name} is not {variable_type} pointer")
            exit()
        elif '*' in variable_type and node.ntype == 'dot':
            print(f"ERROR: (.) variable {variable_name} is {variable_type} pointer, must use -> operator")
            exit()

    # check if arguments are correct (user-functions):
    if node.ntype == 'function-user-call':
        func_name = node.name
        param_node = node
        for child in node.children:
            if child.ntype == 'function-parameters':
                param_node = child
        for child in param_node.children:
            if child.ntype in ['decimal', 'octal', 'binary', 'hexadecimal']:
                if '.' in child.name:
                    func_name += ' float'
                else:
                    func_name += ' int'
            elif child.ntype == 'char':
                func_name += ' char'
            elif child.ntype == 'string':
                func_name += 'string'
            elif child.ntype == 'variable':
                ancestor = child
                found = False
                while not found:
                    ancestor = ancestor.parent
                    for sibling in ancestor.children:
                        if sibling.ntype == 'declare':
                            if sibling.name == child.name:
                                func_name += ' ' + sibling.datatype
                                found = True
                                break
                    if ancestor.ntype == 'root' and not found:
                        print(f"ERROR: undeclared variable in function arguments: {child.name}")
                        exit()
            elif child.ntype == 'array':
                ancestor = child
                found = False
                while not found:
                    ancestor = ancestor.parent
                    for i, sibling in enumerate(ancestor.children):
                        if sibling.ntype == 'declare-array':
                            if sibling.name == child.name:
                                func_name += ' ' + sibling.datatype
                                found = True
                                if i < len(ancestor.children) - 1 and ancestor.children[i + 1].ntype == 'array-size':
                                    func_name += '*' * len(ancestor.children[i + 1].children)

                                found = True
                        if found:
                            break
                    if ancestor.ntype == 'root' and not found:
                        print(f"ERROR: could not find {child.name} declaration")
                        exit()
            elif child.ntype == 'function-standart-call':
                func_name += ' any'
            elif child.ntype == 'function-user-call':
                ancestor = child
                found = False
                while not found:
                    ancestor = ancestor.parent
                    for i, sibling in enumerate(ancestor.children):
                        if sibling.ntype == 'function-user-declare':
                            if sibling.name == child.name:
                                func_name += ' ' + sibling.datatype
                                found = True

                                break
                    if ancestor.ntype == 'root' and not found:
                        print(f"ERROR: could not find {child.name} declaration")
                        exit()

        matched = False
        func_name = func_name.replace('long', '').replace('short', '').replace('signed', '').replace('unsigned',
                                                                                                     '').replace(
            'double', 'float')
        func_name = re.sub(r"\s+", " ", func_name)
        for f in user_functions:
            f = f.replace('long', '').replace('short', '').replace('signed', '').replace('unsigned',
                                                                                                         '').replace(
                'double', 'float')
            f = re.sub(r"\s+", " ", f)
            #print(func_name == f)
            fname = func_name.split(' ')
            f = f.split(' ')

            all_good = True
            if len(f) != len(fname):
                continue
            for i in range(len(f)):
                if fname[i] == 'any' or f[i] == 'float' and fname[i] == 'int' or f[i] == 'fname':
                    all_good = True
                else:
                    all_good = False
            if all_good:
                matched = True
                break
        if not matched:
            print(f"ERROR: Wrong parameters '{func_name}' for function '{f}'")
            exit()

    #check if array indexing is ok
    if node.ntype == 'indexing':
        arr_name = ''
        node.marked = True
        for i, child in enumerate(node.parent.children):
           # print(child.marked, node.parent.children[i].ntype)
            if child.marked and i > 0 and node.parent.children[i-1].ntype == 'array':
                arr_name = node.parent.children[i-1].name
                break
        node.marked=False
        if arr_name != '':
            pass
        else:
            return
        i_arr = []

        for child in node.children:
            if child.ntype == 'decimal':
                i_arr.append( int(child.name))
            elif child.ntype == 'binary':
                i_arr.append( int(child.name),2)
            elif child.ntype == 'hexadecimal':
                i_arr.append( int(child.name),16)
            elif child.ntype == 'octal':
                i_arr.append( int(child.name),8)
            elif child.ntype == 'variable' or isinstance(child.ntype, str) and child.ntype.endswith('-call'):
                i_arr.append('any')
            else:
                print("ERROR: wrong indexing trial!")
                exit()
        #print(i_arr)
        ancestor = node
        found = False
        while not found:
            ancestor = ancestor.parent
            for i, child in enumerate(ancestor.children):
                if child.ntype == 'declare-array' and child.name == arr_name:
                    ancestor = ancestor.children[i+1]
                    found = True
                    break
            if not found and ancestor.ntype == 'root':
                print(f"ERROR: Did not found array {fname} declaration!")
                exit()
        if ancestor.ntype != 'array-size':
            print("ERROR: Grabbed wrong node!")
            exit()
        d_arr = []
        for child in ancestor.children:
            if child.ntype == 'decimal':
                d_arr.append(int(child.name))
            elif child.ntype == 'binary':
                d_arr.append(int(child.name), 2)
            elif child.ntype == 'hexadecimal':
                d_arr.append(int(child.name), 16)
            elif child.ntype == 'octal':
                d_arr.append(int(child.name), 8)
            elif child.ntype == 'variable' or isinstance(child.ntype) and child.ntype.endswith('-call'):
                d_arr.append('any')
            else:
                print("ERROR: wrong array sizing trial!")
                exit()
        # compare indexing
        if len(i_arr)>len(d_arr):
            print(f"ERROR: Wrong indexing: {arr_name} has {len(d_arr)} dimensions, not {len(i_arr)}!")
            exit()
        else:

            for i in range(len(i_arr)):
                if i_arr[i] == 'any' or d_arr[i] == 'any':
                    continue
                elif 0 <= i_arr[i] < d_arr[i]:
                    continue
                else:
                    print(f"ERROR: Wrong index {i}: max = {d_arr[i]-1}, actual: {i_arr[i]}")


    for child in node.children:
        check_semantic_errors(child)


check_semantic_errors(root)
print('\n\n\n')














