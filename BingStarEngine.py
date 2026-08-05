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
            # LOG TRADUZIDO
            LOGGER(t['star_pesquisa'].format(i+1, qtd, tipo_device.upper(), termo_final))
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


def iniciar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy):
    """
    Máquina de Estados que lê o contador unificado de 60 pontos (20 pesquisas)
    e espalha elas organicamente usando a tática de checkpoint.
    """
    LOGGER("==============================================")
    LOGGER(t['star_init'].format(nome_perfil))
    LOGGER("==============================================")
    
    # ---------------------------------------------------------
    # ETAPA 1: Aquecimento PC, Dashboard e Leitura do Limite Único
    # ---------------------------------------------------------
    LOGGER(t['star_etapa1'])
    d_pc = None
    pesquisas_restantes = 0
    try:
        identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
        d_pc = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
        
        # --- DEFESA FAIL-FAST ADICIONADA AQUI ---
        d_pc.get("https://rewards.bing.com/")
        time.sleep(4)
        if RewardsCore.verificar_conta_suspensa(d_pc, nome_perfil):
            return # Aborta o Star Engine na mesma hora se estiver banido!
        # ----------------------------------------
        
        if cfg.get('fazer_tarefas', 'n') == 's': 
            RewardsCore.limpar_todas_as_missoes(d_pc)
            RewardsCore.fazer_pesquisa_visual(d_pc)
            
        # Lê o limite exato unificado direto da Microsoft (A mágica do Checkpoint!)
        pesquisas_restantes = RewardsCore.verificar_pesquisas_restantes(d_pc, 'pc')
        
        if pesquisas_restantes > 0:
            # Pega entre 30% e 45% do que falta para fazer no PC agora
            pc_bloco_1 = random.randint(int(pesquisas_restantes * 0.30), int(pesquisas_restantes * 0.45))
            if pc_bloco_1 > 0:
                _fazer_lote_pesquisas(d_pc, pc_bloco_1, banco, "pc")
                pesquisas_restantes -= pc_bloco_1
                
    except Exception as e:
        LOGGER(t['star_falha1'].format(e), "error")
    finally:
        if d_pc: d_pc.quit()

    if RewardsCore.ABORTAR_PROCESSO or pesquisas_restantes <= 0: return

    # ---------------------------------------------------------
    # ETAPA 2: Foco Parcial no Celular
    # ---------------------------------------------------------
    LOGGER(t['star_etapa2'].format(pesquisas_restantes))
    time.sleep(random.uniform(15.0, 30.0)) 
    
    d_mob = None
    try:
        identidade_mob = RewardsCore.obter_fingerprint(nome_perfil, 'mobile')
        d_mob = RewardsCore.configurar_driver(nome_perfil, 'mobile', cfg['modo_oculto'], identidade_mob, usar_proxy=usar_proxy)
        
        # Pega metade do que sobrou pra fazer no celular
        mob_bloco = random.randint(int(pesquisas_restantes * 0.40), int(pesquisas_restantes * 0.60))
        if mob_bloco > 0:
            _fazer_lote_pesquisas(d_mob, mob_bloco, banco, "mobile")
            pesquisas_restantes -= mob_bloco
            
    except Exception as e:
        LOGGER(t['star_falha2'].format(e), "error")
    finally:
        if d_mob: d_mob.quit()

    if RewardsCore.ABORTAR_PROCESSO or pesquisas_restantes <= 0: return

    # ---------------------------------------------------------
    # ETAPA 3: A Pausa do Café (Pulo do Gato)
    # ---------------------------------------------------------
    pausa_minutos = random.randint(35, 65)
    LOGGER(t['star_etapa3'].format(pausa_minutos), "warning")
    
    segundos_totais = pausa_minutos * 60
    passos = 10
    for i in range(passos):
        if RewardsCore.ABORTAR_PROCESSO: return
        time.sleep(segundos_totais / passos)

    # ---------------------------------------------------------
    # ETAPA 4: Volta ao PC para Liquidar o Saldo
    # ---------------------------------------------------------
    LOGGER(t['star_etapa4'])
    d_pc2 = None
    try:
        d_pc2 = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
        
        # Faz a leitura do painel NOVAMENTE pra ter certeza que não vai extrapolar o limite real
        faltam_real = RewardsCore.verificar_pesquisas_restantes(d_pc2, 'pc')
        if faltam_real > 0:
            _fazer_lote_pesquisas(d_pc2, faltam_real, banco, "pc")
            
    except Exception as e:
        LOGGER(t['star_falha4'].format(e), "error")
    finally:
        if d_pc2: d_pc2.quit()

    hora_atual = time.strftime("%H:%M:%S")
    LOGGER(t['star_sucesso'].format(nome_perfil, hora_atual), "success")