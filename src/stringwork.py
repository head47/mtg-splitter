import re

from colorama import Fore, Style

from src.pack import Pack, PackCard

AMOUNT_PATTERN = r"(\d+)x (.*)"


def format_poss(known_pack_possibilities: list[list[Pack]], idx: int) -> str:
    if idx < 0:
        idx = len(known_pack_possibilities) - 1
    possibilities = known_pack_possibilities[idx]
    if len(possibilities) == 1:
        return Fore.GREEN + possibilities[0].name + Style.RESET_ALL
    else:
        known_name = possibilities[0].known_name
        for i in range(1, len(possibilities)):
            if possibilities[i].known_name != known_name:
                known_name = f"inconclusive {idx+1}"
                break
        return Fore.YELLOW + known_name + Style.RESET_ALL


def parse_card_amount(line: str) -> tuple[str, int]:
    match = re.fullmatch(AMOUNT_PATTERN, line)
    if match:
        card_count = int(match.group(1))
        card_name = match.group(2)
    else:
        card_count = 1
        card_name = line
    return (card_name, card_count)


def print_cur_possibilities(known_pack_possibilities: list[list[Pack]], unassigned_cards: list[str]) -> None:
    print("Status: ", end="")
    to_print: list[str] = []
    for i in range(len(known_pack_possibilities)):
        to_print.append(format_poss(known_pack_possibilities, i))
        total_cards = 0
        total_cards_max = 0
        for c in known_pack_possibilities[i][0].cards:
            total_cards += c.amount
            total_cards_max += c.max_amount
        to_print[-1] += f" x{total_cards}"
        if len(known_pack_possibilities[i]) == 1:
            to_print[-1] += f"/{total_cards_max}"
    to_print.append(f"{Fore.RED}unknown{Style.RESET_ALL} x{len(unassigned_cards)}")
    print(", ".join(to_print))


def print_final_report(known_pack_possibilities: list[list[Pack]], unassigned_cards: list[str]) -> None:
    print("\n\n---FINAL REPORT---\n")
    for i in range(len(known_pack_possibilities)):
        poss = known_pack_possibilities[i]
        if len(poss) == 0:
            pack = poss[0]
            print(f"{i+1}. {format_poss(known_pack_possibilities, i)}")
            for card in pack:
                print(f"- {card.amount}/{card.max_amount} {card.name}")
        else:
            print(
                f"{i+1}. {format_poss(known_pack_possibilities, i)} is one of the following: {', '.join([p.name for p in poss])}"
            )
            common_cards = []
            for card1 in poss[0].cards:
                card_to_add = PackCard(name=card1.name, amount=card1.amount, max_amount=card1.max_amount)
                for pack in poss[1:]:
                    for card2 in pack.cards:
                        if card1.name == card2.name:
                            card_to_add.amount = min(card_to_add.amount, card2.amount)
                            card_to_add.max_amount = min(card_to_add.max_amount, card2.max_amount)
                            break
                    else:
                        break
                else:
                    common_cards.append(card_to_add)
            for card in common_cards:
                print(f"- {card.amount}/{card.max_amount} {card.name}")
            print("...")
        print("\n")
    if len(unassigned_cards) > 0:
        print(f"{Fore.RED}Unassigned{Style.RESET_ALL} cards:")
        while len(unassigned_cards) > 0:
            card = unassigned_cards.pop()
            count = unassigned_cards.count(card) + 1
            print(f"- {count}x {card}")
            unassigned_cards = [c for c in unassigned_cards if c != card]
