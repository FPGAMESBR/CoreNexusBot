import time
import random
import traceback
from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Importamos as ferramentas do seu Core para reutilizar a inteligência base
import RewardsCore
from RewardsCore import wait_human, ghost_click, salvar_historico, LOGGER, t

def _fazer_lote_pesquisas(driver, qtd, banco, tipo_device="pc"):
    """Função que realiza buscas no Bing de forma orgânica, com garantia de execução e fail-safe"""
    import urllib.parse
    
    if not banco:
        banco = ["tecnologia hoje", "noticias brasil", "previsao do tempo", "cinema novidades", "jogos pc"]
    
    # Amostragem segura sem estourar limites
    if len(banco) >= qtd + 5:
        amostra = random.sample(banco, qtd + 5)
    else:
        multiplicador = (qtd // len(banco)) + 2
        amostra = (banco * multiplicador)[:qtd + 5]
    
    for i in range(qtd):
        if RewardsCore.ABORTAR_PROCESSO: break
        try:
            termo_base = amostra[i]
            termo_final = termo_base
            LOGGER(f"   [STAR ENGINE] ({i+1}/{qtd}) [{tipo_device.upper()}] {termo_final}")
            salvar_historico(termo_base)
            
            # Limpeza ocasional de cache durante navegação orgânica
            if (i + 1) % 8 == 0 and random.random() < 0.15:
                try: driver.execute_script("window.localStorage.clear();")
                except Exception: pass

            pesquisa_concluida = False
            
            # 1. TENTATIVA ORGÂNICA (Digitação na barra de busca com Ghost Click)
            try:
                c_url = driver.current_url.lower() if driver.current_url else ""
                if "bing.com" not in c_url:
                    driver.get("https://www.bing.com/")
                    time.sleep(2)
                
                # Auto-dispensa de banners de cookies e overlays de foco do Bing
                try:
                    driver.execute_script("""
                        let b = document.querySelector('#bnp_btn_accept, [id*="accept"], #b_cookie');
                        if (b) b.click();
                        let ov = document.querySelector('.hp_focus_overlay, #b_overlay');
                        if (ov) ov.remove();
                    """)
                except Exception: pass
                
                # Procura a caixa de texto ativa
                sb = None
                for seletor in [
                    (By.ID, "sb_form_q"),
                    (By.NAME, "q"),
                    (By.CSS_SELECTOR, "textarea[name='q'], input[name='q'], #sb_form_q"),
                    (By.CLASS_NAME, "b_searchbox")
                ]:
                    try:
                        el = driver.find_element(*seletor)
                        if el and el.is_displayed():
                            sb = el
                            break
                    except Exception:
                        continue
                
                if sb:
                    ghost_click(driver, sb, cliques=random.randint(1, 2))
                    time.sleep(random.uniform(0.15, 0.35))
                    
                    try: driver.execute_script("arguments[0].value = '';", sb)
                    except Exception:
                        sb.send_keys(Keys.CONTROL + "a")
                        sb.send_keys(Keys.BACKSPACE)
                        
                    # Simulação de erro humano / dislexia
                    if RewardsCore.SPEED != "turbo" and random.random() < 0.20:
                        erros = ["bplo de cenora", "como faser", "donwload gratiz", "iphne 16"]
                        erro = random.choice(erros)
                        for l in erro:
                            sb.send_keys(l)
                            time.sleep(random.uniform(0.04, 0.08))
                        RewardsCore.smart_sleep(0.4, 1.0)
                        for _ in range(len(erro)):
                            sb.send_keys(Keys.BACKSPACE)
                            time.sleep(random.uniform(0.02, 0.04))
                            
                    # Digitação da busca real
                    for l in termo_final:
                        sb.send_keys(l)
                        if RewardsCore.SPEED == "turbo": time.sleep(random.uniform(0.01, 0.02))
                        else: time.sleep(random.uniform(0.04, 0.08))
                        
                    wait_human(0.6, 1.8, long_pause_chance=0.0)
                    sb.send_keys(Keys.RETURN)
                    pesquisa_concluida = True
            except Exception:
                pesquisa_concluida = False
            
            # 2. FAIL-SAFE INFALÍVEL: Navegação direta para /search se a digitação falhou
            if not pesquisa_concluida:
                termo_cod = urllib.parse.quote_plus(termo_final)
                origens = [
                    f"https://www.bing.com/search?q={termo_cod}&form=QBLH",
                    f"https://www.bing.com/search?q={termo_cod}&form=QBRE",
                    f"https://www.bing.com/search?q={termo_cod}&form=HDRSC1",
                    f"https://www.bing.com/search?q={termo_cod}&form=ANNTH1"
                ]
                driver.get(random.choice(origens))
                pesquisa_concluida = True
                
            # Cooldown inteligente entre pesquisas para registro de telemetria
            if RewardsCore.SPEED == "turbo":
                time.sleep(random.uniform(4.0, 7.0))
            else:
                RewardsCore.smart_sleep(7.0, 14.0)
                
            # Interação pós-pesquisa (rolagem e visualização de links)
            if RewardsCore.SPEED != "turbo":
                try:
                    descer = random.randint(350, 950)
                    driver.execute_script(f"window.scrollTo(0, {descer});")
                    wait_human(2.0, 4.0, long_pause_chance=0.05)
                    
                    links = driver.find_elements(By.CSS_SELECTOR, "h2 a, .b_algo h2 a")
                    if links and random.random() < 0.30: 
                        alvo_clique = random.choice(links[:3])
                        janelas_antes = driver.window_handles 
                        ActionChains(driver).move_to_element(alvo_clique).pause(random.uniform(0.6, 1.2)).click().perform()
                        time.sleep(4) 
                        
                        janelas_depois = driver.window_handles
                        if len(janelas_depois) > len(janelas_antes):
                            nova_aba = [j for j in janelas_depois if j not in janelas_antes][0]
                            principal = driver.current_window_handle
                            driver.switch_to.window(nova_aba)
                            wait_human(8.0, 18.0, long_pause_chance=0.2)
                            driver.close()
                            driver.switch_to.window(principal) 
                        else:
                            wait_human(8.0, 16.0, long_pause_chance=0.2)
                            driver.back() 
                    else:
                        if random.random() > 0.4:
                            subir = descer - random.randint(100, 300)
                            driver.execute_script(f"window.scrollTo(0, {subir});")
                except Exception: pass
        except Exception as e_busca:
            LOGGER(f"   [STAR ENGINE] Aviso na busca {i+1}: {e_busca}", "warning")
            wait_human(2.0, 4.0, long_pause_chance=0.0)


def _pausa_do_cafe_organica(nome_perfil, cfg, usar_proxy):
    """
    Abre sites populares para gerar tráfego orgânico e cookies não relacionados à Microsoft,
    mantendo a janela ativa por muito tempo
    """
    LOGGER(t("star_modo_cafe"), "warning")
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
                except Exception: pass
                RewardsCore.smart_sleep(60.0, 60.0) # Dorme 1 minuto monitorando a flag de aborto
                minutos_gastos += 1
                
    except Exception as e:
        LOGGER(f"[STAR ENGINE] [X] Erro no Modo Café: {e}", "error")
    finally:
        if d_cafe: 
            try: d_cafe.quit()
            except Exception: pass
        time.sleep(4) # FOLGA PARA O WINDOWS" LIMPAR A RAM ANTES" DO PR"XIMO CHUNK


def _planejar_acoes_star_bonus(cfg, speed):
    """Organiza blocos aleatoriamente garantindo que o Modo Café só ocorra entre a 1ª e a 2ª metade das pesquisas."""
    primeira_metade = []
    segunda_metade = []

    if int(cfg.get('limite_pc', 0)) > 0:
        primeira_metade.append("PC_CHUNK")
        if speed != "turbo":
            segunda_metade.append("PC_CHUNK")

    if int(cfg.get('limite_mobile', 0)) > 0:
        primeira_metade.append("MOB_CHUNK")
        if speed != "turbo":
            segunda_metade.append("MOB_CHUNK")

    random.shuffle(primeira_metade)
    random.shuffle(segunda_metade)

    acoes = list(primeira_metade)
    if speed != "turbo" and segunda_metade:
        acoes.append("MODO_CAFE")
        acoes.extend(segunda_metade)

    if cfg.get('fazer_tarefas', 'n') == 's':
        if not acoes:
            acoes.append("TAREFAS_DASHBOARD")
        else:
            pos = random.randint(0, len(acoes))
            acoes.insert(pos, "TAREFAS_DASHBOARD")

    return acoes


def deve_pular_modo_cafe(progresso_inicial_por_tipo, pc_chunks_pendentes, mob_chunks_pendentes, speed, limiar_progresso=0.50):
    """Decide se o Modo Café deve ser pulado (Turbo, progresso inicial >= 50%, ou sem pesquisas restantes)."""
    if speed == "turbo":
        return True, "turbo", 0.0

    validos = [
        (atual, total)
        for atual, total in progresso_inicial_por_tipo.values()
        if atual is not None and total is not None and total > 0
    ]
    if validos:
        soma_atual = sum(a for a, _ in validos)
        soma_total = sum(tot for _, tot in validos)
        ratio = soma_atual / soma_total if soma_total > 0 else 0.0
        if ratio >= 1.0:
            return True, "sem_pesquisas", ratio
        if ratio >= limiar_progresso:
            return True, "progresso_alto", ratio

    if pc_chunks_pendentes <= 0 and mob_chunks_pendentes <= 0:
        return True, "sem_pesquisas", 1.0

    return False, None, 0.0


def iniciar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy):
    if RewardsCore.ABORTAR_PROCESSO:
        return False
    return _executar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy)


def _executar_ciclo_star_bonus(nome_perfil, cfg, banco, usar_proxy):
    if RewardsCore.ABORTAR_PROCESSO:
        return False

    RewardsCore.update_ui("bing", f"Preparando {nome_perfil}...", 10)
    LOGGER("======================================================")
    LOGGER(f">>> [BING STAR ENGINE] INICIANDO MODO CAOS: {nome_perfil} <<<")
    LOGGER("======================================================")
    
    acoes = _planejar_acoes_star_bonus(cfg, RewardsCore.SPEED)

    pc_chunks_restantes = acoes.count("PC_CHUNK")
    mob_chunks_restantes = acoes.count("MOB_CHUNK")
    progresso_inicial_por_tipo = {}
    pc_concluido_sessao = False
    mob_concluido_sessao = False
    houve_acao_ok = False
    houve_falha = False
    
    RewardsCore.update_ui("bing", "Pesquisas...", 50)

    for i, acao in enumerate(acoes):
        if RewardsCore.ABORTAR_PROCESSO:
            return False

        if acao == "PC_CHUNK" and pc_concluido_sessao:
            pc_chunks_restantes = max(0, pc_chunks_restantes - 1)
            continue

        if acao == "MOB_CHUNK" and mob_concluido_sessao:
            mob_chunks_restantes = max(0, mob_chunks_restantes - 1)
            continue

        if acao == "MODO_CAFE":
            pc_pend = 0 if pc_concluido_sessao else pc_chunks_restantes
            mob_pend = 0 if mob_concluido_sessao else mob_chunks_restantes
            pular, motivo, ratio = deve_pular_modo_cafe(
                progresso_inicial_por_tipo, pc_pend, mob_pend, RewardsCore.SPEED
            )
            if pular:
                if motivo == "turbo":
                    LOGGER(t("star_turbo_ativado"), "warning")
                elif motivo == "progresso_alto":
                    LOGGER(t("star_cafe_pulado_progresso").format(int(round(ratio * 100))), "info")
                else:
                    LOGGER(t("star_cafe_pulado_sem_pesquisas"), "info")
                continue

        LOGGER(f"[STAR ENGINE] ---> EXECUTANDO AÇÃO {i+1}/{len(acoes)}: [{acao}] <---", "warning")
        
        if acao == "TAREFAS_DASHBOARD":
            d_task = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_task = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                if d_task is None: raise Exception("ChromeDriver não iniciou. Sistema Operacional retendo a porta.")
                    
                d_task.get("https://rewards.bing.com/")
                time.sleep(5)
                if RewardsCore.verificar_conta_suspensa(d_task, nome_perfil):
                    return False
                RewardsCore.limpar_todas_as_missoes(d_task)
                try: 
                    RewardsCore.fazer_pesquisa_visual(d_task)
                except Exception as e:
                    LOGGER(f"[STAR ENGINE] Aviso Pesquisa Visual: {e}", "warning")
                houve_acao_ok = True
            except Exception as e:
                houve_falha = True
                LOGGER(f"[STAR ENGINE] Falha nas tarefas do Dashboard: {e}", "error")
            finally:
                if d_task: 
                    try: d_task.quit()
                    except Exception: pass
                time.sleep(5) # APENAS FOLGA, SEM TASKKILL
                
        elif acao == "PC_CHUNK":
            d_pc = None
            try:
                identidade_pc = RewardsCore.obter_fingerprint(nome_perfil, 'pc')
                d_pc = RewardsCore.configurar_driver(nome_perfil, 'pc', cfg['modo_oculto'], identidade_pc, usar_proxy=usar_proxy)
                
                if d_pc is None: raise Exception("Driver Nulo.")
                faltam, atual_pts, total_pts = RewardsCore.obter_progresso_pesquisas(d_pc, 'pc')
                if atual_pts is None:
                    faltam = int(cfg.get('limite_pc', 20))
                elif 'pc' not in progresso_inicial_por_tipo and total_pts:
                    progresso_inicial_por_tipo['pc'] = (atual_pts, total_pts)

                progresso_pc_alto = (
                    'pc' in progresso_inicial_por_tipo
                    and progresso_inicial_por_tipo['pc'][1] > 0
                    and (progresso_inicial_por_tipo['pc'][0] / progresso_inicial_por_tipo['pc'][1]) >= 0.50
                )

                if faltam > 0:
                    if pc_chunks_restantes > 1 and not progresso_pc_alto:
                        qtd = random.randint(max(1, int(faltam * 0.4)), max(1, int(faltam * 0.6)))
                    else:
                        qtd = faltam
                    if qtd > 0:
                        _fazer_lote_pesquisas(d_pc, qtd, banco, "pc")
                    if qtd >= faltam and not RewardsCore.ABORTAR_PROCESSO:
                        pc_concluido_sessao = True
                else:
                    LOGGER(t("star_meta_pc_atingida"), "success")
                    pc_concluido_sessao = True
                pc_chunks_restantes = max(0, pc_chunks_restantes - 1)
                houve_acao_ok = True
            except Exception as e:
                houve_falha = True
                LOGGER(f"[STAR ENGINE] Falha no Bloco PC: {e}", "error")
            finally:
                if d_pc: 
                    try: d_pc.quit()
                    except Exception: pass
                time.sleep(5)
                
        elif acao == "MOB_CHUNK":
            d_mob = None
            try:
                identidade_mob = RewardsCore.obter_fingerprint(nome_perfil, 'mobile')
                d_mob = RewardsCore.configurar_driver(nome_perfil, 'mobile', cfg['modo_oculto'], identidade_mob, usar_proxy=usar_proxy)
                
                if d_mob is None: raise Exception("Driver Nulo.")
                faltam, atual_pts, total_pts = RewardsCore.obter_progresso_pesquisas(d_mob, 'mobile')
                if atual_pts is None:
                    faltam = int(cfg.get('limite_mobile', 20))
                elif 'mobile' not in progresso_inicial_por_tipo and total_pts:
                    progresso_inicial_por_tipo['mobile'] = (atual_pts, total_pts)

                progresso_mob_alto = (
                    'mobile' in progresso_inicial_por_tipo
                    and progresso_inicial_por_tipo['mobile'][1] > 0
                    and (progresso_inicial_por_tipo['mobile'][0] / progresso_inicial_por_tipo['mobile'][1]) >= 0.50
                )

                if faltam > 0:
                    if mob_chunks_restantes > 1 and not progresso_mob_alto:
                        qtd = random.randint(max(1, int(faltam * 0.4)), max(1, int(faltam * 0.6)))
                    else:
                        qtd = faltam
                    if qtd > 0:
                        _fazer_lote_pesquisas(d_mob, qtd, banco, "mobile")
                    if qtd >= faltam and not RewardsCore.ABORTAR_PROCESSO:
                        mob_concluido_sessao = True
                else:
                    LOGGER(t("star_meta_mob_atingida"), "success")
                    mob_concluido_sessao = True
                mob_chunks_restantes = max(0, mob_chunks_restantes - 1)
                houve_acao_ok = True
            except Exception as e:
                houve_falha = True
                LOGGER(f"[STAR ENGINE] Falha no Bloco Mobile: {e}", "error")
            finally:
                if d_mob: 
                    try: d_mob.quit()
                    except Exception: pass
                time.sleep(5)
                
        elif acao == "MODO_CAFE":
            _pausa_do_cafe_organica(nome_perfil, cfg, usar_proxy)

    if RewardsCore.ABORTAR_PROCESSO:
        return False

    hora_atual = time.strftime("%H:%M:%S")
    RewardsCore.update_ui("bing", "Concluído!", 100)
    LOGGER(f"[STAR ENGINE] >>> SUCESSO ABSOLUTO! Conta {nome_perfil} blindada e farmada. ({hora_atual})", "success")
    return houve_acao_ok and not houve_falha