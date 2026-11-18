import unittest
import sys
import tempfile
import os
import json
import subprocess
from unittest.mock import MagicMock, patch
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

    def test_discord_video_quest_resolution_in_node(self):
        """Verifica se o motor JS identifica corretamente missões de vídeo com Map e taskConfigV2."""
        test_script = """
        const taskKeys = (tasks) => (tasks instanceof Map ? [...tasks.keys()] : Object.keys(tasks ?? {}));
        const taskAt = (tasks, key) => (tasks instanceof Map ? tasks.get(key) : tasks?.[key]);
        const selectTaskConfig = (cfg) => {
            const v2 = cfg?.taskConfigV2 || cfg?.task_config_v2;
            if (taskKeys(v2?.tasks).length > 0) return v2;
            const v1 = cfg?.taskConfig || cfg?.task_config;
            if (taskKeys(v1?.tasks).length > 0) return v1;
            return v2 || v1 || cfg || null;
        };

        const typeMap = [
            { match: k => k.includes("VIDEO"), type: "WATCH_VIDEO", prefer: ["WATCH_VIDEO", "WATCH_VIDEO_ON_MOBILE"] },
            { match: k => k.startsWith("PLAY"), type: "GAME", prefer: ["PLAY_ON_DESKTOP"] }
        ];

        const resolveQuestTask = (q) => {
            let tCfg = selectTaskConfig(q.config);
            const keys = taskKeys(tCfg?.tasks);
            for (const { match, type, prefer } of typeMap) {
                const keyName = (prefer && keys.find(k => prefer.includes(k))) || keys.find(k => match(k));
                if (keyName) {
                    const taskData = taskAt(tCfg.tasks, keyName) || {};
                    return { keyName, type, taskData };
                }
            }
            return null;
        };

        const mockVideoQuest = {
            id: '1562249301252645008',
            config: {
                taskConfig: { tasks: {} },
                taskConfigV2: { tasks: new Map([['WATCH_VIDEO', { target: 30 }]]) }
            }
        };

        const res = resolveQuestTask(mockVideoQuest);
        if (!res || res.type !== 'WATCH_VIDEO' || res.taskData.target !== 30) {
            process.exit(1);
        }
        process.exit(0);
        """
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_path = f.name
        try:
            res = subprocess.run(['node', temp_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, "Falha na resolução de missão de vídeo no motor JS")
        finally:
            try: os.remove(temp_path)
            except Exception: pass

    def test_locales_keys_synchronization(self):
        """Verifica se todas as chaves em pt existem em en e vice-versa sem discrepâncias."""
        locales_path = Path(__file__).parent.parent / "locales.json"
        import json
        with open(locales_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pt_keys = set(data.get("pt", {}).keys())
        en_keys = set(data.get("en", {}).keys())
        self.assertEqual(pt_keys, en_keys, f"Diferença entre chaves: {pt_keys ^ en_keys}")

    def test_discord_video_uses_native_ui_without_spoofed_api(self):
        """Garante que o script de vídeo não envia POST /video-progress falsificado e usa o player real da UI."""
        js = DiscordQuests.SCRIPT_JS
        self.assertNotIn("/video-progress", js)
        self.assertIn("discord-web-video-player-video", js)
        self.assertIn("discord-web-video-player-play-pause-btn", js)
        self.assertIn("ad-video-modal-close-btn", js)
        self.assertIn("recompensas_focus_needed", js)

    def test_discord_video_cta_matching_ignores_promo_buttons(self):
        """Valida em Node que o seletor CTA ignora 'Assista já' / 'Pré-compra aqui' e aceita botões reais de missão."""
        node_code = """
        const excludedRe = /assista\\s+j[áa]|watch\\s+now|novamente|again|pr[ée]-?compra|pre-?purchase|comprar|buy\\b|jogar|play\\b|baixar|download|saiba\\s+mais|learn\\s+more|entrar\\s+no\\s+servidor|join\\s+server/i;
        const exactRe = /^(assistir|continuar|watch|continue)(\\s+(\\d+[smh]?|ao\\s+v[íi]deo|video))?$|^(continue\\s+assistindo|continue\\s+watching|iniciar\\s+miss[ãa]o\\s+de\\s+v[íi]deo|start\\s+video\\s+quest|play\\s+video)$/i;
        const pickBtn = (labels) => {
            const p = labels.find(t => exactRe.test(t.trim()));
            if (p) return p;
            const fb = labels.filter(t => t.trim() && !excludedRe.test(t.trim()) && /\\b(assistir|continuar|continue\\s+assistindo|watch|ver\\s+v[íi]deo|iniciar\\s+miss[ãa]o|video)\\b/i.test(t.trim()));
            return fb.length ? fb[fb.length - 1] : null;
        };
        if (pickBtn(['Assista já', 'Assistir 14s']) !== 'Assistir 14s') process.exit(1);
        if (pickBtn(['Pré-compra aqui', 'Continuar 26s']) !== 'Continuar 26s') process.exit(2);
        if (pickBtn(['Comprar agora', 'Assistir']) !== 'Assistir') process.exit(3);
        if (pickBtn(['Watch now', 'Watch Video']) !== 'Watch Video') process.exit(4);
        if (pickBtn(['Assista já', 'Assistir novamente']) !== null) process.exit(5);
        process.exit(0);
        """
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(node_code)
            temp_path = f.name
        try:
            res = subprocess.run(['node', temp_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Erro no matcher de CTA de vídeo (código {res.returncode})")
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    @staticmethod
    def _fake_http_resp(payload):
        class _Resp:
            def __init__(self, data):
                self._data = json.dumps(data).encode("utf-8")
            def read(self):
                return self._data
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
        return _Resp(payload)

    def test_discord_launch_retries_when_first_attempt_hangs(self):
        """Verifica se o lançador do Discord realiza retentativa automática quando a 1ª tentativa trava na splash."""
        popens = []
        json_polls = {"count": 0}

        def fake_urlopen(url, timeout=2):
            if url.endswith("/json/version"):
                return self._fake_http_resp({"Browser": "Chrome/130.0.0.0"})
            if url.endswith("/json"):
                json_polls["count"] += 1
                # Primeira tentativa (45 polls) fica presa sem janela principal; 2ª tentativa abre janela
                if json_polls["count"] <= 45:
                    return self._fake_http_resp([])
                return self._fake_http_resp([{"type": "page", "url": "https://canary.discord.com/channels/@me", "title": "Discord"}])
            raise AssertionError(f"URL inesperada: {url}")

        fake_driver = MagicMock()
        fake_driver.window_handles = ["win-1"]
        fake_driver.current_url = "https://canary.discord.com/channels/@me"
        fake_driver.execute_script.return_value = True

        orig_abort = RewardsCore.ABORTAR_PROCESSO
        RewardsCore.ABORTAR_PROCESSO = False
        try:
            with patch.object(DiscordQuests.time, "sleep", return_value=None), \
                 patch.object(DiscordQuests, "_encerrar_processo_discord"), \
                 patch.object(DiscordQuests, "localizar_aplicativo_discord", return_value=(r"C:\Fake\DiscordCanary.exe", "DiscordCanary.exe")), \
                 patch.object(DiscordQuests, "bloquear_update_discord"), \
                 patch.object(DiscordQuests.subprocess, "Popen", side_effect=lambda *a, **k: popens.append(MagicMock()) or popens[-1]), \
                 patch.object(DiscordQuests.urllib.request, "urlopen", side_effect=fake_urlopen), \
                 patch.object(DiscordQuests.webdriver, "Chrome", return_value=fake_driver):

                driver, proc, handle, _, _ = DiscordQuests._abrir_sessao_discord(
                    0,
                    {"nome": "Lote Local", "usa_vpn": False},
                    r"C:\Fake\DiscordCanary.exe",
                    "DiscordCanary.exe",
                    {"modo_oculto": "s"},
                    porta_debug=9222,
                    max_tentativas=2
                )

                self.assertIs(driver, fake_driver)
                self.assertEqual(handle, "win-1")
                self.assertEqual(len(popens), 2)
        finally:
            RewardsCore.ABORTAR_PROCESSO = orig_abort

    def test_discord_launch_exhausts_retries_returns_none(self):
        """Se todas as tentativas travarem na splash screen, retorna None sem levantar exceção."""
        def fake_urlopen(url, timeout=2):
            if url.endswith("/json/version"):
                return self._fake_http_resp({"Browser": "Chrome/130.0.0.0"})
            return self._fake_http_resp([])

        popens = []
        orig_abort = RewardsCore.ABORTAR_PROCESSO
        RewardsCore.ABORTAR_PROCESSO = False
        try:
            with patch.object(DiscordQuests.time, "sleep", return_value=None), \
                 patch.object(DiscordQuests, "_encerrar_processo_discord"), \
                 patch.object(DiscordQuests, "localizar_aplicativo_discord", return_value=(r"C:\Fake\DiscordCanary.exe", "DiscordCanary.exe")), \
                 patch.object(DiscordQuests, "bloquear_update_discord"), \
                 patch.object(DiscordQuests.subprocess, "Popen", side_effect=lambda *a, **k: popens.append(MagicMock()) or popens[-1]), \
                 patch.object(DiscordQuests.urllib.request, "urlopen", side_effect=fake_urlopen):

                driver, proc, handle, _, _ = DiscordQuests._abrir_sessao_discord(
                    0,
                    {"nome": "Lote Local", "usa_vpn": False},
                    r"C:\Fake\DiscordCanary.exe",
                    "DiscordCanary.exe",
                    {"modo_oculto": "s"},
                    porta_debug=9222,
                    max_tentativas=2
                )

                self.assertIsNone(driver)
                self.assertIsNone(proc)
                self.assertIsNone(handle)
                self.assertEqual(len(popens), 2)
        finally:
            RewardsCore.ABORTAR_PROCESSO = orig_abort

    def test_quests_navigation_ignores_message_requests_in_node(self):
        """Garante que [data-list-item-id*='quests'] foi removido e /message-requests nunca é confundido com Missões."""
        self.assertNotIn('data-list-item-id*="quests"', DiscordQuests._NAVIGATE_TO_QUESTS_JS)
        node_test = f"""
        const checkPath = (p) => {{
            globalThis.window = {{ location: {{ pathname: p }} }};
            return (function() {{ {DiscordQuests._IS_QUESTS_PATH_JS} }})();
        }};
        if (checkPath('/message-requests') !== false) process.exit(1);
        if (checkPath('/channels/@me') !== false) process.exit(2);
        if (checkPath('/quest-home') !== true) process.exit(3);
        if (checkPath('/quests/123') !== true) process.exit(4);

        const makeEl = (attrs, text, children = []) => ({{
            attrs,
            textContent: text,
            children,
            clicked: false,
            click() {{ this.clicked = true; }},
            getAttribute(k) {{ return this.attrs[k] ?? null; }},
            closest() {{ return this; }},
            querySelectorAll() {{ return []; }}
        }});

        const msgReq = makeEl({{ 'data-list-item-id': 'private-channels-uid_1___message-requests', href: '/message-requests' }}, 'Solicitações de mensagens');
        const questsNoHref = makeEl({{ 'data-list-item-id': 'private-channels-uid_1___quests' }}, 'Missões');
        const allEls = [msgReq, questsNoHref];

        globalThis.document = {{
            querySelector(sel) {{ return null; }},
            querySelectorAll(sel) {{ return sel === '[data-list-item-id]' ? allEls : []; }}
        }};

        // Caso 1: já está em /quest-home -> não clica em nada
        globalThis.window = {{ location: {{ pathname: '/quest-home' }} }};
        const r1 = (function() {{ {DiscordQuests._NAVIGATE_TO_QUESTS_JS} }})();
        if (r1 !== 'already_on_quests' || msgReq.clicked || questsNoHref.clicked) process.exit(5);

        // Caso 2: está em /channels/@me -> seleciona ___quests e nunca ___message-requests
        globalThis.window = {{ location: {{ pathname: '/channels/@me' }} }};
        const r2 = (function() {{ {DiscordQuests._NAVIGATE_TO_QUESTS_JS} }})();
        if (r2 !== 'clicked' || msgReq.clicked || !questsNoHref.clicked) process.exit(6);
        process.exit(0);
        """
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(node_test)
            temp_path = f.name
        try:
            res = subprocess.run(['node', temp_path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Falha na lógica de navegação Quests vs Message Requests (código {res.returncode}): {res.stderr}")
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    def test_navegar_para_missoes_keeps_quest_home_without_reload(self):
        """Se já estiver em /quest-home com tiles visíveis, _navegar_para_missoes retorna True sem driver.get."""
        fake_driver = MagicMock()
        fake_driver.execute_script.side_effect = [
            "already_on_quests",  # _NAVIGATE_TO_QUESTS_JS
            True,                 # WebDriverWait predicate
            True,                 # _IS_QUESTS_PATH_JS
        ]
        orig_abort = RewardsCore.ABORTAR_PROCESSO
        RewardsCore.ABORTAR_PROCESSO = False
        try:
            ok = DiscordQuests._navegar_para_missoes(fake_driver, canal_lixo="")
            self.assertTrue(ok)
            fake_driver.get.assert_not_called()
        finally:
            RewardsCore.ABORTAR_PROCESSO = orig_abort

if __name__ == '__main__':
    unittest.main()

