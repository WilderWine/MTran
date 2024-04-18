datatypes = ['auto', 'void', 'bool', 'char', 'signed char', 'unsigned char', 'short', 'short int', 'signed short int',
             'signed short','char8_t', 'char16_t','char32_t', 'string','uint32_t', 'size_t','unsigned short', 'unsigned short int', 'int', 'signed', 'signed int', 'unsigned', 'unsigned int',
             'long', 'long int', 'signed long', 'signed long int', 'unsigned long', 'unsigned long int',
             'long long', 'long long int', 'signed long long int', 'signed long long',
             'unsigned long long', 'unsigned long long int',
             'float', 'double', 'long double', 'wchar_t', 'const']
datatypes_pieces = ['char', 'int', 'double', 'long', 'const', 'signed', 'unsigned', 'short']
operators = ['+', '-', '*', '/', '%', '++', '--', '==', '!=', '>', '<', '>=', '<=', '&&', '||', '!', '&', '|', '^',
             '~', '<<', '>>', '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=',
             '?', ':', '->', '->*', ',', '.', '.*', '::', '(', ')', '{', '}', '[', ']', '//', '/*', '*/']

math_operators = ['+', '-', '*', '/', '%', '++', '--', '+=', '-=', '*=', '/=', '%=',]
logic_operators = ['&&', '||', '!']
compare_operators = ['==', '<=', '>=', '!=']
comment_operators = ['//', '/*', '*/']
bitwise_operators = ['|', '^', '~']

math_funcs = ['pow', 'sin', 'cos', 'sqrt', 'log', 'exp', 'round', 'abs']
stand_funcs = ['strcpy','strlen','strcat','strstr','strtok','sprintf','strcmp','strchr','strrchr','main', 'printf','scanf']

dividers = [',', ';', '(', ')', '{', '}', '[', ']']
parenthesis = ['(', ')', '{', '}', '[', ']']
delimiters = [',', ';']
keywords = ['for', 'do', 'if', 'else', 'while', 'goto', 'std', 'class', 'struct', 'return',
            'continue', 'break', 'switch', 'case', 'try', 'catch', 'true', 'false', 'new', 'delete',
            'default', 'enum', 'namespace', 'nullptr', 'public', 'private', 'protected', 'null',
            'static', 'this', 'union', 'asm', 'using', 'iostream', 'cout', 'cin', 'endl',
            'system', 'const', 'override', 'virtual', 'typename', 'typedef', 'exception', 'sizeof', 'friend',
            'calloc', 'malloc', 'realloc', 'NULL', 'new', 'static', 'this', 'nullptr','main']
directives = ['#include', '#ifdef', '#ifndef', '#if', '#elif', '#else', '#pragma', '#error', "#warning"]
libraries = ['iostream', 'string', 'vector', 'cmath', 'ctime', 'cstdlib', 'cstdio', 'fstream', 'iomanip','sstream',
             'stdexcept', 'locale', 'memory', 'thread', 'chrono', 'regex', 'tuple', 'utility']
classes = ['ifstream', 'iostream', 'ostream', 'ofstream']
spsymbols = ['$','@']
containers = ['vector', 'list', 'deque', 'queue', 'stack', 'set', 'unordered_set', 'multiset', 'map', 'unordered_map',
              'multimap', 'bitset', 'pair']
stds = ['vector', 'list', 'deque', 'queue', 'stack', 'set', 'unordered_set', 'multiset', 'map', 'unordered_map',
              'multimap', 'bitset', 'pair', 'string', 'cout', 'endln', 'cin', 'cerr']
