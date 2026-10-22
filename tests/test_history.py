import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import RewardsCore

class TestHistory(unittest.TestCase):
    def test_carregar_historico_set(self):
        hist = RewardsCore.carregar_historico()
        self.assertIsInstance(hist, set)

    def test_salvar_historico_em_memoria(self):
        termo_teste = "termo_de_teste_unitario_antigravity_123"
        RewardsCore.salvar_historico(termo_teste)
        hist = RewardsCore.carregar_historico()
        self.assertIn(termo_teste, hist)

if __name__ == '__main__':
    unittest.main()
