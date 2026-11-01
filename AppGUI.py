import sys
import webview  # pyrefly: ignore [missing-import]
import threading
import socket
import os
import platform
import subprocess
import json
import time
import ctypes
import signal
import shutil
from datetime import datetime
from pathlib import Path

import RewardsCore 
import DiscordQuests
from MiniPanel import GerenciadorBandeja, HTML_POPUP, MiniPanelAPI

APP_NAME = "Reward Bot"
APP_VERSION = "v3.2.2"
APP_CODENAME = "Intelligent Bypass"

def carregar_html_ui(nome_arquivo):
    base_dir = getattr(sys, '_MEIPASS', Path(__file__).parent)
    caminho = Path(base_dir) / "ui" / nome_arquivo
    if not caminho.exists():
        caminho = Path(__file__).parent / "ui" / nome_arquivo
    return caminho.read_text(encoding="utf-8")

HTML_INTERFACE = carregar_html_ui("index.html")
HTML_INTERFACE = HTML_INTERFACE.replace("[APP_NAME]", APP_NAME)
HTML_INTERFACE = HTML_INTERFACE.replace("[APP_VERSION]", APP_VERSION)
HTML_INTERFACE = HTML_INTERFACE.replace("[APP_CODENAME]", APP_CODENAME)

class BotAPI:
    def __init__(self):
        self.rodando = False
        RewardsCore.LOGGER = self.log_ui
        
    def verificar_discord(self):
        exe_path, _ = DiscordQuests.localizar_aplicativo_discord()
        return bool(exe_path)
        
    def log_ui(self, texto, tipo='info'):
        # 1. Envia para a janela do pywebview
        try:
            t_seguro = str(texto).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            if webview.windows:
                webview.windows[0].evaluate_js(f"log('{t_seguro}', '{tipo}')")
        except Exception: 
            pass

        # 2. Imprime no console nativo ignorando emojis que o Windows não suporta
        try:
            print(str(texto).encode('utf-8').decode('cp1252', 'ignore'))
        except Exception: 
            pass

        # 3. Grava imediatamente no arquivo de log da sessão no disco (logs/run_*.txt)
        try:
            import re
            from datetime import datetime
            texto_limpo = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', str(texto))
            if RewardsCore.RUN_LOG_PATH:
                with open(RewardsCore.RUN_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{tipo.upper()}] {texto_limpo}\n")
                    f.flush()
        except Exception:
            pass

    def fechar_janela(self):
        self.parar()
        GerenciadorBandeja.parar_tray()
        webview.windows[0].destroy()
        os._exit(0)
        
    def minimizar_janela(self):
        webview.windows[0].hide()
        
    def checar_atualizacao(self):
        def radar_silencioso():
            try:
                import urllib.request
                import json
                
                # Bate na porta da API do seu repositório
                url = "https://api.github.com/repos/FPGAMESBR/CoreNexusBot/releases/latest"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    dados = json.loads(response.read().decode('utf-8'))
                    versao_nuvem = dados.get("tag_name", "").strip()
                    
                    # Se a versão da nuvem for diferente da local, dispara o alerta na UI
                    if versao_nuvem and versao_nuvem != APP_VERSION:
                        webview.windows[0].evaluate_js(f"mostrarAvisoUpdate('{versao_nuvem}')")
            except Exception:
                pass # Falhou por falta de internet ou limite de API? Ignora silenciosamente.

        # Roda em uma thread separada para não travar a abertura do bot
        threading.Thread(target=radar_silencioso, daemon=True).start()

    def iniciar(self):
        if self.rodando: 
            self.log_ui(RewardsCore.t("ja_em_execucao"), "error")
            return
            
        self.rodando = True
        RewardsCore.ABORTAR_PROCESSO = False 
        
        # Garante arquivo de log dedicado para este ciclo
        try:
            from datetime import datetime
            agora_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            RewardsCore.RUN_LOG_PATH = RewardsCore.logs / f"run_{agora_str}.txt"
            RewardsCore.RUN_LOG_PATH.touch(exist_ok=True)
        except Exception:
            pass
            
        try:
            if webview.windows:
                webview.windows[0].evaluate_js("switchTab('console', document.querySelectorAll('.nav-item')[0]);")
        except Exception:
            pass
        self.log_ui("Initializing Stealth loop...", "info")
        
        # INICIA O CRONÔMETRO NO MINI-PAINEL
        GerenciadorBandeja.iniciar_cronometro()
        
        threading.Thread(target=self.loop_farm, daemon=True).start()
        threading.Thread(target=DiscordQuests.iniciar_farm_discord, daemon=True).start()

    def parar(self):
        self.log_ui("KILL SWITCH ACTIVATED. Initiating safe shutdown...", "error")
        self.rodando = False
        RewardsCore.ABORTAR_PROCESSO = True 
        
        # PARA O CRONÔMETRO NO MINI-PAINEL E ZERA AS BARRAS
        GerenciadorBandeja.parar_cronometro()
        RewardsCore.update_ui("discord", "Inativo", 0)
        RewardsCore.update_ui("bing", "Inativo", 0)
        
        sistema = platform.system().lower()
        if sistema == "windows":
            subprocess.run("taskkill /F /T /IM chromedriver.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("taskkill /F /T /IM DiscordCanary.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("taskkill /F /T /IM DiscordPTB.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sistema in ["linux", "darwin"]:
            subprocess.run("pkill -9 -f chromedriver", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -9 -f DiscordCanary", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -9 -f DiscordPTB", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        self.log_ui("All background drivers and proxies terminated gracefully.", "warning")

    def loop_farm(self):
        try:
            RewardsCore.preparar_ambiente_adb()
            RewardsCore.iniciar_ciclo_farm()
            
            RewardsCore.registrar_data_execucao("rewards")
            
            self.log_ui("FARM COMPLETED SUCCESSFULLY!", "success")
        except Exception as e:
            self.log_ui(f"Fatal error: {e}", "error")
        finally:
            self.rodando = False

    def listar_contas(self): return RewardsCore.atualizar_lista_contas()
    
    def deletar_conta(self, nome_perfil):
        if nome_perfil == "DefaultAccount":
            self.log_ui("DefaultAccount is the master profile and cannot be deleted.", "error")
            return self.listar_contas()
            
        caminho = RewardsCore.BASE_PROFILES_DIR / nome_perfil
        try:
            if caminho.exists():
                shutil.rmtree(caminho, ignore_errors=True)
            self.log_ui(f"Profile '{nome_perfil}' deleted successfully.", "warning")
        except Exception as e:
            self.log_ui(f"Failed to delete profile: {e}", "error")
        return self.listar_contas()

    def abrir_setup_conta(self, nome_perfil):
        if self.rodando:
            self.log_ui("Stop the bot before opening setup!", "error")
            return
        self.log_ui(f"Opening browser for '{nome_perfil}'...", "warning")
        threading.Thread(target=RewardsCore.modo_configuracao, args=(nome_perfil,), daemon=True).start()

    def obter_status_startup(self):
        sistema = platform.system().lower()
        if sistema == "windows":
            caminho = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "RewardsBot_Startup.vbs")
        elif sistema == "linux":
            caminho = os.path.expanduser("~/.config/autostart/RewardsBot.desktop")
        elif sistema == "darwin":
            caminho = os.path.expanduser("~/Library/LaunchAgents/com.fpg.rewardsbot.plist")
        else: 
            return False
            
        return os.path.exists(caminho)

    def toggle_startup(self):
        RewardsCore.alternar_startup()
        time.sleep(0.5) 
        estado = self.obter_status_startup()
        webview.windows[0].evaluate_js(f"atualizarBotaoStartup({str(estado).lower()})")
        self.rodar_diagnostico_ui()

    def carregar_configuracoes_ui(self):
        try:
            cfg = RewardsCore.carregar_config()
            webhook_seguro = json.dumps(cfg.get('webhook_url', ''))
            quests_webhook_seguro = json.dumps(cfg.get('quests_webhook_url', ''))
            canal_lixo_seguro = json.dumps(cfg.get('discord_trash_channel', ''))
            lang = cfg.get("language", "pt")
            
            # Injeta o parâmetro cfg.get('discord_global_quests') no final da função JS
            js_cmd = f"popularConfig({cfg.get('limite_pc', 30)}, {cfg.get('limite_mobile', 20)}, '{cfg.get('modo_oculto', 's')}', '{cfg.get('fazer_tarefas', 's')}', '{cfg.get('do_discord', 'n')}', '{cfg.get('multi_account', 'n')}', {cfg.get('discord_cooldown', 3)}, {webhook_seguro}, {quests_webhook_seguro}, {canal_lixo_seguro}, '{lang}', '{cfg.get('ms_new_tasks', 's')}', '{cfg.get('discord_global_quests', 'n')}', '{cfg.get('extended_days', 'n')}', '{cfg.get('speed_mode', 'normal')}')"
            
            webview.windows[0].evaluate_js(js_cmd)
            estado_startup = self.obter_status_startup()
            webview.windows[0].evaluate_js(f"atualizarBotaoStartup({str(estado_startup).lower()})")
        except Exception as e:
            self.log_ui(f"Config load error: {e}", "error")

    def salvar_configuracoes_ui(self, dados_html):
        cfg_atual = RewardsCore.carregar_config()
        cfg_atual['limite_pc'] = int(dados_html['pc'])
        cfg_atual['limite_mobile'] = int(dados_html['mob'])
        
        cfg_atual['modo_oculto'] = 's' if dados_html['headless'] else 'n'
        cfg_atual['fazer_tarefas'] = 's' if dados_html['tasks'] else 'n'
        cfg_atual['do_discord'] = 's' if dados_html['discord'] else 'n'
        cfg_atual['multi_account'] = 's' if dados_html['multi'] else 'n'
        cfg_atual['ms_new_tasks'] = 's' if dados_html['ms_new_tasks'] else 'n'
        
        # Salva o status do botão Global no config.json
        cfg_atual['discord_global_quests'] = 's' if dados_html['discord_global_quests'] else 'n'
        
        cfg_atual['discord_cooldown'] = int(dados_html['discord_cooldown'])
        cfg_atual['webhook_url'] = dados_html['webhook']
        cfg_atual['quests_webhook_url'] = dados_html.get('quests_webhook', '')
        cfg_atual['discord_trash_channel'] = dados_html.get('canal_lixo_url', '')
        
        cfg_atual['speed_mode'] = dados_html.get('speed_mode', 'normal')
        cfg_atual['language'] = dados_html.get('lang', 'pt')
        if 'vpn_user' in cfg_atual: del cfg_atual['vpn_user']
        if 'vpn_pass' in cfg_atual: del cfg_atual['vpn_pass']
        if 'vpn_host' in cfg_atual: del cfg_atual['vpn_host']
        if 'vpn_port' in cfg_atual: del cfg_atual['vpn_port']
        RewardsCore.SPEED = cfg_atual['speed_mode']
        
        # Invalida cache de tradução para recarregar no novo idioma
        RewardsCore._LOCALES_CACHE = None
        
        RewardsCore.salvar_config(cfg_atual)
        self.log_ui(RewardsCore.t("conf_salva"), "success")
        webview.windows[0].evaluate_js("switchTab('console', document.querySelectorAll('.nav-item')[0]);")
        self.rodar_diagnostico_ui()

    def rodar_diagnostico_ui(self):
        resultados_html = ""
        def add_item(nome, status, color_type):
            cor = {"green": "var(--accent-green)", "yellow": "var(--accent-yellow)", "red": "var(--accent-red)"}.get(color_type, "var(--accent-red)")
            nonlocal resultados_html 
            resultados_html += f"<div class='mini-diag-item'><span style='color: var(--text-muted);'>{nome}</span><span style='color: {cor}; font-weight: bold;'>● {status}</span></div>"

        v_chrome = RewardsCore.obter_versao_chrome()
        
        if not hasattr(self, 'chrome_stable_version'):
            self.chrome_stable_version = None
            self.chrome_version_checking = False

        if self.chrome_stable_version is None and not self.chrome_version_checking:
            self.chrome_version_checking = True
            def bg_check():
                try:
                    import urllib.request, json
                    req = urllib.request.Request("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode())
                        self.chrome_stable_version = int(data['channels']['Stable']['version'].split('.')[0])
                except Exception:
                    self.chrome_stable_version = 0
                self.rodar_diagnostico_ui()

            import threading
            threading.Thread(target=bg_check, daemon=True).start()

        cfg = RewardsCore.carregar_config()
        ui_lang = cfg.get("language", "en")
        
        if v_chrome:
            if self.chrome_stable_version is None:
                txt_check = "Verificando..." if ui_lang == "pt" else "Checking..."
                add_item("Chrome", f"v{v_chrome} ({txt_check})", 'yellow')
            elif self.chrome_stable_version > 0:
                if v_chrome < self.chrome_stable_version:
                    txt_outdated = "Desatualizado" if ui_lang == "pt" else "Outdated"
                    add_item("Chrome", f"v{v_chrome} ({txt_outdated})", 'red')
                else:
                    txt_updated = "Atualizado" if ui_lang == "pt" else "Updated"
                    add_item("Chrome", f"v{v_chrome} ({txt_updated})", 'green')
            else:
                add_item("Chrome", f"v{v_chrome}", 'green')
        else:
            add_item("Chrome", "Error", 'red')
        
        if cfg.get("multi_account", "n") == "s":
            ext = ".exe" if platform.system().lower() == "windows" else ""
            caminho_adb = RewardsCore.BASE_DIR / "platform-tools" / f"adb{ext}"
            txt_adb = ("Pronto" if ui_lang == "pt" else "Ready") if caminho_adb.exists() else ("Ausente" if ui_lang == "pt" else "Missing")
            add_item("ADB Core", txt_adb, 'green' if caminho_adb.exists() else 'yellow')
        else:
            txt_not_needed = "Não necessário" if ui_lang == "pt" else "Not needed"
            add_item("ADB Core", txt_not_needed, 'green')

        RewardsCore.BASE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        pastas = [p.name for p in RewardsCore.BASE_PROFILES_DIR.iterdir() if p.is_dir()]
        txt_prof = (f"{len(pastas)} Encontrado(s)" if ui_lang == "pt" else f"{len(pastas)} Found") if pastas else ("Vazio" if ui_lang == "pt" else "Empty")
        add_item("Profiles", txt_prof, 'green' if pastas else 'yellow')

        is_startup_active = self.obter_status_startup()
        txt_startup = ("LIGADO" if ui_lang == "pt" else "ON") if is_startup_active else ("DESLIGADO" if ui_lang == "pt" else "OFF")
        add_item("Startup", txt_startup, 'green' if is_startup_active else 'yellow')
        try:
            webview.windows[0].evaluate_js(f"atualizarBotaoStartup({str(is_startup_active).lower()})")
        except Exception:
            pass

        if cfg.get("do_discord", "n") != "s":
            txt_disc_dis = "Desativado" if ui_lang == "pt" else "Disabled"
            add_item("Discord Bot", txt_disc_dis, 'red')
        else:
            exe_path, _ = DiscordQuests.localizar_aplicativo_discord()
            if not exe_path:
                txt_disc_miss = "App Ausente" if ui_lang == "pt" else "App Missing"
                add_item("Discord Bot", txt_disc_miss, 'red')
            else:
                txt_disc_ready = "Pronto" if ui_lang == "pt" else "Ready"
                if not RewardsCore.ARQUIVO_LOG.exists():
                    add_item("Discord Bot", txt_disc_ready, 'green')
                else:
                    try:
                        with open(RewardsCore.ARQUIVO_LOG, "r", encoding="utf-8") as f:
                            dados_log = json.load(f)
                            hist_discord = dados_log.get("discord", [])
                            if not hist_discord:
                                add_item("Discord Bot", txt_disc_ready, 'green')
                            else:
                                ultima_data_str = hist_discord[-1]
                                formato = "%d/%m/%Y" if len(ultima_data_str.split('/')[-1]) == 4 else "%d/%m/%y"
                                ultima_data = datetime.strptime(ultima_data_str, formato)
                                dias_passados = (datetime.now() - ultima_data).days
                                cooldown_dias = int(cfg.get("discord_cooldown", 3))
                                
                                if dias_passados < cooldown_dias:
                                    txt_wait = f"Aguarde {cooldown_dias - dias_passados}d" if ui_lang == "pt" else f"Wait {cooldown_dias - dias_passados}d"
                                    add_item("Discord Bot", txt_wait, 'yellow')
                                else:
                                    add_item("Discord Bot", txt_disc_ready, 'green')
                    except Exception:
                        add_item("Discord Bot", txt_disc_ready, 'green')

        html_seguro = json.dumps(resultados_html)
        try:
            if webview.windows:
                webview.windows[0].evaluate_js(f"renderDiagnostics({html_seguro})")
        except Exception:
            pass

def aguardar_internet(timeout_horas=1):
    """Verifica conectividade com a internet de forma rápida a cada 4 segundos no boot."""
    inicio = time.time()
    limite_segundos = timeout_horas * 3600
    
    while (time.time() - inicio) < limite_segundos:
        try:
            import urllib.request
            # Testa rapidamente o Google ou a Microsoft
            urllib.request.urlopen("https://www.google.com", timeout=3)
            return True
        except Exception:
            try:
                urllib.request.urlopen("https://www.bing.com", timeout=3)
                return True
            except Exception:
                time.sleep(4)
    return False

def registrar_interceptador_os(api_instance):
    def encerramento_seguro(*args, **kwargs):
        api_instance.log_ui("OS SHUTDOWN DETECTED! Pausando para salvar dados...", "warning")
        
        # 1. Corta a energia do loop do bot imediatamente
        RewardsCore.ABORTAR_PROCESSO = True
        api_instance.rodando = False
        
        # 2. Desmonta a bandeja para evitar ííícones duplicados
        try: GerenciadorBandeja.parar_tray()
        except Exception: pass
        
        time.sleep(4)
        
        # 3. Libera o desligamento
        return True

    sistema = platform.system().lower()
    if sistema == "windows":
        try:
            @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)
            def handler_desligamento(ctrl_type):
                # 2=Fechamento do terminal, 5=Logoff, 6=Desligamento do Windows
                if ctrl_type in (2, 5, 6): 
                    return encerramento_seguro()
                return False
            
            global _hook_desligamento 
            _hook_desligamento = handler_desligamento
            ctypes.windll.kernel32.SetConsoleCtrlHandler(_hook_desligamento, True)
        except Exception: pass
    else:
        # Sinais nativos POSIX (Garante a compatibilidade com Linux e macOS)
        try:
            signal.signal(signal.SIGINT, encerramento_seguro)
            signal.signal(signal.SIGTERM, encerramento_seguro)
        except Exception: pass

if __name__ == '__main__':
    import sys
    
    modo_startup = False
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        modo_startup = True
        if not aguardar_internet(timeout_horas=1):
            sys.exit(1)

    api = BotAPI()
    registrar_interceptador_os(api)
    
    janela_principal = webview.create_window(title=f'{APP_NAME} {APP_VERSION}', html=HTML_INTERFACE, js_api=api, frameless=True, easy_drag=False, width=1050, height=720, background_color='#070b14', resizable=False, hidden=modo_startup)
    
    # ATUALIZAÇÃO DA ALTURA PARA 320 PARA ACOMODAR OS" BOTÕES" DE VELOCIDADE
    janela_popup = webview.create_window(
        'Painel Invisivel', 
        html=HTML_POPUP, 
        width=320, height=320,  
        frameless=True,      
        transparent=True,    
        on_top=True,         
        hidden=True,         
        x=-2000, y=-2000,
        background_color='#111827' 
    )

    def interceptar_fechamento_principal():
        try: janela_principal.hide()
        except Exception: pass
        return False  

    def interceptar_fechamento_popup():
        try: GerenciadorBandeja.fechar_popup_sistema()
        except Exception: pass
        return False  

    janela_principal.events.closing += interceptar_fechamento_principal
    janela_popup.events.closing += interceptar_fechamento_popup

    api_popup = MiniPanelAPI(janela_principal, janela_popup)
    # INCLUSÃO DO EXPOSE PARA O BOTÃO DE MARCHA (VELOCIDADE) FUNCIONAR
    try: janela_popup.expose(api_popup.fechar_popup, api_popup.kill_switch, api_popup.set_marcha)
    except Exception: janela_popup.expose(api_popup.fechar_popup, api_popup.kill_switch)

    GerenciadorBandeja.janela_principal = janela_principal
    GerenciadorBandeja.janela_popup = janela_popup

    GerenciadorBandeja.iniciar_tray_em_background()
    
    # === NOVO: COORDENADOR DE AUTO-CLOSE (FILA SEQUENCIAL BLINDADA) ===
    def coordenador_auto_close():
        if modo_startup:
            api.log_ui("[SISTEMA] Modo Startup: Aplicando delay de segurança (15s)...", "info")
            time.sleep(15)
            
        cfg = RewardsCore.carregar_config()
        
        # 1. O Fim do Fogo Amigo: Limpa processos ANTES" de iniciar os bots em paralelo
        RewardsCore.limpar_processos_zumbis()
        
        # 2. Inicia os robôs em threads paralelas
        import threading
        
        threads = []
        if cfg.get("do_discord", "n") == "s":
            t_discord = threading.Thread(target=DiscordQuests.iniciar_farm_discord, daemon=True)
            threads.append(t_discord)
            t_discord.start()
            
        rodar_rewards = not RewardsCore.verificar_se_rodou_hoje("rewards", dias_cooldown=0)
        if rodar_rewards and not RewardsCore.ABORTAR_PROCESSO:
            t_bing = threading.Thread(target=api.loop_farm, daemon=True)
            threads.append(t_bing)
            t_bing.start()
            
        # 3. Aguarda todos terminarem com teto de segurança (evita travamento eterno no startup)
        t_inicio_farm = time.time()
        limite_total_segundos = 3600 # 60 minutos máximo de execução total
        for t in threads:
            tempo_restante = max(10, limite_total_segundos - int(time.time() - t_inicio_farm))
            t.join(timeout=tempo_restante)
            
        # 4. Extermínio total da memória (Garante que o bot feche de verdade)
        if not RewardsCore.ABORTAR_PROCESSO and modo_startup:
            api.log_ui("[SISTEMA] Automação de Startup finalizada. O bot se desligará em 5s...", "warning")
            time.sleep(5)
            
            # Desmonta o íícone da bandeja graciosamente
            try: GerenciadorBandeja.parar_tray()
            except Exception: pass
            
            # Força o sistema operacional a matar a raiz do programa
            import os
            os._exit(0)

    def evento_inicializacao():
        # Atraso estratégico para o Windows renderizar o processo antes de escondê-lo da barra
        def ocultar_telas_seguro():
            time.sleep(0.8)
            try:
                janela_popup.move(-2000, -2000)
                janela_popup.hide()
                if modo_startup:
                    janela_principal.hide()
            except Exception: pass

        threading.Thread(target=ocultar_telas_seguro, daemon=True).start()
        
        if modo_startup:
            try: janela_principal.evaluate_js("skipAnimation();")
            except Exception: pass
            api.rodando = True
            GerenciadorBandeja.iniciar_cronometro()
            # Chama o coordenador em vez de lançar as threads soltas
            threading.Thread(target=coordenador_auto_close, daemon=True).start()

    webview.start(evento_inicializacao)
