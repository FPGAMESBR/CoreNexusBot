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

SPEED = "normal"

def smart_sleep(base_min, base_max, cancelavel_por_turbo=False):
    import random
    import time
    base = random.uniform(base_min, base_max)
    
    if cancelavel_por_turbo:
        passos = int(base)
        for _ in range(passos):
            if SPEED == "turbo":
                print("[SISTEMA] Turbo ativado! Abortando hibernação massiva.")
                break
            time.sleep(1)
        time.sleep(base - passos)
    else:
        if SPEED == "turbo":
            base *= 0.3
        elif SPEED == "stealth":
            base *= 2.5
        time.sleep(base)

def gerar_banco_cognitivo():
    import random
    from datetime import datetime
    import urllib.request
    import xml.etree.ElementTree as ET
    import json
    
    lang = carregar_config().get("language", "en")
    hora = datetime.now().hour
    banco = []
    
    # 1. Fetch RSS News
    noticias_rss = []
    try:
        url_rss = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419" if lang == "pt" else "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url_rss, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item'):
                title = item.find('title').text
                if title:
                    clean_title = title.rsplit(' - ', 1)[0]
                    noticias_rss.append(clean_title)
    except Exception as e:
        LOGGER(f"[SYSTEM] Erro ao buscar RSS: {e}", "warning")

    # 2. Wikipedia Random API (High Entropy Organic Searches)
    artigos_wiki = []
    try:
        wiki_lang = "pt" if lang == "pt" else "en"
        wiki_url = f"https://{wiki_lang}.wikipedia.org/w/api.php?action=query&list=random&rnlimit=30&rnnamespace=0&format=json"
        req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for r in data.get('query', {}).get('random', []):
                artigos_wiki.append(r['title'])
    except Exception as e:
        LOGGER(f"[SYSTEM] Erro ao buscar Wikipedia: {e}", "warning")

    # Prefixos para misturar com a Wikipedia
    prefixos_wiki_pt = ["quem foi ", "história de ", "o que é ", "onde fica ", "resumo sobre ", "significado de "]
    prefixos_wiki_en = ["who was ", "history of ", "what is ", "where is ", "summary of ", "meaning of "]

    # 2.5 Fetch Google Trends RSS
    noticias_trends = []
    try:
        url_trends = "https://trends.google.com/trending/rss?geo=BR" if lang == "pt" else "https://trends.google.com/trending/rss?geo=US"
        req = urllib.request.Request(url_trends, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall('./channel/item'):
                title = item.find('title').text
                if title: noticias_trends.append(title)
    except Exception as e:
        LOGGER(f"[SYSTEM] Erro ao buscar Google Trends: {e}", "warning")

    # Persona Templates (Fallback e base orgânica expandida)
    templates = []
    if lang == "pt":
        if 6 <= hora <= 11:
            templates = [
                "como está o trânsito na minha região hoje", "previsão do tempo detalhada para hoje",
                "cotação do dólar hoje", "fechamento do ibovespa", "resultados dos jogos de ontem",
                "principais notícias do mercado financeiro hoje", "exercícios matinais para fazer em casa",
                "como fazer café na prensa francesa", "receita de panqueca de aveia fit", "podcasts de notícias da manhã",
                "principais manchetes dos jornais de hoje", "como organizar o dia de trabalho", "como acordar cedo sem cansaço"
            ]
        elif 12 <= hora <= 18:
            templates = [
                "como resolver erro de permissão na AWS IAM", "diferença entre instâncias EC2 e Fargate",
                "melhores cursos para certificação CompTIA Security+", "configurar VPN no Windows 11",
                "como usar o GitHub Copilot no VSCode", "diferença entre processadores AMD Ryzen e Intel Core",
                "qual o melhor SSD NVMe M.2 1TB", "como testar se a memória RAM está com defeito",
                "o que é arquitetura de microsserviços", "como otimizar consultas no banco de dados",
                "onde almoçar perto de mim", "restaurantes com prato feito barato", "como combater o sono depois do almoço",
                "melhores métodos de produtividade pomodoro", "como focar no trabalho", "playlist para trabalhar lofi"
            ]
        else:
            templates = [
                "dicas de builds para {jogo}", "melhores jogos em promoção na Steam",
                "review do microfone condensador HyperX QuadCast", "qual a melhor interface de áudio custo benefício",
                "diferença entre Smart TV OLED e QLED", "melhores aplicativos de delivery",
                "como instalar câmera IP Wi-Fi em casa", "qual o melhor teclado mecânico sem fio",
                "lançamentos netflix dessa semana", "resumo do filme a substância", "melhores animes da temporada",
                "receitas de jantar rápido e fácil", "dicas para dormir melhor rápido", "livros de ficção científica mais vendidos"
            ]
            jogos = ["Deadlock", "Cyberpunk 2077", "Elden Ring", "Valorant", "CS2", "Baldur's Gate 3", "Minecraft", "GTA V", "The Sims 4"]
            templates = [t.format(jogo=random.choice(jogos)) if "{jogo}" in t else t for t in templates]
    else:
        if 6 <= hora <= 11:
            templates = [
                "traffic conditions near me right now", "local weather forecast for today",
                "stock market opening today", "usd exchange rate", "sports highlights from last night",
                "top financial news of the day", "quick morning workout routines",
                "how to make french press coffee", "healthy oatmeal pancake recipe", "morning news podcasts",
                "today's top headlines", "how to organize workday", "how to wake up early without feeling tired"
            ]
        elif 12 <= hora <= 18:
            templates = [
                "how to fix AWS IAM permission denied", "difference between EC2 and Fargate",
                "best study materials for CompTIA Security+", "how to setup VPN on Windows 11",
                "how to use GitHub Copilot in VSCode", "AMD Ryzen vs Intel Core processors comparison",
                "best 1TB NVMe M.2 SSD", "how to test RAM for errors",
                "what is microservices architecture", "how to optimize database queries",
                "lunch near me", "cheap fast food places", "how to fight post lunch sleepiness",
                "best pomodoro productivity methods", "how to focus on work", "lofi beats to work to"
            ]
        else:
            templates = [
                "best builds for {jogo}", "top games on sale on Steam right now",
                "HyperX QuadCast microphone review", "best budget audio interface",
                "OLED vs QLED Smart TV difference", "best food delivery apps",
                "how to install Wi-Fi IP camera at home", "best wireless mechanical keyboard",
                "new releases on netflix this week", "the substance movie explained", "best anime of the season",
                "quick and easy dinner recipes", "tips to fall asleep fast", "best selling sci-fi books"
            ]
            jogos = ["Deadlock", "Cyberpunk 2077", "Elden Ring", "Valorant", "CS2", "Baldur's Gate 3", "Minecraft", "GTA V", "The Sims 4"]
            templates = [t.format(jogo=random.choice(jogos)) if "{jogo}" in t else t for t in templates]

    # 3. Generate 50 searches (Hybrid mix)
    for _ in range(50):
        sorteio = random.random()
        
        # 25% RSS News, 25% Google Trends, 25% Wikipedia, 25% Templates
        if sorteio < 0.25 and noticias_rss:
            noticia = random.choice(noticias_rss)
            if random.random() < 0.30:
                prefixo = "notícias sobre: " if lang == "pt" else "news about: "
                banco.append(f"{prefixo}{noticia}")
            else:
                banco.append(noticia)
                
        elif sorteio >= 0.25 and sorteio < 0.50 and noticias_trends:
            trend = random.choice(noticias_trends)
            banco.append(trend)

        elif sorteio >= 0.50 and sorteio < 0.75 and artigos_wiki:
            artigo = random.choice(artigos_wiki)
            prefixos = prefixos_wiki_pt if lang == "pt" else prefixos_wiki_en
            if random.random() < 0.60:
                banco.append(f"{random.choice(prefixos)}{artigo}")
            else:
                banco.append(artigo)
                
        else:
            banco.append(random.choice(templates))
            
    random.shuffle(banco)
    return banco

_LOCALES_CACHE = None

def t(chave):
    global _LOCALES_CACHE
    if _LOCALES_CACHE is None:
        try:
            with open(BASE_DIR / "locales.json", "r", encoding="utf-8") as f:
                _LOCALES_CACHE = json.load(f)
        except Exception:
            _LOCALES_CACHE = {}
            
    lang = carregar_config().get("language", "en")
    return _LOCALES_CACHE.get(lang, {}).get(chave, _LOCALES_CACHE.get("en", {}).get(chave, chave))


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

def update_ui(modulo, status, porcentagem):
    try:
        import webview
        # Procura a janela ativa do pywebview e injeta o comando JS
        for window in webview.windows:
            window.evaluate_js(f"if(typeof atualizarPainel === 'function') atualizarPainel('{modulo}', '{status}', {porcentagem});")
    except Exception:
        pass

def preparar_ambiente_adb():
    cfg = carregar_config()
    if cfg.get("multi_account", "n") == "n":
        return 
        
    sistema = platform.system().lower()
    ext = ".exe" if sistema == "windows" else ""
    caminho_adb = BASE_DIR / "platform-tools" / f"adb{ext}"
    
    if caminho_adb.exists(): return
    
    LOGGER(t('adb_nao_encontrado').format(sistema.upper()))
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
            
        LOGGER(t('adb_sucesso'))
    except Exception as e:
        LOGGER(t('adb_erro').format(e))

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
        "discord_global_quests": "n",
        "language": "pt",
        "speed_mode": "normal"
    }
    
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                padrao.update(dados_salvos)
        except Exception:
            pass
            
    return padrao

try:
    SPEED = carregar_config().get("speed_mode", "normal")
except:
    SPEED = "normal"

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
        LOGGER(t('4g_ligando_aviao'))
        subprocess.run([str(caminho_adb), "shell", "cmd", "connectivity", "airplane-mode", "enable"], ...)
        time.sleep(5) 
        
        LOGGER(t('4g_desligando_aviao'))
        subprocess.run([str(caminho_adb), "shell", "cmd", "connectivity", "airplane-mode", "disable"], ...)
        time.sleep(10) # Tempo um pouco maior para a operadora "esquecer" o aparelho
        
        ip_novo = localizar_ip_celular()
        if ip_novo and ip_novo != ip_antigo:
            LOGGER(t('4g_rotacao_concluida'))
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
        LOGGER(t('proxy_ativado').format(ip_celular))
    except Exception as e:
        LOGGER(t('proxy_erro').format(e))

# =============================================================================
# FUNÇÕES DE LÓGICA CORE & STEALTH
# =============================================================================
def wait_human(min_s=3.0, max_s=8.0, long_pause_chance=0.15):
    if random.random() < long_pause_chance:
        pausa = random.uniform(35.0, 90.0)
        LOGGER(t('pausa_humana').format(int(pausa)))
        time.sleep(pausa)
    else:
        time.sleep(random.uniform(min_s, max_s))

def ghost_click(driver, elemento, cliques=1):
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
        LOGGER(t('erro_notificacao').format(e))
        
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
    LOGGER(t('otimizando_historico'))
    try:
        if ARQUIVO_HISTORICO.exists():
            historico = list(carregar_historico())
            if len(historico) > 300:
                with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
                    json.dump(historico[-300:], f, ensure_ascii=False, indent=4)
    except Exception: pass


def limpar_todas_as_missoes(driver):
    update_ui("bing", "Painel...", 30)
    LOGGER(f"\n{t('verificando_paineis')}")
    paginas_para_limpar = ["https://rewards.bing.com/dashboard", "https://rewards.bing.com/earn"]
    missoes_feitas = 0
    links_visitados = []
    
    for pagina in paginas_para_limpar:
        LOGGER(f"\n[CHROME] -> Analisando: {pagina}")
        try:
            sucesso_carregamento = False
            for tentativa in range(3):
                if ABORTAR_PROCESSO: return
                try:
                    driver.get(pagina)
                    from selenium.webdriver.support.ui import WebDriverWait
                    try: WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
                    except: pass
                    time.sleep(random.uniform(5.0, 8.0)) 
                    
                    painel_carregou = driver.execute_script("""
                        let oldUi = document.querySelector('#daily-sets') !== null || document.querySelector('.c-card') !== null;
                        let newUi = document.getElementById('dailyset') !== null || document.getElementById('offers') !== null || document.querySelector('[data-rac]') !== null;
                        return oldUi || newUi;
                    """)
                    
                    if painel_carregou:
                        sucesso_carregamento = True
                        break
                    else:
                        LOGGER(f"[CHROME] Painel não validado visualmente. Retentando carregar {pagina} (Tentativa {tentativa+1}/3)...", "warning")
                except Exception: pass
                
            if not sucesso_carregamento:
                LOGGER(f"[CHROME] [ERRO] Falha de Estágio: Página {pagina} não carregou corretamente. Pulando bloco.", "error")
                continue
            
            if verificar_conta_suspensa(driver, "Perfil Atual"):
                break
            principal = driver.current_window_handle
            
            from selenium.webdriver.support import expected_conditions as EC
            
            while True:
                if ABORTAR_PROCESSO: return
                alvo_info = driver.execute_script("""
                    let visitados = arguments[0];
                    let links = document.querySelectorAll('a[class*="rounded-cornerCardDefault"], a[href]');
                    
                    for (let link of links) {
                        let href = link.href || "";
                        if (!href || href === "") continue;
                        let hrefLower = href.toLowerCase();
                        
                        if (link.closest('header, footer, nav, #redeem, #snapshot, #achievements, #welcome')) continue;
                        
                        let ign = ['/redeem', '/about', '/badges', '/status', '/history', '/dashboard', '/earn', '/refer', 'rwgbopen=1', 'microsoft.com/edge', 'xbox.com', 'bingapp.microsoft.com', 'vsstreak', 'support.microsoft.com', 'go.microsoft.com', 'choice.microsoft.com'];
                        if (ign.some(i => hrefLower.includes(i))) continue;
                        
                        let html = link.innerHTML.toLowerCase();
                        let text = link.innerText ? link.innerText.toLowerCase() : '';
                        
                        let isCompleted = 
                            text.includes("concluído") || 
                            text.includes("completed") || 
                            html.includes("bg-statussuccessrewardsbg") || 
                            html.includes("text-statussuccesstintfg") || 
                            html.includes("1.788 1.953 3.25-3.743") || 
                            html.includes("mee-icon-statuscirclecheckmark") ||
                            html.includes("mee-icon-skypecirclecheck") || 
                            html.includes("✓") || 
                            html.includes("10 10s-4.477 10-10 10s2 17.523");
                            
                        let progressBars = link.querySelectorAll('[role="progressbar"]');
                        progressBars.forEach(pb => {
                            let valNow = pb.getAttribute('aria-valuenow');
                            let valMax = pb.getAttribute('aria-valuemax');
                            if (valNow && valMax && valNow === valMax && valMax !== "0") {
                                isCompleted = true;
                            }
                        });
                            
                        if (isCompleted) continue;
                        
                        if (!visitados.includes(href) && link.offsetWidth > 0) {
                            let titleEl = link.querySelector('p.text-globalBody2Strong') || link.querySelector('h3, h4, .title');
                            let titulo = titleEl ? titleEl.innerText : "Missao_Extra";
                            return [link, href, titulo];
                        }
                    }
                    return null;
                """, links_visitados)
                
                if not alvo_info: 
                    LOGGER(t('painel_limpo'))
                    break
                
                alvo_elemento = alvo_info[0]
                link_alvo = alvo_info[1]
                titulo_missao = alvo_info[2]
                
                links_visitados.append(link_alvo)
                LOGGER(f"    - Iniciando Tarefa: {titulo_missao[:40]}")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", alvo_elemento)
                wait_human(1.0, 2.5, long_pause_chance=0.0)
                
                janelas_antes = driver.window_handles
                driver.execute_script("arguments[0].click();", alvo_elemento)
                
                try: WebDriverWait(driver, 6).until(EC.new_window_is_opened(janelas_antes))
                except Exception: pass
                
                janelas_depois = driver.window_handles
                novas = [j for j in janelas_depois if j not in janelas_antes]
                
                if novas:
                    driver.switch_to.window(novas[0])
                    wait_human(8.0, 15.0, long_pause_chance=0.2) 
                    
                    try:
                        from selenium.webdriver.common.by import By
                        espera_quiz = WebDriverWait(driver, 4)
                        try:
                            btn_start = espera_quiz.until(EC.element_to_be_clickable((By.ID, "rqStartQuiz")))
                            btn_start.click()
                            time.sleep(3)
                        except: pass
                        
                        for _ in range(12):
                            if ABORTAR_PROCESSO: break
                            try:
                                opt = driver.find_element(By.CSS_SELECTOR, ".rqOption, .btOption, .b_cards")
                                opt.click()
                                time.sleep(random.uniform(1.5, 3.0))
                            except: break
                    except: pass
                    
                    driver.close()
                    driver.switch_to.window(principal)
                else:
                    wait_human(4.0, 6.0, long_pause_chance=0.0)
                    
                missoes_feitas += 1
        except Exception as e:
            LOGGER(f"    [!] Erro na varredura: {str(e)[:80]}")
            
    LOGGER(f"\n[CHROME] --- Total de {missoes_feitas} missões concluídas com sucesso! ---")

def verificar_pesquisas_restantes(driver, tipo):
    update_ui("bing", "Pesquisas Restantes...", 60)
    valor_ponto = 3 
    
    urls_checagem = [
        "https://rewards.bing.com/earn"
    ]
    
    for url in urls_checagem:
        try:
            nome_url = url.split('/')[-1] if '/' in url else 'home'
            LOGGER(f"   {t('verificando_prog').format(nome_url)}")
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
                    LOGGER(f"   {t('status_concluido').format(tipo.upper(), atual, total)}")
                    return 0
                
                pesquisas_faltantes = faltam_pontos // valor_ponto
                LOGGER(f"   {t('status_real').format(atual, total, pesquisas_faltantes)}")
                return pesquisas_faltantes
                
        except Exception:
            continue 
            
    LOGGER(f"   {t('erro_contador')}")
    return 20

def realizar_pesquisas(driver, num, banco):
    update_ui("bing", "Realizando Pesquisas...", 80)
    num_real = random.choices([num, max(1, num - 1), max(1, num - 2)], weights=[0.6, 0.25, 0.15], k=1)[0]
    LOGGER(t('executando_pesquisas').format(num_real))
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
            LOGGER(f"   {t('aguardando_ponto').format(int(espera_cooldown))}")
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
                            LOGGER(f"   {t('interacao_extra')}")
                            wait_human(3.0, 8.0, long_pause_chance=0.0)
                    except Exception: pass

                links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .b_algo h2 a")
                if links and random.random() < 0.35: 
                    alvo_clique = random.choice(links[:4])
                    janelas_antes = driver.window_handles 
                    webdriver.ActionChains(driver).move_to_element(alvo_clique).pause(random.uniform(0.5, 1.5)).click().perform()
                    LOGGER(f"   {t('lendo_artigo')}")
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
            LOGGER(f"   {t('erro_pesquisa')}")
            wait_human(2.0, 5.0, long_pause_chance=0.0)


def fazer_pesquisa_visual(driver):
    try:
        LOGGER(t('visual_init'), "info")
        
        # --- MÁQUINA DE ESTADOS: VALIDAÇÃO DO DASHBOARD ---
        sucesso_dashboard = False
        for tentativa in range(3):
            driver.get("https://rewards.bing.com/dashboard")
            from selenium.webdriver.support.ui import WebDriverWait
            try: WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
            except: pass
            time.sleep(6)
            
            if driver.execute_script("""
                let text = document.body.innerText.toLowerCase();
                return text.includes('pesquisa visual') || text.includes('visual search');
            """):
                sucesso_dashboard = True
                break
            LOGGER(f"[BING] Interface Visual nao validada. Retentando (Tentativa {tentativa+1}/3)...", "warning")
            
        if not sucesso_dashboard:
            LOGGER("[BING] Erro Critico: Dashboard nao carregou para acionar a Pesquisa Visual.", "error")
            return
        
        # 1. Abre o Flyout lateral clicando no card principal (Novo padrão da Microsoft)
        driver.execute_script("""
            let cards = document.querySelectorAll('div, a, span, button, p');
            for (let el of cards) {
                let texto = el.innerText ? el.innerText.toLowerCase() : '';
                if (texto === 'pesquisa visual' || texto === 'visual search') {
                    let clicavel = el.closest('button, a, [role="button"]') || el;
                    clicavel.click();
                    break;
                }
            }
        """)
        time.sleep(4) 

        # 2. Captura o link de tracking da missão dentro do painel lateral (Flyout) e acessa
        driver.execute_script("""
            let link = document.querySelector('a[href*="vsstreak"]');
            if (link) { window.location.href = link.href; } 
            else { window.location.href = "https://www.bing.com/?features=vsstreak,vstooltip&form=ML2XES"; }
        """)
        
        try: WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
        except: pass
        time.sleep(6) 

        # 3. GERA A IMAGEM E FAZ A PESQUISA DIRETAMENTE PELA URL (Bypassa o bloqueio do Enter)
        semente = random.randint(1, 100000)
        url_imagem_aleatoria = f"https://picsum.photos/seed/{semente}/400/400"
        
        url_pesquisa_direta = f"https://www.bing.com/images/search?view=detailv2&iss=sbi&FORM=SBIHMP&q=imgurl:{url_imagem_aleatoria}&features=vsstreak"
        driver.get(url_pesquisa_direta)
        
        LOGGER(t('visual_img_ok').format(url_imagem_aleatoria), "info")
        time.sleep(12)

        driver.get("https://rewards.bing.com/dashboard")
        LOGGER(t('visual_ok'), "success")

    except Exception as e:
        LOGGER(t('visual_erro_fatal').format(str(e)[:80]), "error")

def fluxo_pesquisas(driver, tipo, limite_fallback, banco):
    LOGGER(f"\n{t('analisando_tipo').format(tipo.upper())}")
    faltam = verificar_pesquisas_restantes(driver, tipo)
    if faltam == 0:
        LOGGER(t('tipo_concluido').format(tipo.upper()))
        return

    if faltam <= 2 and random.random() < 0.4:
        LOGGER(t('fator_preguica').format(tipo.upper()))
        return
    
    if faltam == -1:
        LOGGER(t('erro_status').format(limite_fallback))
        faltam = limite_fallback

    if faltam > 3 and random.random() < 0.05:
        cortar = random.randint(1, 3) 
        faltam_novo = max(1, faltam - cortar) 
        if faltam_novo < faltam:
            LOGGER(t('humor_ativado').format(faltam - faltam_novo, faltam, faltam_novo))
            faltam = faltam_novo
        
    realizar_pesquisas(driver, faltam, banco)
    LOGGER(t('ciclo_encerrado').format(tipo.upper()))
    
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

def configurar_driver(nome_perfil, tipo, oculto, identidade_ua, forcar_visivel=False, usar_proxy=False):
    caminho_perfil = BASE_PROFILES_DIR / nome_perfil
    caminho_perfil.mkdir(parents=True, exist_ok=True)
    
    # --- REMOVEDOR DE TRAVA DO CHROME ---
    try:
        lock_file = caminho_perfil / "SingletonLock"
        if lock_file.exists(): lock_file.unlink()
    except: pass
    
    opts = uc.ChromeOptions()
    opts.add_argument(f"--user-data-dir={caminho_perfil}")
    opts.add_argument("--log-level=3")
    opts.add_argument("--lang=pt-BR")
    
    if usar_proxy: opts.add_argument(f'--proxy-server=http://127.0.0.1:{PORTA_PROXY}')
    
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-features=site-per-process,CalculateNativeWinOcclusion,WebAuthentication,PasswordManagerOnboarding,PasswordManager,EnablePasswordsAccountStorage,Passkeys")
    opts.add_argument("--disable-blink-features=Attestation,AutomationControlled")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    
    modo_invisivel = (oculto == 's') and (not forcar_visivel)
    
    if modo_invisivel:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-position=100000,100000") 
        opts.add_argument("--window-size=1920,1080")
    else:
        opts.add_argument("--window-position=0,0") 
        opts.add_argument("--window-size=1280,800")
        
    driver = None
    
    # === PATCH ANTI-INVISIBILIDADE (FILTRO DE CMD) ===
    _original_popen = subprocess.Popen
    
    if getattr(sys, 'frozen', False) and not modo_invisivel:
        class VisiblePopen(_original_popen):
            def __init__(self, *args, **kwargs):
                if os.name == 'nt':
                    # Verifica qual processo o Python está tentando abrir
                    cmd = args[0]
                    is_driver = False
                    if isinstance(cmd, str) and 'chromedriver' in cmd.lower():
                        is_driver = True
                    elif isinstance(cmd, list) and any('chromedriver' in str(x).lower() for x in cmd):
                        is_driver = True
                    
                    si = kwargs.get('startupinfo')
                    if not si: si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    # 0 = Oculta o CMD preto / 5 = Exibe a janela normal do Chrome
                    si.wShowWindow = 0 if is_driver else 5  
                    kwargs['startupinfo'] = si
                super().__init__(*args, **kwargs)
        subprocess.Popen = VisiblePopen
    # ==============================================================

    for tentativa in range(3):
        try:
            driver = uc.Chrome(options=opts, use_subprocess=True)
            break 
        except Exception as e:
            LOGGER(t('tentativa_chrome').format(tentativa+1))
            time.sleep(3)
            
    # Restaura o sistema ao normal para não bugar outras funções
    subprocess.Popen = _original_popen
    
    if not driver: return None

    # Força a janela a saltar para frente do monitor
    if not modo_invisivel:
        try: driver.maximize_window()
        except: pass

    if tipo == 'mobile' and identidade_ua != "default_pc":
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": identidade_ua, "platform": "MacIntel" if "iPhone" in identidade_ua else "Linux"})
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {"width": 390, "height": 844, "deviceScaleFactor": 3, "mobile": True})
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {'offline': False, 'latency': random.randint(45, 95), 'downloadThroughput': random.randint(1500000, 3500000), 'uploadThroughput': random.randint(500000, 1500000), 'connectionType': 'cellular4g'})

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });
            Object.defineProperty(document, 'hidden', { get: () => false });
            window.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
            
            Object.defineProperty(navigator, 'credentials', { value: { create: () => Promise.reject(new Error('WebAuthn disabled')), get: () => Promise.reject(new Error('WebAuthn disabled')) } });
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); 
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => """ + str(random.choice([4,6,8,12,16])) + """ }); 
            Object.defineProperty(navigator, 'deviceMemory', { get: () => """ + str(random.choice([4,8,16])) + """ }); 
            Object.defineProperty(navigator, 'maxTouchPoints', { get: () => """ + str(random.choice([0,1,5])) + """ });
        """
    })
    return driver

def modo_configuracao(nome_perfil):
    LOGGER(f"\n==============================================")
    LOGGER(f"{t('modo_config_titulo')} {nome_perfil} <<<")
    LOGGER(f"==============================================")
    LOGGER(t('modo_config_nav_aberto'))
    LOGGER(t('modo_config_login'))
    LOGGER(t('modo_config_tempo'))
    
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
        LOGGER(f"{t('modo_config_nota')} {e}")
    finally:
        try:
            if d: d.quit()
        except: pass
    LOGGER(f"{t('modo_config_salvo')} {nome_perfil}!")

    
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
        LOGGER(f"\n  \033[91m{t('startup_erro_criar')}\033[0m")
        return

    if os.path.exists(arquivo_startup):
        try:
            if sistema == "darwin":
                os.system(f"launchctl unload {arquivo_startup} >/dev/null 2>&1")
                
            os.remove(arquivo_startup)
            LOGGER(f"\n  \033[93m{t('startup_desativado')}\033[0m")
        except Exception as e:
            LOGGER(f"\n  \033[91m{t('startup_erro_rem')} {e}\033[0m")
    else:
        try:
            os.makedirs(pasta_startup, exist_ok=True)
            
            with open(arquivo_startup, "w", encoding="utf-8") as f:
                f.write(conteudo)
            
            if sistema == "darwin":
                os.system(f"launchctl load {arquivo_startup} >/dev/null 2>&1")
            elif sistema == "linux":
                os.chmod(arquivo_startup, os.stat(arquivo_startup).st_mode | stat.S_IEXEC)
                
            LOGGER(f"\n  \033[92m{t('startup_ativado')}\033[0m")
        except Exception as e:
            LOGGER(f"\n  \033[91m{t('startup_erro_criar')} {e}\033[0m")

def limpar_processos_zumbis():
    """Garante que nenhum ChromeDriver invisível antigo ficou preso na RAM"""
    LOGGER(t('zumbi_clean'))
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
        cfg = carregar_config()
        
        # CHECAGEM ADICIONADA: Se não tem limite_pc, limite_mobile e nem fazer_tarefas, não iniciar Bing
        if int(cfg.get('limite_pc', 0)) == 0 and int(cfg.get('limite_mobile', 0)) == 0 and cfg.get('fazer_tarefas', 'n') == 'n':
            LOGGER("\n[SYSTEM] Limites de pesquisa zerados e painel desativado. Ignorando bot do Bing.", "info")
            update_ui("bing", "Ignorado", 100)
            return
            
        banco = gerar_banco_cognitivo()
        
        for index, perfil in enumerate(CONTAS_PARA_FARMAR):
            if ABORTAR_PROCESSO: 
                break
                
            usar_proxy = False
            
            if index > 0:
                LOGGER(f"\n{t('prep_4g')} {perfil}")
                ip_cel = localizar_ip_celular()
                
                if not ip_cel:
                    LOGGER(t('cel_nao_det'))
                    espera = 0
                    while not ip_cel and espera < 60:
                        time.sleep(5)
                        espera += 5
                        ip_cel = localizar_ip_celular()
                
                if not ip_cel:
                    LOGGER(t('timeout_4g'))
                    break
                
                rotacionar_ip_celular()
                iniciar_proxy_background(ip_cel)
                usar_proxy = True
                
            # ===== O SELETOR DE MOTOR ALINHADO AQUI DENTRO DO FOR =====
            import BingStarEngine
            BingStarEngine.iniciar_ciclo_star_bonus(perfil, cfg, banco, usar_proxy)
            # ===========================================================
            
        limpar_excesso_historico()
        update_ui("bing", "Concluído!", 100)
        
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
            
        LOGGER(t('crash_log').format(log_path.name), "error")
        alerta_sos = t('crash_sos').format(log_path.name, str(e)[:150])
        enviar_notificacao(alerta_sos)
    
def registrar_data_execucao(modulo):
    arquivo = BASE_DIR / "Exe.json"
    hoje = datetime.now().strftime("%d/%m/%Y")
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
    arquivo = BASE_DIR / "Exe.json"
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
            msg = t('alerta_ban').format(nome_perfil)
            LOGGER(msg, "error")
            enviar_notificacao(msg)
            return True
    except:
        pass
    return False