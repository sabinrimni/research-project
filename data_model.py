class Transformation:
    inflection: str
    lemma: str
    rules: list

    def __str__(self) -> str:
        return f"(lemma: {self.lemma}, inflection: {self.inflection}, rules: {self.rules})"

    def __repr__(self) -> str:
        return f"(lemma: {self.lemma}, inflection: {self.inflection}, rules: {self.rules})"

    def __init__(self, lemma: str, inflection: str, rules: list) -> None:
        super().__init__()
        self.inflection = inflection
        self.lemma = lemma
        self.rules = rules
