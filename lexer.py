# FlowScript Lexer v0.3
# '' = variable reference, "" = string text

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []

    def tokenize(self):
        lines = self.code.strip().split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip blank lines and comments
            if line == "" or line.startswith("#"):
                i += 1
                continue

            lower = line.lower()

            # IF / ELIF / ELSE block
            if lower.startswith("if "):
                block_branches = []

                # Parse if
                condition = line[3:].strip()
                i += 1
                body_lines = []
                while i < len(lines):
                    peek = lines[i].strip()
                    peek_lower = peek.lower()
                    if peek_lower.startswith("elif ") or peek_lower == "else:" or peek_lower.startswith("end"):
                        break
                    if peek == "" or peek.startswith("#"):
                        i += 1
                        continue
                    body_lines.append(peek)
                    i += 1
                block_branches.append({"condition": condition, "body": body_lines})

                # Parse elif branches
                while i < len(lines) and lines[i].strip().lower().startswith("elif "):
                    elif_line = lines[i].strip()
                    elif_condition = elif_line[5:].strip()
                    i += 1
                    body_lines = []
                    while i < len(lines):
                        peek = lines[i].strip()
                        peek_lower = peek.lower()
                        if peek_lower.startswith("elif ") or peek_lower == "else:" or peek_lower.startswith("end"):
                            break
                        if peek == "" or peek.startswith("#"):
                            i += 1
                            continue
                        body_lines.append(peek)
                        i += 1
                    block_branches.append({"condition": elif_condition, "body": body_lines})

                # Parse else
                if i < len(lines) and lines[i].strip().lower() == "else:":
                    i += 1
                    body_lines = []
                    while i < len(lines):
                        peek = lines[i].strip()
                        if peek.lower().startswith("end"):
                            break
                        if peek == "" or peek.startswith("#"):
                            i += 1
                            continue
                        body_lines.append(peek)
                        i += 1
                    block_branches.append({"condition": None, "body": body_lines})

                # Skip "end"
                if i < len(lines) and lines[i].strip().lower().startswith("end"):
                    i += 1

                self.tokens.append(Token("IF_BLOCK", block_branches))
                continue

            else:
                self.tokenize_line(line)
                i += 1

        return self.tokens

    def tokenize_line(self, line):
        lower = line.lower()
        words = line.split()

        # SAY
        if lower.startswith("say "):
            self.tokens.append(Token("SAY", line[4:].strip()))

        # CREATE: create a number called 'age' with value 20
        elif lower.startswith("create a") and "called" in lower:
            parts = line.split()
            name = parts[parts.index("called") + 1].strip("'")
            value = None
            if "with value" in lower:
                idx = lower.split().index("value")
                value = parts[idx + 1]
            self.tokens.append(Token("CREATE", {"name": name, "value": value}))

        # SET: set 'age' to 30
        elif lower.startswith("set ") and " to " in lower:
            parts = line.split()
            name = parts[1].strip("'")
            value = " ".join(parts[3:])
            self.tokens.append(Token("SET", {"name": name, "value": value}))

        # ADD: add 5 to 'age'
        elif lower.startswith("add ") and " to " in lower:
            parts = line.split()
            amount = parts[1]
            name = parts[3].strip("'")
            self.tokens.append(Token("ADD", {"name": name, "amount": amount}))

        # SUBTRACT: subtract 5 from 'age'
        elif lower.startswith("subtract ") and " from " in lower:
            parts = line.split()
            amount = parts[1]
            name = parts[3].strip("'")
            self.tokens.append(Token("SUBTRACT", {"name": name, "amount": amount}))

        # MULTIPLY: multiply 'age' by 2
        elif lower.startswith("multiply ") and " by " in lower:
            parts = line.split()
            name = parts[1].strip("'")
            factor = parts[3]
            self.tokens.append(Token("MULTIPLY", {"name": name, "factor": factor}))

        # DIVIDE: divide 'age' by 2
        elif lower.startswith("divide ") and " by " in lower:
            parts = line.split()
            name = parts[1].strip("'")
            divisor = parts[3]
            self.tokens.append(Token("DIVIDE", {"name": name, "divisor": divisor}))

        # REPEAT: repeat 5 times say "hello"
        elif lower.startswith("repeat ") and " times " in lower:
            parts = line.split(" times ", 1)
            count = parts[0].split()[1].strip("'")
            action = parts[1].strip()
            self.tokens.append(Token("REPEAT", {"count": count, "action": action}))

        # ASK: ask "What is your name?" and save to 'name'
        elif lower.startswith("ask ") and "save to" in lower:
            parts = line.split("save to")
            question = parts[0][4:].strip()
            if question.lower().endswith(" and"):
                question = question[:-4].strip()
            question = question.strip('"')
            var_name = parts[1].strip().strip("'")
            self.tokens.append(Token("ASK", {"question": question, "name": var_name}))

        else:
            self.tokens.append(Token("UNKNOWN", line))
