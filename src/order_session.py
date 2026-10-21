import json
import time
import uuid

from . import config, menu


class OrderItem:
    def __init__(self, drink, size, hot_or_iced, milk, add_ons):
        self.drink = drink
        self.size = size
        self.hot_or_iced = hot_or_iced
        self.milk = milk
        self.add_ons = add_ons
        self.price = menu.price_for(drink, size, add_ons)

    def describe(self):
        parts = [self.size, self.hot_or_iced, self.milk, self.drink["name"]]
        desc = " ".join(p for p in parts if p).title()
        if self.add_ons:
            desc += " with " + ", ".join(a["name"] for a in self.add_ons)
        return f"{desc} - ${self.price:.2f}"


class OrderSession:
    def __init__(self):
        self.items = []
        self.order_id = uuid.uuid4().hex[:8]

    def add_item(self, drink_name, size=None, hot_or_iced=None, milk=None, add_on_names=None):
        drink = menu.find_drink(drink_name)
        if drink is None:
            return None, f"Sorry, we don't have '{drink_name}' on the menu."
        size = menu.normalize_size(size) or "medium"
        milk = menu.normalize_milk(milk)
        add_ons = [a for a in (menu.find_addon(n) for n in (add_on_names or [])) if a]
        item = OrderItem(drink, size, hot_or_iced, milk, add_ons)
        self.items.append(item)
        return item, None

    def remove_last(self):
        return self.items.pop() if self.items else None

    def total(self):
        return round(sum(i.price for i in self.items), 2)

    def receipt_text(self):
        if not self.items:
            return "No items in order yet."
        lines = [i.describe() for i in self.items]
        lines.append(f"Total: ${self.total():.2f}")
        return "\n".join(lines)

    def log(self):
        config.ORDERS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "order_id": self.order_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [i.describe() for i in self.items],
            "total": self.total(),
        }
        with open(config.ORDERS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record
