from __future__ import annotations
from typing import Any, List, Dict, Tuple
from scrython import Named
import re

import projectConstants as C

nonColorRe = re.compile(r"[^WUBRG]")

def extractColor(manaCost: str) -> list[C.MTG_COLORS]:
    colors = nonColorRe.sub("", manaCost)
    ret: list[C.MTG_COLORS] = []
    for c in colors:
        if c in C.MANA_SYMBOLS and c not in ret:
            ret.append(c)
    return ret

class Card:
    """
    Handler class for a card, a card face, or a card half.
    Can be initialized with a Scryfall search result.
    Automatically sets aftermath and fuse layouts.
    Automatically sets layout and card face for transform and modal_dfc faces
    Has a method for color indicator reminder text
    """

    def __init__(self, card: dict[str, Any] | Named):
        if isinstance(card, Named):
            self.data: dict[str, Any] = card.scryfallJson  # type: ignore
        else:
            self.data = card

        try:
            layout = self.layout
        except:
            return
        if layout == "split":
            secondHalfText = self.card_faces[1].oracle_text.split("\n")
            if secondHalfText[0].split(" ")[0] == "Aftermath":
                self.data["layout"] = "aftermath"
            if secondHalfText[-1].split(" ")[0] == "Fuse":
                self.data["layout"] = "fuse"
                self.data["fuse_text"] = secondHalfText[-1]

    def _checkForKey(self, attr: str) -> Any:
        if attr in self.data:
            return self.data[attr]
        raise KeyError(f"This card has no key {attr}: {self.name}")

    @property
    def name(self) -> str:
        return self._checkForKey("name")

    @property
    def colors(self) -> list[C.MTG_COLORS]:
        return self._checkForKey("colors")

    @property
    def color_indicator(self) -> list[C.MTG_COLORS]:
        return self._checkForKey("color_indicator")

    @property
    def mana_cost(self) -> str:
        return self._checkForKey("mana_cost")

    @property
    def oracle_text(self) -> str:
        return self._checkForKey("oracle_text")

    @property
    def type_line(self) -> str:
        return self._checkForKey("type_line")

    @property
    def power(self) -> str:
        return self._checkForKey("power")

    @property
    def toughness(self) -> str:
        return self._checkForKey("toughness")

    @property
    def loyalty(self) -> str:
        return self._checkForKey("loyalty")

    @property
    def layout(self) -> str:
        return self._checkForKey("layout")

    @property
    def fuse_text(self) -> str:
        return self._checkForKey("fuse_text")

    @property
    def card_faces(self) -> list[Card]:
        faces = self._checkForKey("card_faces")
        layout = self.layout
        faces[0]["face_type"] = layout
        faces[1]["face_type"] = layout
        if layout in C.DFC_LAYOUTS:
            layoutSymbol: str = "TDFC" if layout == "transform" else "MDFC"
            faces[0]["face_symbol"] = f"{{{layoutSymbol}_FRONT}}"
            faces[1]["face_symbol"] = f"{{{layoutSymbol}_BACK}}"
            faces[0]["layout"] = layout
            faces[1]["layout"] = layout
        elif layout == "fuse":
            faces[0]["oracle_text"] = faces[0]["oracle_text"].replace(
                "\n" + self.fuse_text, ""
            )
            faces[1]["oracle_text"] = faces[1]["oracle_text"].replace(
                "\n" + self.fuse_text, ""
            )
        if layout in ["split", "fuse", "aftermath"]:
            faces[0]["colors"] = extractColor(faces[0]["mana_cost"])
            faces[1]["colors"] = extractColor(faces[1]["mana_cost"])

        return [Card(face) for face in faces]

    @property
    def face_symbol(self) -> str:
        return self._checkForKey("face_symbol")

    @property
    def face_type(self) -> str:
        try:
            return self._checkForKey("face_type")
        except:
            return "standard"

    @property
    def color_indicator_reminder_text(self) -> str:
        try:
            cardColorIndicator: list[C.MTG_COLORS] = self.color_indicator
        except:
            return ""
        if len(cardColorIndicator) == 5:
            colorIndicatorText = "all colors"
        else:
            colorIndicatorNames = [C.COLOR_NAMES[c] for c in cardColorIndicator]
            if len(colorIndicatorNames) == 1:
                colorIndicatorText = colorIndicatorNames[0]
            else:
                colorIndicatorText = f'{", ".join(colorIndicatorNames[:-1])} and {colorIndicatorNames[-1]}'
        return f"({self.name} is {colorIndicatorText}.)\n"

    def hasPT(self) -> bool:
        try:
            self.power
            return True
        except KeyError:
            return False

    def hasL(self) -> bool:
        try:
            self.loyalty
            return True
        except KeyError:
            return False

    def hasPTL(self) -> bool:
        return self.hasPT() or self.hasL()

    @property
    def flavor_name(self) -> str:
        return self._checkForKey("flavor_name")

    def has_flavor_name(self) -> bool:
        try:
            self.flavor_name
            return True
        except:
            return False


Deck = List[Card]
Flavor = Dict[str, str]

XY = Tuple[int, int]
Box = Tuple[XY, XY]