import random


def generate():

    operators = {'+': lambda x, y: x + y,
                 "-": lambda x, y: x - y,
                 "*": lambda x, y: x * y,
                 }

    x = random.randint(0, 100)
    y = random.randint(0, 100)
    operator = random.choice(list(operators.keys()))

    return f"{x} {operator} {y}\n", str(operators[operator](x, y))
