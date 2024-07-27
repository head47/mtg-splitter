import re
from dataclasses import dataclass, field
from typing import Self

from src import stringwork


@dataclass
class PackCard:
    name: str
    amount: int = 0
    max_amount: int = 1


@dataclass
class Pack:
    name: str
    known_name: str
    cards: list[PackCard] = field(default_factory=list)

    @classmethod
    def from_file(cls, filename: str) -> list[Self]:
        packs: list[cls] = []
        with open(filename) as f:
            for line in f:
                if line.startswith("##"):
                    pack_name = line.lstrip("#1234567890. ").rstrip("\n")
                    known_name = pack_name.rstrip("1234567890 ")
                    packs.append(cls(name=pack_name, known_name=known_name))
                elif line[0] in "-*":
                    if len(packs) < 1:
                        raise Exception(f"Cards enumeration started before pack is named: {line}")
                    stripped_line = line.lstrip("-* ").rstrip("\n")
                    card_name, card_count = stringwork.parse_card_amount(stripped_line)
                    for card in packs[-1].cards:
                        if card.name == card_name:
                            card.max_amount += card_count
                            break
                    else:
                        packs[-1].cards.append(PackCard(name=card_name, max_amount=card_count))
                elif line.rstrip() == "":
                    pass
                else:
                    raise Exception(f"Unknown input: {line}")
        return packs
