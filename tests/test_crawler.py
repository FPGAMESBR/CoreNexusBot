import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import RewardsCore

class TestCrawler(unittest.TestCase):
    def test_gerar_banco_cognitivo(self):
        banco = RewardsCore.gerar_banco_cognitivo()
        self.assertIsInstance(banco, list)
        self.assertGreater(len(banco), 0)
        # Todos os itens devem ser strings nao vazias
        for termo in banco[:10]:
            self.assertIsInstance(termo, str)
            self.assertGreater(len(termo.strip()), 0)

    def test_detectar_idioma(self):
        lang = RewardsCore.detectar_idioma()
        self.assertIn(lang, ["pt", "en"])

if __name__ == '__main__':
    unittest.main()
