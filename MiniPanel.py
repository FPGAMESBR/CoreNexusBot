import webview
import pystray
from PIL import Image, ImageDraw
import threading
import time
import os
import RewardsCore

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
        
        # 2. Desmonta o ícone da bandeja sem deixar fantasmas
        GerenciadorBandeja.parar_tray()
        
        # 3. Destrói as janelas e corta o processo na raiz
        try: self.janela_popup.destroy()
        except: pass
        try: self.janela_principal.destroy()
        except: pass
        os._exit(0)

class SysTrayApp:
    def __init__(self):
        self.janela_principal = None
        self.janela_popup = None
        self.icone_tray = None
        self.sessao_ativa = False
        self.tempo_inicio = 0
        self.popup_aberto = False
        self.ultimo_toggle = 0

    def gerar_icone_emergencia(self):
        """Cria um ícone azul com um círculo branco na memória, caso a foto .ico falte"""
        imagem = Image.new('RGB', (64, 64), color=(14, 165, 233))
        desenho = ImageDraw.Draw(imagem)
        desenho.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
        return imagem

    def acao_clique_esquerdo(self, icone, item):
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
            except: pass
            
            # Avisa o JS para desarmar o blur ANTES de mostrar a janela
            try:
                self.janela_popup.evaluate_js("reiniciarFoco();")
            except: pass

            self.janela_popup.show()
            self.janela_popup.restore()
            self.popup_aberto = True
            
            # Rearma a carência de foco
            try:
                self.janela_popup.evaluate_js("armarAutoClose();")
            except: pass

    def fechar_popup_sistema(self):
        if self.janela_popup and self.popup_aberto:
            # Desarma o blur no JS imediatamente para evitar conflitos de fechamento
            try:
                self.janela_popup.evaluate_js("reiniciarFoco();")
            except: pass

            try: self.janela_popup.move(-2000, -2000)
            except: pass
            self.janela_popup.hide()
            self.popup_aberto = False
            self.ultimo_toggle = time.time()

    def acao_clique_direito(self, icone, item):
        if self.janela_principal:
            self.janela_principal.show()
            self.janela_principal.restore()
            
    def parar_tray(self):
        """Remove o ícone da bandeja graciosamente para não deixar rastro"""
        if self.icone_tray:
            self.icone_tray.stop()
            self.icone_tray = None

    def acao_sair(self, icone, item):
        self.parar_tray()
        if self.janela_popup:
            try: self.janela_popup.destroy()
            except: pass
        if self.janela_principal:
            try: self.janela_principal.destroy()
            except: pass
        os._exit(0)

    def iniciar_tray_em_background(self):
        if self.icone_tray is not None:
            return
            
        # Tenta carregar a imagem original ou gera a de emergência
        try:
            if os.path.exists("rewards.ico"):
                imagem = Image.open("rewards.ico")
            else:
                imagem = self.gerar_icone_emergencia()
        except:
            imagem = self.gerar_icone_emergencia()

        try:
            cfg = RewardsCore.carregar_config()
            lang = cfg.get("language", "pt")
        except:
            lang = "pt"
            
        lbl_main = "Open Main Bot" if lang == "en" else "Abrir Bot Principal"
        lbl_exit = "Exit" if lang == "en" else "Fechar"
        
        menu = pystray.Menu(
            pystray.MenuItem("Toggle Panel", self.acao_clique_esquerdo, default=True, visible=False),
            pystray.MenuItem(lbl_main, self.acao_clique_direito),
            pystray.MenuItem(lbl_exit, self.acao_sair)
        )
        self.icone_tray = pystray.Icon("RewardsBot", imagem, "Reward Bot", menu)
        
        thread_tray = threading.Thread(target=self.icone_tray.run, daemon=True)
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
# CÓDIGO HTML/CSS/JS DO POPUP
# ==========================================
HTML_POPUP = """
<!DOCTYPE html>
<html>
<head>
    <style>
        /* FORÇA A TRANSPARÊNCIA ABSOLUTA NO FUNDO DA JANELA */
        html, body {
            margin: 0; padding: 0; background: transparent !important;
            overflow: hidden; height: 100vh;
        }
        
        /* ENCAPSULA O PAINEL PARA O BORDER-RADIUS FUNCIONAR PERFEITAMENTE */
        .painel-master {
            background: rgba(17, 24, 39, 0.95);
            color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            border-radius: 12px;
            border: 1px solid #334155;
            height: calc(100vh - 2px); width: calc(100vw - 2px);
            margin: 1px; /* O milímetro de respiro para a transparência do Windows atuar */
            box-sizing: border-box;
            display: flex; flex-direction: column; user-select: none;
        }
        
        .header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 15px; border-bottom: 1px solid #334155; background: rgba(30, 41, 59, 0.5);
            border-top-left-radius: 11px; border-top-right-radius: 11px; /* Impede a ponta quadrada de vazar */
        }
        .timer-box { font-size: 13px; font-weight: 600; color: #94a3b8; display: flex; align-items: center; gap: 8px;}
        .close-btn { background: transparent; border: none; color: #64748b; font-size: 16px; cursor: pointer; transition: 0.2s; }
        .close-btn:hover { color: #ef4444; }
        
        .content { padding: 15px; display: flex; flex-direction: column; gap: 15px; }
        
        .module { display: flex; flex-direction: column; gap: 6px; }
        .module-header { display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; }
        .module-title { color: #e2e8f0; }
        .module-status { color: #64748b; }
        
        .progress-bg { width: 100%; height: 6px; background: #334155; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; width: 0%; border-radius: 10px; transition: width 0.4s ease, background 0.4s ease; }
        
        .footer { padding: 10px 15px; text-align: center; margin-top: auto; }
        .kill-btn {
            width: 100%; padding: 10px; background: #ef4444; color: white; border: none; border-radius: 8px;
            font-weight: bold; font-size: 13px; cursor: pointer; transition: 0.2s;
        }
        .kill-btn:hover { background: #dc2626; box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
    </style>
</head>
<body>

    <!-- TUDO AGORA FICA DENTRO DO PAINEL-MASTER -->
    <div class="painel-master">
        <div class="header">
            <div class="timer-box">⏱️ <span id="timer-display">00:00:00</span></div>
            <button class="close-btn" onclick="pywebview.api.fechar_popup()">✕</button>
        </div>

        <div class="content">
            <div class="module">
                <div class="module-header">
                    <span class="module-title">Bing Rewards</span>
                    <span class="module-status" id="bing-status">Inativo</span>
                </div>
                <div class="progress-bg"><div class="progress-fill" id="bing-bar" style="background: #3b82f6;"></div></div>
            </div>

            <div class="module">
                <div class="module-header">
                    <span class="module-title">Discord Quests</span>
                    <span class="module-status" id="discord-status">Inativo</span>
                </div>
                <div class="progress-bg"><div class="progress-fill" id="discord-bar" style="background: #8b5cf6;"></div></div>
            </div>
        </div>

        <div class="footer">
            <button class="kill-btn" onclick="pywebview.api.kill_switch()">FINALIZAR</button>
        </div>
    </div>

    <script>
        let podeFecharPorBlur = false;

        function reiniciarFoco() {
            podeFecharPorBlur = false;
        }

        function armarAutoClose() {
            podeFecharPorBlur = false;
            window.focus();
            
            setTimeout(() => {
                podeFecharPorBlur = true;
                window.focus();
            }, 500);
        }

        function updateTimer(timeStr) {
            document.getElementById('timer-display').innerText = timeStr;
        }
        
        function updateBar(service, percent, statusText, color) {
            document.getElementById(service + '-bar').style.width = percent + '%';
            document.getElementById(service + '-bar').style.background = color;
            document.getElementById(service + '-status').innerText = statusText;
            document.getElementById(service + '-status').style.color = color;
        }

        window.addEventListener('blur', function() {
            if (podeFecharPorBlur) {
                pywebview.api.fechar_popup();
            }
        });
        
        function atualizarPainel(modulo, status, porcentagem) {
        let elStatus = document.getElementById(modulo + '-status');
        let elBarra = document.getElementById(modulo + '-bar');
        
        if (elStatus) elStatus.innerText = status;
        
        if (elBarra) {
            elBarra.style.width = porcentagem + '%';
            
            // Mantém a cor original ou muda para verde (sucesso) no final
            let corBase = modulo === 'bing' ? '#3b82f6' : '#8b5cf6';
            elBarra.style.background = porcentagem === 100 ? '#10b981' : corBase; 
        }
    }
    </script>
</body>
</html>
"""

GerenciadorBandeja = SysTrayApp()