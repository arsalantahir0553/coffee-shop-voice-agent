import difflib
import json

from . import config


def load_menu():
    with open(config.MENU_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


MENU = load_menu()


def find_drink(name):
    if not name:
        return None
    names = [d["name"] for d in MENU["drinks"]]
    matches = difflib.get_close_matches(name.lower().strip(), names, n=1, cutoff=0.6)
    if not matches:
        return None
    return next(d for d in MENU["drinks"] if d["name"] == matches[0])


def find_addon(name):
    if not name:
        return None
    names = [a["name"] for a in MENU["add_ons"]]
    matches = difflib.get_close_matches(name.lower().strip(), names, n=1, cutoff=0.6)
    if not matches:
        return None
    return next(a for a in MENU["add_ons"] if a["name"] == matches[0])


def normalize_size(size):
    if not size:
        return None
    matches = difflib.get_close_matches(size.lower().strip(), MENU["sizes"], n=1, cutoff=0.6)
    return matches[0] if matches else None


def normalize_milk(milk):
    if not milk:
        return None
    matches = difflib.get_close_matches(milk.lower().strip(), MENU["milks"], n=1, cutoff=0.6)
    return matches[0] if matches else None


def price_for(drink, size, add_ons):
    total = drink["base_price"].get(size, min(drink["base_price"].values()))
    for addon in add_ons:
        total += addon["price"]
    return round(total, 2)


def menu_as_text():
    lines = [
        f"Shop: {MENU['shop_name']}",
        "Sizes: " + ", ".join(MENU["sizes"]),
        "Milk options: " + ", ".join(MENU["milks"]),
        "Drinks:",
    ]
    for d in MENU["drinks"]:
        prices = ", ".join(f"{s} ${p:.2f}" for s, p in d["base_price"].items())
        lines.append(f"  - {d['name'].title()} ({prices}) - {'/'.join(d['hot_or_iced'])}")
    lines.append("Add-ons:")
    for a in MENU["add_ons"]:
        lines.append(f"  - {a['name'].title()} (+${a['price']:.2f})")
    return "\n".join(lines)
