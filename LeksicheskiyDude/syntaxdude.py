import regex
word = r'[_a-zA-Z][_a-zA-Z0-9]*'
#import token

from collectios import  (datatypes, datatypes_pieces, operators, math_operators, logic_operators, compare_operators,
                         comment_operators, bitwise_operators, math_funcs, stand_funcs, dividers, parenthesis,
                         delimiters, keywords, directives, libraries, classes, spsymbols, containers, stds)
const_datatypes = ["const "+datatype for datatype in datatypes]
const_datatypes.remove("const const")
from funcs import number_is_correct, is_ptr
from classes import Token, TokenTable
from tokenization import tokenize
from classification import classify


# Base node structure
class Node:
    def __init__(self, name, ntype, datatype=None, array_in=None, parent=None, children=None):
        self.name = name
        self.ntype = ntype
        self.datatype = datatype
        self.array_in = array_in
        self.parent = parent
        self.children = children if children is not None else []
        self.marked = False

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def get_last_child(self):
        if self.children:
            return self.children[-1]
        else:
            return None

    def display(self, level=0):
        indent = "|\t" * level
        treeview = ""
        if self.datatype is not None and self.array_in is not None:
            treeview += f"{indent}|—— {self.ntype}: {self.datatype} {self.name}[{self.array_in}]\n"
        if self.datatype is None and self.array_in is None:
            treeview += f"{indent}|—— {self.ntype}: {self.name}\n"
        elif self.array_in is None:
            treeview += f"{indent}|—— {self.ntype}: {self.datatype} {self.name}\n"
        elif self.datatype is None:
            treeview += f"{indent}|—— {self.ntype}: {self.name}[{self.array_in}]\n"
        for child in self.children:
            treeview += child.display(level + 1)
        return treeview


# node specifications
class NodeDirective(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeStatement(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeClass(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeStructure(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeUnion(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeEnum(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeArray(Node):
    def __init__(self, datatype: None, name, array_in: []):
        if datatype is not None:
            super().__init__(f"{datatype} {name}[{array_in}]", "array")
        else:
            super().__init__(f"{name}[{array_in}]", "array")
        self.datatype = datatype
        self.name = name
        self.size = array_in

    def display(self, level=0):
        indent = "|   " * level
        if self.datatype is not None:
            print(f"{indent}|—— array: {self.datatype} {self.name}[{self.size}]")
        else:
            print(f"{indent}|—— array: {self.name}[{self.size}]")


class VariableNode(Node):
    def __init__(self, datatype: None, name):
        if datatype is not None:
            super().__init__(f"{datatype} {name}", "declaration")
        else:
            super().__init__(f"{name}", "variable")
        self.data_type = datatype
        self.name = name

    def display(self, level=0):
        indent = "|   " * level
        if self.data_type:
            print(f"{indent}|—— declaration: {self.datatype} {self.name}")
        else:
            print(f"{indent}|—— variable: {self.name}")


class NodeCompare(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeAssign(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeValue(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeFor(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeWhile(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeIf(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


class NodeElif(Node):
    def __init__(self, name, ntype):
        super().__init__(name, ntype)


# epic lab requires epic names
def tree_profound_rooting(tokens):
    tokens = [[tok.name, tok.ttype, tok.line] for tok in tokens]
    current_area = "global"
    previous_token = ""
    previous_type = ""
    current_class = ""
    current_class_methods = []

    declare_stack=[]
    angles_spare_stack = []
    scobes_stack = []
    namespaces = []

    # will be used to identify if its variable declaration or usage
    declaration_expected = False
    need_return = False
    declaring = False
    assigning = False
    including = False
    std_option = False
    must_count_angles = False
    scobe_check = True
    static_declaration = False

    # for areas like other
    last_block_reason = ""
    last_area = ""

    # identifying root
    root = Node("program", "root")
    current_node = root


    # to return back to parent node
    nodes_stack = [root]
    areas_stack = [current_area]

    # token[0] - value / area
    # token[1] - type of token
    # token[2] - line in code text
    for i, token in enumerate(tokens):

        ''' if (i > 0 and previous_token == 'namespace' and token[0] != 'std':
            if token[0] not in namespaces: 
                namespaces.append(token[0])
            elif nodes_stack[-1].ntype !='''

        if scobe_check:
            if token[0] in ['(', '[', '{']:
                scobes_stack.append(token[0])
            elif token[0] in [')', '}', ']'] and len(scobes_stack) == 0:
                scobe_check = False
                print(f"ERROR: Odd closing scobe {token[0]}, line {token[2]}")
                exit()
            elif token[0] in [')', '}', ']'] and len(scobes_stack) != 0:
                opening_scobe = scobes_stack.pop()
                if token[0] == ')' and opening_scobe != '(' or token[0] == '}' and opening_scobe != '{' or token[0] == ']' and opening_scobe != '[':
                    scobe_check = False
                    print(f"ERROR: Wrong closing scobe '{token[0]}' for opening '{opening_scobe}', line {token[2]}")
                    exit()
        if token[1] == 'datadype':
            if previous_token not in ['(', ';', '{', ':', ',', 'const', '', 'volatile', 'extern', 'static'] and not previous_token.startswith('@') :
                if not (i < len(tokens) -1 and token[0] in namespaces and tokens[i+1][0] == '::'):
                    print(f"ERROR: Unexpected declaration, line {token[2]}")
                    exit()
            if token[0] in namespaces:
                if i < len(tokens) - 1 and tokens[i + 1][0] == '::':
                    node_class = NodeClass(token[0], 'user-namespace')
                    current_node.add_child(node_class)
                    node_class.parent = current_node
                if i < len(tokens) - 1 and tokens[i + 1][0] == '(':
                    node_constructor= Node(token[0], f"constructor-{token[0]}-call")
                    current_node.add_child(node_constructor)
                    nodes_stack.append(current_node)
                    node_constructor.parent = current_node
                    current_node = node_constructor

        if (token[1].startswith('variable') or token[1].startswith('array')) and (previous_type.startswith('variable') or previous_type.startswith('array')):
            print(f"ERROR: incorrect use of variables: {previous_token}, {token[0]}, line {token[2]}")
            exit()

        # dealing with areas inside tokens
        if token[1] == 'area':
            area_type = [at.strip() for at in token[0][1:-1].split(',')]
            if area_type[0] == 'end':
                last_area = areas_stack.pop()
                if last_area == 'class':
                    current_class = ""
                    current_class_methods = []
                current_area = areas_stack[-1]
            elif area_type[0] == 'class':
                areas_stack.append('class')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'struct':
                areas_stack.append('struct')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'enum':
                areas_stack.append('enum')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'enum':
                areas_stack.append('enum')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'main':
                areas_stack.append('main')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'fparams':
                areas_stack.append('fparams')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'function':
                areas_stack.append('function')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'block':
                areas_stack.append('block')
                last_area = current_area
                current_area = areas_stack[-1]
            elif area_type[0] == 'other':
                # with normal syntax {}-body after ] or )
                if area_type[1] in ['if', 'for', 'while', 'switch']:
                    areas_stack.append('condition')
                    last_area = current_area
                    current_area = areas_stack[-1]
                elif area_type[1] in parenthesis:
                    areas_stack.append('body')
                    last_area = current_area
                    current_area = areas_stack[-1]
                else:
                    areas_stack.append('other')
                    last_area = current_area
                    current_area = areas_stack[-1]
        elif token[0] in directives:
            node_directive = NodeDirective(token[0], 'directive')
            node_directive.parent = current_node
            current_node.add_child(node_directive)
            nodes_stack.append(current_node)
            current_node = node_directive
        elif token[1] == 'library':
            library_node = Node(token[0], 'library', parent=current_node)
            if token[0] == 'iostream':
                namespaces.append('std')
            current_node.add_child(library_node)
        elif token[1] == 'class-name':
           # if not (i < len (tokens) -1 and tokens[i+1][0] == '::'):
            namespaces.append(token[0])
            classes.append(token[0])
            node_class = NodeClass(token[0], 'class')
            current_node.add_child(node_class)
            node_class.parent=current_node
            nodes_stack.append(current_node)
            current_node = node_class
            current_class = token[0]
        elif token[1] == 'structure-name':
            namespaces.append(token[0])
            node_struct = NodeClass(token[0], 'structure')
            node_struct.parent = current_node
            current_node.add_child(node_struct)
            nodes_stack.append(current_node)
            current_node = node_struct
        elif token[1] == 'union-name':
            node_union = NodeUnion(token[0], 'union')
            node_union.parent = current_node
            current_node.add_child(node_union)
            nodes_stack.append(current_node)
            current_node = node_union
        elif token[1] == 'enum-name':
            node_enum = NodeEnum(token[0], 'enum')
            node_enum.parent = current_node
            current_node.add_child(node_enum)
            nodes_stack.append(current_node)
            current_node = node_enum

        # functions, methods, etc.
        # if area
        elif token[1].startswith('function'):
            node_func = None
            func_origin = [fd.strip() for fd in token[1].split(',')][1]
            func_ret_type = 'any'
            if func_origin == 'user':
                func_ret_type = [fd.strip() for fd in token[1].split(',')][2]
            if current_area == 'global':
                # function declaration
                node_func = Node(token[0], f"function-{func_origin}-declare", datatype=func_ret_type)
                if func_origin != 'user' and token[0] != 'main':
                    # standart function redeclaration
                    print(f"ERROR: Standart function {token[0]} redeclaration, line {token[2]}")
                    exit()
            else:
                node_func = Node(token[0], f"function-{func_origin}-call")
            current_node.add_child(node_func)
            node_func.parent = current_node
            nodes_stack.append(current_node)
            current_node = node_func
        elif token[1].startswith('method'):
            node_method=None

            if current_area == 'class':
                method_origin = [fd.strip() for fd in token[1].split(',')][1]
                if method_origin == current_class and token[0] not in current_class_methods:
                    # declaration
                    node_method = Node(token[0], f"method-{method_origin}-declare")
                else:
                    if previous_token not in ['.', '->'] :
                        print(f"ERROR: Inappropriate call of class method, line {token[2]}")
                    node_method = Node(token[0], f"method-{method_origin}-call")
            else:
                if previous_token not in ['.', '->']:
                    print(f"ERROR: Inappropriate call of class method, line {token[2]}")
                node_method = Node(token[0], f"method-{method_origin}-call")
            node_method.parent = current_node
            current_node.add_child(node_method)
            nodes_stack.append(current_node)
            current_node = node_method
        elif token[1] == 'constructor':
            if current_area == 'class' and token[0] == current_class:
                # declaration
                node_constructor = Node(token[0], 'constructor-declare')
            else:
                node_constructor = Node(token[0], 'constructor-call')
            current_node.add_child(node_constructor)
            nodes_stack.append(current_node)
            node_constructor.parent = current_node
            current_node = node_constructor
        elif token[1] == 'destructor':
            if current_area == 'class' and token[0] == current_class:
                node_destructor = Node(token[0], 'destructor-declare')
            else:
                node_destructor = Node(token[0], 'destructor-call')
            current_node.add_child(node_destructor)
            node_destructor.parent = current_node
            nodes_stack.append(current_node)
            current_node = node_destructor
                # call

        # some keywords
        elif token[0] == 'if':
            node_if = NodeIf(token[0], 'if-block')
            current_node.add_child(node_if)
            node_if.parent = current_node
            #nodes_stack.append(current_node)
            #current_node = node_if
        elif token[0] == 'else':
            node_else = NodeElif(token[0], 'if-else-block')
            current_node.add_child(node_else)
            node_else.parent = current_node
            #nodes_stack.append(current_node)
            #current_node = node_else
        elif token[0] == 'for':
            node_for = NodeFor(token[0], 'for-block')
            current_node.add_child(node_for)
            node_for.parent = current_node
            #nodes_stack.append(current_node)
            #current_node = node_for
        elif token[0] == 'while':
            node_while = NodeWhile(token[0], 'while-block')
            current_node.add_child(node_while)
            node_while.parent = current_node
            #nodes_stack.append(current_node)
            #current_node = node_while
        elif token[0] == "new":
            node_new = Node(token[0], "operator-new")
            current_node.add_child(node_new)
            node_new.parent = current_node
        elif token[0] == "delete":
            node_delete = Node(token[0], "operator-delete")
            current_node.add_child(node_delete)
            node_delete.parent = current_node
        elif token[0] == "break":
            node_break = Node(token[0], "operator-break")
            current_node.add_child(node_break)
            node_break.parent = current_node
        elif token[0] == "continue":
            node_continue = Node(token[0], "operator-continue")
            current_node.add_child(node_continue)
            node_continue.parent = current_node
        elif token[0] == 'std':
            node_std = Node(token[0], 'namespace')
            current_node.add_child(node_std)
            if i < len(tokens) -1:
                if tokens[i+1][0]=='::':
                    std_option = True
                    nodes_stack.append(current_node)
                    current_node = node_std
            if 'std' not in namespaces:
                print(f"ERROR: iostream library is not included -> can not use std")
                exit()
            node_std.parent = current_node

            #nodes_stack.append(current_node)
            #current_node = node_std

        elif token[0] == 'return':
            node_return = Node(token[0], 'return-statement')
            current_node.add_child(node_return)
            nodes_stack.append(current_node)
            node_return.parent = current_node
            current_node = node_return
            need_return = True

        elif token[1].startswith('variable'):
            var_type = [tok.strip() for tok in token[1].split(',')][1]
            var_context = [tok.strip() for tok in token[1].split(',')][2]
            if var_context == 'declare':
                node_var = Node(token[0], 'declare', var_type)
                current_node.add_child(node_var)
                nodes_stack.append(current_node)
                node_var.parent = current_node
                current_node = node_var
                declaring = True
            elif var_context == 'use':
                node_var = Node(token[0], 'variable')
                current_node.add_child(node_var)
                node_var.parent = current_node

        elif token[0] == '::':
            if previous_token not in namespaces:
                print("ERROR: Wrong usage of colon")
                exit()
            node_colon = Node(token[0], 'operator-colon')
            current_node.add_child(node_colon)
            node_colon.parent = current_node

            #if std_option:
            #    nodes_stack.append(current_node)
            #    current_node = node_colon


        # const literals
        elif token[1].startswith('number') or token[1] == 'string' or token[1] == 'char':
            if token[1].startswith('number'):
                lit_type = [tok.strip() for tok in token[1].split(',')][1]
            elif token[1] == 'char':
                lit_type = 'char'
            elif token[1] == 'string':
                lit_type = 'string'
            node_literal = NodeValue(token[0], lit_type)
            current_node.add_child(node_literal)
            node_literal.parent = current_node

        # access areas
        elif token[0] in ['public', 'private', 'protected']:
            node_access = Node(token[0], 'access-modification')
            if current_node.ntype not in ['class-body', 'struct-body']:
                current_node = nodes_stack.pop()
                pass
            nodes_stack.append(current_node)
            current_node.add_child(node_access)
            node_access.parent = current_node
            current_node = node_access

        elif token[0] == ',':
            node_comma = Node(token[0], 'comma')
            if declaring:
                current_node = nodes_stack.pop()
            if assigning:
                current_node = nodes_stack.pop()
                assigning = False
            current_node.add_child(node_comma)
            node_comma.parent = current_node
        elif token[0] == '.':
            node_dot = Node(token[0], 'dot')
            current_node.add_child(node_dot)
            node_dot.parent = current_node
        elif token[0] == '=':
            if i < len(tokens)-1 and tokens[i+1][0] == 'new' and current_node.ntype == 'declare' and current_node.datatype in namespaces:
                current_node.datatype += '*'
            node_assign = Node(token[0], 'assign')
            current_node.add_child(node_assign)
            nodes_stack.append(current_node)
            node_assign.parent = current_node
            current_node = node_assign
            assigning = True

        # ( ) { } [ ]
        elif token[0] in parenthesis:
            if token[0] == '(':
                if current_area == 'fparams':
                    node_params = Node('',f"function-parameters")
                elif current_area == 'condition':
                    node_params = Node('', f"block-condition")
                else:
                    node_params = Node('', f"other-area")
                current_node.add_child(node_params)
                nodes_stack.append(current_node)
                node_params.parent = current_node
                current_node = node_params
            elif token[0] == ')':
                # call of a function/method
                if current_area == 'fparams' and i < len(tokens)-2 and tokens[i+3][0] != '{':
                    current_node = nodes_stack.pop()
                current_node = nodes_stack.pop()
            elif token[0] == '{':
                if current_area == 'block' or current_area == 'body':
                    node_body = Node('', 'block-body')
                if current_area == 'class':
                    node_body = Node('', 'class-body')
                if current_area == 'struct':
                    node_body = Node('', 'struct-body')
                if current_area == 'union':
                    node_body = Node('', 'union-body')
                if current_area == 'enum':
                    node_body = Node('', 'enum-body')
                if current_area == 'main':
                    node_body = Node('', 'main-body')
                if current_area == 'function':
                    node_body = Node('', 'function-body')
                if current_area == 'other':
                    node_body = Node('', 'inline')
                current_node.add_child(node_body)
                nodes_stack.append(current_node)
                node_body.parent = current_node
                current_node = node_body
            elif token[0] == '}':
                if current_area in ['class', 'struct', 'enum', 'union']:
                    while current_node.name != 'program':
                        current_node = nodes_stack.pop()
                elif current_area == 'function' or current_area=='main':
                    while current_node.ntype not in ['class-body','access-modification','root']:
                        current_node = nodes_stack.pop()
                else:
                    current_node = nodes_stack.pop()
            elif token[0] == '[' and previous_token != ']':
                if len([tok.strip() for tok in previous_type.split(',')]) > 2:
                    var_context = [tok.strip() for tok in previous_type.split(',')][2]
                else:
                    var_context = 'indexing'
                if var_context == 'declare':
                    # size of array
                    node_arr = Node('', 'array-size')
                else:
                    # indexing
                    node_arr = Node('', 'indexing')
                current_node.add_child(node_arr)
                nodes_stack.append(current_node)
                node_arr.parent = current_node
                current_node = node_arr
            elif token[0] == ']'and i != len(tokens[i+1])-1 and tokens[i+1][0] != '[':
                current_node = nodes_stack.pop()

        elif token[1].startswith('operator'):
            op_type = [tok.strip() for tok in token[1].split(',')][1]
            op_node = None
            if op_type == 'logic':
                op_node = Node(token[0], 'operator-logic')
            elif op_type == 'bitwise':
                op_node = Node(token[0], 'operator-bitwise')
            elif op_type == 'compare':
                op_node = NodeCompare(token[0], 'operator-compare')
            elif op_type == 'arithmetic':
                op_node = Node(token[0], 'operator-arithmetic')
            elif op_type == 'dereferencing':
                op_node = Node(token[0], 'operator-dereferencing')
            elif op_type == 'ternary':
                op_node = Node(token[0], 'operator-ternary')
            elif op_type == 'special':
                op_node = Node(token[0], 'operator-special')
            else:
                #print(current_node.ntype)
                if token[0] != ':':
                    op_node = Node(token[0], 'operator')
            if op_node is not None:
                current_node.add_child(op_node)
                op_node.parent = current_node
            if token[0] == '>' and current_node.ntype == 'directive':
                current_node = nodes_stack.pop()
            if token[0] == '<' and must_count_angles:
                angles_spare_stack.append('<')
            if token[0] == '>' and must_count_angles:
                angles_spare_stack.pop()
                if len(angles_spare_stack) == 0:

                    must_count_angles = False
                    current_node = nodes_stack.pop()
                    std_option = False

        # ;
        elif token[1] == 'eoc':
            declaration_expected = True
            node_eoc = Node(';', 'eoc')
            current_node.add_child(node_eoc)
            node_eoc.parent = current_node
            if len(nodes_stack) > 1:
                pass#current_node = nodes_stack.pop()
            if need_return:
                current_node = nodes_stack.pop()
                need_return = False
            if declaring:
                current_node = nodes_stack.pop()
                declaring = False
            if assigning:
                current_node = nodes_stack.pop()
                assigning = False
            if including:
                current_node = nodes_stack.pop()
                including = False
            if static_declaration:
                current_node = nodes_stack.pop()
                static_declaration = False
        elif token[0] in stds and std_option:
            node_std = Node(token[0], std_option)
            current_node.add_child(node_std)
            node_std.parent = current_node
            if i < len(tokens)-1 and tokens[i+1][0] != '<':
                current_node = nodes_stack.pop()
                std_option=False
            else:
                print('counting')
                must_count_angles = True
        elif token[0] in ['cout', 'endl', 'cerr', 'cin']:
            node_io = Node(token[0], 'std-option')
            current_node.add_child(node_io)
            node_io.parent = current_node

        elif token[1].startswith('array'):
            var_type = [tok.strip() for tok in token[1].split(',')][1]
            var_context = [tok.strip() for tok in token[1].split(',')][2]
            if var_context == 'declare':
                node_var = Node(token[0], 'declare-array', var_type)
            elif var_context == 'use':
                node_var = Node(token[0], 'array')
            current_node.add_child(node_var)
            node_var.parent = current_node
            # nodes_stack.append(current_node)
            # current_node = node_var
        elif token[0] in keywords:
            if token[0] == 'using':
                node_key = Node(token[0], 'namespace-include')
                current_node.add_child(node_key)
                node_key.parent = current_node
                including = True
                nodes_stack.append(current_node)
                current_node = node_key
            elif token[0] == 'static':
                node_static = Node(token[0], 'static')
                current_node.add_child(node_static)
                node_static.parent = current_node
                nodes_stack.append(current_node)
                current_node = node_static
                static_declaration = True
            else:
                node_key = Node(token[0], 'keyword')
                current_node.add_child(node_key)
                node_key.parent = current_node


        previous_token = token[0]
        previous_type = token[1]
    if len(scobes_stack) > 0:
        print(f"ERROR: clobes {scobes_stack} were never closed!" )
    #print(print(root.display()))
    #for tok in tokens:
    #   print(tok)

    return root, namespaces


