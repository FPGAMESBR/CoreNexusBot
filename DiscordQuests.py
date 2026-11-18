import os
import glob
import time
import subprocess
import urllib.request
import json
import platform
import shutil
import tempfile
import re
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 

import RewardsCore

# ======================================================
# GERENCIAMENTO GLOBAL DE PROCESSOS CAMUFLADOS (JOGOS / PING)
# ======================================================
DUMMY_PROCESSES = []

def matar_processos_camuflados():
    """Mata todos os processos falsos (ex: ping.exe camuflado de jogo) e limpa arquivos temporários"""
    global DUMMY_PROCESSES
    for dp, path in list(DUMMY_PROCESSES):
        try:
            if dp and hasattr(dp, 'pid'):
                subprocess.run(f'taskkill /F /PID {dp.pid} /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if dp and hasattr(dp, 'kill'):
                dp.kill()
        except Exception:
            pass
        if platform.system().lower() == "windows" and path:
            try:
                base = os.path.basename(path)
                subprocess.run(f'taskkill /F /IM "{base}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    DUMMY_PROCESSES.clear()

    # Varredura de segurança para matar processos órfãos derivados de jogos falsos no temp
    if platform.system().lower() == "windows":
        try:
            temp_dir = tempfile.gettempdir()
            for exe_file in glob.glob(os.path.join(temp_dir, "*.exe")):
                nome = os.path.basename(exe_file)
                if any(k in nome.lower() for k in ["maple", "callofduty", "cod", "rust", "endfield", "kof", "resident", "valorant", "outlanders", "wumpus"]):
                    subprocess.run(f'taskkill /F /IM "{nome}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try: os.remove(exe_file)
                    except Exception: pass
            # Elimina com certeza cirúrgica qualquer processo ping residual gerado para simulação de jogos
            subprocess.run('wmic process where "CommandLine like \'%127.0.0.1 -n 3600%\'" call terminate', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

import atexit
atexit.register(matar_processos_camuflados)

# ======================================================
# JAVASCRIPT INJETOR ATUALIZADO (PONTE DE COMUNICAÇÃO SEGURA)
# ======================================================
SCRIPT_JS = r"""
(async function() {
    window.discordQuestsDone = false;
    window.recompensas_logs = window.recompensas_logs || [];
    const logP = (msg) => { window.recompensas_logs.push(msg); };

    try {
        delete window.$;

        let wpRequire = window.webpackChunkdiscord_app.push([[Symbol()], {}, r => r]);
        window.webpackChunkdiscord_app.pop();
        
        let ApplicationStreamingStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getStreamerActiveStreamMetadata)?.exports?.A;
        let RunningGameStore = Object.values(wpRequire.c).find(x => x?.exports?.Ay?.getRunningGames)?.exports?.Ay;
        let QuestsStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getQuest)?.exports?.A;
        let ChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.A?.__proto__?.getAllThreadsForParent)?.exports?.A;
        let GuildChannelStore = Object.values(wpRequire.c).find(x => x?.exports?.Ay?.getSFWDefaultChannel)?.exports?.Ay;
        let FluxDispatcher = window._d || Object.values(wpRequire.c).find(x => x?.exports?.h?.__proto__?.flushWaitQueue)?.exports?.h;
        
        let modules = Object.values(wpRequire.c);
        let findStore = (fn) => {
            for (let m of modules) {
                if (!m?.exports) continue;
                for (let exp of [m.exports, m.exports?.Z, m.exports?.A, m.exports?.ZP, m.exports?.Ay, m.exports?.default]) {
                    if (exp && typeof exp === 'object' && !exp.Messages && !exp.getLocale && fn(exp)) return exp;
                }
            }
            return null;
        };
        let token = findStore(x => typeof x.getToken === 'function')?.getToken();

        if (!token) {
            logP("[JS] ERRO FATAL: Token VIP nao encontrado!");
            window.discordQuestsDone = true; return;
        }

        let findAPI = () => {
            for (let m of modules) {
                try {
                    let exp = m?.exports;
                    if (!exp || typeof exp !== 'object') continue;
                    for (let key of Object.keys(exp)) {
                        let prop = exp[key];
                        if (prop && typeof prop.get === 'function'
                            && typeof prop.post === 'function'
                            && typeof prop.del === 'function'
                            && !prop._dispatcher) {
                            return prop;
                        }
                    }
                } catch(e) {}
            }
            return null;
        };
        let DiscordAPI = findAPI();

        const sealedFor = (questId) => {
            try { return QuestsStore?.getQuest?.(questId)?.trafficMetadataSealed ?? null; }
            catch (_) { return null; }
        };

        const request = async (method, path, body = null) => {
            let options = { method: method, headers: { 'Authorization': token, 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            let res = await fetch(`/api/v9${path}`, options);
            let data = {}; try { data = await res.json(); } catch(e) {}
            return data;
        };

        const safePost = async (path, body = null) => {
            if (DiscordAPI && typeof DiscordAPI.post === 'function') {
                try {
                    let res = await DiscordAPI.post({ url: path, body: body || {} });
                    return { ok: true, body: res?.body || res, status: res?.status || 200, raw: res };
                } catch(err) {
                    return { ok: false, error: err, status: err?.status || 500, body: err?.body || {} };
                }
            }
            try {
                let res = await request('POST', path, body);
                return { ok: true, body: res, status: 200 };
            } catch(err) {
                return { ok: false, error: err, status: 500 };
            }
        };

        window.peloMenosUmSucesso = false;

        const globalIds = INJECT_GLOBAL_IDS;
        const questsWebhookUrl = "INJECT_QUESTS_WEBHOOK";
        if (globalIds && globalIds.length > 0) {
            const pendingGlobalIds = globalIds.filter(id => {
                let q = QuestsStore?.getQuest?.(id);
                if (!q) return true;
                let us = q.userStatus || q.user_status || {};
                if (us.completedAt || us.completed_at || us.enrolledAt || us.enrolled_at) return false;
                let cfg = q.config || {};
                let tCfg = cfg.taskConfigV2 || cfg.taskConfig || cfg.task_config_v2 || cfg.task_config || {};
                let keys = tCfg.tasks instanceof Map ? [...tCfg.tasks.keys()] : Object.keys(tCfg.tasks || {});
                return !keys.some(k => k.includes("VIDEO"));
            });
            if (pendingGlobalIds.length > 0) {
                logP(`[JS] Sincronizando ${pendingGlobalIds.length} missoes globais pendentes...`);
                for (let id of pendingGlobalIds) {
                    try {
                        await safePost(`/quests/${id}/enroll`, {
                            location: 11,
                            platform: 0,
                            is_targeted: false,
                            metadata_sealed: null,
                            traffic_metadata_sealed: sealedFor(id)
                        });
                    } catch(e) {}
                    await new Promise(r => setTimeout(r, 900 + Math.floor(Math.random() * 600)));
                }
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        // VERIFICAÇÃO CRÍTICA DE SEGURANÇA: Checa se a conta está sob quarentena do Discord
        let isSuspended = QuestsStore?.isQuestAccessSuspended || false;
        let suspendedUntil = QuestsStore?.questAccessSuspendedUntil;
        if (!isSuspended && suspendedUntil) {
            let d = new Date(suspendedUntil);
            if (d.getTime() > Date.now()) isSuspended = true;
        }
        if (isSuspended) {
            let dataStr = suspendedUntil ? new Date(suspendedUntil).toLocaleString() : "Data indeterminada";
            logP(`[JS] [ALERTA CRÍTICO DE SEGURANÇA] Acesso a Quests desta conta está suspenso até ${dataStr}.`);
            logP(`[JS] Abortando imediatamente para preservar o Account Standing. Zero pacotes serão enviados.`);
            window.discordQuestsDone = true;
            return;
        }

        let quests = QuestsStore ? [...QuestsStore.quests.values()] : [];
        if (quests.length === 0) {
            let resData = await request('GET', '/quests/@me');
            if (resData?.is_quest_access_suspended || resData?.quest_access_suspended_until) {
                logP(`[JS] [ALERTA] Suspensão detectada na API: ${resData.quest_access_suspended_until}. Abortando.`);
                window.discordQuestsDone = true;
                return;
            }
            let questsList = resData.quests || resData || [];
            quests = Array.isArray(questsList) ? questsList : Object.values(questsList);
        }

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
            { match: k => k.startsWith("PLAY"), type: "GAME", prefer: ["PLAY_ON_DESKTOP"] },
            { match: k => k.startsWith("STREAM"), type: "STREAM", prefer: ["STREAM_ON_DESKTOP"] },
            { match: k => k.includes("ACTIVITY"), type: "ACTIVITY", prefer: ["PLAY_ACTIVITY"] }
        ];

        const resolveQuestTask = (q) => {
            if (!q || !q.config) return null;
            let uStatus = q.user_status || q.userStatus || {};
            if (uStatus.completed_at || uStatus.completedAt) return null;
            let exp = q.config.expires_at || q.config.expiresAt;
            if (exp && new Date(exp).getTime() < Date.now()) return null;
            let tCfg = selectTaskConfig(q.config);
            if (!tCfg || !tCfg.tasks) return null;
            const keys = taskKeys(tCfg.tasks);
            for (const { match, type, prefer } of typeMap) {
                const keyName = (prefer && keys.find(k => prefer.includes(k))) || keys.find(k => match(k));
                if (keyName) {
                    const taskData = taskAt(tCfg.tasks, keyName) || {};
                    return { keyName, type, taskData, tCfg };
                }
            }
            return null;
        };

        quests = quests.filter(x => resolveQuestTask(x) !== null);

        if(quests.length === 0) {
            logP("[JS] Nenhuma missao compativel pendente na sua conta.");
            window.discordQuestsDone = true; return;
        }

        logP(`[JS] Encontrada(s) ${quests.length} missao(oes) pendente(s). Iniciando motor contextual...`);

        let doJob = async function() {
            const quest = quests.pop();
            if(!quest) {
                logP("[JS] Operacao finalizada. Farm concluido com sucesso absoluto!");
                window.discordQuestsDone = true; return;
            }

            let resolved = resolveQuestTask(quest);
            if (!resolved) {
                setTimeout(doJob, 500);
                return;
            }

            let uStatus = quest.user_status || quest.userStatus || {};
            let qConfig = quest.config || {};
            let qMessages = qConfig.messages || {};
            let qApp = qConfig.application || {};
            
            const questName = qMessages.quest_name || qMessages.questName || qApp.name || "Unknown Quest";
            const taskName = resolved.keyName;
            const taskData = resolved.taskData;
            const applicationId = taskData.applications?.[0]?.id || qApp.id || "0";
            
            const secondsNeeded = taskData.target || 900;
            const rawProgress = (uStatus.progress instanceof Map ? uStatus.progress.get(taskName) : uStatus.progress?.[taskName])?.value 
                || (uStatus.progress instanceof Map ? uStatus.progress.get("WATCH_VIDEO") : uStatus.progress?.WATCH_VIDEO)?.value 
                || uStatus.stream_progress_seconds || 0;
            const secondsDone = rawProgress;
            const isVideo = (resolved.type === "WATCH_VIDEO" || taskName.includes("VIDEO"));
            const isGame = (resolved.type === "GAME" || taskName.startsWith("PLAY"));
            const extraSeconds = isVideo ? 0 : Math.floor(Math.random() * 240) + 60; 
            const targetTimeWithFat = secondsNeeded + extraSeconds;

            logP(`[JS] -> Missao: ${questName} | Base: ${secondsNeeded}s | Furtiva: ${targetTimeWithFat}s`);

            if (!isVideo && !(uStatus.enrolled_at || uStatus.enrolledAt)) {
                logP(`[JS] Matrícula JIT na missao '${questName}'...`);
                try {
                    await safePost(`/quests/${quest.id}/enroll`, {
                        location: 11,
                        platform: 0,
                        is_targeted: false,
                        metadata_sealed: null,
                        traffic_metadata_sealed: sealedFor(quest.id)
                    });
                } catch(e) {}
                await new Promise(r => setTimeout(r, 1500));
            }

                        // 1. Auto-seleção de plataforma Desktop (Área de trabalho) para missões multi-plataforma (ex: Valorant, CoD)
            try {
                let card = document.getElementById('quest-tile-' + quest.id)
                    || document.querySelector(`[data-quest-id="${quest.id}"]`)
                    || Array.from(document.querySelectorAll('[class*="quest"], [class*="card"], [class*="container"]')).find(el => (el.innerText || el.textContent || '').includes(questName));
                
                if (card && typeof card.scrollIntoView === 'function') {
                    card.scrollIntoView({ behavior: 'instant', block: 'center' });
                    await new Promise(r => setTimeout(r, 400));
                }

                let scope = card || document;
                let selector = scope.querySelector('[class*="platformSelectorPrimary"], [aria-haspopup="listbox"], button[class*="select"]');
                if (!selector) {
                    let allCandidateButtons = Array.from(scope.querySelectorAll('button, [role="button"], div[class*="select"]'));
                    selector = allCandidateButtons.find(b => /selecione uma plataforma|select a platform/i.test(b.innerText || b.textContent || ''));
                }
                
                let selectorText = selector ? (selector.innerText || selector.textContent || '') : '';
                if (selector && /selecione uma plataforma|select a platform/i.test(selectorText)) {
                    logP(`[JS] Seletor de plataforma detectado em '${questName}'. Selecionando Área de trabalho...`);
                    selector.click();
                    await new Promise(r => setTimeout(r, 800));
                    
                    let options = Array.from(document.querySelectorAll('[role="listbox"] [role="option"], [role="option"], [class*="option"], [data-value*="desktop"]'));
                    if (options.length === 0) options = Array.from(document.querySelectorAll('div[class*="select"] div, li'));
                    let desktopOpt = options.find(o => {
                        let t = (o.innerText || o.textContent || '').trim().toLowerCase();
                        return t.includes('área de trabalho') || t.includes('area de trabalho') || t.includes('desktop') || t.includes('computador') || t === 'pc' || t.startsWith('pc ');
                    });
                    if (desktopOpt) {
                        desktopOpt.click();
                        logP(`[JS] Plataforma 'Área de trabalho' selecionada com sucesso para '${questName}'!`);
                        await new Promise(r => setTimeout(r, 1200));
                    } else {
                        let firstOpt = document.querySelector('[role="option"]');
                        if (firstOpt) {
                            firstOpt.click();
                            await new Promise(r => setTimeout(r, 1200));
                        }
                    }
                }
                
                // Fecha qualquer modal/popup de detalhes que possa abrir (ex: 'Jogos participantes' no Resident Evil)
                let closeBtn = document.querySelector('[class*="modal"] [aria-label*="Fechar"], [class*="modal"] [aria-label*="Close"], [class*="modal"] button[class*="close"], [role="dialog"] [aria-label*="Fechar"], [role="dialog"] [aria-label*="Close"]');
                if (closeBtn) {
                    try { closeBtn.click(); } catch(e) {}
                }
            } catch(e) {}

            try {
                let card = document.getElementById('quest-tile-' + quest.id)
                    || document.querySelector(`[data-quest-id="${quest.id}"]`)
                    || Array.from(document.querySelectorAll('[class*="quest"], [class*="card"], [class*="container"]')).find(el => (el.innerText || el.textContent || '').includes(questName));
                let scope = card || document;
                // 2. Aciona botão de aceitar caso visível na interface
                let acceptBtn = Array.from(scope.querySelectorAll('button, [role="button"]')).find(b => /^(aceitar|accept|aceitar missão|accept quest)/i.test((b.innerText || b.textContent || '').trim()));
                if (acceptBtn && !acceptBtn.disabled) {
                    logP(`[JS] Acionando botão Aceitar Missão para '${questName}'...`);
                    acceptBtn.click();
                    await new Promise(r => setTimeout(r, 1000));
                }
            } catch(e) {}

            if(taskName === "WATCH_VIDEO_ON_MOBILE") {
                logP(`[JS] -> Missao: ${questName} requer dispositivo movel. Pulando...`);
                setTimeout(doJob, 1000);
                return;
            }

            let ghostInterval = null;
            if (isVideo) {
                try {
                    if (!window.__rewardsFocusHooked) {
                        window.__rewardsFocusHooked = true;
                        Document.prototype.hasFocus = function() { return true; };
                        Object.defineProperty(Document.prototype, 'visibilityState', { get: () => 'visible', configurable: true });
                        Object.defineProperty(Document.prototype, 'hidden', { get: () => false, configurable: true });
                        const ogDocAdd = Document.prototype.addEventListener;
                        Document.prototype.addEventListener = function(type, listener, options) {
                            if (['visibilitychange', 'webkitvisibilitychange', 'blur', 'focusout', 'pagehide'].includes(type)) return;
                            return ogDocAdd.call(this, type, listener, options);
                        };
                        const ogWinAdd = Window.prototype.addEventListener;
                        Window.prototype.addEventListener = function(type, listener, options) {
                            if (['visibilitychange', 'webkitvisibilitychange', 'blur', 'focusout', 'pagehide'].includes(type)) return;
                            return ogWinAdd.call(this, type, listener, options);
                        };
                    }
                } catch(e) {}

                const ghostMouseVideo = () => {
                    try {
                        let videoContainer = document.querySelector('[data-testid="discord-web-video-player-container"]');
                        if (videoContainer) {
                            let rect = videoContainer.getBoundingClientRect();
                            let x = rect.left + Math.floor(Math.random() * Math.max(10, rect.width));
                            let y = rect.top + Math.floor(Math.random() * Math.max(10, rect.height));
                            videoContainer.dispatchEvent(new MouseEvent('mousemove', {
                                view: window, bubbles: true, cancelable: true,
                                clientX: x, clientY: y,
                                movementX: Math.floor(Math.random() * 12 - 6),
                                movementY: Math.floor(Math.random() * 12 - 6)
                            }));
                        }
                    } catch(e) {}
                    ghostInterval = setTimeout(ghostMouseVideo, 5000 + Math.floor(Math.random() * 7000));
                };
                ghostMouseVideo();

            } else if (isGame) {
                logP(`[JS] Missao de Jogo detectada. Executando 'Alt+Tab' virtual (Blur)...`);
                window.dispatchEvent(new Event('blur'));
                let startDelay = 12000 + Math.floor(Math.random() * 25000);
                logP(`[JS] Simulando abertura do jogo. Aguardando ${Math.floor(startDelay/1000)}s...`);
                await new Promise(r => setTimeout(r, startDelay));
            }

            const executarDesligamento = (sucesso = false) => {
                if (ghostInterval) clearTimeout(ghostInterval);
                let endDelay = 3000 + Math.floor(Math.random() * 4000);
                if (sucesso) {
                    logP(`[JS] Objetivo cumprido! Descompressao organica de ${Math.floor(endDelay/1000)}s...`);
                } else {
                    logP(`[JS] Avancando para a proxima missao (${Math.floor(endDelay/1000)}s)...`);
                }
                setTimeout(() => {
                    window.recompensas_cmd = "REWARDS_KILL:ALL";
                    setTimeout(doJob, 2500);
                }, endDelay);
            };

            if(isVideo) {
                logP(`[JS] -> Missao de Video detectada: ${questName} (Player Nativo Real)`);

                const readQuestProgress = () => {
                    try {
                        let liveQ = QuestsStore?.getQuest?.(quest.id) || quest;
                        let liveUs = liveQ?.userStatus || liveQ?.user_status || {};
                        let completed = Boolean(liveUs.completedAt || liveUs.completed_at);
                        let prog = liveUs.progress;
                        let getVal = (p, k) => (p instanceof Map ? p.get(k) : p?.[k])?.value;
                        let val = getVal(prog, taskName) ?? getVal(prog, "WATCH_VIDEO");
                        return {
                            completed,
                            seconds: (typeof val === 'number' && !isNaN(val)) ? val : null
                        };
                    } catch(e) {
                        return { completed: false, seconds: null };
                    }
                };

                const findNativeVideoPlayer = () => (
                    document.querySelector('video[data-testid="discord-web-video-player-video"]')
                    || document.querySelector('[data-testid="discord-web-video-player-container"] video')
                );

                const findQuestCardElement = () => {
                    let byId = document.getElementById('quest-tile-' + quest.id)
                        || document.querySelector(`[data-quest-id="${quest.id}"]`);
                    if (byId) return byId;
                    let specificTile = Array.from(document.querySelectorAll('[id^="quest-tile-"], [class*="questTile"], [class*="embed"]'))
                        .find(el => (el.innerText || el.textContent || '').includes(questName));
                    if (specificTile) return specificTile;
                    let nameEls = Array.from(document.querySelectorAll('h1, h2, h3, h4, span, div, p')).filter(el => {
                        if (el.children.length > 0) return false;
                        let t = (el.innerText || el.textContent || '').trim();
                        return t === questName || (t.length < 120 && t.includes(questName));
                    });
                    for (let nel of nameEls) {
                        let card = nel.closest('[id^="quest-tile-"], [class*="questTile"], [class*="embed"], [class*="card"], [role="listitem"]');
                        if (card) return card;
                    }
                    return null;
                };

                const findWatchCtaButton = async () => {
                    const isQuestsUrlNow = () => {
                        let p = (window.location.pathname || '').toLowerCase();
                        return p === '/quest-home' || p.startsWith('/quest-home/') || p === '/quests' || p.startsWith('/quests/');
                    };
                    if (!window.location.pathname.toLowerCase().startsWith('/channels/') && !isQuestsUrlNow()) {
                        let qLink = document.querySelector('a[href="/quest-home"]')
                            || document.querySelector('[href="/quest-home"]')
                            || document.querySelector('a[href="/quests"]')
                            || document.querySelector('[href="/quests"]')
                            || Array.from(document.querySelectorAll('[data-list-item-id]')).find(el => {
                                const id = (el.getAttribute('data-list-item-id') || '').toLowerCase();
                                return id && !id.includes('request') && !id.includes('message')
                                    && (id.endsWith('___quests') || id.endsWith('___quest-home') || /(^|[_-])quests?$/.test(id) || id.includes('quest-home'));
                            });
                        if (qLink) {
                            logP('[JS] Corrigindo aba para Missoes (/quest-home)...');
                            qLink.click();
                            await new Promise(r => setTimeout(r, 2000));
                        }
                    }

                    let card = findQuestCardElement();
                    if (!card) {
                        let scrollers = Array.from(document.querySelectorAll('[class*="scroller"]'));
                        for (let sc of scrollers) {
                            if (sc.clientWidth >= 300 && sc.scrollHeight > sc.clientHeight + 50) {
                                sc.scrollTop = 0;
                                await new Promise(r => setTimeout(r, 250));
                                card = findQuestCardElement();
                                if (card) break;
                                let stepSize = Math.max(350, Math.floor(sc.clientHeight * 0.75));
                                for (let step = 0; step < 25 && !card && (sc.scrollTop + sc.clientHeight < sc.scrollHeight - 2); step++) {
                                    let prevTop = sc.scrollTop;
                                    sc.scrollTop = Math.min(sc.scrollHeight, sc.scrollTop + stepSize);
                                    if (sc.scrollTop === prevTop) break;
                                    await new Promise(r => setTimeout(r, 250));
                                    card = findQuestCardElement();
                                }
                                if (card) break;
                            }
                        }
                    }
                    if (!card) return null;
                    if (typeof card.scrollIntoView === 'function') {
                        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await new Promise(r => setTimeout(r, 350));
                    }
                    let btns = Array.from(card.querySelectorAll('button, [role="button"]')).filter(b => !b.disabled);
                    let excludedRe = /assista\s+j[áa]|watch\s+now|novamente|again|pr[ée]-?compra|pre-?purchase|comprar|buy\b|jogar|play\b|baixar|download|saiba\s+mais|learn\s+more|entrar\s+no\s+servidor|join\s+server/i;
                    let exactRe = /^(assistir|continuar|watch|continue)(\s+(\d+[smh]?|ao\s+v[íi]deo|video))?$|^(continue\s+assistindo|continue\s+watching|iniciar\s+miss[ãa]o\s+de\s+v[íi]deo|start\s+video\s+quest|play\s+video)$/i;
                    let primaryBtn = btns.find(b => exactRe.test((b.innerText || b.textContent || '').trim()));
                    if (primaryBtn) return primaryBtn;
                    let fallbackCandidates = btns.filter(b => {
                        let txt = (b.innerText || b.textContent || '').trim();
                        if (!txt || excludedRe.test(txt)) return false;
                        return /\b(assistir|continuar|continue\s+assistindo|watch|ver\s+v[íi]deo|iniciar\s+miss[ãa]o|video)\b/i.test(txt);
                    });
                    return fallbackCandidates.length ? fallbackCandidates[fallbackCandidates.length - 1] : null;
                };

                const closeNativeVideoModal = () => {
                    try {
                        let closeBtns = document.querySelectorAll('button[data-testid="ad-video-modal-close-btn"], button[data-testid="video-quest-close-btn"], [role="dialog"] button[aria-label="Fechar"], [role="dialog"] button[aria-label="Close"]');
                        closeBtns.forEach(b => { try { b.click(); } catch(e) {} });
                        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, bubbles: true }));
                    } catch(e) {}
                };

                const ensureNativePlayerActive = () => {
                    let v = findNativeVideoPlayer();
                    if (!v) return null;
                    try {
                        v.muted = true;
                        let playPauseBtn = document.querySelector('button[data-testid="discord-web-video-player-play-pause-btn"]');
                        let aria = (playPauseBtn?.getAttribute('aria-label') || '').trim().toLowerCase();
                        let needsPlayClick = playPauseBtn && /^(jogar|play|retomar|resume|reproduzir)$/.test(aria);
                        if (needsPlayClick) {
                            playPauseBtn.click();
                        }
                        if (v.paused && !v.ended) {
                            v.play().catch(() => {});
                        }
                    } catch(e) {}
                    return v;
                };

                // 1. Localiza e clica no botão real da interface para abrir o player nativo do Discord
                let videoEl = findNativeVideoPlayer();
                if (!videoEl) {
                    for (let openTry = 0; openTry < 2 && !videoEl; openTry++) {
                        let watchBtn = await findWatchCtaButton();
                        if (watchBtn) {
                            let btnTxt = (watchBtn.innerText || watchBtn.textContent || '').trim();
                            logP(`[JS] Clicando no botao real da UI ('${btnTxt}') para abrir player de video...`);
                            watchBtn.click();
                            for (let waitStep = 0; waitStep < 16; waitStep++) {
                                await new Promise(r => setTimeout(r, 500));
                                window.recompensas_keepalive = Date.now();
                                videoEl = findNativeVideoPlayer();
                                if (videoEl) break;
                            }
                        } else {
                            break;
                        }
                    }
                }

                if (!videoEl) {
                    let checkNow = readQuestProgress();
                    if (checkNow.completed) {
                        window.peloMenosUmSucesso = true;
                        logP(`[JS] Missao de video '${questName}' ja marcada como concluida pelo cliente!`);
                        executarDesligamento(true);
                        return;
                    }
                    logP(`[JS] [AVISO] Player nativo (<video>) nao apareceu para '${questName}'. Pulando sem forjar API.`);
                    executarDesligamento(false);
                    return;
                }

                // 2. Monitoramento passivo do <video> nativo até o cliente Discord confirmar conclusão
                let curProgress = secondsDone;
                let targetSec = secondsNeeded;
                let videoFinished = false;
                let pausedStallCount = 0;
                let lastFocusRequestMs = 0;
                let lastLoggedBucket = -1;
                const startTimeVideo = Date.now();
                const remainingNeed = Math.max(15, targetSec - curProgress);
                const maxVideoTime = (remainingNeed + 120) * 1000;

                logP(`[JS] Player nativo aberto! Progresso atual: ${Math.floor(curProgress)}s / ${targetSec}s`);
                window.recompensas_cmd = `REWARDS_PROGRESS:${Math.floor(curProgress)}:${targetSec}:video`;
                ensureNativePlayerActive();

                while (!videoFinished) {
                    await new Promise(r => setTimeout(r, 2200));
                    window.recompensas_keepalive = Date.now();

                    let statusNow = readQuestProgress();
                    if (statusNow.seconds !== null && statusNow.seconds > curProgress) {
                        curProgress = Math.min(targetSec, statusNow.seconds);
                    }

                    let v = ensureNativePlayerActive();
                    if (!v) {
                        if (statusNow.completed || (statusNow.seconds !== null && statusNow.seconds >= targetSec)) {
                            videoFinished = true;
                            window.peloMenosUmSucesso = true;
                            logP(`[JS] Conclusao do video confirmada pelo cliente Discord!`);
                            break;
                        }
                        logP(`[JS] Modal de video fechado antes de concluir. Tentando reabrir pela UI...`);
                        let reWatchBtn = await findWatchCtaButton();
                        if (reWatchBtn) {
                            reWatchBtn.click();
                            await new Promise(r => setTimeout(r, 2000));
                            v = ensureNativePlayerActive();
                        }
                        if (!v) {
                            statusNow = readQuestProgress();
                            if (statusNow.completed) {
                                videoFinished = true;
                                window.peloMenosUmSucesso = true;
                            }
                            break;
                        }
                    }

                    if (v && v.paused && !v.ended) {
                        pausedStallCount++;
                        if (pausedStallCount >= 4 && (Date.now() - lastFocusRequestMs > 20000)) {
                            lastFocusRequestMs = Date.now();
                            pausedStallCount = 0;
                            logP(`[JS] Video pausado em segundo plano. Solicitando restauracao de visibilidade...`);
                            window.recompensas_focus_needed = true;
                        }
                    } else {
                        pausedStallCount = 0;
                    }

                    let domElapsed = (v && typeof v.currentTime === 'number' && !isNaN(v.currentTime)) ? Math.floor(v.currentTime) : 0;
                    let displayProgress = Math.min(targetSec, Math.max(Math.floor(curProgress), domElapsed));
                    let logBucket = Math.floor(displayProgress / 8);
                    if (logBucket !== lastLoggedBucket) {
                        lastLoggedBucket = logBucket;
                        logP(`[JS] Assistindo video na UI: ${displayProgress} / ${targetSec}s`);
                        window.recompensas_cmd = `REWARDS_PROGRESS:${displayProgress}:${targetSec}:video`;
                    }

                    if (statusNow.completed || (statusNow.seconds !== null && statusNow.seconds >= targetSec)) {
                        if (!statusNow.completed) {
                            for (let poll = 0; poll < 5; poll++) {
                                await new Promise(r => setTimeout(r, 1000));
                                window.recompensas_keepalive = Date.now();
                                if (readQuestProgress().completed) break;
                            }
                        }
                        videoFinished = true;
                        window.peloMenosUmSucesso = true;
                        logP(`[JS] Meta do video confirmada organicamente pelo cliente Discord!`);
                        break;
                    }

                    if (Date.now() - startTimeVideo > maxVideoTime) {
                        logP(`[JS] [TIMEOUT] Tempo maximo do player excedido para '${questName}'.`);
                        break;
                    }
                }

                // 3. Fechamento seguro do modal nativo de vídeo
                closeNativeVideoModal();

                if (videoFinished) {
                    logP(`[JS] Missao de video '${questName}' concluida com exito!`);
                    executarDesligamento(true);
                } else {
                    logP(`[JS] Missao de video '${questName}' incompleta. Avancando...`);
                    executarDesligamento(false);
                }
                return;
            }
            else if(taskName === "PLAY_ON_DESKTOP") {
                let appDataRes = await request('GET', `/applications/public?application_ids=${applicationId}`);
                let appData = Array.isArray(appDataRes) ? appDataRes[0] : (appDataRes || {});
                let rawExeName = appData?.executables?.find(x => x.os === "win32")?.name || appData?.name || questName;
                let cleanExeName = rawExeName.replace(/[\/\\:*?"<>|\n\r]/g, "").trim();
                if (!cleanExeName.toLowerCase().endsWith(".exe")) cleanExeName += ".exe";

                logP(`[JS] Solicitando camuflagem OS ao Python: ${cleanExeName}`);
                window.novoPidCamuflado = null; 
                window.recompensas_cmd = "REWARDS_EXE:" + cleanExeName;
                
                let waitCycles = 0;
                while (!window.novoPidCamuflado && waitCycles < 40) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                    waitCycles++;
                }
                
                if(!window.novoPidCamuflado) logP("[JS] Alerta: Python demorou para responder. Usando PID generico de fallback.");
                const pid = window.novoPidCamuflado || 10432; 

                const fakeGame = { cmdLine: `C:\\Program Files\\${appData.name || questName}\\${cleanExeName}`, exeName: cleanExeName, exePath: `c:/program files/${(appData.name || questName).toLowerCase()}/${cleanExeName}`, hidden: false, isLauncher: false, id: applicationId, name: appData.name || questName, pid: pid, pidPath: [pid], processName: appData.name || questName, start: Date.now() };
                const realGames = RunningGameStore ? RunningGameStore.getRunningGames() : [];
                const fakeGames = [fakeGame];
                const realGetRunningGames = RunningGameStore ? RunningGameStore.getRunningGames : null;
                const realGetGameForPID = RunningGameStore ? RunningGameStore.getGameForPID : null;
                
                if (RunningGameStore) {
                    RunningGameStore.getRunningGames = () => fakeGames;
                    RunningGameStore.getGameForPID = (p) => p === fakeGame.pid ? fakeGame : null;
                }
                if (FluxDispatcher) FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: realGames, added: [fakeGame], games: fakeGames});
                
                let consecutiveFailures = 0;
                let completingThisQuest = false;
                let fatTimerStarted = false;
                let lastHeartbeatTime = Date.now();
                let watchdogInterval = null;

                const finishUp = (sucesso = false) => {
                    if (completingThisQuest) return;
                    completingThisQuest = true;
                    if (sucesso) window.peloMenosUmSucesso = true;
                    if (watchdogInterval) clearInterval(watchdogInterval);
                    if (RunningGameStore) { 
                        RunningGameStore.getRunningGames = realGetRunningGames; 
                        RunningGameStore.getGameForPID = realGetGameForPID; 
                    }
                    if (FluxDispatcher) { 
                        FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: [fakeGame], added: [], games: []}); 
                        FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fnSuccess); 
                        FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_FAILURE", fnFailure);
                    }
                    executarDesligamento(sucesso);
                };

                // WATCHDOG (Inspirado no Orion): se o Discord nao enviar heartbeats por > 90s, aborta com seguranca
                watchdogInterval = setInterval(() => {
                    if (completingThisQuest) return;
                    window.recompensas_keepalive = Date.now();
                    let elapsed = Date.now() - lastHeartbeatTime;
                    if (elapsed > 90000) {
                        logP(`[JS] [WATCHDOG] Nao houve resposta de progresso do Discord para '${questName}' apos ${Math.floor(elapsed/1000)}s.`);
                        logP(`[JS] [WATCHDOG] Pulando missao com seguranca para evitar travamento.`);
                        finishUp(false);
                    }
                }, 15000);

                let fnFailure = data => {
                    if(completingThisQuest) return;
                    let qId = data?.questId || data?.quest_id;
                    if (qId && qId !== quest.id) return;
                    consecutiveFailures++;
                    logP(`[JS] [AVISO] Heartbeat falhou (${consecutiveFailures}/5) para '${questName}' (erro temporario do Discord).`);
                    if (data?.error) {
                        try { logP(`[JS] Motivo da rejeicao: ${JSON.stringify(data.error)}`); } catch(e) {}
                    }
                    if (consecutiveFailures >= 5) {
                        logP(`[JS] [ERRO] 5 falhas consecutivas de heartbeat para '${questName}'. Pulando missao.`);
                        finishUp(false);
                    } else {
                        // Rearma watchdog pois o Discord continua rodando a contagem de heartbeat
                        lastHeartbeatTime = Date.now();
                    }
                };

                let fnSuccess = data => {
                    if(completingThisQuest) return;
                    let qId = data?.questId || data?.quest_id;
                    if (qId && qId !== quest.id) return;
                    
                    consecutiveFailures = 0;
                    lastHeartbeatTime = Date.now(); // Rearma o watchdog
                    window.recompensas_keepalive = Date.now();
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    if(!fatTimerStarted) {
                        logP(`[JS] Tracker Nativo: ${progress} / ${targetTimeWithFat}s`);
                        window.recompensas_cmd = "REWARDS_PROGRESS:" + progress + ":" + targetTimeWithFat;
                    }
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        if (watchdogInterval) clearInterval(watchdogInterval);
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        
                        logP(`[JS] Meta oficial atingida! Mantendo o jogo aberto por mais ${fatRemaining}s (Gordura Stealth)...`);
                        let simulatedProgress = progress;

                        if(fatRemaining <= 0) finishUp(true);
                        else {
                            const queimarGordura = () => {
                                if (completingThisQuest) return;
                                if(simulatedProgress >= targetTimeWithFat) { finishUp(true); return; }
                                window.recompensas_keepalive = Date.now();
                                let ganho = 8 + Math.floor(Math.random() * 12);
                                simulatedProgress += ganho;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                logP(`[JS] Tracker Furtivo: ${simulatedProgress} / ${targetTimeWithFat}s`);
                                window.recompensas_cmd = "REWARDS_PROGRESS:" + simulatedProgress + ":" + targetTimeWithFat;
                                setTimeout(queimarGordura, (ganho * 1000) + Math.floor(Math.random() * 2000));
                            };
                            queimarGordura();
                        }
                    }
                };
                if (FluxDispatcher) {
                    FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fnSuccess);
                    FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_FAILURE", fnFailure);
                }
            } 
            else if(taskName === "STREAM_ON_DESKTOP") {
                let cleanExeName = questName.replace(/[\/\\:*?"<>|\n\r]/g, "").trim() + ".exe";
                window.novoPidCamuflado = null; 
                window.recompensas_cmd = "REWARDS_EXE:" + cleanExeName;
                
                let waitCycles = 0;
                while (!window.novoPidCamuflado && waitCycles < 40) { await new Promise(resolve => setTimeout(resolve, 500)); waitCycles++; }
                
                const pid = window.novoPidCamuflado || 10432;
                let realFunc = ApplicationStreamingStore ? ApplicationStreamingStore.getStreamerActiveStreamMetadata : null;
                if (ApplicationStreamingStore) ApplicationStreamingStore.getStreamerActiveStreamMetadata = () => ({ id: applicationId, pid: pid, sourceName: null });
                
                let consecutiveFailures = 0;
                let completingThisQuest = false;
                let fatTimerStarted = false;
                let lastHeartbeatTime = Date.now();
                let watchdogInterval = null;

                const finishUp = (sucesso = false) => {
                    if (completingThisQuest) return;
                    completingThisQuest = true;
                    if (sucesso) window.peloMenosUmSucesso = true;
                    if (watchdogInterval) clearInterval(watchdogInterval);
                    if (ApplicationStreamingStore) ApplicationStreamingStore.getStreamerActiveStreamMetadata = realFunc;
                    if (FluxDispatcher) {
                        FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fnSuccess);
                        FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_FAILURE", fnFailure);
                    }
                    executarDesligamento(sucesso);
                };

                watchdogInterval = setInterval(() => {
                    if (completingThisQuest) return;
                    window.recompensas_keepalive = Date.now();
                    let elapsed = Date.now() - lastHeartbeatTime;
                    if (elapsed > 90000) {
                        logP(`[JS] [WATCHDOG] Stream sem resposta do Discord apos ${Math.floor(elapsed/1000)}s (requer transmissao ao vivo com amigos em call).`);
                        logP(`[JS] [WATCHDOG] Pulando missao de stream com seguranca.`);
                        finishUp(false);
                    }
                }, 15000);

                let fnFailure = data => {
                    if(completingThisQuest) return;
                    let qId = data?.questId || data?.quest_id;
                    if (qId && qId !== quest.id) return;
                    consecutiveFailures++;
                    logP(`[JS] [AVISO] Heartbeat de stream falhou (${consecutiveFailures}/5) para '${questName}'!`);
                    if (consecutiveFailures >= 5) {
                        finishUp(false);
                    } else {
                        lastHeartbeatTime = Date.now();
                    }
                };

                let fnSuccess = data => {
                    if(completingThisQuest) return;
                    let qId = data?.questId || data?.quest_id;
                    if (qId && qId !== quest.id) return;
                    consecutiveFailures = 0;
                    lastHeartbeatTime = Date.now();
                    window.recompensas_keepalive = Date.now();
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    if(!fatTimerStarted) {
                        logP(`[JS] Stream Nativo: ${progress} / ${targetTimeWithFat}s`);
                        window.recompensas_cmd = "REWARDS_PROGRESS:" + progress + ":" + targetTimeWithFat;
                    }
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        if (watchdogInterval) clearInterval(watchdogInterval);
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        logP(`[JS] Meta oficial da Stream atingida! Queimando gordura stealth (${fatRemaining}s)...`);
                        
                        let simulatedProgress = progress;
                        if(fatRemaining <= 0) finishUp(true);
                        else {
                            const queimarGorduraStream = () => {
                                if (completingThisQuest) return;
                                if(simulatedProgress >= targetTimeWithFat) { finishUp(true); return; }
                                window.recompensas_keepalive = Date.now();
                                let ganho = 8 + Math.floor(Math.random() * 12);
                                simulatedProgress += ganho;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                logP(`[JS] Tracker Furtivo (Stream): ${simulatedProgress} / ${targetTimeWithFat}s`);
                                window.recompensas_cmd = "REWARDS_PROGRESS:" + simulatedProgress + ":" + targetTimeWithFat;
                                setTimeout(queimarGorduraStream, (ganho * 1000) + Math.floor(Math.random() * 2000));
                            };
                            queimarGorduraStream();
                        }
                    }
                };
                if (FluxDispatcher) {
                    FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fnSuccess);
                    FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_FAILURE", fnFailure);
                }
            }
            else if(taskName === "PLAY_ACTIVITY") {
                let channelId = "0";
                try { channelId = ChannelStore?.getSortedPrivateChannels()?.[0]?.id || Object.values(GuildChannelStore?.getAllGuilds() || {}).find(x => x != null && x.VOCAL?.length > 0)?.VOCAL?.[0]?.channel?.id || "0"; } catch(e) {}
                const streamKey = `call:${channelId}:1`;
                let startTime = Date.now();
                let initialSeconds = secondsDone;
                
                let fn = async () => {
                    logP(`[JS] Call detectada (${questName}). Iniciando heartbeats hibridos...`);
                    while(true) {
                        let progress = 0;
                        try {
                            const res = await request('POST', `/quests/${quest.id}/heartbeat`, {stream_key: streamKey, terminal: false});
                            progress = res?.progress?.[taskName]?.value || 0;
                        } catch(e) {}
                        
                        let elapsed = Math.floor((Date.now() - startTime) / 1000);
                        let bestProg = Math.max(progress, initialSeconds + elapsed);
                        logP(`[JS] Atividade Call: ${bestProg} / ${targetTimeWithFat}s`);
                        window.recompensas_cmd = "REWARDS_PROGRESS:" + bestProg + ":" + targetTimeWithFat;
                        
                        if(bestProg >= targetTimeWithFat) {
                            try { await request('POST', `/quests/${quest.id}/heartbeat`, {stream_key: streamKey, terminal: true}); } catch(e) {}
                            break;
                        }
                        await new Promise(resolve => setTimeout(resolve, 18000 + Math.floor(Math.random() * 8000)));
                    }
                    logP(`[JS] Atividade Call finalizada e disfarçada!`);
                    executarDesligamento();
                };
                fn();
            }
            else {
                logP(`[JS] Tipo de tarefa nao suportado ou indisponivel no momento: '${taskName}'. Avancando...`);
                setTimeout(doJob, 1500);
                return;
            }
        };
        doJob();

    } catch(err) {
        logP("[JS] Erro critico na espinha dorsal: " + err.message);
        window.discordQuestsDone = true;
    }
})();
"""

def _encerrar_processo_discord(exe_name, proc=None):
    """Encerra o Discord e toda sua árvore de subprocessos para evitar janelas zumbis."""
    try:
        if proc:
            proc.kill()
    except Exception:
        pass
    if platform.system().lower() == "windows":
        subprocess.run(f'taskkill /F /IM "{exe_name}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(f'pkill -9 -f "{exe_name}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def localizar_aplicativo_discord():
    sistema = platform.system().lower()
    if sistema == "windows":
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        pastas = {
            "Canary": os.path.join(local_app_data, "DiscordCanary"),
            "PTB": os.path.join(local_app_data, "DiscordPTB")
        }
        for versao, caminho_base in pastas.items():
            if os.path.exists(caminho_base):
                pastas_app = glob.glob(os.path.join(caminho_base, "app-*"))
                if pastas_app:
                    pastas_app.sort(
                        key=lambda p: tuple(int(n) for n in re.findall(r"\d+", os.path.basename(p))) or (0,),
                        reverse=True
                    )
                    exe_name = f"Discord{versao}.exe"
                    for pasta_app in pastas_app:
                        exe_path = os.path.join(pasta_app, exe_name)
                        if os.path.exists(exe_path) and os.path.exists(os.path.join(pasta_app, "icudtl.dat")):
                            return exe_path, exe_name
    elif sistema == "linux":
        for exe_name in ["discord-canary", "discord-ptb"]:
            exe_path = shutil.which(exe_name)
            if exe_path: return exe_path, exe_name
    elif sistema == "darwin": 
        pastas = {
            "Canary": "/Applications/Discord Canary.app/Contents/MacOS/Discord Canary",
            "PTB": "/Applications/Discord PTB.app/Contents/MacOS/Discord PTB"
        }
        for versao, exe_path in pastas.items():
            if os.path.exists(exe_path): return exe_path, versao 
    return None, None

def bloquear_update_discord(exe_name):
    if platform.system().lower() != "windows": return
    pasta_appdata = os.environ.get('APPDATA', '')
    pasta_discord = "discordcanary" if "canary" in exe_name.lower() else "discordptb"
    settings_path = os.path.join(pasta_appdata, pasta_discord, "settings.json")
    try:
        dados = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f: dados = json.load(f)
        if not dados.get("SKIP_HOST_UPDATE"):
            dados["SKIP_HOST_UPDATE"] = True
            with open(settings_path, "w", encoding="utf-8") as f: json.dump(dados, f, indent=4)
            RewardsCore.LOGGER(RewardsCore.t("discord_update_blocker"))
    except Exception: pass

def _aplicar_override_foco_visibilidade(driver):
    """Mantem foco e visibilidade ativos via CDP e DOM para evitar pausa automatica de video."""
    try:
        driver.execute_cdp_cmd("Emulation.setFocusEmulationEnabled", {"enabled": True})
    except Exception:
        pass
    try:
        driver.execute_cdp_cmd("Page.setWebLifecycleState", {"state": "active"})
    except Exception:
        pass

    js_focus_override = """
        try {
            Document.prototype.hasFocus = function() { return true; };
            Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
            Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
            if (!window.__rewardsVisibilityBound) {
                window.__rewardsVisibilityBound = true;
                window.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                window.addEventListener('blur', e => e.stopImmediatePropagation(), true);
                document.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                document.addEventListener('blur', e => e.stopImmediatePropagation(), true);
            }
        } catch(e) {}
    """
    try:
        driver.execute_script(js_focus_override)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_focus_override})
    except Exception:
        pass


def _abrir_sessao_discord(fase_idx, fase, exe_path, exe_name, cfg, porta_debug=9222, max_tentativas=3):
    """Inicia o Discord com debug remoto e realiza retentativas automaticas caso trave no boot/splash."""
    for tentativa in range(1, max_tentativas + 1):
        if RewardsCore.ABORTAR_PROCESSO:
            return None, None, None, exe_path, exe_name

        if tentativa > 1:
            RewardsCore.LOGGER(RewardsCore.t("discord_launch_retry").format(tentativa, max_tentativas), "warning")
            RewardsCore.update_ui("discord", f"Reiniciando Discord ({tentativa}/{max_tentativas})...", 22)
            for _ in range(4):
                if RewardsCore.ABORTAR_PROCESSO:
                    return None, None, None, exe_path, exe_name
                time.sleep(1)
            novo_exe_path, novo_exe_name = localizar_aplicativo_discord()
            if novo_exe_path:
                exe_path, exe_name = novo_exe_path, novo_exe_name
                bloquear_update_discord(exe_name)

        args_discord = [
            exe_path, f"--remote-debugging-port={porta_debug}",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--autoplay-policy=no-user-gesture-required"
        ]

        if fase.get("usa_vpn") and fase.get("proxy_host"):
            if tentativa == 1:
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_inject").format(fase['proxy_host']))
            args_discord.append(f"--proxy-server=socks5://{fase['proxy_host']}")
            temp_profile = os.path.join(tempfile.gettempdir(), f"discord_vpn_{fase_idx}")
            args_discord.append(f"--user-data-dir={temp_profile}")

        modo_oculto = cfg.get("modo_oculto", "s") == "s"
        if modo_oculto:
            args_discord.append("--start-minimized")

        _encerrar_processo_discord(exe_name)
        if RewardsCore.ABORTAR_PROCESSO:
            return None, None, None, exe_path, exe_name

        try:
            settings_path = os.path.join(os.environ.get('APPDATA', ''), exe_name.replace('.exe', ''), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    discord_settings = json.load(f)
                discord_settings["SKIP_HOST_UPDATE"] = True
                if "UPDATE_ENDPOINT" in discord_settings:
                    del discord_settings["UPDATE_ENDPOINT"]
                with open(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(discord_settings, f, indent=2)
        except Exception as e:
            RewardsCore.LOGGER(RewardsCore.t("discord_update_ignore_err").format(e))

        RewardsCore.LOGGER(f"[DISCORD] Iniciando {exe_name} (Porta {porta_debug})...")
        RewardsCore.update_ui("discord", "Iniciando Discord...", 25)
        processo = subprocess.Popen(args_discord, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        porta_aberta = False
        RewardsCore.update_ui("discord", "Aguardando Debugger...", 30)
        for _ in range(45):
            if RewardsCore.ABORTAR_PROCESSO:
                _encerrar_processo_discord(exe_name, processo)
                return None, None, None, exe_path, exe_name
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{porta_debug}/json/version", timeout=2):
                    porta_aberta = True
                    RewardsCore.LOGGER(f"[DISCORD] Porta de depuração {porta_debug} conectada!")
                    break
            except Exception:
                time.sleep(1)

        if not porta_aberta:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.LOGGER(RewardsCore.t("discord_timeout_9222"), "error")
                RewardsCore.update_ui("discord", "Timeout Debugger 9222", 0)
            _encerrar_processo_discord(exe_name, processo)
            continue

        RewardsCore.update_ui("discord", "Localizando janela...", 35)
        RewardsCore.LOGGER("[DISCORD] Aguardando janela principal do Discord carregar...")
        janela_pronta = False
        for _ in range(45):
            if RewardsCore.ABORTAR_PROCESSO:
                _encerrar_processo_discord(exe_name, processo)
                return None, None, None, exe_path, exe_name
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{porta_debug}/json", timeout=2) as resp:
                    targets = json.loads(resp.read().decode())
                    for t in targets:
                        t_url = t.get("url", "").lower()
                        t_type = t.get("type", "")
                        if t_type == "page" and any(x in t_url for x in ["discord.com/app", "discord.com/channels", "discord.com/login", "canary.discord.com"]):
                            janela_pronta = True
                            RewardsCore.LOGGER(f"[DISCORD] Janela detectada via DevTools ({t.get('title', 'Discord')}: {t_url.split('?')[0]})!")
                            break
            except Exception:
                pass
            if janela_pronta:
                break
            time.sleep(1)

        if not janela_pronta:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.LOGGER("[DISCORD] Timeout: Discord Canary não carregou a janela principal (ficou preso na tela inicial).", "error")
                RewardsCore.update_ui("discord", "Travado na tela inicial", 0)
            _encerrar_processo_discord(exe_name, processo)
            continue

        chrome_options = Options()
        chrome_options.debugger_address = f"127.0.0.1:{porta_debug}"

        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{porta_debug}/json/version", timeout=3) as req:
                dados_json = json.loads(req.read().decode())
                match = re.search(r"Chrome/(\d+)", dados_json.get("Browser", ""))
                if match:
                    chrome_options.browser_version = match.group(1)
        except Exception:
            pass

        servico = Service()
        if os.name == 'nt':
            servico.creation_flags = 0x08000000

        driver = None
        for _ in range(3):
            if RewardsCore.ABORTAR_PROCESSO:
                _encerrar_processo_discord(exe_name, processo)
                return None, None, None, exe_path, exe_name
            try:
                driver = webdriver.Chrome(service=servico, options=chrome_options)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)
                break
            except Exception:
                time.sleep(2)

        if not driver:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.LOGGER(RewardsCore.t("discord_selenium_err"), "error")
            _encerrar_processo_discord(exe_name, processo)
            continue

        janela_correta = None
        try:
            for handle in driver.window_handles:
                try:
                    driver.switch_to.window(handle)
                    c_url = driver.current_url.lower()
                    if any(x in c_url for x in ["discord.com/app", "discord.com/channels", "discord.com/login", "canary.discord.com"]):
                        janela_correta = handle
                        RewardsCore.LOGGER(f"[DISCORD] Janela conectada com sucesso ({c_url.split('?')[0]})!")
                        break
                except Exception:
                    continue
        except Exception:
            pass

        if not janela_correta:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.LOGGER("[DISCORD] Erro ao alternar para a janela principal do Discord.", "error")
                RewardsCore.update_ui("discord", "Erro ao alternar janela", 0)
            try:
                driver.quit()
            except Exception:
                pass
            _encerrar_processo_discord(exe_name, processo)
            continue

        _aplicar_override_foco_visibilidade(driver)

        RewardsCore.update_ui("discord", "Carregando Webpack...", 45)
        webpack_pronto = False
        for _ in range(25):
            if RewardsCore.ABORTAR_PROCESSO:
                try:
                    driver.quit()
                except Exception:
                    pass
                _encerrar_processo_discord(exe_name, processo)
                return None, None, None, exe_path, exe_name
            try:
                if driver.execute_script("return typeof window.webpackChunkdiscord_app !== 'undefined';"):
                    webpack_pronto = True
                    break
            except Exception:
                pass
            time.sleep(2)

        if not webpack_pronto:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.LOGGER("[DISCORD] Timeout: Webpack do Discord Canary não inicializou.", "error")
                RewardsCore.update_ui("discord", "Erro Webpack Discord", 0)
            try:
                driver.quit()
            except Exception:
                pass
            _encerrar_processo_discord(exe_name, processo)
            continue

        return driver, processo, janela_correta, exe_path, exe_name

    return None, None, None, exe_path, exe_name


_IS_QUESTS_PATH_JS = """
const p = (window.location.pathname || '').toLowerCase();
return p === '/quest-home' || p.startsWith('/quest-home/') || p === '/quests' || p.startsWith('/quests/');
"""

_IS_QUESTS_READY_JS = """
const p = (window.location.pathname || '').toLowerCase();
const okPath = (p === '/quest-home' || p.startsWith('/quest-home/') || p === '/quests' || p.startsWith('/quests/'));
return okPath && (document.querySelector('[id^="quest-tile-"], [class*="questTile"]') !== null);
"""

_NAVIGATE_TO_QUESTS_JS = """
const p = (window.location.pathname || '').toLowerCase();
if (p === '/quest-home' || p.startsWith('/quest-home/') || p === '/quests' || p.startsWith('/quests/')) {
    return 'already_on_quests';
}

// Prioridade sequencial estrita evita coincidir substring com message-requests
let btnMissao = document.querySelector('a[href="/quest-home"]')
    || document.querySelector('[href="/quest-home"]')
    || document.querySelector('a[href="/quests"]')
    || document.querySelector('[href="/quests"]');

if (!btnMissao) {
    btnMissao = Array.from(document.querySelectorAll('[data-list-item-id]')).find(el => {
        const id = (el.getAttribute('data-list-item-id') || '').toLowerCase();
        if (!id || id.includes('request') || id.includes('message')) return false;
        return id.endsWith('___quests') || id.endsWith('___quest-home') || /(^|[_\\-])quests?$/.test(id) || id.includes('quest-home');
    });
}

if (!btnMissao) {
    const sidebar = document.querySelector('[class*="privateChannels"]')
        || document.querySelector('nav[aria-label]')
        || document;
    for (const el of sidebar.querySelectorAll('*')) {
        if (el.children.length !== 0) continue;
        const txt = (el.textContent || '').trim();
        if (txt !== 'Missões' && txt !== 'Quests') continue;
        const item = el.closest('[role="listitem"], [role="treeitem"], [role="link"], a, li') || el;
        const href = (item.getAttribute('href') || '').toLowerCase();
        const listId = (item.getAttribute('data-list-item-id') || '').toLowerCase();
        if (href.includes('request') || listId.includes('request')) continue;
        btnMissao = item;
        break;
    }
}

if (btnMissao) {
    btnMissao.click();
    return 'clicked';
}
return 'not_found';
"""


def _navegar_para_missoes(driver, canal_lixo=""):
    """Navega com seguranca ate a aba real de Missoes (/quest-home) ou canal_lixo configurado."""
    from selenium.webdriver.support.ui import WebDriverWait

    def _aguardar_tiles_missoes(timeout_s=20):
        try:
            WebDriverWait(driver, timeout_s).until(lambda d: d.execute_script(_IS_QUESTS_READY_JS))
        except Exception:
            pass

    for tentativa_nav in range(3):
        if RewardsCore.ABORTAR_PROCESSO:
            return False
        try:
            if canal_lixo and canal_lixo.startswith("http"):
                if driver.current_url != canal_lixo:
                    driver.get(canal_lixo)
                try:
                    WebDriverWait(driver, 35).until(
                        lambda d: d.execute_script(
                            "return window.location.pathname !== '/login' && "
                            "(document.querySelector('[class*=\"embed\"]') !== null || window.location.pathname.startsWith('/channels/'));"
                        )
                    )
                except Exception:
                    pass
                if RewardsCore.ABORTAR_PROCESSO:
                    return False
                try:
                    if driver.execute_script("return window.location.pathname !== '/login';"):
                        return True
                except Exception:
                    pass
            else:
                nav_status = driver.execute_script(_NAVIGATE_TO_QUESTS_JS)
                _aguardar_tiles_missoes(20)

                if RewardsCore.ABORTAR_PROCESSO:
                    return False

                try:
                    if bool(driver.execute_script(_IS_QUESTS_PATH_JS)):
                        return True
                except Exception:
                    pass

                if tentativa_nav >= 1 or nav_status == "not_found":
                    try:
                        origin = driver.execute_script("return window.location.origin;")
                        if not isinstance(origin, str) or not origin.startswith("http"):
                            origin = "https://discord.com"
                        driver.get(f"{origin.rstrip('/')}/quest-home")
                        WebDriverWait(driver, 25).until(
                            lambda d: d.execute_script("return typeof window.webpackChunkdiscord_app !== 'undefined';")
                        )
                        _aplicar_override_foco_visibilidade(driver)
                        _aguardar_tiles_missoes(15)
                        if bool(driver.execute_script(_IS_QUESTS_PATH_JS)):
                            return True
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            driver.refresh()
        except Exception:
            break
        time.sleep(5)

    try:
        return bool(driver.execute_script(_IS_QUESTS_PATH_JS))
    except Exception:
        return False


def iniciar_farm_discord():
    import threading
    if not hasattr(RewardsCore, 'TRAVA_EXECUCAO'):
        RewardsCore.TRAVA_EXECUCAO = threading.Lock()
        
    if RewardsCore.TRAVA_EXECUCAO.locked():
        RewardsCore.LOGGER(RewardsCore.t("discord_bing_waiting"), "warning")
        
    with RewardsCore.TRAVA_EXECUCAO:
        if RewardsCore.ABORTAR_PROCESSO: return False
        
        cfg = RewardsCore.carregar_config()
        lang = "pt" if cfg.get("language", "pt") == "pt" else "en"
        
        
        cooldown_dias = int(cfg.get("discord_cooldown", 3))
        if cfg.get("do_discord", "n") != "s": return True
        if RewardsCore.verificar_se_rodou_hoje("discord", dias_cooldown=cooldown_dias):
            RewardsCore.LOGGER(RewardsCore.t("discord_cooldown"))
            return True

        exe_path, exe_name = localizar_aplicativo_discord()
        if not exe_path: 
            RewardsCore.LOGGER(RewardsCore.t("discord_not_found"))
            return False

        PORTA_DEBUG = 9222
        RewardsCore.update_ui("discord", "Iniciando Preparativos...", 10)
        
        fazer_globais = cfg.get("discord_global_quests", "n") == "s"
        is_over_18 = cfg.get("is_over_18", True)

        api_quests = []
        try:
            RewardsCore.update_ui("discord", "Consultando Radar Global...", 10)
            req = urllib.request.Request("https://api.discordquest.com/api/quests", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                api_quests = json.loads(response.read().decode('utf-8'))
        except Exception as e: 
            RewardsCore.LOGGER(RewardsCore.t("discord_api_error").format(e))

        from datetime import datetime, timezone
        
        def validate_quest_eligibility(q, is_over_18):
            if not is_over_18 and q.get('age_restricted', False): return False
            cfg_q = q.get('config', {})
            
            expires_at = cfg_q.get('expires_at') or cfg_q.get('expiresAt')
            if expires_at:
                try:
                    exp_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if exp_date < datetime.now(timezone.utc): return False
                except Exception: pass
                
            t_config = cfg_q.get('task_config') or cfg_q.get('taskConfig') or cfg_q.get('task_config_v2') or cfg_q.get('taskConfigV2') or cfg_q
            tasks = t_config.get('tasks', {})
            task_names = list(tasks.keys())
            
            if "WATCH_VIDEO_ON_MOBILE" in task_names: return False
            if "PLAY_ON_MOBILE" in task_names: return False
            
            supported = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP"]
            if not any(t in task_names for t in supported): return False
            
            return True

        region_batches = {}
        try:
            if isinstance(api_quests, list):
                for q in api_quests:
                    if not validate_quest_eligibility(q, is_over_18):
                        continue

                    cfg_q = q.get('config', {})
                    r = q.get('region')
                    if r is None:
                        txt = str(q).lower()
                        if 'us only' in txt or 'boiuna' in txt or 'united states' in txt:
                            r = 'us'
                        elif 'eu only' in txt or 'europe' in txt or 'germany' in txt:
                            r = 'de'
                        elif 'uk only' in txt or 'united kingdom' in txt:
                            r = 'gb'
                        else:
                            r = 'local'
                    else:
                        r = str(r).lower()
                    
                    if r not in region_batches: region_batches[r] = []
                    region_batches[r].append(q.get('id'))
            else:
                RewardsCore.LOGGER(RewardsCore.t("discord_api_unexpected").format(type(api_quests)))
        except Exception as e:
            RewardsCore.LOGGER(RewardsCore.t("discord_api_filter_error").format(e))

        def obter_proxy_socks5_por_pais(country_code):
            import requests
            try:
                api_proxies = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks5&proxy_format=protocolipport&format=json&timeout=1500"
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_fetching"))
                
                resposta = requests.get(api_proxies, timeout=10).json()
                
                proxies_pais = [
                    p['proxy'] for p in resposta.get('proxies', []) 
                    if p.get('ip_data', {}).get('countryCode') == country_code.upper()
                ]
                
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_found").format(len(proxies_pais), country_code.upper()))
                
                for proxy in proxies_pais[:15]:
                    RewardsCore.LOGGER(RewardsCore.t("discord_proxy_testing").format(proxy))
                    proxies_config = {
                        "http": proxy,
                        "https": proxy
                    }
                    try:
                        teste_ip = requests.get("https://api.ipify.org?format=json", proxies=proxies_config, timeout=5)
                        if teste_ip.status_code == 200:
                            ip_camuflado = teste_ip.json().get('ip')
                            RewardsCore.LOGGER(RewardsCore.t("discord_proxy_clean"))
                            RewardsCore.LOGGER(RewardsCore.t("discord_proxy_success"))
                            RewardsCore.LOGGER(RewardsCore.t("discord_proxy_ip").format(ip_camuflado))
                            return proxy.replace('socks5://', '').replace('socks4://', '').replace('http://', '').replace('https://', '')
                    except requests.exceptions.SSLError:
                        RewardsCore.LOGGER(RewardsCore.t("discord_proxy_dirty"))
                    except requests.exceptions.Timeout:
                        RewardsCore.LOGGER(RewardsCore.t("discord_proxy_slow"))
                    except requests.exceptions.RequestException:
                        RewardsCore.LOGGER(RewardsCore.t("discord_proxy_dead"))
                
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_none"))
            except Exception as e:
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_search_error").format(country_code, e))
            return None

        fases = []
        if not region_batches:
            fases.append({"nome": "Lote Local (Nativo)", "usa_vpn": False, "ids": [], "proxy_host": ""})
        else:
            for region, ids in region_batches.items():
                if region == 'local' or not fazer_globais:
                    fases.append({"nome": f"Lote Local", "usa_vpn": False, "ids": ids, "proxy_host": ""})
                else:
                    RewardsCore.LOGGER(RewardsCore.t("discord_proxy_searching_region").format(region.upper()))
                    proxy = obter_proxy_socks5_por_pais(region)
                    if proxy:
                        fases.append({
                            "nome": f"Lote Global ({region.upper()})", 
                            "usa_vpn": True, 
                            "ids": ids,
                            "proxy_host": proxy
                        })
                    else:
                        RewardsCore.LOGGER(RewardsCore.t("discord_proxy_fallback").format(region.upper()))
                        fases.append({"nome": f"Lote Local (Fallback {region.upper()})", "usa_vpn": False, "ids": ids, "proxy_host": ""})

        global_discord_token = None
        houve_ao_menos_um_sucesso = False
        houve_fase_conectada = False
        fases.sort(key=lambda x: x["usa_vpn"])
        if fases and not any(f["usa_vpn"] == False for f in fases):
            fases.insert(0, {"nome": "Extração de Sessão (Bridge)", "usa_vpn": False, "ids": [], "proxy_host": "", "token_only": True})

        for i, fase in enumerate(fases):
            if RewardsCore.ABORTAR_PROCESSO:
                return False
            RewardsCore.LOGGER(RewardsCore.t("discord_batch_start").format(fase['nome'].upper()))
            RewardsCore.update_ui("discord", fase["nome"], 20 + (i * 30))

            driver, processo, janela_correta, exe_path, exe_name = _abrir_sessao_discord(
                i, fase, exe_path, exe_name, cfg, porta_debug=PORTA_DEBUG, max_tentativas=3
            )
            if not driver:
                if RewardsCore.ABORTAR_PROCESSO:
                    return False
                continue

            houve_fase_conectada = True

            # --- ISOLAMENTO ABSOLUTO DE CACHE: EXTRACT OU INJECT TOKEN ---
            if not global_discord_token and not fase["usa_vpn"]:
                try:
                    global_discord_token = driver.execute_script("""
                        let t = "";
                        try {
                            t = (window.webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken();
                        } catch(e) {}
                        return t;
                    """)
                    if global_discord_token:
                        RewardsCore.LOGGER(RewardsCore.t("discord_session_cloned"))
                except Exception:
                    pass
                
                if fase.get("token_only"):
                    try: driver.quit()
                    except Exception: pass
                    _encerrar_processo_discord(exe_name, processo)
                    continue

            elif fase["usa_vpn"] and global_discord_token:
                try:
                    RewardsCore.LOGGER(RewardsCore.t("discord_token_inject"))
                    driver.execute_script(f"""
                        let token = "{global_discord_token}";
                        let iframe = document.createElement('iframe');
                        document.body.appendChild(iframe);
                        iframe.contentWindow.localStorage.setItem('token', '"' + token + '"');
                        setTimeout(() => location.reload(), 500);
                    """)
                    time.sleep(4)
                except Exception:
                    pass

            try:
                logado = driver.execute_script("return window.location.pathname !== '/login';")
                if not logado:
                    espera = 0
                    while espera < 300: 
                        if RewardsCore.ABORTAR_PROCESSO:
                            try: driver.quit()
                            except Exception: pass
                            _encerrar_processo_discord(exe_name, processo)
                            return False
                        try:
                            if driver.execute_script("return window.location.pathname !== '/login';"):
                                time.sleep(10); break
                        except Exception:
                            pass
                        time.sleep(5); espera += 5
                    else:
                        if not RewardsCore.ABORTAR_PROCESSO:
                            RewardsCore.LOGGER(RewardsCore.t("discord_login_stuck"))
                        try: driver.quit()
                        except Exception: pass
                        _encerrar_processo_discord(exe_name, processo)
                        continue
            except Exception:
                pass
                
            RewardsCore.update_ui("discord", "Sincronizando...", 50)
            
            ids_globais = fase.get("ids", [])
            quests_webhook_url = cfg.get("quests_webhook_url", "")
            canal_lixo = cfg.get("canal_lixo_url", "")

            # Fazer disparo Python Webhook-Embed antes de navegar!
            if ids_globais and quests_webhook_url:
                try:
                    RewardsCore.LOGGER(RewardsCore.t("discord_webhook_gen"))
                    import requests
                    for qid in ids_globais:
                        requests.post(quests_webhook_url, json={"content": f"https://discord.com/quests/{qid}"}, timeout=5)
                        time.sleep(1)
                except Exception as e:
                    RewardsCore.LOGGER(RewardsCore.t("discord_webhook_err").format(e))

            _navegar_para_missoes(driver, canal_lixo)

            if RewardsCore.ABORTAR_PROCESSO:
                try: driver.quit()
                except Exception: pass
                _encerrar_processo_discord(exe_name, processo)
                break

            ids_globais = fase.get("ids", [])
            quests_webhook_url = cfg.get("quests_webhook_url", "")
            script_injetado = SCRIPT_JS.replace("INJECT_GLOBAL_IDS", json.dumps(ids_globais))
            script_injetado = script_injetado.replace('"INJECT_QUESTS_WEBHOOK"', json.dumps(quests_webhook_url))
            
            try: driver.execute_script(script_injetado)
            except Exception:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(RewardsCore.t("discord_webpack_err"))
                try: driver.quit()
                except Exception: pass
                _encerrar_processo_discord(exe_name, processo)
                break
            
            RewardsCore.update_ui("discord", "Processando Tarefas...", 80)
            
            matar_processos_camuflados()
            try:
                watchdog_timeout = 180 # 3 minutos sem qualquer sinal de vida do JS
                last_active_time = time.time()
                falhas_consecutivas_script = 0
                
                while True:
                    if RewardsCore.ABORTAR_PROCESSO: break
                    
                    time.sleep(2) 
                    
                    try:
                        js_data = driver.execute_script("""
                            let res = { 
                                cmd: window.recompensas_cmd, 
                                logs: window.recompensas_logs || [],
                                keepalive: window.recompensas_keepalive || 0,
                                focus_needed: Boolean(window.recompensas_focus_needed)
                            };
                            window.recompensas_cmd = null;
                            window.recompensas_logs = [];
                            window.recompensas_keepalive = 0;
                            window.recompensas_focus_needed = false;
                            return res;
                        """)
                        
                        if js_data and (js_data.get('logs') or js_data.get('cmd') or js_data.get('keepalive') or js_data.get('focus_needed')):
                            last_active_time = time.time()
                            
                        if time.time() - last_active_time > watchdog_timeout:
                            RewardsCore.LOGGER(RewardsCore.t("discord_watchdog"), "warning")
                            break
                            
                        if js_data:
                            for msg in js_data.get('logs', []):
                                RewardsCore.LOGGER(msg)

                            if js_data.get('focus_needed') or js_data.get('cmd') == "REWARDS_FOCUS_WINDOW":
                                _aplicar_override_foco_visibilidade(driver)
                                try:
                                    win_info = driver.execute_cdp_cmd("Browser.getWindowForTarget", {})
                                    win_id = win_info.get("windowId")
                                    if win_id is not None and win_info.get("bounds", {}).get("windowState") == "minimized":
                                        driver.execute_cdp_cmd("Browser.setWindowBounds", {
                                            "windowId": win_id,
                                            "bounds": {"windowState": "normal"}
                                        })
                                except Exception:
                                    pass

                            cmd = js_data.get('cmd')
                            if cmd:
                                if "REWARDS_EXE:" in cmd:
                                    exe_needed = cmd.split("REWARDS_EXE:")[1].strip()
                                    temp_dir = tempfile.gettempdir()
                                    fake_exe_path = os.path.join(temp_dir, exe_needed)
                                    
                                    if platform.system().lower() == "windows":
                                        try:
                                            # Encerra qualquer processo anterior bloqueando o arquivo temporário
                                            subprocess.run(f'taskkill /F /IM "{exe_needed}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                            time.sleep(0.3)
                                            if os.path.exists(fake_exe_path):
                                                os.remove(fake_exe_path)
                                        except Exception:
                                            pass
                                        shutil.copy(r"C:\Windows\System32\ping.exe", fake_exe_path)
                                        dp = subprocess.Popen([fake_exe_path, "127.0.0.1", "-n", "3600"], creationflags=subprocess.CREATE_NO_WINDOW)
                                    else:
                                        try:
                                            if os.path.exists(fake_exe_path):
                                                os.remove(fake_exe_path)
                                        except Exception:
                                            pass
                                        shutil.copy(shutil.which("sleep") or "/bin/sleep", fake_exe_path)
                                        os.chmod(fake_exe_path, 0o755) 
                                        dp = subprocess.Popen([fake_exe_path, "3600"])

                                    DUMMY_PROCESSES.append((dp, fake_exe_path))
                                    driver.execute_script(f"window.novoPidCamuflado = {dp.pid};") 
                                    
                                elif "REWARDS_KILL:ALL" in cmd:
                                    matar_processos_camuflados()

                                elif "REWARDS_PROGRESS:" in cmd:
                                    try:
                                        partes = cmd.split("REWARDS_PROGRESS:")[1].split(":")
                                        c_prog = int(partes[0])
                                        t_prog = int(partes[1])
                                        modo_prog = partes[2].strip() if len(partes) >= 3 else ""
                                        percent = min(99, int((c_prog / t_prog) * 100)) if t_prog > 0 else 0
                                        cm = c_prog // 60; cs = c_prog % 60
                                        tm = t_prog // 60; ts = t_prog % 60
                                        prefixo = "Assistindo vídeo" if modo_prog == "video" else "Jogando"
                                        status_text = f"{prefixo} ({cm:02d}:{cs:02d} / {tm:02d}:{ts:02d})"
                                        RewardsCore.update_ui("discord", status_text, percent, total_segundos=t_prog)
                                    except Exception: pass
                    except Exception: pass
                    
                    try:
                        sucesso_flag = driver.execute_script("return window.peloMenosUmSucesso === true;")
                        if sucesso_flag:
                            houve_ao_menos_um_sucesso = True
                            
                        if driver.execute_script("return window.discordQuestsDone === true;"):
                            if driver.execute_script("return window.peloMenosUmSucesso === true;"):
                                houve_ao_menos_um_sucesso = True
                            break
                        falhas_consecutivas_script = 0
                    except Exception as err:
                        falhas_consecutivas_script += 1
                        if falhas_consecutivas_script >= 10:
                            RewardsCore.LOGGER(f"[DISCORD] Conexao com Discord perdida ({err}). Encerrando lote...", "warning")
                            break
                        time.sleep(1)
                    
            except Exception as e:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(RewardsCore.t("discord_loop_error").format(str(e)[:100]))
                
            matar_processos_camuflados()
                
            try:
                driver.execute_script("try { window.DiscordNative.app.quit(); } catch(e) {}")
                time.sleep(2)
                driver.quit() 
            except Exception: pass
            
            _encerrar_processo_discord(exe_name, processo)
            
            if i < len(fases) - 1: 
                for _ in range(7):
                    if RewardsCore.ABORTAR_PROCESSO: break
                    time.sleep(2)
                if RewardsCore.ABORTAR_PROCESSO: break

        if houve_ao_menos_um_sucesso:
            RewardsCore.registrar_data_execucao("discord")
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.update_ui("discord", "Concluído!", 100)
                RewardsCore.LOGGER(RewardsCore.t("discord_success_total"))
                return True
            else:
                RewardsCore.update_ui("discord", "Abortado/Pausado (Progresso Salvo)", 100)
                RewardsCore.LOGGER(RewardsCore.t("discord_abortado_salvo"))
                return False
        else:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.update_ui("discord", "Falha na Execução" if not houve_fase_conectada else "Concluído (Sem Pendências)", 0 if not houve_fase_conectada else 100)
                RewardsCore.LOGGER("[DISCORD] Processo encerrado sem concluir missões. Cooldown preservado.", "error" if not houve_fase_conectada else "info")
                return bool(houve_fase_conectada)
            return False