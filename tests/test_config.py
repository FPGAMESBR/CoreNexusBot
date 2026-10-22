import unittest
import sys
from pathlib import Path

# Adiciona o diretorio raiz do bot ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import RewardsCore

class TestConfig(unittest.TestCase):
    def test_carregar_config_padrao(self):
        cfg = RewardsCore.carregar_config()
        self.assertIsInstance(cfg, dict)
        self.assertIn("limite_pc", cfg)
        self.assertIn("limite_mobile", cfg)
        self.assertIn("modo_oculto", cfg)
        self.assertIn("fazer_tarefas", cfg)
        self.assertIn("language", cfg)

    def test_salvar_e_carregar_config(self):
        cfg_original = RewardsCore.carregar_config()
        test_val = 999
        cfg_original["_teste_temp"] = test_val
        RewardsCore.salvar_config(cfg_original)

        cfg_recarregada = RewardsCore.carregar_config()
        self.assertEqual(cfg_recarregada.get("_teste_temp"), test_val)

        # Limpa o teste
        del cfg_original["_teste_temp"]
        RewardsCore.salvar_config(cfg_original)

if __name__ == '__main__':
    unittest.main()
