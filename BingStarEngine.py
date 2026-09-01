import time
import random
import traceback
from datetime import datetime

# Importamos as ferramentas do seu Core para reutilizar a inteligência base
import RewardsCore
from RewardsCore import wait_human, ghost_click, gerar_termo_humanizado, salvar_historico, LOGGER, t

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
            termo_final = gerar_termo_humanizado([termo_base], idioma=RewardsCore.IDIOMA_GLOBAL)
            # LOG TRADUZIDO E ADAPTADO
            LOGGER(f"   [STAR ENGINE] ({i+1}/{qtd}) [{tipo_device.upper()}] {termo_final}")
            salvar_historico(termo_base)
            
            # Ghost Click com erro humano
            ghost_click(driver, sb, cliques=random.randint(2,3)) 
            sb.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.2, 0.6))
            
            # Digitação orgânica lenta
            for letra in termo_final:
                sb.send_keys(letra)
                time.sleep(random.uniform(0.08, 0.25))
            
            # Chance alta de simular erro de digitação
            if random.random() < 0.35: 
                time.sleep(random.uniform(0.5, 1.2))
                qtd_apagar = random.randint(2, min(8, len(termo_final)))
                for _ in range(qtd_apagar):
                    sb.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.05, 0.2))
                nova_palavra = random.choice([" online", " review", " news", " grátis", " preço"])
                for letra in nova_palavra:
                    sb.send_keys(letra)
                    time.sleep(random.uniform(0.08, 0.25))
                
            wait_human(1.0, 3.5, long_pause_chance=0.0)
            sb.send_keys(Keys.RETURN)
            
            # Cooldown MAIOR entre pesquisas (para a telemetria do Bing Star)
            espera_cooldown = random.uniform(12.0, 25.0)
            time.sleep(espera_cooldown)
            
            # Comportamento pós-pesquisa (rolar tela e ler algo)
            try:
                descer = random.randint(400, 1200)
                driver.execute_script(f"window.scrollTo(0, {descer});")
                wait_human(3.0, 6.0, long_pause_chance=0.05)
                
                # Clica em um link aleatório 40% das vezes
                links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .b_algo h2 a")
                if links and random.random() < 0.40: 
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
                        wait_human(20.0, 50.0, long_pause_chance=0.3) # Fica lendo a notícia 
                        driver.close()
                        driver.switch_to.window(principal) 
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
            "https://edition.cnn.com/"
        ]
        site_escolhido = random.choice(sites_organicos)
        LOGGER(f"   [CAFE] Acessando '{site_escolhido}' para gerar tráfego fantasma...", "info")
        d_cafe.get(site_escolhido)
        
        # Define a pausa entre 35 e 65 minutos
        minutos = random.randint(35, 65)
        LOGGER(f"   [CAFE] Tempo estimado do descanso: {minutos} minutos.", "info")
        
        # A cada 5 minutos, ele dá um scroll aleatório na página para simular que você está lendo/assistindo
        ciclos = minutos // 5
        for i in range(ciclos):
            if RewardsCore.ABORTAR_PROCESSO: break
            time.sleep(5 * 60) # Dorme por 5 minutos
            try:
                LOGGER(f"   [CAFE] Status: Assistindo/Lendo... ({i+1}/{ciclos})", "info")
                d_cafe.execute_script("window.scrollBy(0, Math.random() * 800 + 200);")
            except: pass
            
    except Exception as e:
        LOGGER(f"[STAR ENGINE] [X] Erro no Modo Café: {e}", "error")
    finally:
        if d_cafe: d_cafe.quit()


def iniciar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy):
    # CORREÇÃO APLICADA: RewardsCore. antes do update_ui
    RewardsCore.update_ui("bing", f"Preparando {nome_perfil}...", 10)
    LOGGER("======================================================")
    LOGGER(f"\n>>> [BING STAR ENGINE] INICIANDO MODO CAOS: {nome_perfil} <<<")
    LOGGER("======================================================")
    
    # ---------------------------------------------------------
    # MONTAGEM DA "RODA DO CAOS" (Pool de Tarefas)
    # ---------------------------------------------------------
    acoes = []
    
    if cfg.get('fazer_tarefas', 'n') == 's':
        acoes.append("TAREFAS_DASHBOARD")
        
    # Dividimos o farm do PC em 2 metades (para espalhar as pesquisas)
    if cfg.get('limite_pc', 0) > 0:
        acoes.extend(["PC_CHUNK", "PC_CHUNK"])
        
    # Dividimos o farm do Celular em 2 metades
    if cfg.get('limite_mobile', 0) > 0:
        acoes.extend(["MOB_CHUNK", "MOB_CHUNK"])
        
    # A Pausa Orgânica para não parecer um robô
    acoes.append("MODO_CAFE")
    
    # Embaralha tudo de forma orgânica
    random.shuffle(acoes)
    
    # Regra de Segurança: Impede que o "Modo Café" seja a última ação da lista
    # (Para garantir que o bot termine o ciclo pesquisando ou abrindo o painel para o Bing registrar)
    if acoes[-1] == "MODO_CAFE":
        acoes[-1], acoes[0] = acoes[0], acoes[-1]

    # Contadores para sabermos se devemos fazer 'metade' ou 'tudo' do que falta
    pc_chunks_restantes = acoes.count("PC_CHUNK")
    mob_chunks_restantes = acoes.count("MOB_CHUNK")
    
    # CORREÇÃO APLICADA: RewardsCore. antes do update_ui
    RewardsCore.update_ui("bing", "Pesquisas...", 50)

    # ---------------------------------------------------------
    # EXECUÇÃO DINÂMICA DA FILA
    # ---------------------------------------------------------
    for i, acao in enumerate(acoes):
        if RewardsCore.ABORTAR_PROCESSO: break
        
        LOGGER(f"\n[STAR ENGINE] ---> EXECUTANDO AÇÃO {i+1}/{len(acoes)}: [{acao}] <---", "warning")
        
        if acao == "TAREFAS_DASHBOARD":
            d_task = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_task = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                d_task.get("https://rewards.bing.com/")
                time.sleep(5)
                
                # Defesa Fail-Fast nativa
                if RewardsCore.verificar_conta_suspensa(d_task, nome_perfil):
                    return 
                    
                RewardsCore.limpar_todas_as_missoes(d_task)
                RewardsCore.fazer_pesquisa_visual(d_task)
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha nas tarefas do Dashboard: {e}", "error")
            finally:
                if d_task: d_task.quit()
                
        elif acao == "PC_CHUNK":
            d_pc = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_pc = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                # O segredo: Avalia o saldo a cada bloco, nunca faz de forma cega!
                faltam = RewardsCore.verificar_pesquisas_restantes(d_pc, 'pc')
                
                if faltam > 0:
                    if pc_chunks_restantes > 1:
                        # Se ainda tem outro bloco de PC na fila, faz só de 40% a 60% do que falta
                        qtd = random.randint(int(faltam * 0.4), int(faltam * 0.6))
                    else:
                        # Se é o último bloco de PC na fila, tenta zerar o saldo
                        qtd = faltam
                        
                    if qtd > 0:
                        _fazer_lote_pesquisas(d_pc, qtd, banco, "pc")
                else:
                    LOGGER("   [STAR ENGINE] Meta de PC já atingida. Pulando bloco.", "success")
                        
                pc_chunks_restantes -= 1
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha no Bloco PC: {e}", "error")
            finally:
                if d_pc: d_pc.quit()
                
        elif acao == "MOB_CHUNK":
            d_mob = None
            try:
                identidade_mob = RewardsCore.obter_fingerprint(nome_perfil, 'mobile')
                d_mob = RewardsCore.configurar_driver(nome_perfil, 'mobile', cfg['modo_oculto'], identidade_mob, usar_proxy=usar_proxy)
                
                faltam = RewardsCore.verificar_pesquisas_restantes(d_mob, 'mobile')
                # Fallback de segurança se falhar a leitura
                if faltam == -1: faltam = cfg.get('limite_mobile', 20)
                    
                if faltam > 0:
                    if mob_chunks_restantes > 1:
                        qtd = random.randint(int(faltam * 0.4), int(faltam * 0.6))
                    else:
                        qtd = faltam
                        
                    if qtd > 0:
                        _fazer_lote_pesquisas(d_mob, qtd, banco, "mobile")
                else:
                    LOGGER("   [STAR ENGINE] Meta Mobile já atingida. Pulando bloco.", "success")
                        
                mob_chunks_restantes -= 1
            except Exception as e:
                LOGGER(f"[STAR ENGINE] Falha no Bloco Mobile: {e}", "error")
            finally:
                if d_mob: d_mob.quit()
                
        elif acao == "MODO_CAFE":
            _pausa_do_cafe_organica(nome_perfil, cfg, usar_proxy)

    hora_atual = time.strftime("%H:%M:%S")
    RewardsCore.update_ui("bing", "Concluído!", 100)
    LOGGER(f"\n[STAR ENGINE] >>> SUCESSO ABSOLUTO! Conta {nome_perfil} blindada e farmada. ({hora_atual})", "success")