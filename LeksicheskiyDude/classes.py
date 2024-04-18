from dataclasses import dataclass


@dataclass
class Token:
    def __init__(self, name, ttype, line):
        self.line = line
        self.name = name
        self.ttype = ttype


class TokenTable:
    def __init__(self):
        self.table = {}
        self.current_id = 1

    def add_token(self, token):
        self.table[self.current_id] = token
        self.current_id += 1

    def print_tokens(self):
        for i in self.table.keys():
            token = self.table.get(i)
            print(f"id: {i}\t\ttoken: {token.name}\t\ttype: {token.ttype}")

    def print_tokens_with_lines(self):
        for i in self.table.keys():
            token = self.table.get(i)
            print(f"id: {i}\t\ttoken: {token.name}\t\ttype: {token.ttype}\t\tlines: {sorted(token.lines)}")

    def get_token_by_id(self, token_id: int):
        return self.table.get(token_id)

    def get_token_by_name(self, token_name: str):
        for i in self.table.keys():
            token = self.table.get(i)
            if token.name == token_name:
                return i, token
        return None, None

    def check_token_in_table(self, name : str):
        for i in self.table.keys():
            token = self.table.get(i)
            if token.name == name:
                return True
        return False

    def get_values(self):
        return self.table.values()

