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
            logP(`[JS] Injetando ${globalIds.length} missoes da API Global...`);
            for (let id of globalIds) {
                try {
                    await safePost(`/quests/${id}/enroll`, {
                        location: 11,
                        platform: 0,
                        is_targeted: false,
                        metadata_sealed: null,
                        traffic_metadata_sealed: sealedFor(id)
                    });
                } catch(e) {}
            }
            await new Promise(r => setTimeout(r, 2000));
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

        const supportedTasks = ["WATCH_VIDEO", "PLAY_ON_DESKTOP", "STREAM_ON_DESKTOP", "PLAY_ACTIVITY", "WATCH_VIDEO_ON_MOBILE"];
        
        quests = quests.filter(x => {
            if (!x || !x.config) return false;
            let uStatus = x.user_status || x.userStatus || {};
            if (uStatus.completed_at || uStatus.completedAt) return false;
            let exp = x.config.expires_at || x.config.expiresAt;
            if (exp && new Date(exp).getTime() < Date.now()) return false;
            let tConfig = x.config.task_config || x.config.taskConfig || x.config.task_config_v2 || x.config.taskConfigV2 || x.config;
            if (!tConfig || !tConfig.tasks) return false;
            return supportedTasks.some(y => Object.keys(tConfig.tasks).includes(y));
        });

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

            let uStatus = quest.user_status || quest.userStatus || {};
            let qConfig = quest.config || {};
            let qMessages = qConfig.messages || {};
            let qApp = qConfig.application || {};
            
            const questName = qMessages.quest_name || qMessages.questName || qApp.name || "Unknown Quest";
            let tConfig = qConfig.task_config || qConfig.taskConfig || qConfig.task_config_v2 || qConfig.taskConfigV2 || qConfig;
            const taskName = supportedTasks.find(x => tConfig.tasks?.[x] != null);
            const taskData = tConfig.tasks[taskName];
            const applicationId = taskData.applications?.[0]?.id || qApp.id || "0";
            
            const secondsNeeded = taskData.target || 900;
            const secondsDone = uStatus.progress?.[taskName]?.value || uStatus.stream_progress_seconds || 0;
            const isVideo = (taskName === "WATCH_VIDEO" || taskName === "WATCH_VIDEO_ON_MOBILE");
            const isGame = (taskName === "PLAY_ON_DESKTOP" || taskName === "STREAM_ON_DESKTOP");
            const extraSeconds = isVideo ? 0 : Math.floor(Math.random() * 240) + 60; 
            const targetTimeWithFat = secondsNeeded + extraSeconds;

            logP(`[JS] -> Missao: ${questName} | Base: ${secondsNeeded}s | Furtiva: ${targetTimeWithFat}s`);

            if (!(uStatus.enrolled_at || uStatus.enrolledAt)) {
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
                } catch(e) {}

                const ghostMouseVideo = () => {
                    try {
                        let videoContainer = document.querySelector('[data-testid="discord-web-video-player-container"]');
                        if (videoContainer) {
                            let rect = videoContainer.getBoundingClientRect();
                            let x = rect.left + Math.floor(Math.random() * rect.width);
                            let y = rect.top + Math.floor(Math.random() * rect.height);
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
                logP(`[JS] -> Missao de Video detectada: ${questName}`);
                
                // 1. Tenta reproduzir qualquer elemento <video> que esteja na tela
                const ensureVideoPlayback = () => {
                    try {
                        document.querySelectorAll('video').forEach(v => {
                            v.muted = true;
                            if (v.paused) v.play().catch(() => {});
                        });
                    } catch(e) {}
                };
                ensureVideoPlayback();
                
                // 2. Procura botão de Play / Assistir / Continuar na UI do Card ou tela
                try {
                    let card = document.getElementById('quest-tile-' + quest.id)
                        || document.querySelector(`[data-quest-id="${quest.id}"]`)
                        || Array.from(document.querySelectorAll('[class*="quest"], [class*="card"], [class*="container"]')).find(el => (el.innerText || el.textContent || '').includes(questName));
                    let scope = card || document;
                    let allBtns = Array.from(scope.querySelectorAll('button, [role="button"], a'));
                    let watchBtn = allBtns.find(b => {
                        let txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                        return /^(assistir|continuar|watch|ver v[íi]deo|play)/i.test(txt) || txt.includes('continuar') || txt.includes('assistir') || txt.includes('watch');
                    });
                    if (watchBtn) {
                        let btnTxt = (watchBtn.innerText || watchBtn.textContent || '').trim();
                        logP(`[JS] Botao de video detectado na interface ('${btnTxt}'). Acionando...`);
                        watchBtn.click();
                        await new Promise(r => setTimeout(r, 2000));
                        ensureVideoPlayback();
                    }
                } catch(e) {}

                // 3. Loop de Heartbeat e Progressão Oficial via API (/video-progress)
                let curProgress = secondsDone;
                let targetSec = secondsNeeded;
                let failCount = 0;
                
                logP(`[JS] Progresso inicial do video: ${Math.floor(curProgress)}s / ${targetSec}s`);
                window.recompensas_cmd = `REWARDS_PROGRESS:${Math.floor(curProgress)}:${targetSec}`;
                
                let videoFinished = false;
                const startTimeVideo = Date.now();
                const maxVideoTime = (targetSec + 60) * 1000;
                
                while (!videoFinished && curProgress < targetSec) {
                    let delayMs = 7000 + Math.floor(Math.random() * 2500); // 7.0s a 9.5s
                    await new Promise(r => setTimeout(r, delayMs));
                    
                    ensureVideoPlayback();
                    
                    let elapsed = (delayMs / 1000) + (Math.random() * 0.04 - 0.02);
                    let payloadTs = Number(Math.min(targetSec, curProgress + elapsed).toFixed(6));
                    
                    try {
                        let res = await safePost(`/quests/${quest.id}/video-progress`, { timestamp: payloadTs });
                        if (res.ok) {
                            failCount = 0;
                            let b = res.body || {};
                            let serverVal = b.progress?.[taskName]?.value ?? b.progress?.WATCH_VIDEO?.value ?? b.progress?.WATCH_VIDEO_ON_MOBILE?.value ?? b.user_status?.progress?.[taskName]?.value;
                            if (typeof serverVal === 'number' && serverVal > curProgress) {
                                curProgress = Math.min(targetSec, serverVal);
                            } else {
                                curProgress = Math.min(targetSec, curProgress + elapsed);
                            }
                            
                            logP(`[JS] Video em reproducao: ${Math.floor(curProgress)} / ${targetSec}s`);
                            window.recompensas_cmd = `REWARDS_PROGRESS:${Math.floor(curProgress)}:${targetSec}`;

                            if (b.completed_at || b.user_status?.completed_at || curProgress >= targetSec) {
                                videoFinished = true;
                                window.peloMenosUmSucesso = true;
                                logP(`[JS] Meta do video confirmada pelo servidor Discord com sucesso!`);
                                break;
                            }
                        } else {
                            failCount++;
                            logP(`[JS] [AVISO] Heartbeat video falhou (${failCount}/5). Status: ${res.status}`);
                            if (failCount >= 5) {
                                logP(`[JS] [ERRO] Falha persistente no progresso de video para '${questName}'. Pulando...`);
                                break;
                            }
                        }
                    } catch(errApi) {
                        failCount++;
                        logP(`[JS] Aviso heartbeat video: ${errApi}`);
                        if (failCount >= 5) break;
                    }
                    
                    if (Date.now() - startTimeVideo > maxVideoTime) {
                        logP(`[JS] [TIMEOUT] Tempo maximo de video excedido para '${questName}'.`);
                        break;
                    }
                }
                
                // 4. Fechamento seguro de modal de vídeo se existir na interface
                try {
                    let closeBtns = document.querySelectorAll('button[data-testid="video-quest-close-btn"], button[aria-label="Fechar"], button[aria-label="Close"], [aria-label*="Fechar"]');
                    closeBtns.forEach(b => b.click());
                    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, bubbles: true }));
                } catch(e) {}
                
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
                    pastas_app.sort(reverse=True)
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

def iniciar_farm_discord():
    import threading
    if not hasattr(RewardsCore, 'TRAVA_EXECUCAO'):
        RewardsCore.TRAVA_EXECUCAO = threading.Lock()
        
    if RewardsCore.TRAVA_EXECUCAO.locked():
        RewardsCore.LOGGER(RewardsCore.t("discord_bing_waiting"), "warning")
        
    with RewardsCore.TRAVA_EXECUCAO:
        if RewardsCore.ABORTAR_PROCESSO: return
        
        cfg = RewardsCore.carregar_config()
        lang = "pt" if cfg.get("language", "pt") == "pt" else "en"
        
        
        cooldown_dias = int(cfg.get("discord_cooldown", 3))
        if cfg.get("do_discord", "n") != "s": return
        if RewardsCore.verificar_se_rodou_hoje("discord", dias_cooldown=cooldown_dias):
            RewardsCore.LOGGER(RewardsCore.t("discord_cooldown"))
            return

        exe_path, exe_name = localizar_aplicativo_discord()
        if not exe_path: 
            RewardsCore.LOGGER(RewardsCore.t("discord_not_found"))
            return

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
        fases.sort(key=lambda x: x["usa_vpn"])
        if fases and not any(f["usa_vpn"] == False for f in fases):
            fases.insert(0, {"nome": "Extração de Sessão (Bridge)", "usa_vpn": False, "ids": [], "proxy_host": "", "token_only": True})

        for i, fase in enumerate(fases):
            if RewardsCore.ABORTAR_PROCESSO: return
            RewardsCore.LOGGER(RewardsCore.t("discord_batch_start").format(fase['nome'].upper()))
            RewardsCore.update_ui("discord", fase["nome"], 20 + (i * 30))
            
            args_discord = [
                exe_path, f"--remote-debugging-port={PORTA_DEBUG}",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]

            if fase["usa_vpn"] and fase.get("proxy_host"):
                RewardsCore.LOGGER(RewardsCore.t("discord_proxy_inject").format(fase['proxy_host']))
                args_discord.append(f"--proxy-server=socks5://{fase['proxy_host']}")
                temp_profile = os.path.join(tempfile.gettempdir(), f"discord_vpn_{i}")
                args_discord.append(f"--user-data-dir={temp_profile}")
                    
            modo_oculto = cfg.get("modo_oculto", "s") == "s"
            if modo_oculto: args_discord.append("--start-minimized")

            # Garante encerramento limpo antes de abrir nova instância
            _encerrar_processo_discord(exe_name)
            if RewardsCore.ABORTAR_PROCESSO: return

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

            # KICKSTART DE STARTUP (Bounce de Aquecimento):
            # Ao iniciar o Windows, o Discord Canary frequentemente trava na checagem inicial do Electron.
            # O bounce rápido (abre, aguarda 4s e reabre limpo) destrava o loop de inicialização sem perder o login.
            RewardsCore.LOGGER(f"[DISCORD] Executando kickstart de aquecimento para {exe_name}...")
            RewardsCore.update_ui("discord", "Aquecendo Discord...", 15)
            proc_kick = subprocess.Popen(args_discord, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(4)
            _encerrar_processo_discord(exe_name, proc_kick)
            time.sleep(2)

            RewardsCore.LOGGER(f"[DISCORD] Iniciando instância principal do {exe_name} (Porta {PORTA_DEBUG})...")
            RewardsCore.update_ui("discord", "Iniciando Discord...", 25)
            processo = subprocess.Popen(args_discord, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            porta_aberta = False
            RewardsCore.update_ui("discord", "Aguardando Debugger...", 30)
            for seg in range(45):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{PORTA_DEBUG}/json/version", timeout=2) as resp:
                        porta_aberta = True
                        RewardsCore.LOGGER(f"[DISCORD] Porta de depuração {PORTA_DEBUG} conectada!")
                        break
                except Exception:
                    time.sleep(2)

            if not porta_aberta:
                if not RewardsCore.ABORTAR_PROCESSO:
                    RewardsCore.LOGGER(RewardsCore.t("discord_timeout_9222"), "error")
                    RewardsCore.update_ui("discord", "Timeout Debugger 9222", 0)
                _encerrar_processo_discord(exe_name, processo)
                continue
            
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            chrome_options = Options()
            chrome_options.debugger_address = f"127.0.0.1:{PORTA_DEBUG}"

            try:
                req = urllib.request.urlopen(f"http://127.0.0.1:{PORTA_DEBUG}/json/version", timeout=5)
                dados_json = json.loads(req.read())
                match = re.search(r"Chrome/(\d+)", dados_json.get("Browser", ""))
                if match: chrome_options.browser_version = match.group(1)
            except Exception: pass

            driver = None
            for _ in range(3):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    servico = Service()
                    if os.name == 'nt': servico.creation_flags = 0x08000000
                    driver = webdriver.Chrome(service=servico, options=chrome_options)
                    driver.set_page_load_timeout(60)
                    break
                except Exception: time.sleep(5)
                
            if not driver:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(RewardsCore.t("discord_selenium_err"))
                try: processo.kill()
                except Exception: pass
                continue

            RewardsCore.update_ui("discord", "Localizando janela...", 38)
            RewardsCore.LOGGER("[DISCORD] Aguardando janela principal do Discord carregar...")
            janela_correta = None
            for tentativa_win in range(35):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        c_url = driver.current_url.lower()
                        if any(x in c_url for x in ["discord.com/app", "discord.com/channels", "discord.com/login"]):
                            janela_correta = handle
                            RewardsCore.LOGGER(f"[DISCORD] Janela detectada com sucesso ({c_url.split('?')[0]})!")
                            break
                    if janela_correta: break
                except Exception: pass
                time.sleep(2)
                
            if not janela_correta:
                if not RewardsCore.ABORTAR_PROCESSO:
                    RewardsCore.LOGGER("[DISCORD] Timeout: Discord Canary não carregou a janela principal (ficou preso na tela inicial).", "error")
                    RewardsCore.update_ui("discord", "Travado na tela inicial", 0)
                try: driver.quit()
                except Exception: pass
                _encerrar_processo_discord(exe_name, processo)
                continue
                
            # BYPASS GLOBAL DA PAGE VISIBILITY API
            try:
                driver.execute_script("""
                    Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
                    Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
                    window.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                    window.addEventListener('blur', e => e.stopImmediatePropagation(), true);
                    document.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                    document.addEventListener('blur', e => e.stopImmediatePropagation(), true);
                """)
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
                        Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
                        window.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                        window.addEventListener('blur', e => e.stopImmediatePropagation(), true);
                        document.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
                        document.addEventListener('blur', e => e.stopImmediatePropagation(), true);
                    """
                })
            except Exception: pass
                
            RewardsCore.update_ui("discord", "Carregando Webpack...", 45)
            webpack_pronto = False
            for _ in range(25): # 50s
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    if driver.execute_script("return typeof window.webpackChunkdiscord_app !== 'undefined';"):
                        webpack_pronto = True
                        break
                except Exception: pass
                time.sleep(2)

            if not webpack_pronto:
                if not RewardsCore.ABORTAR_PROCESSO:
                    RewardsCore.LOGGER("[DISCORD] Timeout: Webpack do Discord Canary não inicializou.", "error")
                    RewardsCore.update_ui("discord", "Erro Webpack Discord", 0)
                try: driver.quit()
                except Exception: pass
                _encerrar_processo_discord(exe_name, processo)
                continue

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
                except Exception: pass
                
                if fase.get("token_only"):
                    try: driver.quit()
                    except Exception: pass
                    try: processo.kill()
                    except Exception: pass
                    if platform.system().lower() == "windows": subprocess.run(f"taskkill /F /PID {processo.pid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
                except Exception: pass

            try:
                logado = driver.execute_script("return window.location.pathname !== '/login';")
                if not logado:
                    espera = 0
                    while espera < 300: 
                        if RewardsCore.ABORTAR_PROCESSO: return
                        try:
                            if driver.execute_script("return window.location.pathname !== '/login';"):
                                time.sleep(10); break
                        except Exception: pass
                        time.sleep(5); espera += 5
                    else:
                        if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(RewardsCore.t("discord_login_stuck"))
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

            from selenium.webdriver.support.ui import WebDriverWait
            for _ in range(3):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    if canal_lixo and canal_lixo.startswith("http"):
                        if driver.current_url != canal_lixo:
                            driver.get(canal_lixo)
                    else:
                        driver.execute_script("""
                            let btnMissao = document.querySelector('[href="/quest-home"], [href="/quests"], [data-list-item-id*="quests"]');
                            if (btnMissao) { 
                                btnMissao.click(); 
                            } else {
                                let els = document.querySelectorAll('*');
                                for (let el of els) {
                                    if (el.children.length === 0 && (el.textContent.trim() === 'Missões' || el.textContent.trim() === 'Quests' || el.textContent.trim() === 'Descobrir')) {
                                        (el.closest('[role="listitem"], [role="treeitem"], [role="link"], a') || el).click(); 
                                        break;
                                    }
                                }
                            }
                        """)
                except Exception: pass
                
                # Dynamic Delay Handling com WebDriverWait
                try:
                    WebDriverWait(driver, 35).until(
                        lambda d: d.execute_script(
                            "return (window.location.pathname !== '/login' && window.location.pathname !== '/') || "
                            "document.querySelector('[class*=\"questTile\"]') !== null || document.querySelector('[class*=\"embed\"]') !== null;"
                        )
                    )
                except Exception:
                    pass

                if RewardsCore.ABORTAR_PROCESSO: break
                
                try:
                    if canal_lixo and canal_lixo.startswith("http"):
                        if driver.execute_script("return window.location.pathname !== '/login';"): break
                    else:
                        if driver.execute_script("return window.location.pathname.includes('quest') || document.querySelector('[class*=\"questTile\"]') !== null;"): break
                except Exception: pass
                
                try: driver.refresh()
                except Exception: break
                time.sleep(5)

            if RewardsCore.ABORTAR_PROCESSO: break

            ids_globais = fase.get("ids", [])
            quests_webhook_url = cfg.get("quests_webhook_url", "")
            script_injetado = SCRIPT_JS.replace("INJECT_GLOBAL_IDS", json.dumps(ids_globais))
            script_injetado = script_injetado.replace('"INJECT_QUESTS_WEBHOOK"', json.dumps(quests_webhook_url))
            
            try: driver.execute_script(script_injetado)
            except Exception:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(RewardsCore.t("discord_webpack_err"))
                break
            
            RewardsCore.update_ui("discord", "Processando Tarefas...", 80)
            
            dummy_processes = []
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
                                keepalive: window.recompensas_keepalive || 0
                            };
                            window.recompensas_cmd = null;
                            window.recompensas_logs = [];
                            window.recompensas_keepalive = 0;
                            return res;
                        """)
                        
                        if js_data and (js_data.get('logs') or js_data.get('cmd') or js_data.get('keepalive')):
                            last_active_time = time.time()
                            
                        if time.time() - last_active_time > watchdog_timeout:
                            RewardsCore.LOGGER(RewardsCore.t("discord_watchdog"), "warning")
                            break
                            
                        if js_data:
                            for msg in js_data.get('logs', []):
                                RewardsCore.LOGGER(msg)
                                
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

                                    dummy_processes.append((dp, fake_exe_path))
                                    driver.execute_script(f"window.novoPidCamuflado = {dp.pid};") 
                                    
                                elif "REWARDS_KILL:ALL" in cmd:
                                    for dp, path in dummy_processes:
                                        try: dp.kill()
                                        except Exception: pass
                                        try: os.remove(path)
                                        except Exception: pass
                                    dummy_processes.clear()
                                    
                                elif "REWARDS_PROGRESS:" in cmd:
                                    try:
                                        partes = cmd.split("REWARDS_PROGRESS:")[1].split(":")
                                        c_prog = int(partes[0])
                                        t_prog = int(partes[1])
                                        percent = min(99, int((c_prog / t_prog) * 100)) if t_prog > 0 else 0
                                        # Formata tempo de mm:ss
                                        cm = c_prog // 60; cs = c_prog % 60
                                        tm = t_prog // 60; ts = t_prog % 60
                                        status_text = f"Jogando ({cm:02d}:{cs:02d} / {tm:02d}:{ts:02d})"
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
                
            for dp, path in dummy_processes:
                try: dp.kill()
                except Exception: pass
                if platform.system().lower() == "windows":
                    try: subprocess.run(f'taskkill /F /IM "{os.path.basename(path)}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception: pass
                try:
                    if os.path.exists(path): os.remove(path)
                except Exception: pass
            dummy_processes.clear()
                
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
            else:
                RewardsCore.update_ui("discord", "Abortado/Pausado (Progresso Salvo)", 100)
                RewardsCore.LOGGER(RewardsCore.t("discord_abortado_salvo"))
        else:
            if not RewardsCore.ABORTAR_PROCESSO:
                RewardsCore.update_ui("discord", "Falha na Execução", 0)
                RewardsCore.LOGGER("[DISCORD] Processo encerrado sem concluir missões. Cooldown preservado.", "error")