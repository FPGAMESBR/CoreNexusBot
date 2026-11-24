import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import AppGUI
import BingStarEngine
import DiscordQuests
import RewardsCore


class TestBingDailyLockAndCoffeeMode(unittest.TestCase):
    def setUp(self):
        self._orig_abort = RewardsCore.ABORTAR_PROCESSO
        self._orig_speed = RewardsCore.SPEED
        self._orig_base_dir = RewardsCore.BASE_DIR
        RewardsCore.ABORTAR_PROCESSO = False
        RewardsCore.SPEED = "normal"

    def tearDown(self):
        RewardsCore.ABORTAR_PROCESSO = self._orig_abort
        RewardsCore.SPEED = self._orig_speed
        RewardsCore.BASE_DIR = self._orig_base_dir

    def test_planejar_acoes_coloca_modo_cafe_entre_chunks(self):
        cfg = {"limite_pc": 20, "limite_mobile": 10, "fazer_tarefas": "s"}
        for _ in range(50):
            acoes = BingStarEngine._planejar_acoes_star_bonus(cfg, "normal")
            idx_cafe = acoes.index("MODO_CAFE")
            antes = acoes[:idx_cafe]
            depois = acoes[idx_cafe + 1:]
            self.assertIn("PC_CHUNK", antes)
            self.assertIn("MOB_CHUNK", antes)
            self.assertIn("PC_CHUNK", depois)
            self.assertIn("MOB_CHUNK", depois)

    def test_planejar_acoes_turbo_sem_modo_cafe(self):
        cfg = {"limite_pc": 20, "limite_mobile": 0, "fazer_tarefas": "s"}
        acoes = BingStarEngine._planejar_acoes_star_bonus(cfg, "turbo")
        self.assertNotIn("MODO_CAFE", acoes)
        self.assertEqual(acoes.count("PC_CHUNK"), 1)

    def test_deve_pular_modo_cafe_limiar_50_porcento(self):
        # 0% e 40% devem executar o Modo Café normalmente
        pular0, _, _ = BingStarEngine.deve_pular_modo_cafe({"pc": (0, 60)}, 1, 0, "normal")
        self.assertFalse(pular0)

        pular40, _, _ = BingStarEngine.deve_pular_modo_cafe({"pc": (24, 60)}, 1, 0, "normal")
        self.assertFalse(pular40)

        # 50%, 60% e 100% devem pular o Modo Café
        pular50, motivo50, ratio50 = BingStarEngine.deve_pular_modo_cafe({"pc": (30, 60)}, 1, 0, "normal")
        self.assertTrue(pular50)
        self.assertEqual(motivo50, "progresso_alto")
        self.assertAlmostEqual(ratio50, 0.5)

        pular60, motivo60, ratio60 = BingStarEngine.deve_pular_modo_cafe({"pc": (36, 60)}, 1, 0, "normal")
        self.assertTrue(pular60)
        self.assertEqual(motivo60, "progresso_alto")
        self.assertAlmostEqual(ratio60, 0.6)

        # Sem chunks pendentes -> pula imediatamente
        pular_vazio, motivo_vazio, _ = BingStarEngine.deve_pular_modo_cafe({"pc": (0, 60)}, 0, 0, "normal")
        self.assertTrue(pular_vazio)
        self.assertEqual(motivo_vazio, "sem_pesquisas")

    def test_star_engine_pula_cafe_quando_50_porcento_ja_feito(self):
        cfg = {"limite_pc": 20, "limite_mobile": 0, "fazer_tarefas": "n", "modo_oculto": "s"}
        fake_driver = MagicMock()
        lotes_executados = []

        with patch.object(BingStarEngine.time, "sleep", return_value=None), \
             patch.object(RewardsCore, "obter_fingerprint", return_value={}), \
             patch.object(RewardsCore, "configurar_driver", return_value=fake_driver) as mock_driver, \
             patch.object(RewardsCore, "obter_progresso_pesquisas", return_value=(10, 30, 60)), \
             patch.object(BingStarEngine, "_fazer_lote_pesquisas", side_effect=lambda d, qtd, b, dev: lotes_executados.append(qtd)), \
             patch.object(BingStarEngine, "_pausa_do_cafe_organica") as mock_cafe:

            ok = BingStarEngine._executar_ciclo_star_bonus("DefaultAccount", cfg, ["termo"], False)

            self.assertTrue(ok)
            mock_cafe.assert_not_called()
            self.assertEqual(lotes_executados, [10])
            # Não deve abrir um segundo navegador redundante após concluir tudo no 1º bloco
            self.assertEqual(mock_driver.call_count, 1)

    def test_star_engine_executa_cafe_quando_comeca_em_zero(self):
        cfg = {"limite_pc": 20, "limite_mobile": 0, "fazer_tarefas": "n", "modo_oculto": "s"}
        fake_driver = MagicMock()
        lotes_executados = []

        with patch.object(BingStarEngine.time, "sleep", return_value=None), \
             patch.object(RewardsCore, "obter_fingerprint", return_value={}), \
             patch.object(RewardsCore, "configurar_driver", return_value=fake_driver), \
             patch.object(RewardsCore, "obter_progresso_pesquisas", side_effect=[(20, 0, 60), (10, 30, 60)]), \
             patch.object(BingStarEngine, "_fazer_lote_pesquisas", side_effect=lambda d, qtd, b, dev: lotes_executados.append(qtd)), \
             patch.object(BingStarEngine, "_pausa_do_cafe_organica") as mock_cafe:

            ok = BingStarEngine._executar_ciclo_star_bonus("DefaultAccount", cfg, ["termo"], False)

            self.assertTrue(ok)
            mock_cafe.assert_called_once()
            self.assertEqual(len(lotes_executados), 2)

    def test_trava_diaria_bing_impede_reexecucao_no_mesmo_dia(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            RewardsCore.BASE_DIR = Path(tmpdir)
            RewardsCore.registrar_data_execucao("rewards")

            self.assertTrue(RewardsCore.verificar_se_rodou_hoje("rewards", dias_cooldown=1))

            bot = AppGUI.BotAPI()
            logs = []
            bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))
            bot.rodando = True
            bot.orquestrador.iniciar_ciclo()
            bot.orquestrador.registrar_ticket_entrada("bing")

            with patch.object(RewardsCore, "preparar_ambiente_adb") as mock_adb, \
                 patch.object(RewardsCore, "iniciar_ciclo_farm") as mock_farm:
                bot.loop_farm()
                mock_adb.assert_not_called()
                mock_farm.assert_not_called()

            self.assertFalse(bot.rodando)
            self.assertTrue(any("FARM COMPLETED SUCCESSFULLY!" in msg for msg, _ in logs))

    def test_trava_diaria_nao_grava_exe_json_quando_abortado(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            RewardsCore.BASE_DIR = Path(tmpdir)

            bot = AppGUI.BotAPI()
            bot.log_ui = lambda msg, tipo="info": None
            bot.rodando = True
            bot.orquestrador.iniciar_ciclo()
            bot.orquestrador.registrar_ticket_entrada("bing")

            def fake_aborted_farm():
                RewardsCore.ABORTAR_PROCESSO = True
                return False

            with patch.object(RewardsCore, "preparar_ambiente_adb"), \
                 patch.object(RewardsCore, "iniciar_ciclo_farm", side_effect=fake_aborted_farm):
                bot.loop_farm()

            self.assertFalse(RewardsCore.verificar_se_rodou_hoje("rewards", dias_cooldown=1))

    def test_discord_close_selectors_protect_dm_sidebar(self):
        self.assertNotIn('[class*="modal"] [aria-label*="Fechar"]', DiscordQuests.SCRIPT_JS)
        self.assertIn("privateChannels", DiscordQuests.SCRIPT_JS)

    def test_falha_parcial_em_bloco_pc_nao_trava_dia_inteiro(self):
        cfg = {"limite_pc": 20, "limite_mobile": 0, "fazer_tarefas": "s", "modo_oculto": "s"}
        fake_driver = MagicMock()

        def driver_side_effect(*args, **kwargs):
            # Dashboard abre normalmente, mas bloco PC falha com Driver Nulo
            driver_side_effect.calls += 1
            return fake_driver if driver_side_effect.calls == 1 else None
        driver_side_effect.calls = 0

        with patch.object(BingStarEngine.time, "sleep", return_value=None), \
             patch.object(BingStarEngine, "_planejar_acoes_star_bonus", return_value=["TAREFAS_DASHBOARD", "PC_CHUNK"]), \
             patch.object(RewardsCore, "obter_fingerprint", return_value={}), \
             patch.object(RewardsCore, "configurar_driver", side_effect=driver_side_effect), \
             patch.object(RewardsCore, "verificar_conta_suspensa", return_value=False), \
             patch.object(RewardsCore, "limpar_todas_as_missoes"), \
             patch.object(RewardsCore, "fazer_pesquisa_visual"):

            ok = BingStarEngine._executar_ciclo_star_bonus("DefaultAccount", cfg, ["termo"], False)
            self.assertFalse(ok)

    def test_config_legada_stealth_e_chrono_gating_normalizada_sem_quebrar(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "RewardsConfig.json"
            cfg_path.write_text('{"speed_mode": "stealth", "extended_days": "a", "limite_pc": 20}', encoding="utf-8")
            orig_cfg = RewardsCore.ARQUIVO_CONFIG
            try:
                RewardsCore.ARQUIVO_CONFIG = cfg_path
                cfg = RewardsCore.carregar_config()
                self.assertEqual(cfg["speed_mode"], "normal")
                self.assertNotIn("extended_days", cfg)
            finally:
                RewardsCore.ARQUIVO_CONFIG = orig_cfg

        self.assertFalse(hasattr(BingStarEngine, "check_extended_days"))

        root = Path(__file__).parent.parent
        index_html = (root / "ui" / "index.html").read_text(encoding="utf-8")
        popup_html = (root / "ui" / "popup.html").read_text(encoding="utf-8")
        readme_md = (root / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("cfg-extended-days", index_html)
        self.assertNotIn('value="stealth"', index_html)
        self.assertNotIn("btn-stealth", popup_html)
        self.assertNotIn("Chrono-Gating", readme_md)


if __name__ == "__main__":
    unittest.main()
