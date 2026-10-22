from pathlib import Path
import webview
import pystray
from PIL import Image, ImageDraw
import threading
import time
import sys
import os
import RewardsCore

def resource_path(relative_path):
    try:
        # PyInstaller cria uma pasta temporária e guarda o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MiniPanelAPI:
    def __init__(self, janela_principal, janela_popup):
        self.janela_principal = janela_principal
        self.janela_popup = janela_popup

    def fechar_popup(self):
        GerenciadorBandeja.fechar_popup_sistema()

    def kill_switch(self):
        print("[SISTEMA] Kill Switch Acionado! Exterminando processos...")
        
        # 1. Avisa a Máquina de Estados para abortar tudo
        RewardsCore.ABORTAR_PROCESSO = True
        
        # 2. Desmonta o íícone da bandeja sem deixar fantasmas
        GerenciadorBandeja.parar_tray()
        
        # 3. Destrói as janelas e corta o processo na raiz
        try: self.janela_popup.destroy()
        except Exception: pass
        try: self.janela_principal.destroy()
        except Exception: pass
        os._exit(0)

    def mudar_marcha(self, nova_marcha):
        print(f"[SISTEMA] Marcha alterada para: {nova_marcha}")
        RewardsCore.SPEED = nova_marcha
        RewardsCore.LOGGER(f"[SISTEMA] ⚙️ Marcha alterada em tempo real para: {nova_marcha.upper()}", "warning")

class SysTrayApp:
    def __init__(self):
        self.janela_principal = None
        self.janela_popup = None
        self.iícone_tray = None
        self.sessao_ativa = False
        self.tempo_inicio = 0
        self.popup_aberto = False
        self.ultimo_toggle = 0

    def gerar_iícone_emergencia(self):
        """Cria um íícone azul com um círculo branco na memória, caso a foto .ico falte"""
        imagem = Image.new('RGB', (64, 64), color=(14, 165, 233))
        desenho = ImageDraw.Draw(imagem)
        desenho.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
        return imagem

    def acao_clique_esquerdo(self, iícone, item):
        if not self.janela_popup:
            return

        agora = time.time()
        if agora - self.ultimo_toggle < 0.4:
            return
        self.ultimo_toggle = agora

        if self.popup_aberto:
            self.fechar_popup_sistema()
        else:
            self.abrir_popup_sistema()

    def abrir_popup_sistema(self):
        if self.janela_popup and not self.popup_aberto:
            try:
                telas = webview.screens
                if telas:
                    tela = telas[0]
                    x = tela.width - 340 
                    y = tela.height - 380 
                    self.janela_popup.move(x, y)
            except Exception: pass
            
            # Avisa o JS" para desarmar o blur ANTES" de mostrar a janela
            try:
                self.janela_popup.evaluate_js("reiniciarFoco();")
            except Exception: pass

            self.janela_popup.show()
            self.janela_popup.restore()
            self.popup_aberto = True
            
            # Rearma a carência de foco
            try:
                self.janela_popup.evaluate_js("armarAutoClose();")
            except Exception: pass

    def fechar_popup_sistema(self):
        if self.janela_popup and self.popup_aberto:
            # Desarma o blur no JS" imediatamente para evitar conflitos de fechamento
            try:
                self.janela_popup.evaluate_js("reiniciarFoco();")
            except Exception: pass

            try: self.janela_popup.move(-2000, -2000)
            except Exception: pass
            self.janela_popup.hide()
            self.popup_aberto = False
            self.ultimo_toggle = time.time()

    def acao_clique_direito(self, iícone, item):
        if self.janela_principal:
            self.janela_principal.show()
            self.janela_principal.restore()
            
    def parar_tray(self):
        """Remove o íícone da bandeja graciosamente para não deixar rastro"""
        if self.iícone_tray:
            self.iícone_tray.stop()
            self.iícone_tray = None

    def acao_sair(self, iícone, item):
        self.parar_tray()
        if self.janela_popup:
            try: self.janela_popup.destroy()
            except Exception: pass
        if self.janela_principal:
            try: self.janela_principal.destroy()
            except Exception: pass
        os._exit(0)

    def iniciar_tray_em_background(self):
        if self.iícone_tray is not None:
            return
            
        # Tenta carregar a imagem embutida no EXE ou gera a de emergência
        try:
            caminho_iícone = resource_path("rewards.ico")
            if os.path.exists(caminho_iícone):
                imagem = Image.open(caminho_iícone)
            else:
                imagem = self.gerar_iícone_emergencia()
        except Exception:
            imagem = self.gerar_iícone_emergencia()

        try:
            cfg = RewardsCore.carregar_config()
            lang = cfg.get("language", "pt")
        except Exception:
            lang = "pt"
            
        lbl_main = "Open Main Bot" if lang == "en" else "Abrir Bot Principal"
        lbl_exit = "Exit" if lang == "en" else "Fechar"
        
        menu = pystray.Menu(
            pystray.MenuItem("Toggle Panel", self.acao_clique_esquerdo, default=True, visible=False),
            pystray.MenuItem(lbl_main, self.acao_clique_direito),
            pystray.MenuItem(lbl_exit, self.acao_sair)
        )
        self.iícone_tray = pystray.Icon("RewardsBot", imagem, "Reward Bot", menu)
        
        thread_tray = threading.Thread(target=self.iícone_tray.run, daemon=True)
        thread_tray.start()

    def atualizar_progresso(self, servico, porcentagem, status, cor):
        if self.janela_popup:
            js = f"updateBar('{servico}', {porcentagem}, '{status}', '{cor}');"
            self.janela_popup.evaluate_js(js)

    def iniciar_cronometro(self):
        self.sessao_ativa = True
        self.tempo_inicio = time.time()
        threading.Thread(target=self._loop_cronometro, daemon=True).start()

    def parar_cronometro(self):
        self.sessao_ativa = False

    def _loop_cronometro(self):
        while self.sessao_ativa:
            segundos_totais = int(time.time() - self.tempo_inicio)
            horas = segundos_totais // 3600
            minutos = (segundos_totais % 3600) // 60
            segundos = segundos_totais % 60
            tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            
            if self.janela_popup:
                self.janela_popup.evaluate_js(f"updateTimer('{tempo_formatado}');")
            time.sleep(1)


# ==========================================
# C"DIGO HTML/CSS/JS" DO POPUP
def carregar_html_ui(nome_arquivo):
    base_dir = getattr(sys, '_MEIPASS', Path(__file__).parent)
    caminho = Path(base_dir) / "ui" / nome_arquivo
    if not caminho.exists():
        caminho = Path(__file__).parent / "ui" / nome_arquivo
    return caminho.read_text(encoding="utf-8")

HTML_POPUP = carregar_html_ui("popup.html")

GerenciadorBandeja = SysTrayApp()