# FlowScript Interpreter v0.3
# Executes tokens
# '' = variable, "" = string

class Interpreter:
    def __init__(self, tokens):
        self.tokens = tokens
        self.variables = {}

    def run(self):
        for token in self.tokens:
            self.execute(token)

    def execute(self, token):
        if token.type == "SAY":
            self.execute_say(token.value)
        elif token.type == "CREATE":
            self.execute_create(token.value)
        elif token.type == "SET":
            self.execute_set(token.value)
        elif token.type == "ADD":
            self.execute_add(token.value)
        elif token.type == "SUBTRACT":
            self.execute_subtract(token.value)
        elif token.type == "MULTIPLY":
            self.execute_multiply(token.value)
        elif token.type == "DIVIDE":
            self.execute_divide(token.value)
        elif token.type == "IF_BLOCK":
            self.execute_if_block(token.value)
        elif token.type == "REPEAT":
            self.execute_repeat(token.value)
        elif token.type == "ASK":
            self.execute_ask(token.value)
        elif token.type == "UNKNOWN":
            print(f"FlowScript Error: I don't understand '{token.value}'")

    # ── SAY ──────────────────────────────────────────
    def execute_say(self, value):
        print(self.resolve(value))

    # ── CREATE ───────────────────────────────────────
    def execute_create(self, data):
        name = data["name"]
        value = data["value"]
        if value is not None:
            resolved = self.resolve(value)
            resolved = self._try_number(resolved)
            self.variables[name] = resolved
        else:
            self.variables[name] = None

    # ── SET ──────────────────────────────────────────
    def execute_set(self, data):
        name = data["name"]
        value = self._try_number(self.resolve(data["value"]))
        self.variables[name] = value

    # ── MATH ─────────────────────────────────────────
    def execute_add(self, data):
        name = data["name"]
        amount = self.resolve(data["amount"])
        self.variables[name] = float(self.variables.get(name, 0)) + float(amount)
        self._clean_number(name)

    def execute_subtract(self, data):
        name = data["name"]
        amount = self.resolve(data["amount"])
        self.variables[name] = float(self.variables.get(name, 0)) - float(amount)
        self._clean_number(name)

    def execute_multiply(self, data):
        name = data["name"]
        factor = self.resolve(data["factor"])
        self.variables[name] = float(self.variables.get(name, 0)) * float(factor)
        self._clean_number(name)

    def execute_divide(self, data):
        name = data["name"]
        divisor = float(self.resolve(data["divisor"]))
        if divisor == 0:
            print("FlowScript Error: Cannot divide by zero")
            return
        self.variables[name] = float(self.variables.get(name, 0)) / divisor
        self._clean_number(name)

    def _clean_number(self, name):
        val = self.variables[name]
        if isinstance(val, float) and val.is_integer():
            self.variables[name] = int(val)

    def _try_number(self, value):
        try:
            s = str(value)
            if '.' in s:
                return float(s)
            return int(s)
        except (ValueError, TypeError):
            return value

    # ── IF / ELIF / ELSE ─────────────────────────────
    def execute_if_block(self, branches):
        for branch in branches:
            condition = branch["condition"]
            body = branch["body"]

            # else branch has condition = None, always runs if reached
            if condition is None:
                self._run_body(body)
                return

            if self._evaluate_condition(condition):
                self._run_body(body)
                return  # stop after first true branch

    def _evaluate_condition(self, condition):
        parts = condition.split()
        try:
            if "greater than" in condition:
                idx = parts.index("greater")
                left = self.resolve(parts[0])
                right = self.resolve(parts[idx + 2])
                return float(left) > float(right)

            elif "less than" in condition:
                idx = parts.index("less")
                left = self.resolve(parts[0])
                right = self.resolve(parts[idx + 2])
                return float(left) < float(right)

            elif "greater than or equal" in condition:
                idx = parts.index("greater")
                left = self.resolve(parts[0])
                right = self.resolve(parts[idx + 4])
                return float(left) >= float(right)

            elif "less than or equal" in condition:
                idx = parts.index("less")
                left = self.resolve(parts[0])
                right = self.resolve(parts[idx + 4])
                return float(left) <= float(right)

            elif "not equals" in condition or "is not" in condition:
                if "not equals" in condition:
                    idx = parts.index("not")
                    left = str(self.resolve(parts[0]))
                    right = str(self.resolve(parts[idx + 2]))
                else:
                    idx = parts.index("not")
                    left = str(self.resolve(parts[0]))
                    right = str(self.resolve(parts[idx + 1]))
                return left != right

            elif "equals" in condition:
                idx = parts.index("equals")
                left = str(self.resolve(parts[0]))
                right = str(self.resolve(parts[idx + 1]))
                return left == right

            elif "is" in condition:
                idx = parts.index("is")
                left = str(self.resolve(parts[0]))
                right = str(self.resolve(parts[idx + 1]))
                return left == right

            else:
                print(f"FlowScript Error: Don't understand condition '{condition}'")
                return False

        except Exception as e:
            print(f"FlowScript Error in condition '{condition}': {e}")
            return False

    def _run_body(self, body_lines):
        from lexer import Lexer
        code = "\n".join(body_lines)
        tokens = Lexer(code).tokenize()
        for t in tokens:
            self.execute(t)

    # ── REPEAT ───────────────────────────────────────
    def execute_repeat(self, data):
        count = int(self.resolve(data["count"]))
        action = data["action"]
        from lexer import Lexer
        tokens = Lexer(action).tokenize()
        for _ in range(count):
            for t in tokens:
                self.execute(t)

    # ── ASK ──────────────────────────────────────────
    def execute_ask(self, data):
        answer = input(data["question"] + " ")
        self.variables[data["name"]] = answer

    # ── RESOLVE ──────────────────────────────────────
    def resolve(self, value):
        if value is None:
            return None
        value = str(value).strip()

        # "" = string literal
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]

        # '' = variable reference
        if value.startswith("'") and value.endswith("'"):
            var_name = value[1:-1]
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                print(f"FlowScript Error: Variable '{var_name}' does not exist")
                return None

        # Number literal
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Bare variable name (backward compat)
        if value in self.variables:
            return self.variables[value]

        return value
