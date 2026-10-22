import unittest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import RewardsCore

class TestLocales(unittest.TestCase):
    def test_locales_json_valido(self):
        locales_path = Path(__file__).parent.parent / "locales.json"
        self.assertTrue(locales_path.exists())
        with open(locales_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("pt", data)
        self.assertIn("en", data)
        self.assertGreater(len(data["pt"]), 10)
        self.assertGreater(len(data["en"]), 10)

    def test_sem_caracteres_corrompidos(self):
        locales_path = Path(__file__).parent.parent / "locales.json"
        text = locales_path.read_text(encoding="utf-8")
        bad_chars = ["\ufffd", "ǜ", "ǟ", "ǭ", "Ǹ"]
        for bad in bad_chars:
            self.assertNotIn(bad, text, f"Caractere corrompido encontrado: {bad}")

    def test_funcao_t_traducao(self):
        msg_pt = RewardsCore.t("invalido")
        self.assertIsInstance(msg_pt, str)
        self.assertGreater(len(msg_pt), 0)

if __name__ == '__main__':
    unittest.main()
