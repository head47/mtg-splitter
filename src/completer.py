from dataclasses import dataclass, field
from typing import Optional, Self

from src.pack import Pack
from src.stringwork import parse_card_amount


@dataclass
class Completer:
    variants: list[str] = field(default_factory=list)

    def complete(self, text: str, idx: int) -> Optional[str]:
        variants = [c for c in self.variants if c.startswith(text)]
        if idx < len(variants):
            return variants[idx]


class CardCompleter(Completer):
    def complete(self, text: str, idx: int) -> Optional[str]:
        text, count = parse_card_amount(text)
        completed = super().complete(text, idx)
        if completed is None:
            return completed
        else:
            return f"{count}x {text}"
