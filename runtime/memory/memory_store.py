import json
import os


class MemoryStore:

    FILE = "memory.json"

    @classmethod
    def load(cls):

        if not os.path.exists(cls.FILE):
            return {}

        with open(cls.FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save(cls, data):

        with open(cls.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)