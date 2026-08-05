import re
import time
import datetime
import random
import winreg
import locale
import json
import os
import zipfile
import io
import platform
import stat
import shutil
import sys
import traceback
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import socket
import threading

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

def detectar_idioma():
    """Descobre o idioma do Windows. Retorna 'pt' para português, senão 'en'."""
    try:
        idioma_so, _ = locale.getdefaultlocale()
        if idioma_so and idioma_so.lower().startswith('pt'):
            return "pt"
    except:
        pass
    return "en"

IDIOMA_GLOBAL = detectar_idioma()

TEXTOS = {
    "pt": {
        # ==========================================
        # INTERFACE / MENU
        # ==========================================
        "janela_titulo": "title FPGAMESBR Rewards",
        "menu_titulo": "SELECIONE UMA OPERAÇÃO",
        "op_config": "Modo Configuração (Fazer Login / Criar Conta)",
        "op_manual": "Modo Manual (Iniciar Farm com config. salva)",
        "op_startup": "Ligar/Desligar Startup (Iniciar invisível com o Windows)",
        "op_avancado": "Configurações Avançadas (Webhook, Limites, Headless)",
        "escolha": "> Escolha uma opção (1 a 4): ",
        "fechar": "Pressione ENTER para continuar/fechar...",
        "contas_disp": "CONTAS DISPONÍVEIS:",
        "add_conta": "+ Adicionar Nova Conta",
        "escolha_num": "Escolha o número da conta (ou a opção de adicionar): ",
        "digite_nome": "Digite o nome da nova conta: ",
        "menu_avancado_titulo": "CONFIGURAÇÕES AVANÇADAS & WEBHOOK",
        "dica_enter": "[Dica] Aperte ENTER sem digitar nada para manter o valor atual.",
        "dica_webhook": "[Dica] Digite '0' no Webhook para desativar as notificações.",
        "conf_webhook": "[Discord] URL do Webhook atual",
        "conf_pc": "[Buscas] Limite para PC atual",
        "conf_mob": "[Buscas] Limite para Mobile atual",
        "conf_oculto": "[Sistema] Rodar navegador invisível (Headless)? (s/n)",
        "conf_tarefas": "[Sistema] Fazer tarefas do painel/cards? (s/n)",
        "conf_os_titulo": "[Sistema] Sistema Operacional atual:",
        "conf_os_opcoes": "  [1] Windows  [2] Linux  [3] Mac",
        "conf_os_escolha": "  > Digite 1, 2 ou 3 (ou ENTER para manter): ",
        "voltar_menu": "> Pressione ENTER para voltar ao menu...",
        "discord_sucesso": "✅ **Rewards Bot**\nO farm da conta `{0}` foi finalizado com sucesso às {1}!",

        # ==========================================
        # [SYSTEM] - NÚCLEO, ARQUIVOS E OS
        # ==========================================
        "invalido": "[SYSTEM] [!] Opção inválida! Fechando o bot...",
        "nome_inv": "[SYSTEM] [!] Nome inválido!",
        "op_inv": "[SYSTEM] [!] Opção inválida!",
        "ent_inv": "[SYSTEM] [!] Entrada inválida!",
        "carregando": "[SYSTEM] [INFO] Carregando preferências do RewardsConfig.json...",
        "sucesso": "[SYSTEM] [SUCESSO] Ciclo completo finalizado!",
        "conf_salva": "[SYSTEM] [OK] Configurações salvas com sucesso no arquivo 'RewardsConfig.json'!",
        "startup_desativado": "[SYSTEM] [!] Startup Desativado: O bot não iniciará mais com o OS.",
        "startup_erro_rem": "[SYSTEM] [X] Erro ao remover startup:",
        "startup_ativado": "[SYSTEM] [OK] Startup Ativado: O bot iniciará 100% invisível com o OS!",
        "startup_erro_criar": "[SYSTEM] [X] Erro ao criar startup:",
        "modo_config_salvo": "[SYSTEM] -> Configuração salva para",
        "erro_notificacao": "[SYSTEM] [!] Aviso: Falha ao enviar notificação: {}",
        "otimizando_historico": "[SYSTEM] -> Otimizando arquivo de histórico no disco...",
        "zumbi_clean": "\n[SYSTEM] Escaneando e eliminando processos zumbis (chromedriver)...",
        "alerta_ban": "⛔ **ALERTA CRÍTICO** ⛔\nA conta `{0}` parece ter sido SUSPENSA pela Microsoft! O bot abortou o farm para este perfil.",
        "crash_log": "[SYSTEM] Erro fatal detectado! Crash log salvo em: {0}",
        "crash_sos": "🚨 **ERRO FATAL (Crash)** 🚨\nO motor principal do bot desarmou!\n**Log gerado:** `{0}`\n**Detalhe:** `{1}`",

        # ==========================================
        # [NETWORK] - REDE, 4G E PROXY
        # ==========================================
        "prep_4g": "[NETWORK] [INFO] Preparando isolamento de rede (4G) para:",
        "timeout_4g": "[NETWORK] [ERRO] Tempo limite excedido. Encerrando o farm para proteger o seu IP!",
        "4g_ligando_aviao": "   [NETWORK] [4G] Ligando Modo Avião (Cortando sinal)...",
        "4g_desligando_aviao": "   [NETWORK] [4G] Desligando Modo Avião (Buscando novo IP)...",
        "4g_rotacao_concluida": "   [NETWORK] [4G] Rotação concluída! Novo IP atribuído pela torre.",
        "proxy_ativado": "   [NETWORK] [PROXY] Túnel invisível ativado com sucesso ({}).",
        "proxy_erro": "   [NETWORK] [ERRO] Falha ao iniciar proxy: {}",

        # ==========================================
        # [MOBILE] - ADB E AÇÕES NO CELULAR
        # ==========================================
        "cel_nao_det": "[MOBILE] [!] Celular não detectado. Aguardando conexão USB (Tentando por 1 min)...",
        "sessao_mob_fim": "[MOBILE] -> Sessão Mobile finalizada. Mantendo aba aberta por um tempo residual...",
        "erro_mob": "[MOBILE] [ERRO] Erro Crítico Mobile",
        "adb_nao_encontrado": "\n[MOBILE] [!] ADB não encontrado para {}. Iniciando download...",
        "adb_sucesso": "[MOBILE] [SUCESSO] Ferramentas ADB instaladas!",
        "adb_erro": "[MOBILE] [ERRO] Falha ao instalar ADB automaticamente: {}",

        # ==========================================
        # [CHROME] - NAVEGADOR PC E PESQUISAS
        # ==========================================
        "iniciando_conta": "[CHROME] >>> INICIANDO CONTA ISOLADA:",
        "sessao_pc_fim": "[CHROME] -> Sessão PC finalizada. Mantendo aba aberta por um tempo residual...",
        "erro_pc": "[CHROME] [ERRO] Erro Crítico PC",
        "modo_config_titulo": "[CHROME] >>> MODO CONFIGURAÇÃO:",
        "modo_config_nav_aberto": "[CHROME] -> O navegador foi aberto para você.",
        "modo_config_login": "[CHROME] -> Por favor, faça o LOGIN manualmente na sua conta da Microsoft.",
        "modo_config_tempo": "[CHROME] -> Você tem 10 MINUTOS de tela aberta. Quando terminar, FECHE O NAVEGADOR.",
        "modo_config_nota": "[CHROME] -> Nota de configuração:",
        "tentativa_chrome": "[CHROME] [!] Tentativa {} de abrir o Chrome falhou. Retentando...",
        "analisando_tipo": "[CHROME] --- Analisando {} ---",
        "tipo_concluido": "[CHROME] -> [OK] {} já está totalmente concluído. Pulando...",
        "fator_preguica": "[CHROME] -> [STEALTH] Fator Preguiça: Decidido ignorar os últimos pontos de {} hoje.",
        "erro_status": "[CHROME] -> [!] Não foi possível ler o status. Usando limite padrão de segurança: {}",
        "humor_ativado": "[CHROME] -> [STEALTH] Humor ativado: O bot decidiu pular {} pesquisas neste ciclo.",
        "ciclo_encerrado": "[CHROME] -> Ciclo de {} encerrado.",
        "executando_pesquisas": "[CHROME] -> Executando {} pesquisas orgânicas...",
        "aguardando_ponto": "[CHROME] [~] Aguardando o ponto contabilizar ({}s)...",
        "interacao_extra": "[CHROME] [~] Interação extra detectada...",
        "lendo_artigo": "[CHROME] [~] Lendo um artigo dos resultados...",
        "erro_pesquisa": "[CHROME] [AVISO] Ocorreu um erro nesta pesquisa. Pulando...",
        "verificando_paineis": "[CHROME] --- Verificando Painéis de Missões (Conjunto Diário e Extras) ---",
        "analisando_pagina": "[CHROME] -> Analisando: {}",
        "painel_limpo": "[CHROME] -> Painel limpo! Nenhuma missão pendente encontrada aqui.",
        "clicando_missao": "[CHROME] -> Clicando na missão ({})...",
        "erro_pagina": "[CHROME] -> Erro leve na página: {}",
        "total_missoes": "[CHROME] --- Total de {} missões concluídas com sucesso! ---",
        "verificando_prog": "[CHROME] [~] Verificando progresso em: {}",
        "status_concluido": "[CHROME] [OK] {} já está totalmente concluído ({}/{}). Pulando...",
        "status_real": "[CHROME] [INFO] Status Real: {}/{} pontos. Faltam {} pesquisas.",
        "erro_contador": "[CHROME] [!] Não foi possível ler o contador real. Usando limite de segurança (20).",
        "pausa_humana": "   [CHROME] [~] Pausa estendida humana de {}s (lendo a tela/descanso)...",

        # ==========================================
        # [BING VISUAL] & [BING STAR ENGINE]
        # ==========================================
        "visual_init": "[BING] Iniciando tarefa de Pesquisa Visual (Streak)...",
        "visual_img_ok": "[BING] Imagem enviada com sucesso: {0}",
        "visual_ok": "[BING] Pesquisa Visual concluída e contabilizada!",
        "visual_erro_campo": "[BING] Erro: Campo de colar URL não encontrado no popup da câmera.",
        "visual_erro_fatal": "[BING] Erro fatal durante a Pesquisa Visual: {0}...",
        
        "star_init": "\n>>> [BING STAR ENGINE] INICIANDO: {0} <<<",
        "star_etapa1": "\n[STAR ENGINE] ETAPA 1/4: Aquecimento PC & Verificação do Contador Unificado...",
        "star_falha1": "[STAR ENGINE] [X] Falha no Bloco 1 (PC): {0}",
        "star_etapa2": "\n[STAR ENGINE] ETAPA 2/4: Transição para o Smartphone... (Restam {0} no saldo unificado)",
        "star_falha2": "[STAR ENGINE] [X] Falha no Bloco 2 (Mob): {0}",
        "star_etapa3": "\n[STAR ENGINE] ETAPA 3/4: Ativando Ociosidade Humana ({0} min)...",
        "star_etapa4": "\n[STAR ENGINE] ETAPA 4/4: Retorno ao PC. Lendo painel novamente e finalizando...",
        "star_falha4": "[STAR ENGINE] [X] Falha no Bloco Final (PC): {0}",
        "star_sucesso": "\n[STAR ENGINE] >>> SUCESSO ABSOLUTO! Conta {0} blindada e farmada. ({1})",
        "star_pesquisa": "   [STAR ENGINE] ({0}/{1}) [{2}] {3}",

        # ==========================================
        # DIAGNÓSTICO
        # ==========================================
        "diag_titulo": ">>> DIAGNÓSTICO DO SISTEMA <<<",
        "diag_chrome_ok": " [DIAG] \033[92m[OK]\033[0m Google Chrome detectado (v{})",
        "diag_chrome_err": " [DIAG] \033[91m[ X]\033[0m Google Chrome não encontrado!",
        "diag_adb_ok": " [DIAG] \033[92m[OK]\033[0m Ferramentas ADB prontas",
        "diag_adb_err": " [DIAG] \033[93m[!]\033[0m Ferramentas ADB ausentes (Pulando mobile)",
        "diag_cfg_ok": " [DIAG] \033[92m[OK]\033[0m Arquivo Config carregado",
        "diag_cfg_err": " [DIAG] \033[93m[!]\033[0m Arquivo Config ausente (Usando padrão)",
        "diag_prof_ok": " [DIAG] \033[92m[OK]\033[0m Pasta Profiles ({} contas encontradas)",
        "diag_prof_err": " [DIAG] \033[91m[X]\033[0m Pasta Profiles vazia (Requer login)",
        "diag_xbox": " [DIAG] \033[91m[X]\033[0m Token Xbox (coming soon)",
        "diag_startup_ok": " [DIAG] \033[92m[OK]\033[0m Startup Automático Ativado",
        "diag_startup_err": " [DIAG] \033[93m[!]\033[0m Startup Automático Desativado",
    },
    "en": {
        # ==========================================
        # INTERFACE / MENU
        # ==========================================
        "janela_titulo": "title FPGAMESBR Rewards",
        "menu_titulo": "SELECT AN OPERATION",
        "op_config": "Setup Mode (Login / Add Account)",
        "op_manual": "Manual Mode (Start Farm with saved config)",
        "op_startup": "Toggle Startup (Run invisibly with Windows)",
        "op_avancado": "Advanced Settings (Webhook, Limits, Headless)",
        "escolha": "> Choose an option (1 to 4): ",
        "fechar": "Press ENTER to continue/close...",
        "contas_disp": "AVAILABLE ACCOUNTS:",
        "add_conta": "+ Add New Account",
        "escolha_num": "Choose the account number (or the add option): ",
        "digite_nome": "Enter the new account name: ",
        "menu_avancado_titulo": "ADVANCED SETTINGS & WEBHOOK",
        "dica_enter": "[Hint] Press ENTER without typing to keep the current value.",
        "dica_webhook": "[Hint] Type '0' in Webhook to disable notifications.",
        "conf_webhook": "[Discord] Current Webhook URL",
        "conf_pc": "[Search] Current PC Limit",
        "conf_mob": "[Search] Current Mobile Limit",
        "conf_oculto": "[System] Run invisible browser (Headless)? (y/n)",
        "conf_tarefas": "[System] Do dashboard tasks/cards? (y/n)",
        "conf_os_titulo": "[System] Current Operating System:",
        "conf_os_opcoes": "  [1] Windows  [2] Linux  [3] Mac",
        "conf_os_escolha": "  > Type 1, 2 or 3 (or ENTER to keep): ",
        "voltar_menu": "> Press ENTER to return to the menu...",
        "discord_sucesso": "✅ **Rewards Bot**\nThe farm for account `{0}` was successfully completed at {1}!",

        # ==========================================
        # [SYSTEM] - NÚCLEO, ARQUIVOS E OS
        # ==========================================
        "invalido": "[SYSTEM] [!] Invalid option! Closing bot...",
        "nome_inv": "[SYSTEM] [!] Invalid name!",
        "op_inv": "[SYSTEM] [!] Invalid option!",
        "ent_inv": "[SYSTEM] [!] Invalid input!",
        "carregando": "[SYSTEM] [INFO] Loading preferences from RewardsConfig.json...",
        "sucesso": "[SYSTEM] [SUCCESS] Full cycle completed!",
        "conf_salva": "[SYSTEM] [OK] Settings successfully saved to 'RewardsConfig.json'!",
        "startup_desativado": "[SYSTEM] [!] Startup Disabled: The bot will no longer start with OS.",
        "startup_erro_rem": "[SYSTEM] [X] Error removing startup:",
        "startup_ativado": "[SYSTEM] [OK] Startup Enabled: The bot will start 100% invisibly with OS!",
        "startup_erro_criar": "[SYSTEM] [X] Error creating startup:",
        "modo_config_salvo": "[SYSTEM] -> Setup saved for",
        "erro_notificacao": "[SYSTEM] [!] Warning: Failed to send notification: {}",
        "otimizando_historico": "[SYSTEM] -> Optimizing history file on disk...",
        "zumbi_clean": "\n[SYSTEM] Scanning and eliminating zombie processes (chromedriver)...",
        "alerta_ban": "⛔ **CRITICAL ALERT** ⛔\nThe account `{0}` appears to be SUSPENDED by Microsoft! Bot aborted farming for this profile.",
        "crash_log": "[SYSTEM] Fatal error detected! Crash log saved to: {0}",
        "crash_sos": "🚨 **FATAL ERROR (Crash)** 🚨\nThe bot's main engine failed!\n**Log generated:** `{0}`\n**Detail:** `{1}`",

        # ==========================================
        # [NETWORK] - REDE, 4G E PROXY
        # ==========================================
        "prep_4g": "[NETWORK] [INFO] Preparing network isolation (4G) for:",
        "timeout_4g": "[NETWORK] [ERROR] Timeout. Stopping farm to protect your main IP!",
        "4g_ligando_aviao": "   [NETWORK] [4G] Enabling Airplane Mode (Cutting signal)...",
        "4g_desligando_aviao": "   [NETWORK] [4G] Disabling Airplane Mode (Searching for new IP)...",
        "4g_rotacao_concluida": "   [NETWORK] [4G] Rotation complete! New IP assigned by the tower.",
        "proxy_ativado": "   [NETWORK] [PROXY] Invisible tunnel successfully activated ({}).",
        "proxy_erro": "   [NETWORK] [PROXY-ERROR] Failed to start proxy: {}",

        # ==========================================
        # [MOBILE] - ADB E AÇÕES NO CELULAR
        # ==========================================
        "cel_nao_det": "[MOBILE] [!] Phone not detected. Waiting for USB connection (Trying for 1 minute)...",
        "sessao_mob_fim": "[MOBILE] -> Mobile session finished. Keeping tab open for residual time...",
        "erro_mob": "[MOBILE] [ERROR] Critical Mobile Error",
        "adb_nao_encontrado": "\n[MOBILE] [!] ADB not found for {}. Starting download...",
        "adb_sucesso": "[MOBILE] [SUCCESS] ADB tools installed!",
        "adb_erro": "[MOBILE] [ERROR] Failed to install ADB automatically: {}",

        # ==========================================
        # [CHROME] - NAVEGADOR PC E PESQUISAS
        # ==========================================
        "iniciando_conta": "[CHROME] >>> STARTING ISOLATED ACCOUNT:",
        "sessao_pc_fim": "[CHROME] -> PC session finished. Keeping tab open for residual time...",
        "erro_pc": "[CHROME] [ERROR] Critical PC Error",
        "modo_config_titulo": "[CHROME] >>> SETUP MODE:",
        "modo_config_nav_aberto": "[CHROME] -> The browser has been opened for you.",
        "modo_config_login": "[CHROME] -> Please manually LOGIN to your Microsoft account.",
        "modo_config_tempo": "[CHROME] -> You have 10 MINUTES with the screen open. When done, CLOSE THE BROWSER.",
        "modo_config_nota": "[CHROME] -> Setup note:",
        "tentativa_chrome": "[CHROME] [!] Attempt {} to open Chrome failed. Retrying...",
        "analisando_tipo": "[CHROME] --- Analyzing {} ---",
        "tipo_concluido": "[CHROME] -> [OK] {} is already fully completed. Skipping...",
        "fator_preguica": "[CHROME] -> [STEALTH] Laziness Factor: Decided to ignore the last points for {} today.",
        "erro_status": "[CHROME] -> [!] Could not read status. Using default safety limit: {}",
        "humor_ativado": "[CHROME] -> [STEALTH] Mood activated: Bot decided to skip {} searches this cycle.",
        "ciclo_encerrado": "[CHROME] -> Cycle for {} ended.",
        "executando_pesquisas": "[CHROME] -> Executing {} organic searches...",
        "aguardando_ponto": "[CHROME] [~] Waiting for point to register ({}s)...",
        "interacao_extra": "[CHROME] [~] Extra interaction detected...",
        "lendo_artigo": "[CHROME] [~] Reading an article from the results...",
        "erro_pesquisa": "[CHROME] [WARNING] An error occurred in this search. Skipping...",
        "verificando_paineis": "[CHROME] --- Checking Mission Dashboards (Daily and Extras) ---",
        "analisando_pagina": "[CHROME] -> Analyzing: {}",
        "painel_limpo": "[CHROME] -> Dashboard clean! No pending missions found here.",
        "clicando_missao": "[CHROME] -> Clicking on mission ({})...",
        "erro_pagina": "[CHROME] -> Minor page error: {}",
        "total_missoes": "[CHROME] --- Total of {} missions successfully completed! ---",
        "verificando_prog": "[CHROME] [~] Checking progress on: {}",
        "status_concluido": "[CHROME] [OK] {} is already fully completed ({}/{}). Skipping...",
        "status_real": "[CHROME] [INFO] Real Status: {}/{} points. {} searches left.",
        "erro_contador": "[CHROME] [!] Could not read the real counter. Using default safety limit (20).",
        "pausa_humana": "   [CHROME] [~] Extended human pause of {}s (reading screen/resting)...",

        # ==========================================
        # [BING VISUAL] & [BING STAR ENGINE]
        # ==========================================
        "visual_init": "[BING] Starting Visual Search task (Streak)...",
        "visual_img_ok": "[BING] Image successfully submitted: {0}",
        "visual_ok": "[BING] Visual Search completed and accounted for!",
        "visual_erro_campo": "[BING] Error: Paste URL field not found in camera popup.",
        "visual_erro_fatal": "[BING] Fatal error during Visual Search: {0}...",
        
        "star_init": "\n>>> [BING STAR ENGINE] STARTING: {0} <<<",
        "star_etapa1": "\n[STAR ENGINE] STEP 1/4: PC Warm-up & Unified Counter Verification...",
        "star_falha1": "[STAR ENGINE] [X] Failure in Block 1 (PC): {0}",
        "star_etapa2": "\n[STAR ENGINE] STEP 2/4: Transition to Smartphone... ({0} searches left in unified balance)",
        "star_falha2": "[STAR ENGINE] [X] Failure in Block 2 (Mob): {0}",
        "star_etapa3": "\n[STAR ENGINE] STEP 3/4: Activating Human Idleness ({0} min)...",
        "star_etapa4": "\n[STAR ENGINE] STEP 4/4: Return to PC. Reading dashboard again and finishing...",
        "star_falha4": "[STAR ENGINE] [X] Failure in Final Block (PC): {0}",
        "star_sucesso": "\n[STAR ENGINE] >>> ABSOLUTE SUCCESS! Account {0} shielded and farmed. ({1})",
        "star_pesquisa": "   [STAR ENGINE] ({0}/{1}) [{2}] {3}",

        # ==========================================
        # DIAGNÓSTICO
        # ==========================================
        "diag_titulo": ">>> SYSTEM DIAGNOSTICS <<<",
        "diag_chrome_ok": " [DIAG] \033[92m[OK]\033[0m Google Chrome detected (v{})",
        "diag_chrome_err": " [DIAG] \033[91m[X]\033[0m Google Chrome not found!",
        "diag_adb_ok": " [DIAG] \033[92m[OK]\033[0m ADB Tools ready",
        "diag_adb_err": " [DIAG] \033[93m[!]\033[0m ADB Tools missing (Skipping mobile)",
        "diag_cfg_ok": " [DIAG] \033[92m[OK]\033[0m Config file loaded",
        "diag_cfg_err": " [DIAG] \033[93m[!]\033[0m Config file missing (Using defaults)",
        "diag_prof_ok": " [DIAG] \033[92m[OK]\033[0m Profiles folder ({} accounts found)",
        "diag_prof_err": " [DIAG] \033[91m[X]\033[0m Profiles folder empty (Requires login)",
        "diag_xbox": " [DIAG] \033[91m[ X]\033[0m Xbox Token (coming soon)",
        "diag_startup_ok": " [DIAG] \033[92m[OK]\033[0m Automatic Startup Enabled",
        "diag_startup_err": " [DIAG] \033[93m[!]\033[0m Automatic Startup Disabled",
    }
}

t = TEXTOS[IDIOMA_GLOBAL]

if getattr(sys, 'frozen', False):
    # Se estiver rodando como .exe (compilado), usa a pasta onde o .exe está
    BASE_DIR = Path(sys.executable).parent
else:
    # Se estiver rodando como .py normal, usa a pasta do script
    BASE_DIR = Path(__file__).parent

BASE_PROFILES_DIR = BASE_DIR / "RewardsProfiles"
ARQUIVO_HISTORICO = BASE_DIR / "historic.json"
ARQUIVO_LOG = BASE_DIR / "Exe.json"
ARQUIVO_CONFIG = BASE_DIR / "RewardsConfig.json"

def preparar_ambiente_adb():
    cfg = carregar_config()
    if cfg.get("multi_account", "n") == "n":
        return 
        
    sistema = platform.system().lower()
    ext = ".exe" if sistema == "windows" else ""
    caminho_adb = BASE_DIR / "platform-tools" / f"adb{ext}"
    
    if caminho_adb.exists(): return
    
    LOGGER(t['adb_nao_encontrado'].format(sistema.upper()))
    urls = {
        "windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        "linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
        "darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    }
    url = urls.get(sistema, urls["windows"])
    
    try:
        with urllib.request.urlopen(url) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                z.extractall(path=BASE_DIR)
        
        if sistema != "windows":
            st = os.stat(caminho_adb)
            os.chmod(caminho_adb, st.st_mode | stat.S_IEXEC)
            
        LOGGER(t['adb_sucesso'])
    except Exception as e:
        LOGGER(t['adb_erro'].format(e))

def atualizar_lista_contas():
    cfg = carregar_config()
    if cfg.get("multi_account", "n") == "n":
        return ["DefaultAccount"]
        
    BASE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    pastas = [p.name for p in BASE_PROFILES_DIR.iterdir() if p.is_dir()]
    if not pastas:
        return ["DefaultAccount"]
    return pastas

def carregar_config():
    """Carrega as configurações salvas ou cria um padrão de fábrica"""
    padrao = {
        "webhook_url": "",
        "limite_pc": 20,
        "limite_mobile": 0,
        "modo_oculto": "s",   
        "fazer_tarefas": "s",
        "multi_account": "n",
        "do_discord": "n",
        "discord_cooldown": 5,
        "ms_new_tasks": "n",
        "language": "pt"
    }
    
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                padrao.update(dados_salvos)
        except Exception:
            pass
            
    return padrao

def obter_fingerprint(nome_perfil, tipo):
    """Garante que a identidade de HW (User-Agent) não mude entre sessões"""
    caminho_perfil = BASE_PROFILES_DIR / nome_perfil
    caminho_perfil.mkdir(parents=True, exist_ok=True)
    arquivo_fingerprint = caminho_perfil / "fingerprint.json"
    
    identidade = {}
    if arquivo_fingerprint.exists():
        try:
            with open(arquivo_fingerprint, "r", encoding="utf-8") as f:
                identidade = json.load(f)
        except Exception:
            pass

    if tipo not in identidade:
        if tipo == 'mobile':
            uas = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 15; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
            ]
            identidade[tipo] = random.choice(uas)
        else:
            identidade[tipo] = "default_pc"
            
        try:
            with open(arquivo_fingerprint, "w", encoding="utf-8") as f:
                json.dump(identidade, f, indent=4)
        except Exception:
            pass
            
    return identidade[tipo]

def salvar_config(config):
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        LOGGER(f"  \033[91m[X] Erro ao salvar configurações: {e}\033[0m")
        

def atualizar_lista_contas():
    cfg = carregar_config()
    BASE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    pastas = [p.name for p in BASE_PROFILES_DIR.iterdir() if p.is_dir()]
    
    # Remove a DefaultAccount da lista dinâmica para não duplicar
    if "DefaultAccount" in pastas:
        pastas.remove("DefaultAccount")
        
    # Se multi-conta for "n", ignora as outras pastas e mostra SÓ a principal
    if cfg.get("multi_account", "n") == "n":
        return ["DefaultAccount"]
        
    # Se for "s", a Conta Principal é sempre a primeira, seguida das outras em ordem alfabética
    return ["DefaultAccount"] + sorted(pastas)

CONTAS_PARA_FARMAR = atualizar_lista_contas()
URL_WEBHOOK_DISCORD = ""
LOGGER = print

# =============================================================================
# MOTOR V15: PROXY FANTASMA E ADB ROTAÇÃO
# =============================================================================
PORTA_PROXY = 8899
PROXY_RODANDO = False
ABORTAR_PROCESSO = False

def localizar_ip_celular():
    try:
        resultado = subprocess.check_output("ipconfig /all", encoding="cp850")
        for bloco in resultado.split("Adaptador"):
            if "NDIS" in bloco or "Remote NDIS" in bloco:
                match_ip = re.search(r"IPv4.+?: (\d+\.\d+\.\d+\.\d+)", bloco)
                if match_ip:
                    return match_ip.group(1)
    except: pass
    return None

def rotacionar_ip_celular():
    ext = ".exe" if platform.system().lower() == "windows" else ""
    caminho_adb = BASE_DIR / "platform-tools" / f"adb{ext}"
    
    ip_antigo = localizar_ip_celular() # Anota o IP atual
    
    for tentativa in range(3): # Tenta até 3 vezes
        LOGGER(t['4g_ligando_aviao'])
        subprocess.run([str(caminho_adb), "shell", "cmd", "connectivity", "airplane-mode", "enable"], ...)
        time.sleep(5) 
        
        LOGGER(t['4g_desligando_aviao'])
        subprocess.run([str(caminho_adb), "shell", "cmd", "connectivity", "airplane-mode", "disable"], ...)
        time.sleep(10) # Tempo um pouco maior para a operadora "esquecer" o aparelho
        
        ip_novo = localizar_ip_celular()
        if ip_novo and ip_novo != ip_antigo:
            LOGGER(t['4g_rotacao_concluida'])
            return # Sucesso! Sai da função.
            
        LOGGER("   [!] A operadora devolveu o mesmo IP. Forçando nova rotação...")

def transferir_dados(origem, destino):
    try:
        while True:
            dados = origem.recv(8192)
            if not dados: break
            destino.sendall(dados)
    except: pass
    finally:
        origem.close()
        destino.close()

def tratar_cliente(cliente_socket, ip_celular):
    try:
        requisicao = cliente_socket.recv(8192)
        if not requisicao: return cliente_socket.close()
        
        primeira_linha = requisicao.split(b'\n')[0]
        if primeira_linha.startswith(b'CONNECT'):
            url = primeira_linha.split(b' ')[1]
            host, porta = url.split(b':')
            
            servidor_remoto = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            servidor_remoto.bind((ip_celular, 0))
            servidor_remoto.connect((host.decode('utf-8'), int(porta)))
            
            cliente_socket.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            threading.Thread(target=transferir_dados, args=(cliente_socket, servidor_remoto), daemon=True).start()
            threading.Thread(target=transferir_dados, args=(servidor_remoto, cliente_socket), daemon=True).start()
        else:
            cliente_socket.close()
    except:
        cliente_socket.close()

def iniciar_proxy_background(ip_celular):
    global PROXY_RODANDO
    if PROXY_RODANDO: return
    
    try:
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind(('127.0.0.1', PORTA_PROXY))
        servidor.listen(100)
        
        def aceitar_conexoes():
            while True:
                try:
                    cliente, _ = servidor.accept()
                    threading.Thread(target=tratar_cliente, args=(cliente, ip_celular), daemon=True).start()
                except: break
                
        threading.Thread(target=aceitar_conexoes, daemon=True).start()
        PROXY_RODANDO = True
        LOGGER(t['proxy_ativado'].format(ip_celular))
    except Exception as e:
        LOGGER(t['proxy_erro'].format(e))

# =============================================================================
# FUNÇÕES DE LÓGICA CORE & STEALTH
# =============================================================================
def wait_human(min_s=3.0, max_s=8.0, long_pause_chance=0.15):
    if random.random() < long_pause_chance:
        pausa = random.uniform(35.0, 90.0)
        LOGGER(t['pausa_humana'].format(int(pausa)))
        time.sleep(pausa)
    else:
        time.sleep(random.uniform(min_s, max_s))

def ghost_click(driver, elemento, cliques=1):
    """Clica com desvio aleatório para evitar padrão de pixel perfeito"""
    actions = ActionChains(driver)
    x_offset = random.randint(-5, 5)
    y_offset = random.randint(-5, 5)
    
    LOGGER(f"   [STEALTH] Ghost Click ativado. Desvio de mira: X:{x_offset}px | Y:{y_offset}px")
    
    try:
        actions.move_to_element_with_offset(elemento, x_offset, y_offset)
        for _ in range(cliques):
            actions.click()
            if cliques > 1:
                time.sleep(random.uniform(0.05, 0.15))
        actions.perform()
    except Exception:
        try:
            elemento.click()
        except Exception:
            pass

def enviar_notificacao(mensagem):
    if not URL_WEBHOOK_DISCORD: return 
    try:
        data = {"content": mensagem}
        req = urllib.request.Request(URL_WEBHOOK_DISCORD, data=json.dumps(data).encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        LOGGER(t['erro_notificacao'].format(e))
        
def carregar_historico():
    try:
        if ARQUIVO_HISTORICO.exists():
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except Exception: pass
    return set()

def salvar_historico(termo):
    historico = list(carregar_historico())
    if termo not in historico:
        historico.append(termo)
        try:
            with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
                json.dump(historico, f, ensure_ascii=False, indent=4)
        except Exception: pass

def limpar_excesso_historico():
    LOGGER(t['otimizando_historico'])
    try:
        if ARQUIVO_HISTORICO.exists():
            historico = list(carregar_historico())
            if len(historico) > 300:
                with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
                    json.dump(historico[-300:], f, ensure_ascii=False, indent=4)
    except Exception: pass

def carregar_termos_online():
    if IDIOMA_GLOBAL == "pt":
        LOGGER("-> Sincronizando banco de dados de pesquisas...")
    else:
        LOGGER("-> Synchronizing search database...")
        
    historico = carregar_historico()
    termos = []
    
    if IDIOMA_GLOBAL == "pt":
        feeds = [
            "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-150",
            "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=pt-BR&gl=BR&ceid=BR:pt-150",
            "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=pt-BR&gl=BR&ceid=BR:pt-150",
            "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=pt-BR&gl=BR&ceid=BR:pt-150",
            "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=pt-BR&gl=BR&ceid=BR:pt-150",
            "https://news.google.com/rss/headlines/section/topic/WORLD?hl=pt-BR&gl=BR&ceid=BR:pt-150"
        ]
    else:
        feeds = [
            "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-US&gl=US&ceid=US:en",
            "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
        ]

    for url in feeds:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                root = ET.parse(response).getroot()
                for item in root.findall('./channel/item/title')[:15]:
                    txt = item.text.split(" - ")[0]
                    if len(txt) > 4 and txt not in historico: termos.append(txt)
        except Exception: pass

    if IDIOMA_GLOBAL == "pt":
        fallback = [
            "Receitas fáceis para o jantar", "Resultados do futebol hoje", "Melhores filmes de ação",
            "Dicas para economizar dinheiro", "Como perder peso rápido", "Exercícios para fazer em casa",
            "Previsão do tempo fim de semana", "Notícias de tecnologia", "Smartphones mais vendidos",
            "Como investir na bolsa", "Jogos de videogame lançamentos", "Séries mais assistidas",
            "Dicas de viagens baratas", "Receita de bolo de chocolate", "Principais notícias do Brasil",
            "Inteligência Artificial na medicina", "Carros elétricos", "Dicas de decoração para sala",
            "Como aprender inglês sozinho", "Melhores restaurantes", "Benefícios do café",
            "Como cuidar de plantas em casa", "Maquiagem passo a passo", "Moda outono inverno",
            "Tabela do campeonato brasileiro", "Resumo de novelas", "Horóscopo do dia",
            "Receitas de airfryer", "Dicas de produtividade", "Como meditar para iniciantes"
        ]
        termo_emergencia = "Dicas novidade"
    else:
        fallback = [
            "Easy dinner recipes", "Live sports scores", "Best action movies",
            "Money saving tips", "How to lose weight fast", "Home workout routines",
            "Weekend weather forecast", "Latest technology news", "Best selling smartphones",
            "How to invest in stocks", "New video game releases", "Most watched TV shows",
            "Budget travel tips", "Chocolate cake recipe", "Top breaking news",
            "Artificial Intelligence in medicine", "Electric cars", "Living room decor ideas",
            "How to learn Spanish fast", "Best restaurants near me", "Health benefits of coffee",
            "How to care for indoor plants", "Makeup tutorial for beginners", "Fall winter fashion trends",
            "Premier league standings", "Celebrity gossip", "Daily horoscope",
            "Airfryer recipes", "Productivity hacks", "Meditation for beginners"
        ]
        termo_emergencia = "Trending tips"

    for f in fallback:
        if f not in historico: termos.append(f)
        
    if len(termos) < 50: 
        termos.extend([f"{termo_emergencia} {random.randint(1000,9999)}" for _ in range(50)])
        
    random.shuffle(termos)
    return termos

def gerar_termo_humanizado(banco, idioma="pt"):
    MATRIZ = {
        "pt": {
            "prefixos": [
                'sobre', 'o que é', 'notícias de', 'preço de', 'como funciona', 
                'melhor', 'tutorial', 'fotos', 'opinião', 'tudo sobre', 
                'como resolver erro', 'assistir online', 'quem é', 'como instalar', 
                'cupom de desconto', 'como usar', 'horário de', 'vale a pena',
                'onde comprar', 'qual a diferença entre', 'análise', 'review de'
            ],
            "sufixos": [
                '2026', 'atualizado', 'brasil', 'novidades', 'guia para iniciantes', 
                'fórum', 'hoje', 'é bom', 'reclame aqui', 'twitter', 'reddit', 
                'barato', 'online', 'app', 'youtube', 'funciona mesmo', 'grátis', 
                'download', 'pdf', 'login', 'whatsapp', 'oficial', 'wikipedia', 
                'agora', 'valor', 'passo a passo', 'dicas e truques', 'pdf download'
            ],
            "nova_palavra_erro": [" online", " review", " hoje", " grátis", " preço"]
        },
        "en": {
            "prefixos": [
                'about', 'what is', 'news on', 'price of', 'how does', 
                'best', 'tutorial', 'pictures of', 'opinion on', 'all about', 
                'how to fix error', 'watch online', 'who is', 'how to install', 
                'discount code', 'how to use', 'schedule of', 'is it worth it',
                'where to buy', 'difference between', 'analysis', 'review of'
            ],
            "sufixos": [
                '2026', 'updated', 'usa', 'news', 'beginners guide', 
                'forum', 'today', 'is it good', 'twitter', 'reddit', 
                'cheap', 'online', 'app', 'youtube', 'does it work', 'free', 
                'download', 'pdf', 'login', 'whatsapp', 'official', 'wikipedia', 
                'now', 'value', 'step by step', 'tips and tricks', 'pdf download'
            ],
            "nova_palavra_erro": [" online", " review", " today", " free", " price"]
        }
    }
    
    if idioma != "pt": idioma = "en"
    
    t = random.choice(banco)
    palavras = t.split()
    
    if len(palavras) > 6 and random.random() < 0.50:
        tamanho_corte = random.randint(3, 5)
        inicio = random.randint(0, len(palavras) - tamanho_corte)
        t = " ".join(palavras[inicio:inicio+tamanho_corte])
        t = t.rstrip(',.:;-').lstrip(',.:;-')

    if random.random() < 0.70:
        if random.random() > 0.5:
            return f"{random.choice(MATRIZ[idioma]['prefixos'])} {t}"
        else:
            return f"{t} {random.choice(MATRIZ[idioma]['sufixos'])}"
    return t

def limpar_todas_as_missoes(driver):
    LOGGER(f"\n{t['verificando_paineis']}")
    paginas_para_limpar = ["https://rewards.bing.com/dashboard", "https://rewards.bing.com/earn"]
    missoes_feitas = 0
    links_visitados = set() 
    
    for pagina in paginas_para_limpar:
        LOGGER(f"\n{t['analisando_pagina'].format(pagina)}")
        try:
            driver.get(pagina)
            time.sleep(random.uniform(5.0, 8.0)) 
            if verificar_conta_suspensa(driver, "Perfil Atual"):
                break
            principal = driver.current_window_handle
            
            while True:
                alvo, link_alvo = None, ""
                cartoes = driver.find_elements(By.CSS_SELECTOR, "a.group\\/ctrl.rounded-cornerCardDefault[href]")
                for card in cartoes:
                    try:
                        if not card.is_displayed(): continue
                        href = card.get_attribute("href")
                        if not href or href in links_visitados: continue
                        url_lower = href.lower()
                        
                        # --- LISTA DE EXCLUSÃO ATUALIZADA ---
                        ignorar = [
                            '/redeem', '/about', '/badges', '/status', '/history', 
                            '/dashboard', '/earn', '/refer', '/welcome', 'rwgbopen=1', 
                            'microsoft.com/edge', 'xbox.com',
                            'bingapp.microsoft.com', # Bloqueia a missão de Check-in Mobile
                            'vsstreak'               # Bloqueia a missão Visual (tratada separadamente)
                        ]
                        if any(ign in url_lower for ign in ignorar): continue 
                        
                        texto_card = card.text.lower()
                        html_card = card.get_attribute("innerHTML").lower()
                        if "concluído" in texto_card or "completed" in texto_card or "bg-statussuccess" in html_card: continue
                            
                        alvo, link_alvo = card, href
                        break 
                    except Exception: continue
                
                if not alvo: 
                    LOGGER(t['painel_limpo'])
                    break
                
                links_visitados.add(link_alvo)
                LOGGER(t['clicando_missao'].format(missoes_feitas + 1))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", alvo)
                wait_human(1.0, 2.5, long_pause_chance=0.0)
                
                janelas_antes = driver.window_handles
                driver.execute_script("arguments[0].click();", alvo)
                
                try: WebDriverWait(driver, 5).until(EC.new_window_is_opened(janelas_antes))
                except TimeoutException: pass
                
                janelas_depois = driver.window_handles
                novas = [j for j in janelas_depois if j not in janelas_antes]
                
                if novas:
                    driver.switch_to.window(novas[0])
                    wait_human(8.0, 15.0, long_pause_chance=0.2) 
                    driver.close()
                    driver.switch_to.window(principal)
                else:
                    wait_human(4.0, 6.0, long_pause_chance=0.0)
                    
                missoes_feitas += 1
        except Exception as e:
            LOGGER(t['erro_pagina'].format(e))
            
    LOGGER(f"\n{t['total_missoes'].format(missoes_feitas)}")

def verificar_pesquisas_restantes(driver, tipo):
    valor_ponto = 3 
    
    urls_checagem = [
        "https://rewards.bing.com/earn"
    ]
    
    for url in urls_checagem:
        try:
            nome_url = url.split('/')[-1] if '/' in url else 'home'
            LOGGER(f"   {t['verificando_prog'].format(nome_url)}")
            driver.get(url)
            time.sleep(random.uniform(5.0, 7.0))
            
            script_leitura = """
            let termos = ["pesquisa do bing", "bing search", "pc search", "desktop search", "pesquisa no computador", "pesquisas no computador", "pesquisa móvel", "pesquisar no celular", "mobile search"];
            
            // 1. TENTA LER O PAINEL SE ELE JÁ ESTIVER ABERTO
            let containers = document.querySelectorAll('.wrap-anywhere, p, div');
            for (let el of containers) {
                let text = el.textContent.trim().toLowerCase();
                if (termos.includes(text)) {
                    let irmao = el.nextElementSibling;
                    if (irmao) {
                        let match = irmao.textContent.match(/(\\d+)\\s*\\/\\s*(\\d+)/);
                        if (match && parseInt(match[2]) >= 15) {
                            return match[0];
                        }
                    }
                }
            }
            
            // 2. FORÇA BRUTA (Ignora estrutura HTML e varre todo o texto da tela)
            let allText = document.body.textContent.replace(/\\s+/g, " ");
            let regexForcaBruta = /(?:Pesquisa do Bing|Bing search|Pesquisa no computador|PC search|Desktop search|Pesquisa m[óo]vel|Pesquisar no celular|Mobile search).{0,150}?(\\d+)\\s*\\/\\s*(\\d+)/i;
            let fallbackMatch = allText.match(regexForcaBruta);
            if (fallbackMatch && parseInt(fallbackMatch[2]) >= 15) {
                return fallbackMatch[1] + "/" + fallbackMatch[2];
            }
            
            // 3. CAÇADOR DE BOTÃO (Acha o texto e clica no elemento pai clicável)
            let tags = document.querySelectorAll('p, span, h2, h3');
            for (let tag of tags) {
                let txt = tag.textContent.trim().toLowerCase();
                if (txt === "detalhamento de pontos" || txt === "points breakdown") {
                    // Sobe na árvore HTML até achar o Card interativo
                    let btn = tag.closest('.cursor-pointer') || tag;
                    btn.click();
                    return "ABRIR_MENU";
                }
            }
            return null;
            """
            
            resultado = driver.execute_script(script_leitura)
            
            if resultado == "ABRIR_MENU":
                # Espera a animação do menu lateral carregar na tela
                time.sleep(3.0) 
                
                # Executa o script novamente! Como o menu já está aberto, a TENTATIVA 1 ou 2 vai capturar os pontos e encerrar.
                resultado = driver.execute_script(script_leitura)
                
                # Prevenção: se por algum motivo sobrenatural ele ainda pedir para abrir, nós abortamos e retornamos null.
                if resultado == "ABRIR_MENU":
                    resultado = None
            
            if resultado:
                atual, total = map(int, resultado.replace(" ", "").split('/'))
                faltam_pontos = total - atual
                
                if faltam_pontos <= 0:
                    LOGGER(f"   {t['status_concluido'].format(tipo.upper(), atual, total)}")
                    return 0
                
                pesquisas_faltantes = faltam_pontos // valor_ponto
                LOGGER(f"   {t['status_real'].format(atual, total, pesquisas_faltantes)}")
                return pesquisas_faltantes
                
        except Exception:
            continue 
            
    LOGGER(f"   {t['erro_contador']}")
    return 20

def realizar_pesquisas(driver, num, banco):
    num_real = random.choices([num, max(1, num - 1), max(1, num - 2)], weights=[0.6, 0.25, 0.15], k=1)[0]
    LOGGER(t['executando_pesquisas'].format(num_real))
    amostra = random.sample(banco, min(num_real + 5, len(banco)))
    
    for i in range(num_real):
        if ABORTAR_PROCESSO: break
        try:
            if (i + 1) % 10 == 0 and random.random() < 0.15:
                try: driver.execute_script("window.localStorage.clear();")
                except Exception: pass

            origens_bing = [
                "https://www.bing.com/?form=QBLH",         
                "https://www.bing.com/?form=ANNTH1",       
                "https://www.bing.com/?form=HDRSC1",       
                "https://www.bing.com/?form=Z9FD1",        
                "https://www.bing.com/"                    
            ]
            driver.get(random.choice(origens_bing))
            try: driver.switch_to.window(driver.window_handles[0])
            except Exception: pass
            
            espera = WebDriverWait(driver, 10)
            try: sb = espera.until(EC.element_to_be_clickable((By.ID, "sb_form_q")))
            except TimeoutException:
                try: sb = driver.find_element(By.NAME, "q")
                except NoSuchElementException:
                    try: sb = driver.find_element(By.CLASS_NAME, "b_searchbox")
                    except Exception: continue
            
            termo_base = amostra[i]
            termo_final = gerar_termo_humanizado([termo_base], idioma=IDIOMA_GLOBAL)
            LOGGER(f"({i+1}/{num_real}) {termo_final}")
            salvar_historico(termo_base)
            
            # GHOST CLICK INTEGRADO
            ghost_click(driver, sb, cliques=3) 
            sb.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.1, 0.3))
            
            for letra in termo_final:
                sb.send_keys(letra)
                time.sleep(random.uniform(0.05, 0.20))
            
            if random.random() < 0.20: 
                time.sleep(random.uniform(0.4, 0.9))
                qtd_apagar = random.randint(3, min(10, len(termo_final)))
                for _ in range(qtd_apagar):
                    sb.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.05, 0.15))
                nova_palavra = random.choice([" online", " review", " hoje", " grátis", " preço"])
                for letra in nova_palavra:
                    sb.send_keys(letra)
                    time.sleep(random.uniform(0.05, 0.15))
                
            wait_human(0.8, 2.5, long_pause_chance=0.0)
            sb.send_keys(Keys.RETURN)
            
            espera_cooldown = random.uniform(8.0, 15.0)
            LOGGER(f"   {t['aguardando_ponto'].format(int(espera_cooldown))}")
            time.sleep(espera_cooldown)
            
            try:
                descer = random.randint(400, 1000)
                driver.execute_script(f"window.scrollTo(0, {descer});")
                wait_human(2.0, 4.5, long_pause_chance=0.0)
                
                if random.random() < 0.15:
                    try:
                        extra_elements = driver.find_elements(By.CSS_SELECTOR, ".b_expansionImage, .df_img, .b_vList")
                        if extra_elements:
                            alvo_extra = random.choice(extra_elements)
                            webdriver.ActionChains(driver).move_to_element(alvo_extra).pause(random.uniform(0.5, 1.5)).perform()
                            LOGGER(f"   {t['interacao_extra']}")
                            wait_human(3.0, 8.0, long_pause_chance=0.0)
                    except Exception: pass

                links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .b_algo h2 a")
                if links and random.random() < 0.35: 
                    alvo_clique = random.choice(links[:4])
                    janelas_antes = driver.window_handles 
                    webdriver.ActionChains(driver).move_to_element(alvo_clique).pause(random.uniform(0.5, 1.5)).click().perform()
                    LOGGER(f"   {t['lendo_artigo']}")
                    time.sleep(4) 
                    
                    janelas_depois = driver.window_handles
                    if len(janelas_depois) > len(janelas_antes):
                        nova_aba = [j for j in janelas_depois if j not in janelas_antes][0]
                        principal = driver.current_window_handle
                        driver.switch_to.window(nova_aba)
                        wait_human(15.0, 40.0, long_pause_chance=0.2) 
                        driver.close()
                        driver.switch_to.window(principal) 
                    else:
                        wait_human(15.0, 40.0, long_pause_chance=0.2) 
                        driver.back() 
                else:
                    if random.random() > 0.5:
                        subir = descer - random.randint(150, 400)
                        driver.execute_script(f"window.scrollTo(0, {subir});")
            except Exception: pass
        except Exception: 
            LOGGER(f"   {t['erro_pesquisa']}")
            wait_human(2.0, 5.0, long_pause_chance=0.0)


def fazer_pesquisa_visual(driver):
    try:
        LOGGER(t['visual_init'], "info")
        
        # 1. Garante que está no painel de controle do Rewards
        driver.get("https://rewards.bing.com/dashboard")
        time.sleep(5)
        
        # 2. Clica no card da Pesquisa Visual para abrir a barra lateral
        driver.execute_script("""
            let cards = document.querySelectorAll('div, a, span');
            for (let el of cards) {
                let texto = el.innerText ? el.innerText.toLowerCase() : '';
                if (texto.includes('pesquisa visual') && (el.onclick || el.tagName === 'A' || el.getAttribute('role') === 'button')) {
                    el.click();
                    break;
                }
            }
        """)
        time.sleep(4)

        # 3. Clica no círculo de scanner dentro da barra lateral para ir para a página de pesquisa visual
        driver.execute_script("""
            let alvoScanner = document.querySelector('.vs_cont svg, #vs_cont, [class*="vs"], [aria-label*="Visual"], [aria-label*="visual"], div[class*="medallion"], div[class*="scanner"]');
            if (alvoScanner) { alvoScanner.click(); }
        """)
        time.sleep(6) 
        
        # Fallback de segurança: Se o clique não redirecionou, força a rota direta
        if "rewards.bing.com" in driver.current_url:
            driver.get("https://www.bing.com/?features=vsstreak,vstooltip&form=ML2XES")
            time.sleep(5)

        # 4. Verifica se o modal já está aberto; se não estiver, clica na câmera
        driver.execute_script("""
            let modal = document.getElementById('sb_sbidialog');
            let campo = document.getElementById('sb_imgpst');
            // Se o painel estiver escondido, aperta o botão da câmera na barra de busca
            if (!modal || modal.style.display === 'none' || modal.getAttribute('aria-hidden') === 'true' || !campo) {
                let camBtn = document.querySelector('#sbi_b, [aria-label*="Visual"], [aria-label*="visual"], .sbi_b');
                if (camBtn) { camBtn.click(); }
            }
        """)
        time.sleep(3)

        # 5. Gera uma URL de imagem aleatória
        semente = random.randint(1, 100000)
        url_imagem_aleatoria = f"https://picsum.photos/seed/{semente}/400/400"
        
        # 6. Injeta a URL diretamente via JavaScript (Bypassa bloqueios de visibilidade do Selenium)
        sucesso_injecao = driver.execute_script("""
            let input1 = document.getElementById('sb_imgpst'); // Campo visual
            let input2 = document.getElementById('sb_sbi_ipt'); // Formulário oculto
            
            let inputReal = input1 || input2;
            
            if(inputReal) {
                // Cola o link no campo de forma instantânea
                inputReal.value = arguments[0];
                
                // Dispara os eventos de digitação para o Bing achar que você digitou
                inputReal.dispatchEvent(new Event('input', { bubbles: true }));
                inputReal.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Simula a tecla Enter física
                let enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                });
                inputReal.dispatchEvent(enterEvent);
                
                // Fallback matador: clica no botão oculto de enviar da Microsoft se o Enter falhar
                let submitBtn = document.getElementById('sb_sbi_gh');
                if(submitBtn) { submitBtn.click(); }
                
                return true;
            }
            return false;
        """, url_imagem_aleatoria)
        
        if sucesso_injecao:
            LOGGER(t['visual_img_ok'].format(url_imagem_aleatoria), "info")
            time.sleep(8) # Aguarda a Microsoft analisar a imagem da API
            LOGGER(t['visual_ok'], "success")
        else:
            LOGGER(t['visual_erro_campo'], "warning")

    except Exception as e:
        LOGGER(t['visual_erro_fatal'].format(str(e)[:80]), "error")

def fluxo_pesquisas(driver, tipo, limite_fallback, banco):
    LOGGER(f"\n{t['analisando_tipo'].format(tipo.upper())}")
    faltam = verificar_pesquisas_restantes(driver, tipo)
    if faltam == 0:
        LOGGER(t['tipo_concluido'].format(tipo.upper()))
        return

    if faltam <= 2 and random.random() < 0.4:
        LOGGER(t['fator_preguica'].format(tipo.upper()))
        return
    
    if faltam == -1:
        LOGGER(t['erro_status'].format(limite_fallback))
        faltam = limite_fallback

    if faltam > 3 and random.random() < 0.05:
        cortar = random.randint(1, 3) 
        faltam_novo = max(1, faltam - cortar) 
        if faltam_novo < faltam:
            LOGGER(t['humor_ativado'].format(faltam - faltam_novo, faltam, faltam_novo))
            faltam = faltam_novo
        
    realizar_pesquisas(driver, faltam, banco)
    LOGGER(t['ciclo_encerrado'].format(tipo.upper()))
    
def obter_versao_chrome():
    sistema = platform.system().lower()
    
    if sistema == "windows":
        try:
            import winreg 
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            versao, _ = winreg.QueryValueEx(chave, "version")
            return int(versao.split('.')[0])
        except Exception:
            try:
                chave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Google\Chrome\BLBeacon")
                versao, _ = winreg.QueryValueEx(chave, "version")
                return int(versao.split('.')[0])
            except Exception:
                return None
                
    elif sistema == "linux":
        try:
            # Chama o comando google-chrome --version
            out = subprocess.check_output(["google-chrome", "--version"], text=True)
            match = re.search(r"Google Chrome (\d+)", out)
            if match: return int(match.group(1))
        except Exception:
            pass
            
    elif sistema == "darwin": # macOS
        try:
            # Chama o binário do Chrome direto no diretório de Aplicativos
            out = subprocess.check_output(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], text=True)
            match = re.search(r"Google Chrome (\d+)", out)
            if match: return int(match.group(1))
        except Exception:
            pass
            
    return None

# ==============================================================
# CONFIGURAÇÃO DO DRIVER BLINDADA (WebAuthn + Identidade Fixa)
# ==============================================================
def configurar_driver(nome_perfil, tipo, oculto, identidade_ua, forcar_visivel=False, usar_proxy=False):
    caminho_perfil = BASE_PROFILES_DIR / nome_perfil
    caminho_perfil.mkdir(parents=True, exist_ok=True)
    
    opts = uc.ChromeOptions()
    opts.add_argument(f"--user-data-dir={caminho_perfil}")
    opts.add_argument("--log-level=3")
    opts.add_argument("--lang=pt-BR")
    
    if usar_proxy:
        opts.add_argument(f'--proxy-server=http://127.0.0.1:{PORTA_PROXY}')
    
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    
    # NOVAS FLAGS DE EVASÃO
    opts.add_argument("--disable-features=site-per-process,CalculateNativeWinOcclusion,WebAuthentication,PasswordManagerOnboarding,PasswordManager,EnablePasswordsAccountStorage,Passkeys")
    opts.add_argument("--disable-blink-features=Attestation,AutomationControlled")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    
    modo_invisivel = True if (oculto == 's' and not forcar_visivel) else False

    if modo_invisivel:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-position=100000,100000") 
        opts.add_argument("--window-size=1920,1080")
    else:
        opts.add_argument("--window-position=0,0") 
        opts.add_argument("--window-size=1280,800")
        
    versao_local = obter_versao_chrome()
    driver = None
    for tentativa in range(3):
        try:
            if versao_local:
                driver = uc.Chrome(options=opts, use_subprocess=True, version_main=versao_local)
            else:
                driver = uc.Chrome(options=opts, use_subprocess=True)
            break 
        except Exception:
            LOGGER(f"   {t['tentativa_chrome'].format(tentativa+1)}")
            time.sleep(3)
            
    if not driver:
        return None

    # Injeção da Identidade Fixa para Celular
    if tipo == 'mobile' and identidade_ua != "default_pc":
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": identidade_ua, "platform": "MacIntel" if "iPhone" in identidade_ua else "Linux"})
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {"width": 390, "height": 844, "deviceScaleFactor": 3, "mobile": True})
        driver.execute_cdp_cmd('Network.enable', {})
        latencia = random.randint(45, 95)
        download_bps = random.randint(1500000, 3500000)
        upload_bps = random.randint(500000, 1500000)
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {'offline': False, 'latency': latencia, 'downloadThroughput': download_bps, 'uploadThroughput': upload_bps, 'connectionType': 'cellular4g'})

    # Scripts anti-detecção finais (WebAuthn + Sensores forjados)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'credentials', { 
                value: { 
                    create: () => Promise.reject(new Error('WebAuthn disabled')), 
                    get: () => Promise.reject(new Error('WebAuthn disabled')) 
                } 
            });
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); 
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => """ + str(random.choice([4,6,8,12,16])) + """ }); 
            Object.defineProperty(navigator, 'deviceMemory', { get: () => """ + str(random.choice([4,8,16])) + """ }); 
            Object.defineProperty(navigator, 'maxTouchPoints', { get: () => """ + str(random.choice([0,1,5])) + """ });
        """
    })
    
    return driver

def modo_configuracao(nome_perfil):
    LOGGER(f"\n==============================================")
    LOGGER(f"{t['modo_config_titulo']} {nome_perfil} <<<")
    LOGGER(f"==============================================")
    LOGGER(t['modo_config_nav_aberto'])
    LOGGER(t['modo_config_login'])
    LOGGER(t['modo_config_tempo'])
    
    d = None
    try:
        # CORREÇÃO APLICADA: Passando identidade_ua="default_pc"
        d = configurar_driver(nome_perfil, 'pc', 'n', identidade_ua="default_pc", forcar_visivel=True, usar_proxy=False)
        d.get("https://rewards.bing.com/")
        for i in range(600):
            try:
                if not d.window_handles: break
            except: break 
            time.sleep(1)
    except Exception as e:
        LOGGER(f"{t['modo_config_nota']} {e}")
    finally:
        try:
            if d: d.quit()
        except: pass
    LOGGER(f"{t['modo_config_salvo']} {nome_perfil}!")

def processar_conta(nome_perfil, cfg, banco, usar_proxy=False):
    LOGGER(f"\n==============================================")
    LOGGER(f"{t['iniciando_conta']} {nome_perfil} <<<")
    LOGGER(f"==============================================")
    
    if cfg['fazer_tarefas'] == 's' or cfg['limite_pc'] > 0:
        d = None
        try:
            identidade_pc = obter_fingerprint(nome_perfil, 'pc')
            d = configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
            
            # --- ÁREA DAS TAREFAS (DASHBOARD) ---
            if cfg['fazer_tarefas'] == 's': 
                limpar_todas_as_missoes(d)     # 1. Limpa os cards normais
                fazer_pesquisa_visual(d)       # 2. Executa a missão de Pesquisa Visual (NOVO)
                
            # --- ÁREA DAS PESQUISAS ---
            if cfg['limite_pc'] > 0: 
                fluxo_pesquisas(d, 'pc', cfg['limite_pc'], banco)
                
            LOGGER(t['sessao_pc_fim'])
            wait_human(10.0, 30.0, long_pause_chance=0.0)
            
        except Exception as e: 
            LOGGER(f"{t['erro_pc']} ({nome_perfil}): {e}")
        finally:
            if d: d.quit()

    if cfg['limite_mobile'] > 0:
        d_m = None
        try:
            identidade_mob = obter_fingerprint(nome_perfil, 'mobile')
            d_m = configurar_driver(nome_perfil, 'mobile', cfg['modo_oculto'], identidade_mob, usar_proxy=usar_proxy)
            
            fluxo_pesquisas(d_m, 'mobile', cfg['limite_mobile'], banco)
            
            LOGGER(t['sessao_mob_fim'])
            wait_human(10.0, 30.0, long_pause_chance=0.0)
            
        except Exception as e: 
            LOGGER(f"{t['erro_mob']} ({nome_perfil}): {e}")
        finally:
            if d_m: d_m.quit()
         
    hora_atual = time.strftime("%H:%M:%S")
    msg = t['discord_sucesso'].format(nome_perfil, hora_atual)
    enviar_notificacao(msg)
    
def alternar_startup():
    sistema = platform.system().lower()
    caminho_exe = os.path.abspath(sys.argv[0])
    
    if sistema == "windows":
        pasta_startup = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        arquivo_startup = os.path.join(pasta_startup, "RewardsBot_Startup.vbs")
        conteudo = (
            f'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WScript.Sleep 90000\n' # ATUALIZAÇÃO: Aguarda 90 segundos antes de iniciar
            f'WshShell.Run chr(34) & "{caminho_exe}" & chr(34) & " --auto", 0\n'
            f'Set WshShell = Nothing'
        )
        
    elif sistema == "linux":
        pasta_startup = os.path.expanduser("~/.config/autostart")
        arquivo_startup = os.path.join(pasta_startup, "RewardsBot.desktop")
        conteudo = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            f"Exec=\"{caminho_exe}\" --auto\n"
            "Hidden=false\n"
            "NoDisplay=false\n"
            "X-GNOME-Autostart-enabled=true\n"
            "Name=RewardsBot\n"
            "Comment=FPG Rewards Auto Start\n"
        )
        
    elif sistema == "darwin": 
        pasta_startup = os.path.expanduser("~/Library/LaunchAgents")
        arquivo_startup = os.path.join(pasta_startup, "com.fpg.rewardsbot.plist")
        conteudo = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
            "<plist version=\"1.0\">\n"
            "<dict>\n"
            "    <key>Label</key>\n"
            "    <string>com.fpg.rewardsbot</string>\n"
            "    <key>ProgramArguments</key>\n"
            "    <array>\n"
            f"        <string>{caminho_exe}</string>\n"
            "        <string>--auto</string>\n"
            "    </array>\n"
            "    <key>RunAtLoad</key>\n"
            "    <true/>\n"
            "</dict>\n"
            "</plist>\n"
        )
    else:
        LOGGER(f"\n  \033[91m{t['startup_erro_criar']}\033[0m")
        return

    if os.path.exists(arquivo_startup):
        try:
            if sistema == "darwin":
                os.system(f"launchctl unload {arquivo_startup} >/dev/null 2>&1")
                
            os.remove(arquivo_startup)
            LOGGER(f"\n  \033[93m{t['startup_desativado']}\033[0m")
        except Exception as e:
            LOGGER(f"\n  \033[91m{t['startup_erro_rem']} {e}\033[0m")
    else:
        try:
            os.makedirs(pasta_startup, exist_ok=True)
            
            with open(arquivo_startup, "w", encoding="utf-8") as f:
                f.write(conteudo)
            
            if sistema == "darwin":
                os.system(f"launchctl load {arquivo_startup} >/dev/null 2>&1")
            elif sistema == "linux":
                os.chmod(arquivo_startup, os.stat(arquivo_startup).st_mode | stat.S_IEXEC)
                
            LOGGER(f"\n  \033[92m{t['startup_ativado']}\033[0m")
        except Exception as e:
            LOGGER(f"\n  \033[91m{t['startup_erro_criar']} {e}\033[0m")

def criar_kill_switch():
    sistema = platform.system().lower()
    pasta_usuario = os.path.expanduser("~") 
    
    if sistema == "windows":
        arquivo = os.path.join(pasta_usuario, "StopBot.bat")
        conteudo = (
            "@echo off\ntitle BotReward Kill Switch\ncolor 0C\n"
            "echo [!] Alvo na mira: Encerrando motor principal do Bot...\n"
            "taskkill /F /IM RewardsBot.exe /T >nul 2>&1\n"
            "taskkill /F /IM python.exe /T >nul 2>&1\n"
            "echo [!] Encerrando motor Selenium invisivel (preservando o Chrome)...\n"
            "taskkill /F /IM chromedriver.exe /T >nul 2>&1\n"
            "echo [!] Limpando rastros de jogos camuflados na memoria...\n"
            "taskkill /F /IM ping.exe /T >nul 2>&1\n"
            "echo [!] Solicitando fechamento seguro do Discord (preservando Token)...\n"
            "taskkill /IM DiscordCanary.exe /T >nul 2>&1\n"
            "taskkill /IM DiscordPTB.exe /T >nul 2>&1\n"
            "echo [OK] Ameaca neutralizada e RAM limpa!\ntimeout /t 3 >nul\nexit"
        )
    else:
        arquivo = os.path.join(pasta_usuario, "StopBot.sh")
        conteudo = (
            "#!/bin/bash\n"
            "echo '[!] Encerrando motor principal do Bot...'\n"
            "pkill -9 -f RewardsBot\n"
            "pkill -9 -f python\n"
            "echo '[!] Encerrando Selenium e limpando camuflagens...'\n"
            "pkill -9 -f chromedriver\n"
            "pkill -9 -f ping\n"
            "echo '[!] Solicitando fechamento seguro do Discord...'\n"
            "pkill -15 -f DiscordCanary\n"
            "pkill -15 -f DiscordPTB\n"
            "echo '[OK] Ameaca neutralizada e RAM limpa!'\n"
        )
        
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        if sistema != "windows":
            os.chmod(arquivo, os.stat(arquivo).st_mode | stat.S_IEXEC)
    except Exception:
        pass

def limpar_processos_zumbis():
    """Garante que nenhum ChromeDriver invisível antigo ficou preso na RAM"""
    LOGGER(t['zumbi_clean'])
    sistema = platform.system().lower()
    try:
        if sistema == "windows":
            subprocess.run("taskkill /F /IM chromedriver.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run("pkill -9 -f chromedriver", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    except: 
        pass


def iniciar_ciclo_farm():
    """Função central chamada pela GUI"""
    try:
        limpar_processos_zumbis()
        cfg = carregar_config()
        banco = carregar_termos_online()
        
        for index, perfil in enumerate(CONTAS_PARA_FARMAR):
            if ABORTAR_PROCESSO: 
                break
                
            usar_proxy = False
            
            if index > 0:
                LOGGER(f"\n{t['prep_4g']} {perfil}")
                ip_cel = localizar_ip_celular()
                
                if not ip_cel:
                    LOGGER(t['cel_nao_det'])
                    espera = 0
                    while not ip_cel and espera < 60:
                        time.sleep(5)
                        espera += 5
                        ip_cel = localizar_ip_celular()
                
                if not ip_cel:
                    LOGGER(t['timeout_4g'])
                    break
                
                rotacionar_ip_celular()
                iniciar_proxy_background(ip_cel)
                usar_proxy = True
                
            # ===== O SELETOR DE MOTOR ALINHADO AQUI DENTRO DO FOR =====
            if cfg.get('ms_new_tasks', 's') == 's':
                # Usa o novo motor com pausas humanizadas de 40 min+
                import BingStarEngine
                BingStarEngine.iniciar_ciclo_star_bonus(perfil, cfg, banco, usar_proxy)
            else:
                # Usa a versão clássica rápida (processar_conta)
                processar_conta(perfil, cfg, banco, usar_proxy)
            # ===========================================================
            
        limpar_excesso_historico()
        
    except Exception as e:
        # GERADOR DE CRASH LOG (A "Caixa Preta")
        data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = BASE_DIR / f"CRASH_LOG_{data_hora}.txt"
        
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"=== REWARD BOT CRASH REPORT ===\n")
            f.write(f"DATA: {data_hora}\n")
            f.write(f"ERRO: {str(e)}\n\n")
            f.write("=== TRACEBACK COMPLETO ===\n")
            f.write(traceback.format_exc())
            
        LOGGER(t['crash_log'].format(log_path.name), "error")
        alerta_sos = t['crash_sos'].format(log_path.name, str(e)[:150])
        enviar_notificacao(alerta_sos)
    
def registrar_data_execucao(modulo):
    arquivo = BASE_DIR / "Time_Exe.json"
    hoje = datetime.now().strftime("%d/%m/%Y") # <-- CORRIGIDO AQUI
    dados = {}
    if arquivo.exists():
        with open(arquivo, 'r', encoding='utf-8') as f:
            try: dados = json.load(f)
            except: pass
    
    # Salva apenas a string da data mais recente, apagando a anterior
    dados[modulo] = hoje
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)

def verificar_se_rodou_hoje(modulo, dias_cooldown=0):
    arquivo = BASE_DIR / "Time_Exe.json"
    if not arquivo.exists(): return False
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        try: dados = json.load(f)
        except: return False
        
    ultimo_uso = dados.get(modulo, "")
    
    # Se o arquivo antigo estiver quebrado com uma lista [ ], ignora e roda
    if not ultimo_uso or isinstance(ultimo_uso, list): 
        return False 
    
    try:
        data_salva = datetime.strptime(ultimo_uso, "%d/%m/%Y").date()
        hoje = datetime.now().date() 
        if (hoje - data_salva).days >= dias_cooldown:
            return False # Já passou o tempo, pode rodar
        return True # Ainda está no cooldown, não roda
    except:
        return False
        


def verificar_conta_suspensa(driver, nome_perfil):
    """Lê a tela atual em busca de avisos de suspensão da Microsoft"""
    try:
        texto_pagina = driver.find_element(By.TAG_NAME, "body").text.lower()
        termos_ban = ["conta suspensa", "account suspended", "sua conta do microsoft rewards foi suspensa", "contact microsoft support"]
        
        if any(termo in texto_pagina for termo in termos_ban):
            msg = t['alerta_ban'].format(nome_perfil)
            LOGGER(msg, "error")
            enviar_notificacao(msg)
            return True
    except:
        pass
    return False