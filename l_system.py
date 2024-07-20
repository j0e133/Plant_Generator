import random



Rules = dict[str, tuple[tuple[str, ...], tuple[float, ...]] | str]



class LSystem:
    __slots__ = ('alphabet', 'rules', 'axiom', 'state')


    def __init__(self, alphabet: str, rules: Rules, axiom: str) -> None:
        self.alphabet = alphabet
        self.rules = rules
        self.axiom = axiom
        self.state = axiom


    def __repr__(self) -> str:
        return self.state
    

    def reset(self) -> None:
        self.state = self.axiom


    def step(self, n: int = 1) -> None:
        for _ in range(n):
            next_state = ''

            for symbol in self.state:
                if symbol in self.rules:
                    symbol_rule = self.rules[symbol]

                    if isinstance(symbol_rule, str):
                        next_state += symbol_rule
                    else:
                        population, weights = symbol_rule
                        next_state += random.choices(population, weights)[0]
                else:
                    next_state += symbol

            self.state = next_state

