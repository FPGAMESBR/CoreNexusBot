import unittest
import sys
import tempfile
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import RewardsCore
import AppGUI
import DiscordQuests

class TestSessionLoggingAndQuests(unittest.TestCase):
    def test_disk_logging_writes_to_file(self):
        """Verifica se o log da sessão no disco é criado e grava linhas reais sem ficar em 0 bytes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_log_path = Path(tmpdir) / "run_test_session.txt"
            orig_path = RewardsCore.RUN_LOG_PATH
            try:
                RewardsCore.RUN_LOG_PATH = test_log_path
                api = AppGUI.BotAPI()
                
                # Executa múltiplos registros de log
                api.log_ui("FARM_SESSION_STARTED", "info")
                api.log_ui("FARM_PROGRESS_CHECK: 10/60", "warning")
                api.log_ui("FARM COMPLETED SUCCESSFULLY!", "success")
                
                self.assertTrue(test_log_path.exists(), "Arquivo de log não foi criado no disco")
                self.assertGreater(test_log_path.stat().st_size, 0, "Arquivo de log permaneceu com 0 bytes")
                
                content = test_log_path.read_text(encoding="utf-8")
                self.assertIn("FARM_SESSION_STARTED", content)
                self.assertIn("FARM_PROGRESS_CHECK", content)
                self.assertIn("FARM COMPLETED SUCCESSFULLY!", content)
            finally:
                RewardsCore.RUN_LOG_PATH = orig_path

    def test_discord_script_js_syntax(self):
        """Valida que o script injetado de Quests do Discord não possui erros de sintaxe JS."""
        js = DiscordQuests.SCRIPT_JS.replace('INJECT_GLOBAL_IDS', '[]').replace('INJECT_QUESTS_WEBHOOK', '')
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js)
            temp_path = f.name
        try:
            res = subprocess.run(['node', '--check', temp_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Erro de sintaxe no JavaScript de Quests:\n{res.stderr}")
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    def test_locales_keys_synchronization(self):
        """Verifica se todas as chaves em pt existem em en e vice-versa sem discrepâncias."""
        locales_path = Path(__file__).parent.parent / "locales.json"
        import json
        with open(locales_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pt_keys = set(data.get("pt", {}).keys())
        en_keys = set(data.get("en", {}).keys())
        self.assertEqual(pt_keys, en_keys, f"Diferença entre chaves: {pt_keys ^ en_keys}")

if __name__ == '__main__':
    unittest.main()

