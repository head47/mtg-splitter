#!/usr/bin/env python3

import readline
from typing import Optional

from colorama import Fore, Style

from src import stringwork
from src.completer import CardCompleter, Completer
from src.pack import Pack, PackCard


def try_add_to_existing(card_name: str, known_pack_possibilities: list[list[Pack]]) -> bool:
    for i in range(len(known_pack_possibilities)):
        poss = known_pack_possibilities[i]
        if len(poss) == 0:
            for card in poss[0].cards:
                if card_name == card.name and card.amount < card.max_amount:
                    card.amount += 1
                    print(f"{card_name} -> {stringwork.format_poss(known_pack_possibilities, i)}")
                    return True
        else:
            found_cards: list[PackCard] = []
            for poss_pack in poss:
                for card in poss_pack.cards:
                    if card_name == card.name and card.amount < card.max_amount:
                        found_cards.append(card)
                        break
            if len(found_cards) == len(poss):
                for card in found_cards:
                    card.amount += 1
                print(f"{card_name} -> {stringwork.format_poss(known_pack_possibilities, i)}")
                return True
    return False


def try_add_to_new(
    card_name: str,
    known_pack_possibilities: list[list[Pack]],
    packs: list[Pack],
) -> bool:
    for poss in known_pack_possibilities:
        for pack in poss:
            for card in pack.cards:
                if card_name == card.name and card.amount < card.max_amount:
                    return False  # this card might be a part of an existing pack, play it safe
    possibilities: list[Pack] = []
    for pack in packs:
        for card in pack.cards:
            if card_name == card.name:
                for poss in known_pack_possibilities:
                    if pack in poss:
                        break
                else:
                    possibilities.append(pack)
                    card.amount += 1
    if len(possibilities) == 0:
        return False
    else:
        known_pack_possibilities.append(possibilities)
        poss_formatted = stringwork.format_poss(known_pack_possibilities, -1)
        poss_len = len(possibilities)
        if poss_len == 1:
            print(f"New pack: {poss_formatted}")
        else:
            print(f"New pack: {poss_formatted} ({poss_len} possibilities)")
        print(f"{card_name} -> {poss_formatted}")
        return True


def try_differentiate(
    card_name: str,
    known_pack_possibilities: list[list[Pack]],
    pack_amount: Optional[int],
    packs: list[Pack],
) -> bool:
    if len(known_pack_possibilities) != pack_amount:
        # make sure no new packs can be added
        for pack in packs:
            for card in pack.cards:
                if card.name == card_name:
                    for poss in known_pack_possibilities:
                        if pack in poss:
                            break
                    else:
                        return False
                    break

    target_poss_idx: Optional[int] = None
    possible_pack_idxs: list[int] = []
    for i in range(len(known_pack_possibilities)):
        for j in range(len(known_pack_possibilities[i])):
            for card in known_pack_possibilities[i][j].cards:
                if card_name == card.name and card.amount < card.max_amount:
                    if target_poss_idx is not None and target_poss_idx != i:
                        return False
                    else:
                        target_poss_idx = i
                        possible_pack_idxs.append(j)
                        break
    if target_poss_idx is None:
        return False
    poss_old_len = len(known_pack_possibilities[target_poss_idx])
    poss_new_len = len(possible_pack_idxs)
    if poss_new_len < poss_old_len:
        poss_old_formatted = stringwork.format_poss(known_pack_possibilities, target_poss_idx)
        # leave only target packs in possibility
        possible_packs = []
        for i in possible_pack_idxs:
            possible_packs.append(known_pack_possibilities[target_poss_idx][i])
            for card in known_pack_possibilities[target_poss_idx][i].cards:
                if card_name == card.name and card.amount < card.max_amount:
                    card.amount += 1
                    break
        known_pack_possibilities[target_poss_idx] = possible_packs
        poss_new_formatted = stringwork.format_poss(known_pack_possibilities, target_poss_idx)
        if poss_new_len == 1:
            print(f"{poss_old_formatted} is now {poss_new_formatted}")
        else:
            print(
                f"{poss_old_formatted} is now {poss_new_formatted} ({poss_old_len} possibilities reduced to {poss_new_len})"
            )
        print(f"{card_name} -> {poss_new_formatted}")
        return True
    else:
        return False


def try_assign(
    card_name: str,
    known_pack_possibilities: list[list[Pack]],
    pack_amount: Optional[int],
    packs: list[Pack],
) -> str:
    # pass 1: check if can add to existing pack
    card_assigned = try_add_to_existing(card_name, known_pack_possibilities)
    if card_assigned:
        return "noupdate"

    # pass 2: check if can differentiate
    card_assigned = try_differentiate(card_name, known_pack_possibilities, pack_amount, packs)
    if card_assigned:
        return "update"

    # pass 3: check if can add new pack
    if len(known_pack_possibilities) != pack_amount:
        card_assigned = try_add_to_new(card_name, known_pack_possibilities, packs)
        if card_assigned:
            return "update"

    return "unassigned"


def main():
    print("Loading pack data...")
    packs = Pack.from_file("packs.md")
    known_pack_possibilities: list[list[Pack]] = []
    unassigned_cards: list[str] = []

    all_pack_names = [p.known_name for p in packs]
    all_card_names = set()
    for pack in packs:
        for card in pack.cards:
            all_card_names.add(card.name)
    all_card_names = list(all_card_names)

    pack_amount = input("Amount of packs [unknown]: ")
    pack_amount = None if pack_amount in ("unknown", "") else int(pack_amount)

    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims("")

    if pack_amount:
        completer = Completer(variants=all_pack_names)
        readline.set_completer(completer.complete)
        for i in range(pack_amount):
            pack_known_name = input(f"Enter name of pack {i+1} [unknown]: ")
            while pack_known_name not in ("unknown", "") and pack_known_name not in all_pack_names:
                print("ERROR: no such pack")
                pack_known_name = input(f"Enter name of pack {i+1} [unknown]: ")
            if pack_known_name in ("unknown", ""):
                continue
            possibilities = [p for p in packs if p.known_name == pack_known_name]
            known_pack_possibilities.append(possibilities)

    completer = CardCompleter(variants=all_card_names)
    readline.set_completer(completer.complete)
    while True:
        stringwork.print_cur_possibilities(known_pack_possibilities, unassigned_cards)
        try:
            line = input("Enter card name, or press EOF to finish: ")
        except EOFError:
            break
        card_name, card_count = stringwork.parse_card_amount(line)
        while card_name not in all_card_names:
            print("ERROR: no such card")
            stringwork.print_cur_possibilities(known_pack_possibilities, unassigned_cards)
            try:
                line = input("Enter card name, or press EOF to finish: ")
            except EOFError:
                break
            card_name, card_count = stringwork.parse_card_amount(line)
        for _ in range(card_count):
            result = try_assign(card_name, known_pack_possibilities, pack_amount, packs)
            match result:
                case "update":
                    updated = True
                    print("Reassigning cards to new packs")
                    while updated:
                        updated = False
                        to_reprocess = unassigned_cards
                        unassigned_cards = []
                        for card_name in to_reprocess:
                            result = try_assign(card_name, known_pack_possibilities, pack_amount, packs)
                            match result:
                                case "update":
                                    updated = True
                                case "unassigned":
                                    unassigned_cards.append(card_name)
                        print("Reassigned.")
                case "unassigned":
                    print(f"{card_name} -> {Fore.RED}unknown{Style.RESET_ALL} x{len(unassigned_cards)}")
                    unassigned_cards.append(card_name)

    stringwork.print_final_report(known_pack_possibilities, unassigned_cards)


if __name__ == "__main__":
    main()
