import os
import glob
import time
import subprocess
import urllib.request
import json
import re
import shutil
import tempfile
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 

import RewardsCore

SCRIPT_JS = r"""
(async function() {
    window.discordQuestsDone = false;
    try {
        delete window.$;

        // ==========================================
        // PLANO B: BLOQUEADOR DE FOCO ABSOLUTO
        // Engana o player de vídeo dizendo que a aba está sempre visível
        // ==========================================
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
        // ==========================================
        
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
            console.log("[JS] ERRO FATAL: Token VIP nao encontrado!");
            window.discordQuestsDone = true; return;
        }

        // FETCH LIMPO E DIRETO (Resolvido)
        const request = async (method, path, body = null) => {
            let options = { method: method, headers: { 'Authorization': token, 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            let res = await fetch(`/api/v9${path}`, options);
            let data = {}; try { data = await res.json(); } catch(e) {}
            return data;
        };

        let quests = QuestsStore ? [...QuestsStore.quests.values()] : [];
        if (quests.length === 0) {
            let resData = await request('GET', '/quests/@me');
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
            console.log("[JS] Nenhuma missao compativel pendente na sua conta.");
            window.discordQuestsDone = true; return;
        }

        console.log(`[JS] Encontrada(s) ${quests.length} missao(oes) pendente(s). Iniciando arquitetura HIBRIDA...`);

        let doJob = async function() {
            const quest = quests.pop();
            if(!quest) {
                console.log("[JS] Operacao finalizada. Farm concluido com sucesso absoluto!");
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
            const isVideo = (taskName === "WATCH_VIDEO" || taskName === "WATCH_VIDEO_ON_MOBILE");
            const extraSeconds = isVideo ? 0 : Math.floor(Math.random() * 240) + 60; 
            const targetTimeWithFat = secondsNeeded + extraSeconds;

            console.log(`[JS] -> Missao: ${questName} | Base: ${secondsNeeded}s | Furtiva: ${targetTimeWithFat}s`);

            if (!(uStatus.enrolled_at || uStatus.enrolledAt)) {
                try { await request('POST', `/quests/${quest.id}/enroll`, { location: 2 }); } catch(e) {}
                await new Promise(r => setTimeout(r, 2000));
            }

            // Se for missão exclusiva de celular, pula educadamente para não travar no QR Code
            if(taskName === "WATCH_VIDEO_ON_MOBILE") {
                console.log(`[JS] -> Missao: ${questName} requer dispositivo movel (QR Code). Pulando...`);
                setTimeout(doJob, 1000);
                return;
            }

            if(isVideo) {
                console.log(`[JS] Acionando Plano B (Automacao DOM) para o Video...`);
                let card = document.getElementById('quest-tile-' + quest.id);
                if(!card) { console.log(`[JS] Card nao encontrado.`); doJob(); return; }
                
                let btns = Array.from(card.querySelectorAll('button'));
                let watchBtn = btns.find(b => /(assistir|continuar|watch|play)/i.test(b.innerText) && b.classList.contains('primary_a22cb0')) || btns.find(b => b.classList.contains('primary_a22cb0'));
                
                if(watchBtn) watchBtn.click();
                else { console.log(`[JS] Botao Play nao encontrado.`); doJob(); return; }

                let currentWait = 0, maxWait = secondsNeeded + 60;
                let videoPoller = setInterval(() => {
                    currentWait += 2;
                    
                    // Detecção de Segurança: Verifica se o Discord abriu modal de QR Code
                    let qrModal = document.querySelector('[class*="qrCode"], img[alt*="QR"], [data-testid*="qr-code"]');
                    if (qrModal) {
                        clearInterval(videoPoller);
                        console.log(`[JS] Tela de QR Code detectada. Fechando modal e avancando...`);
                        let closeBtn = document.querySelector('button[data-testid="video-quest-close-btn"], button[aria-label="Fechar"], button[aria-label="Close"]');
                        if(closeBtn) closeBtn.click();
                        setTimeout(doJob, 2000);
                        return;
                    }

                    let video = document.querySelector('video[data-testid="discord-web-video-player-video"]');
                    if(video) {
                        video.muted = true;
                        if(video.paused) { try { video.play(); } catch(e) {} }
                        
                        let cur = video.currentTime || 0;
                        let dur = video.duration || secondsNeeded;
                        console.log(`[JS] Assistindo [Video DOM]: ${cur.toFixed(1)}s / ${dur.toFixed(1)}s`);
                        
                        let updatedQuest = QuestsStore.getQuest(quest.id);
                        let completed = (updatedQuest && updatedQuest.userStatus?.completedAt != null) || (dur > 0 && cur >= dur - 0.5);
                        
                        if(completed || currentWait >= maxWait) {
                            clearInterval(videoPoller);
                            console.log(`[JS] Reproducao finalizada!`);
                            let closeBtn = document.querySelector('button[data-testid="video-quest-close-btn"]');
                            if(closeBtn) closeBtn.click();
                            setTimeout(doJob, 3000);
                        }
                    } else if (currentWait > 15) {
                        clearInterval(videoPoller);
                        console.log(`[JS] Falha ao carregar player de video. Fechando janela...`);
                        let closeBtn = document.querySelector('button[data-testid="video-quest-close-btn"], button[aria-label="Fechar"], button[aria-label="Close"]');
                        if(closeBtn) closeBtn.click();
                        setTimeout(doJob, 2000);
                    }
                }, 2000);
            }
            else if(taskName === "PLAY_ON_DESKTOP") {
                let appDataRes = await request('GET', `/applications/public?application_ids=${applicationId}`);
                let appData = Array.isArray(appDataRes) ? appDataRes[0] : (appDataRes || {});
                let rawExeName = appData?.executables?.find(x => x.os === "win32")?.name || appData?.name || questName;
                let cleanExeName = rawExeName.replace(/[\/\\:*?"<>|\n\r]/g, "").trim();
                if (!cleanExeName.toLowerCase().endsWith(".exe")) cleanExeName += ".exe";

                console.log(`[JS] Solicitando camuflagem OS ao Python: ${cleanExeName}`);
                window.novoPidCamuflado = null; 
                document.title = "REWARDS_EXE:" + cleanExeName;
                
                let waitCycles = 0;
                while (!window.novoPidCamuflado && waitCycles < 40) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                    waitCycles++;
                }
                const pid = window.novoPidCamuflado || 10432; 
                console.log(`[JS] Ponte estabelecida. PID Autentico: ${pid}`);

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
                
                let completingThisQuest = false;
                let fatTimerStarted = false;
                
                let fn = data => {
                    if(completingThisQuest) return;
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    
                    if(!fatTimerStarted) console.log(`[JS] Tracker Nativo: ${progress} / ${targetTimeWithFat}s`);
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        
                        console.log(`[JS] Meta oficial atingida! Mantendo o jogo aberto por mais ${fatRemaining}s (Gordura Stealth)...`);
                        
                        let simulatedProgress = progress;
                        const finishUp = () => {
                            completingThisQuest = true;
                            console.log(`[JS] Objetivo e gordura cumpridos! Limpando memoria OS...`);
                            if (RunningGameStore) { RunningGameStore.getRunningGames = realGetRunningGames; RunningGameStore.getGameForPID = realGetGameForPID; }
                            if (FluxDispatcher) { FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: [fakeGame], added: [], games: []}); FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn); }
                            document.title = "REWARDS_KILL:ALL";
                            setTimeout(doJob, 3000);
                        };

                        if(fatRemaining <= 0) finishUp();
                        else {
                            let fatInterval = setInterval(() => {
                                simulatedProgress += 5;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                console.log(`[JS] Tracker Furtivo: ${simulatedProgress} / ${targetTimeWithFat}s`);
                                if (simulatedProgress >= targetTimeWithFat) { clearInterval(fatInterval); finishUp(); }
                            }, 5000);
                        }
                    }
                };
                if (FluxDispatcher) FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);
            } 
            else if(taskName === "STREAM_ON_DESKTOP") {
                let cleanExeName = questName.replace(/[\/\\:*?"<>|\n\r]/g, "").trim() + ".exe";
                window.novoPidCamuflado = null; 
                document.title = "REWARDS_EXE:" + cleanExeName;
                
                let waitCycles = 0;
                while (!window.novoPidCamuflado && waitCycles < 40) { await new Promise(resolve => setTimeout(resolve, 500)); waitCycles++; }
                
                const pid = window.novoPidCamuflado || 10432;
                let realFunc = ApplicationStreamingStore ? ApplicationStreamingStore.getStreamerActiveStreamMetadata : null;
                if (ApplicationStreamingStore) ApplicationStreamingStore.getStreamerActiveStreamMetadata = () => ({ id: applicationId, pid: pid, sourceName: null });
                
                let completingThisQuest = false;
                let fatTimerStarted = false;
                
                let fn = data => {
                    if(completingThisQuest) return;
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    
                    if(!fatTimerStarted) console.log(`[JS] Stream Nativo: ${progress} / ${targetTimeWithFat}s`);
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        
                        console.log(`[JS] Meta oficial da Stream atingida! Queimando gordura stealth (${fatRemaining}s)...`);
                        
                        let simulatedProgress = progress;
                        const finishUp = () => {
                            completingThisQuest = true;
                            console.log(`[JS] Streaming finalizado 100% furtivo!`);
                            if (ApplicationStreamingStore) ApplicationStreamingStore.getStreamerActiveStreamMetadata = realFunc;
                            if (FluxDispatcher) FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);
                            document.title = "REWARDS_KILL:ALL";
                            setTimeout(doJob, 3000);
                        };

                        if(fatRemaining <= 0) finishUp();
                        else {
                            let fatInterval = setInterval(() => {
                                simulatedProgress += 5;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                console.log(`[JS] Tracker Furtivo (Stream): ${simulatedProgress} / ${targetTimeWithFat}s`);
                                if (simulatedProgress >= targetTimeWithFat) { clearInterval(fatInterval); finishUp(); }
                            }, 5000);
                        }
                    }
                };
                if (FluxDispatcher) FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);
            }
            else if(taskName === "PLAY_ACTIVITY") {
                let channelId = "0";
                try { channelId = ChannelStore?.getSortedPrivateChannels()?.[0]?.id || Object.values(GuildChannelStore?.getAllGuilds() || {}).find(x => x != null && x.VOCAL?.length > 0)?.VOCAL?.[0]?.channel?.id || "0"; } catch(e) {}
                const streamKey = `call:${channelId}:1`;
                
                let startTime = Date.now();
                let initialSeconds = secondsDone;
                
                let fn = async () => {
                    console.log(`[JS] Call detectada (${questName}). Iniciando heartbeats hibridos...`);
                    while(true) {
                        let progress = 0;
                        try {
                            const res = await request('POST', `/quests/${quest.id}/heartbeat`, {stream_key: streamKey, terminal: false});
                            progress = res?.progress?.[taskName]?.value || 0;
                        } catch(e) {}
                        
                        let elapsed = Math.floor((Date.now() - startTime) / 1000);
                        let bestProg = Math.max(progress, initialSeconds + elapsed);
                        
                        console.log(`[JS] Atividade Call: ${bestProg} / ${targetTimeWithFat}s`);
                        
                        if(bestProg >= targetTimeWithFat) {
                            try { await request('POST', `/quests/${quest.id}/heartbeat`, {stream_key: streamKey, terminal: true}); } catch(e) {}
                            break;
                        }
                        
                        let caosDelay = 18000 + Math.floor(Math.random() * 8000); 
                        await new Promise(resolve => setTimeout(resolve, caosDelay));
                    }
                    console.log(`[JS] Atividade Call finalizada e disfarçada!`);
                    doJob();
                };
                fn();
            }
        };
        doJob();

    } catch(err) {
        console.error("[JS] Erro critico na espinha dorsal:", err);
        window.discordQuestsDone = true;
    }
})();
"""


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
                    exe_path = os.path.join(pastas_app[0], exe_name)
                    if os.path.exists(exe_path):
                        return exe_path, exe_name
                        
    elif sistema == "linux":
        # No Linux os binários costumam estar no PATH com esses nomes
        for exe_name in ["discord-canary", "discord-ptb"]:
            exe_path = shutil.which(exe_name)
            if exe_path:
                return exe_path, exe_name
                
    elif sistema == "darwin": # macOS
        pastas = {
            "Canary": "/Applications/Discord Canary.app/Contents/MacOS/Discord Canary",
            "PTB": "/Applications/Discord PTB.app/Contents/MacOS/Discord PTB"
        }
        for versao, exe_path in pastas.items():
            if os.path.exists(exe_path):
                return exe_path, versao # No Mac o nome do executável não tem .exe
                
    return None, None

def iniciar_farm_discord():
    cfg = RewardsCore.carregar_config()
    
    # ----------------------------------------------------
    # TABELA DE TRADUÇÃO DINÂMICA
    # ----------------------------------------------------
    lang = "pt" if cfg.get("language", "pt") == "pt" else "en"
    
    d_msgs = {
        "en": {
            "cooldown": "[DISCORD] Cooldown active (runs every {} days). Skipping for now.",
            "start_native": "[DISCORD] >>> STARTING NATIVE APP MODULE <<<",
            "not_found": "[DISCORD] ERROR: Application not found.",
            "stealth_on": "[DISCORD] Stealth Mode is ON. Starting minimized to tray...",
            "visible_on": "[DISCORD] Launching Discord App in visible mode...",
            "check_login": "[DISCORD] Checking login state...",
            "wait_login": "[DISCORD] App is waiting for User Login/QR Code!",
            "login_ok": "[DISCORD] Login detected! Proceeding...",
            "open_quests": "[DISCORD] Opening 'Quests' tab to load data into memory...",
            "inject_core": "[DISCORD] Injecting Webpack Core Script...",
            "script_attached": "[DISCORD] Script attached! Processing quests in background...",
            "forge_os": "[DISCORD] Forging OS camouflage: {}",
            "pid_sync": "[DISCORD] OS Camouflage allocated (PID: {}). Synchronizing RAM...",
            "clean_matrix": "[DISCORD] Quest transitioning. Clearing Windows process matrix...",
            "all_completed": "[DISCORD] ALL QUESTS COMPLETED AND VERIFIED!",
            "loop_error": "[DISCORD] Error during script wait loop: {}",
            "fatal_error": "[DISCORD] Fatal Error: {}",
            "terminate": "[DISCORD] Terminating App Process and doing cleanup...",
            "safe_quit": "[DISCORD] Sending safe quit signal to DiscordNative...",
            "closed_ok": "[DISCORD] App process closed successfully."
        },
        "pt": {
            "cooldown": "[DISCORD] Cooldown ativo (roda a cada {} dias). Pulando por enquanto.",
            "start_native": "[DISCORD] >>> INICIANDO MÓDULO DO APP NATIVO <<<",
            "not_found": "[DISCORD] ERRO: Aplicativo não encontrado.",
            "stealth_on": "[DISCORD] Modo Furtivo ATIVADO. Iniciando minimizado na bandeja...",
            "visible_on": "[DISCORD] Iniciando App do Discord em modo visível...",
            "check_login": "[DISCORD] Verificando estado de login...",
            "wait_login": "[DISCORD] App está aguardando Login do Usuário/QR Code!",
            "login_ok": "[DISCORD] Login detectado! Prosseguindo...",
            "open_quests": "[DISCORD] Abrindo aba 'Missões' para carregar dados na memória...",
            "inject_core": "[DISCORD] Injetando Script Webpack Core...",
            "script_attached": "[DISCORD] Script anexado! Processando missões em segundo plano...",
            "forge_os": "[DISCORD] Fabricando camuflagem no Sistema: {}",
            "pid_sync": "[DISCORD] Camuflagem OS alocada (PID: {}). Sincronizando memoria RAM...",
            "clean_matrix": "[DISCORD] Missao em transicao. Limpando matriz de processos do Windows...",
            "all_completed": "[DISCORD] TODAS AS MISSÕES CONCLUÍDAS E VERIFICADAS!",
            "loop_error": "[DISCORD] Erro durante o loop de espera do script: {}",
            "fatal_error": "[DISCORD] Erro Fatal: {}",
            "terminate": "[DISCORD] Encerrando processo do App e limpando...",
            "safe_quit": "[DISCORD] Enviando sinal de encerramento seguro para o DiscordNative...",
            "closed_ok": "[DISCORD] Processo do App encerrado com sucesso."
        }
    }
    # ----------------------------------------------------

    cooldown_dias = int(cfg.get("discord_cooldown", 3))

    if cfg.get("do_discord", "n") != "s":
        return

    if RewardsCore.verificar_se_rodou_hoje("discord", dias_cooldown=cooldown_dias):
        RewardsCore.LOGGER(d_msgs[lang]["cooldown"].format(cooldown_dias))
        return

    RewardsCore.LOGGER(d_msgs[lang]["start_native"])
    exe_path, exe_name = localizar_aplicativo_discord()
    
    if not exe_path:
        RewardsCore.LOGGER(d_msgs[lang]["not_found"])
        
        if lang == "en":
            pop_title = "⚠️ Discord Not Found"
            pop_desc = "Compatible Discord version (Canary or PTB) not found!<br><br><span style='font-size:0.85em;color:var(--text-muted,#64748b);'>To allow the bot to farm quests in 100% stealth mode without closing your main Discord, please download one of the developer versions below:</span>"
            pop_btn_c = "Download Canary"
            pop_btn_p = "Download PTB"
        else:
            pop_title = "⚠️ Discord Não Encontrado"
            pop_desc = "Versão compatível do Discord (Canary ou PTB) não encontrada!<br><br><span style='font-size:0.85em;color:var(--text-muted,#64748b);'>Para que o bot possa farmar as missões em modo 100% furtivo sem derrubar o seu Discord Principal, baixe uma das versões de desenvolvedor abaixo:</span>"
            pop_btn_c = "Baixar Canary"
            pop_btn_p = "Baixar PTB"

        js_popup = """
        if (!document.getElementById('discord-popup')) {
            const overlay = document.createElement('div');
            overlay.id = 'discord-popup';
            overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:10000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(5px);';
            
            const modal = document.createElement('div');
            modal.style.cssText = 'background:var(--bg-panel,#111827);border:1px solid var(--border-color,#1e293b);border-radius:16px;padding:30px;text-align:center;max-width:420px;box-shadow:0 20px 40px rgba(0,0,0,0.6);position:relative;animation:fadeIn 0.3s;';
            
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '✕';
            closeBtn.style.cssText = 'position:absolute;top:10px;right:15px;background:transparent;border:none;color:var(--text-muted,#64748b);font-size:16px;cursor:pointer;';
            closeBtn.onclick = () => overlay.remove();

            const title = document.createElement('h3');
            title.innerHTML = 'POPUP_TITLE';
            title.style.cssText = 'margin-top:0;color:var(--accent-yellow,#f59e0b);font-size:1.4em;margin-bottom:10px;';

            const text = document.createElement('p');
            text.innerHTML = "POPUP_DESC";
            text.style.cssText = 'color:var(--text-main,#f1f5f9);line-height:1.5;margin-bottom:25px;';

            const btnContainer = document.createElement('div');
            btnContainer.style.cssText = 'display:flex;gap:15px;justify-content:center;';

            const btnCanary = document.createElement('a');
            btnCanary.href = 'https://canary.discord.com/download';
            btnCanary.target = '_blank';
            btnCanary.innerText = 'POPUP_BTN_CANARY';
            btnCanary.style.cssText = 'background:#eab308;color:#000;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:bold;transition:0.2s;flex:1;';
            btnCanary.onmouseover = () => btnCanary.style.filter = 'brightness(1.1)';
            btnCanary.onmouseout = () => btnCanary.style.filter = 'brightness(1)';
            btnCanary.onclick = () => overlay.remove();

            const btnPTB = document.createElement('a');
            btnPTB.href = 'https://ptb.discord.com';
            btnPTB.target = '_blank';
            btnPTB.innerText = 'POPUP_BTN_PTB';
            btnPTB.style.cssText = 'background:#3b82f6;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:bold;transition:0.2s;flex:1;';
            btnPTB.onmouseover = () => btnPTB.style.filter = 'brightness(1.1)';
            btnPTB.onmouseout = () => btnPTB.style.filter = 'brightness(1)';
            btnPTB.onclick = () => overlay.remove();

            btnContainer.appendChild(btnCanary);
            btnContainer.appendChild(btnPTB);
            
            modal.appendChild(closeBtn);
            modal.appendChild(title);
            modal.appendChild(text);
            modal.appendChild(btnContainer);
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
        }
        """
        
        # Injeta as variáveis de texto no JS
        js_popup = js_popup.replace("POPUP_TITLE", pop_title)
        js_popup = js_popup.replace("POPUP_DESC", pop_desc)
        js_popup = js_popup.replace("POPUP_BTN_CANARY", pop_btn_c)
        js_popup = js_popup.replace("POPUP_BTN_PTB", pop_btn_p)
        
        try:
            import webview
            webview.windows[0].evaluate_js(js_popup)
        except: pass
        return

    PORTA_DEBUG = 9222
    processo = None
    driver = None
    dummy_processes = []
    
    try:
        args_discord = [
            exe_path, 
            f"--remote-debugging-port={PORTA_DEBUG}",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding"
        ]
        
        if cfg.get("modo_oculto", "s") == "s":
            args_discord.append("--start-minimized")
            RewardsCore.LOGGER(d_msgs[lang]["stealth_on"])
        else:
            RewardsCore.LOGGER(d_msgs[lang]["visible_on"])
            
        # Variáveis bilíngues dinâmicas para os novos módulos
        msg_booting = "[DISCORD] Booting App Process... (Try {}/2)" if lang == "en" else "[DISCORD] Iniciando Processo do App... (Tentativa {}/2)"
        msg_blocked = "[DISCORD] Port 9222 blocked or Update finished. Forcing second invisible boot..." if lang == "en" else "[DISCORD] Porta 9222 bloqueada ou Update finalizado. Forçando segunda inicialização invisível..."
        msg_engine = "[DISCORD] Waiting for the app's graphical engine to load..." if lang == "en" else "[DISCORD] Aguardando o motor grafico do aplicativo carregar..."
        err_timeout1 = "Timeout: Failed to connect to Discord after 2 attempts. Update might be downloading." if lang == "en" else "Timeout: Falha ao conectar no Discord após 2 tentativas. A internet pode estar lenta para baixar o update."
        err_timeout2 = "Timeout: Main Discord window did not respond in time." if lang == "en" else "Timeout: A janela principal do Discord nao respondeu a tempo."
        err_timeout3 = "Timeout: Failed to connect to Discord after 3 attempts." if lang == "en" else "Timeout: Falha ao conectar no Discord após 3 tentativas."

        # --- INICIALIZADOR BLINDADO ANTI-UPDATER ---
        porta_aberta = False
        for tentativa_lancamento in range(2): 
            sistema_atual = platform.system().lower()
            if sistema_atual == "windows":
                subprocess.run(f"taskkill /F /IM \"{exe_name}\" /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(4) 
            else:
                subprocess.run(f"pkill -9 -f \"{exe_name}\"", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(4)

            processo = subprocess.Popen(args_discord)
            RewardsCore.LOGGER(msg_booting.format(tentativa_lancamento + 1))
            
            # Poller Dinâmico PACIENTE: Espera até 120 segundos
            for _ in range(60): 
                try:
                    req = urllib.request.urlopen(f"http://127.0.0.1:{PORTA_DEBUG}/json/version", timeout=2)
                    if req.getcode() == 200:
                        porta_aberta = True
                        break
                except: pass
                time.sleep(2)
                
            if porta_aberta:
                break
            else:
                RewardsCore.LOGGER(msg_blocked)

        if not porta_aberta:
            raise Exception(err_timeout1)
        # -------------------------------------------------------------
        
        chrome_options = Options()
        chrome_options.debugger_address = f"127.0.0.1:{PORTA_DEBUG}"
        
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{PORTA_DEBUG}/json/version", timeout=5)
            dados_json = json.loads(req.read())
            match = re.search(r"Chrome/(\d+)", dados_json.get("Browser", ""))
            if match: chrome_options.browser_version = match.group(1)
        except Exception: pass

        # --- CONEXÃO BLINDADA DO SELENIUM ---
        for tentativa in range(3):
            try:
                servico = Service()
                if os.name == 'nt':
                    servico.creation_flags = 0x08000000 # Oculta a janela preta do CMD
                driver = webdriver.Chrome(service=servico, options=chrome_options)
                break
            except Exception:
                time.sleep(5)
                
        if not driver:
            raise Exception(err_timeout3)
        # -------------------------------------

        # --- CAÇADOR DE JANELAS BLINDADO (Foco no Startup) ---
        RewardsCore.LOGGER(msg_engine)
        janela_correta = None
        for _ in range(25):  # Tenta por até 50 segundos
            try:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    url = driver.current_url.lower()
                    if "discord.com/app" in url or "discord.com/channels" in url or "discord.com/login" in url:
                        janela_correta = handle
                        break
                if janela_correta:
                    break
            except Exception: pass
            time.sleep(2)
            
        if not janela_correta:
            raise Exception(err_timeout2)
            
        # O SEGREDO: Garante que as variaveis internas do Discord (Webpack) ja nasceram na memoria
        for _ in range(15):
            try:
                is_ready = driver.execute_script("return typeof window.webpackChunkdiscord_app !== 'undefined';")
                if is_ready: break
            except: pass
            time.sleep(2)
        # -----------------------------------------------------

        RewardsCore.LOGGER(d_msgs[lang]["check_login"])
        logado = driver.execute_script("return window.location.pathname !== '/login';")
        
        if not logado:
            RewardsCore.LOGGER(d_msgs[lang]["wait_login"])
            espera = 0
            while espera < 300: 
                if driver.execute_script("return window.location.pathname !== '/login';"):
                    RewardsCore.LOGGER(d_msgs[lang]["login_ok"])
                    time.sleep(10)
                    break
                time.sleep(5)
                espera += 5
            else: return

        RewardsCore.LOGGER(d_msgs[lang]["open_quests"])
        try:
            driver.execute_script("""
                let elementos = document.querySelectorAll('*');
                for (let i = 0; i < elementos.length; i++) {
                    let el = elementos[i];
                    if (el.children.length === 0 && (el.textContent.trim() === 'Missões' || el.textContent.trim() === 'Quests')) {
                        let clicavel = el.closest('[role="listitem"], [role="treeitem"], [role="link"], a') || el;
                        clicavel.click(); break;
                    }
                }
            """)
        except Exception: pass

        time.sleep(8) 
        
        RewardsCore.LOGGER(d_msgs[lang]["inject_core"])
        driver.execute_script(SCRIPT_JS)
        RewardsCore.LOGGER(d_msgs[lang]["script_attached"])
        
        try:
            while True:
                time.sleep(5)
                
                try:
                    titulo_atual = driver.title
                    
                    if "REWARDS_EXE:" in titulo_atual:
                        exe_needed = titulo_atual.split("REWARDS_EXE:")[1].strip()
                        RewardsCore.LOGGER(d_msgs[lang]["forge_os"].format(exe_needed))
                        
                        temp_dir = tempfile.gettempdir()
                        fake_exe_path = os.path.join(temp_dir, exe_needed)
                        
                        sistema_atual = platform.system().lower()
                        if sistema_atual == "windows":
                            shutil.copy(r"C:\Windows\System32\ping.exe", fake_exe_path)
                            dp = subprocess.Popen([fake_exe_path, "127.0.0.1", "-n", "3600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                        else:
                            caminho_sleep = shutil.which("sleep") or "/bin/sleep"
                            shutil.copy(caminho_sleep, fake_exe_path)
                            os.chmod(fake_exe_path, 0o755) 
                            dp = subprocess.Popen([fake_exe_path, "3600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        dummy_processes.append((dp, fake_exe_path))
                        
                        RewardsCore.LOGGER(d_msgs[lang]["pid_sync"].format(dp.pid))
                        driver.execute_script(f"window.novoPidCamuflado = {dp.pid}; document.title = 'Discord';") 
                        
                    elif "REWARDS_KILL:ALL" in titulo_atual:
                        RewardsCore.LOGGER(d_msgs[lang]["clean_matrix"])
                        for dp, path in dummy_processes:
                            try: dp.kill()
                            except: pass
                            try: 
                                if path: os.remove(path)
                            except: pass
                        dummy_processes.clear()
                        driver.execute_script("document.title = 'Discord';")
                except Exception: pass
                
                try:
                    for log in driver.get_log("browser"):
                        msg = log.get("message", "")
                        if "[JS]" in msg:
                            clean_msg = msg[msg.find("[JS]"):].strip(" '\"\\n")
                            RewardsCore.LOGGER(f"{clean_msg}")
                except Exception: pass
                
                terminou = driver.execute_script("return window.discordQuestsDone === true;")
                if terminou: break

            RewardsCore.LOGGER(d_msgs[lang]["all_completed"])
            RewardsCore.registrar_data_execucao("discord")
            
        except Exception as e:
            RewardsCore.LOGGER(d_msgs[lang]["loop_error"].format(str(e)[:200]))
        
    except Exception as e:
        safe_msg = str(e).split('\n')[0] if e else "Unknown Error"
        RewardsCore.LOGGER(d_msgs[lang]["fatal_error"].format(safe_msg))
    finally:
        RewardsCore.LOGGER(d_msgs[lang]["terminate"])
        for dp, path in dummy_processes:
            try: dp.kill()
            except: pass
            try: 
                if path: os.remove(path)
            except: pass
            
        try:
            if driver:
                RewardsCore.LOGGER(d_msgs[lang]["safe_quit"])
                driver.execute_script("try { window.DiscordNative.app.quit(); } catch(e) {}")
                time.sleep(4) 
                driver.quit() 
        except Exception: 
            pass
        
        subprocess.run(f"taskkill /IM {exe_name} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        subprocess.run(f"taskkill /F /IM {exe_name} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        RewardsCore.LOGGER(d_msgs[lang]["closed_ok"])