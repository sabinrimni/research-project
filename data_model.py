from typing import List


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


class Operation:
    index: int
    letters: str

    def __init__(self, index: int, letters: str) -> None:
        super().__init__()
        self.index = index
        self.letters = letters

    def __str__(self) -> str:
        return f"(index: {self.index}, letters: {self.letters})"

    def __repr__(self) -> str:
        return f"(index: {self.index}, letters: {self.letters})"


class Operations:
    transformation: Transformation
    inserts: List[Operation]
    deletes: List[Operation]

    def __init__(self, transformation: Transformation, inserts: List[Operation],
                 deletes: List[Operation]) -> None:
        super().__init__()
        self.transformation = transformation
        self.inserts = inserts
        self.deletes = deletes

    def __str__(self) -> str:
        return f"(transformation: {self.transformation}, inserts: {self.inserts}, deletes: {self.deletes})"

    def __repr__(self) -> str:
        return f"(transformation: {self.transformation}, inserts: {self.inserts}, deletes: {self.deletes})"


