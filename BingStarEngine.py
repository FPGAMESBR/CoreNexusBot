import time
import random
import traceback
from datetime import datetime

# Importamos as ferramentas do seu Core para reutilizar a inteligência base
import RewardsCore
from RewardsCore import wait_human, ghost_click, salvar_historico, LOGGER, t

def _fazer_lote_pesquisas(driver, qtd, banco, tipo_device="pc"):
    """Função interna que faz 'X' pesquisas da forma mais humana possível"""
    
    amostra = random.sample(banco, min(qtd + 5, len(banco)))
    
    for i in range(qtd):
        if RewardsCore.ABORTAR_PROCESSO: break
        try:
            # Limpeza ocasional de cache para simular navegador real
            if (i + 1) % 5 == 0 and random.random() < 0.20:
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
            
            # Encontra a barra de pesquisa
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            espera = WebDriverWait(driver, 10)
            try: sb = espera.until(EC.element_to_be_clickable((By.ID, "sb_form_q")))
            except TimeoutException:
                try: sb = driver.find_element(By.NAME, "q")
                except NoSuchElementException:
                    try: sb = driver.find_element(By.CLASS_NAME, "b_searchbox")
                    except Exception: continue
            
            termo_base = amostra[i]
            termo_final = termo_base
            # LOG TRADUZIDO E ADAPTADO
            LOGGER(f"   [STAR ENGINE] ({i+1}/{qtd}) [{tipo_device.upper()}] {termo_final}")
            salvar_historico(termo_base)
            
            # Ghost Click com erro humano
            ghost_click(driver, sb, cliques=random.randint(2,3)) 
            sb.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.2, 0.6))
            
            # Phase 4 - Dislexia Cognitiva
            if RewardsCore.SPEED != "turbo" and random.random() < 0.25:
                erro_palavras = ["bplo de cenora", "como faser", "donwload gratiz", "iphne 16"]
                erro = random.choice(erro_palavras)
                
                # Typing speed logic based on SPEED
                for letra in erro:
                    sb.send_keys(letra)
                    if RewardsCore.SPEED == "stealth": time.sleep(random.uniform(0.12, 0.18))
                    else: time.sleep(random.uniform(0.06, 0.10))
                
                RewardsCore.smart_sleep(1.0, 3.0)
                
                for _ in range(len(erro)):
                    sb.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.02, 0.05))
                    
                RewardsCore.smart_sleep(0.5, 1.0)
                
            # Digitação orgânica lenta
            for letra in termo_final:
                sb.send_keys(letra)
                if RewardsCore.SPEED == "turbo": time.sleep(random.uniform(0.01, 0.03))
                elif RewardsCore.SPEED == "stealth": time.sleep(random.uniform(0.12, 0.18))
                else: time.sleep(random.uniform(0.06, 0.10))
                
            wait_human(1.0, 3.5, long_pause_chance=0.0)
            sb.send_keys(Keys.RETURN)
            
            # Cooldown MAIOR entre pesquisas (para a telemetria do Bing Star)
            RewardsCore.smart_sleep(12.0, 25.0)
            
            # Comportamento pós-pesquisa (rolar tela e ler algo)
            if RewardsCore.SPEED != "turbo":
                try:
                    descer = random.randint(400, 1200)
                    driver.execute_script(f"window.scrollTo(0, {descer});")
                    wait_human(3.0, 6.0, long_pause_chance=0.05)
                    
                    # Clica em um link aleatório
                    links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .b_algo h2 a")
                    chance_clique = 0.90 if RewardsCore.SPEED == "stealth" else 0.40
                    if links and random.random() < chance_clique: 
                        alvo_clique = random.choice(links[:3])
                        janelas_antes = driver.window_handles 
                        import selenium.webdriver
                        selenium.webdriver.ActionChains(driver).move_to_element(alvo_clique).pause(random.uniform(1.0, 2.0)).click().perform()
                        time.sleep(5) 
                        
                        janelas_depois = driver.window_handles
                        if len(janelas_depois) > len(janelas_antes):
                            nova_aba = [j for j in janelas_depois if j not in janelas_antes][0]
                            principal = driver.current_window_handle
                            driver.switch_to.window(nova_aba)
                            if RewardsCore.SPEED == "stealth":
                                RewardsCore.smart_sleep(40.0, 90.0)
                            else:
                                wait_human(20.0, 50.0, long_pause_chance=0.3)
                            driver.close()
                            driver.switch_to.window(principal) 
                        else:
                            if RewardsCore.SPEED == "stealth":
                                RewardsCore.smart_sleep(40.0, 90.0)
                            else:
                                wait_human(20.0, 45.0, long_pause_chance=0.3)
                            driver.back() 
                    else:
                        if random.random() > 0.4:
                            subir = descer - random.randint(150, 400)
                            driver.execute_script(f"window.scrollTo(0, {subir});")
                except Exception: pass
            
        except Exception: 
            wait_human(3.0, 6.0, long_pause_chance=0.0)


def _pausa_do_cafe_organica(nome_perfil, cfg, usar_proxy):
    """
    Abre sites populares para gerar tráfego orgânico e cookies não relacionados à Microsoft,
    mantendo a janela ativa por muito tempo
    """
    LOGGER("\n[STAR ENGINE] ☕ INICIANDO O MODO CAFÉ (Navegação Orgânica Ociosa)...", "warning")
    d_cafe = None
    try:
        identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
        d_cafe = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
        
        sites_organicos = [
            "https://www.youtube.com/feed/trending",
            "https://www.reddit.com/",
            "https://x.com/explore",
            "https://pt.wikipedia.org/wiki/Especial:Aleatória",
            "https://edition.cnn.com/",
            "https://g1.globo.com/",
            "https://www.amazon.com/",
            "https://www.twitch.tv/",
            "https://techcrunch.com/",
            "https://www.theverge.com/"
        ]
        
        minutos_totais = random.randint(35, 65)
        LOGGER(f"   [CAFE] Tempo total do descanso será de: {minutos_totais} minutos.", "info")
        
        minutos_gastos = 0
        ultimo_site = ""
        
        while minutos_gastos < minutos_totais:
            if RewardsCore.ABORTAR_PROCESSO: break
            
            opcoes = [s for s in sites_organicos if s != ultimo_site]
            site_escolhido = random.choice(opcoes)
            ultimo_site = site_escolhido
            
            LOGGER(f"   [CAFE] Acessando '{site_escolhido}'...", "info")
            try:
                d_cafe.get(site_escolhido)
            except Exception:
                pass
            
            # Fica entre 5 a 10 minutos neste site
            tempo_site = random.randint(5, 10)
            if minutos_gastos + tempo_site > minutos_totais:
                tempo_site = minutos_totais - minutos_gastos
                
            LOGGER(f"   [CAFE] Navegando neste site por {tempo_site} minutos...", "info")
            
            for _ in range(tempo_site):
                if RewardsCore.ABORTAR_PROCESSO: break
                try:
                    d_cafe.execute_script("window.scrollBy(0, Math.random() * 800 + 200);")
                except: pass
                RewardsCore.smart_sleep(60.0, 60.0) # Dorme 1 minuto monitorando a flag de aborto
                minutos_gastos += 1
                
    except Exception as e:
        LOGGER(f"[STAR ENGINE] [X] Erro no Modo Café: {e}", "error")
    finally:
        if d_cafe: 
            try: d_cafe.quit()
            except: pass
        time.sleep(4) # FOLGA PARA O WINDOWS LIMPAR A RAM ANTES DO PRÓXIMO CHUNK


def check_extended_days(cfg):
    from datetime import datetime
    ext = cfg.get('extended_days', 'n')
    if ext == 'a':
        return True
    if ext == 'w' and datetime.now().weekday() >= 5:
        return True
    return False

def iniciar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy):
    if RewardsCore.ABORTAR_PROCESSO: return

    RewardsCore.update_ui("bing", f"Preparando {nome_perfil}...", 10)
    LOGGER("======================================================")
    LOGGER(f"\n>>> [BING STAR ENGINE] INICIANDO MODO CAOS: {nome_perfil} <<<")
    LOGGER("======================================================")
    
    acoes = []
    if cfg.get('fazer_tarefas', 'n') == 's':
        acoes.append("TAREFAS_DASHBOARD")
        
    if cfg.get('limite_pc', 0) > 0:
        if RewardsCore.SPEED == "turbo":
            acoes.append("PC_CHUNK")
        else:
            acoes.extend(["PC_CHUNK", "PC_CHUNK"])
        
    if cfg.get('limite_mobile', 0) > 0:
        if RewardsCore.SPEED == "turbo":
            acoes.append("MOB_CHUNK")
        else:
            acoes.extend(["MOB_CHUNK", "MOB_CHUNK"])
        
    if RewardsCore.SPEED != "turbo" and (cfg.get('limite_pc', 0) > 0 or cfg.get('limite_mobile', 0) > 0):
        acoes.append("MODO_CAFE")
        
    random.shuffle(acoes)
        
    if "MODO_CAFE" in acoes and len(acoes) > 1:
        if acoes[0] == "MODO_CAFE":
            acoes[0], acoes[1] = acoes[1], acoes[0]
        if acoes[-1] == "MODO_CAFE":
            acoes[-1], acoes[-2] = acoes[-2], acoes[-1]

    pc_chunks_restantes = acoes.count("PC_CHUNK")
    mob_chunks_restantes = acoes.count("MOB_CHUNK")
    
    RewardsCore.update_ui("bing", "Pesquisas...", 50)

    for i, acao in enumerate(acoes):
        if RewardsCore.ABORTAR_PROCESSO: break
        LOGGER(f"\n[STAR ENGINE] ---> EXECUTANDO AÇÃO {i+1}/{len(acoes)}: [{acao}] <---", "warning")
        
        if acao == "MODO_CAFE" and RewardsCore.SPEED == "turbo":
            LOGGER("[STAR ENGINE] Marcha Turbo ativada. Pulando o Modo Café.", "warning")
            continue
            
        if check_extended_days(cfg) and i < len(acoes) - 1 and RewardsCore.SPEED != "turbo":
            LOGGER("[STAR ENGINE] Chrono-Gating: Iniciando hibernação massiva entre blocos.", "info")
            RewardsCore.smart_sleep(3600.0, 10800.0, cancelavel_por_turbo=True)
        
        if acao == "TAREFAS_DASHBOARD":
            d_task = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_task = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                if d_task is None: raise Exception("ChromeDriver não iniciou. Sistema Operacional retendo a porta.")
                    
                d_task.get("https://rewards.bing.com/")
                time.sleep(5)
                if RewardsCore.verificar_conta_suspensa(d_task, nome_perfil): return 
                RewardsCore.limpar_todas_as_missoes(d_task)
                try: RewardsCore.fazer_pesquisa_visual(d_task)
                except: pass
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha nas tarefas do Dashboard: {e}", "error")
            finally:
                if d_task: 
                    try: d_task.quit()
                    except: pass
                time.sleep(5) # APENAS FOLGA, SEM TASKKILL
                
        elif acao == "PC_CHUNK":
            d_pc = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_pc = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                if d_pc is None: raise Exception("Driver Nulo.")
                faltam = RewardsCore.verificar_pesquisas_restantes(d_pc, 'pc')
                if RewardsCore.SPEED == "stealth" and faltam > 0:
                    faltam += random.randint(5, 12)
                if faltam > 0:
                    qtd = random.randint(int(faltam * 0.4), int(faltam * 0.6)) if pc_chunks_restantes > 1 else faltam
                    if qtd > 0: _fazer_lote_pesquisas(d_pc, qtd, banco, "pc")
                else: LOGGER("   [STAR ENGINE] Meta de PC já atingida. Pulando bloco.", "success")
                pc_chunks_restantes -= 1
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha no Bloco PC: {e}", "error")
            finally:
                if d_pc: 
                    try: d_pc.quit()
                    except: pass
                time.sleep(5)
                
        elif acao == "MOB_CHUNK":
            d_mob = None
            try:
                identidade_mob = RewardsCore.obter_fingerprint(nome_perfil, 'mobile')
                d_mob = RewardsCore.configurar_driver(nome_perfil, 'mobile', cfg['modo_oculto'], identidade_mob, usar_proxy=usar_proxy)
                
                if d_mob is None: raise Exception("Driver Nulo.")
                faltam = RewardsCore.verificar_pesquisas_restantes(d_mob, 'mobile')
                if faltam == -1: faltam = cfg.get('limite_mobile', 20)
                if RewardsCore.SPEED == "stealth" and faltam > 0:
                    faltam += random.randint(5, 12)
                if faltam > 0:
                    qtd = random.randint(int(faltam * 0.4), int(faltam * 0.6)) if mob_chunks_restantes > 1 else faltam
                    if qtd > 0: _fazer_lote_pesquisas(d_mob, qtd, banco, "mobile")
                else: LOGGER("   [STAR ENGINE] Meta Mobile já atingida. Pulando bloco.", "success")
                mob_chunks_restantes -= 1
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha no Bloco Mobile: {e}", "error")
            finally:
                if d_mob: 
                    try: d_mob.quit()
                    except: pass
                time.sleep(5)
                
        elif acao == "MODO_CAFE":
            _pausa_do_cafe_organica(nome_perfil, cfg, usar_proxy)

    hora_atual = time.strftime("%H:%M:%S")
    RewardsCore.update_ui("bing", "Concluído!", 100)
    LOGGER(f"\n[STAR ENGINE] >>> SUCESSO ABSOLUTO! Conta {nome_perfil} blindada e farmada. ({hora_atual})", "success")