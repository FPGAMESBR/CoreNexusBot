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
import tarfile
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

        const request = async (method, path, body = null) => {
            let options = { method: method, headers: { 'Authorization': token, 'Content-Type': 'application/json' } };
            if (body) options.body = JSON.stringify(body);
            let res = await fetch(`/api/v9${path}`, options);
            let data = {}; try { data = await res.json(); } catch(e) {}
            return data;
        };

        const globalIds = INJECT_GLOBAL_IDS;
        const questsWebhookUrl = "INJECT_QUESTS_WEBHOOK";
        if (globalIds && globalIds.length > 0) {
            logP(`[JS] Injetando ${globalIds.length} missoes da API Global...`);
            for (let id of globalIds) {
                try { await request('POST', `/quests/${id}/enroll`, { location: 2 }); } catch(e) {}
            }
            await new Promise(r => setTimeout(r, 2000));
        }

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
            const isVideo = (taskName === "WATCH_VIDEO" || taskName === "WATCH_VIDEO_ON_MOBILE");
            const isGame = (taskName === "PLAY_ON_DESKTOP" || taskName === "STREAM_ON_DESKTOP");
            const extraSeconds = isVideo ? 0 : Math.floor(Math.random() * 240) + 60; 
            const targetTimeWithFat = secondsNeeded + extraSeconds;

            logP(`[JS] -> Missao: ${questName} | Base: ${secondsNeeded}s | Furtiva: ${targetTimeWithFat}s`);

            if (!(uStatus.enrolled_at || uStatus.enrolledAt)) {
                try { await request('POST', `/quests/${quest.id}/enroll`, { location: 2 }); } catch(e) {}
                await new Promise(r => setTimeout(r, 2000));
            }

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

            const executarDesligamento = () => {
                if (ghostInterval) clearTimeout(ghostInterval);
                let endDelay = 4000 + Math.floor(Math.random() * 8000);
                logP(`[JS] Objetivo cumprido! Descompressao organica de ${Math.floor(endDelay/1000)}s...`);
                setTimeout(() => {
                    window.recompensas_cmd = "REWARDS_KILL:ALL";
                    setTimeout(doJob, 3000);
                }, endDelay);
            };

            if(isVideo) {
                if (questsWebhookUrl && questsWebhookUrl !== "INJECT_QUESTS_WEBHOOK" && questsWebhookUrl.startsWith("http")) {
                    logP(`[JS] Webhook configurado! Enviando missao de video para la...`);
                    try {
                        await fetch(questsWebhookUrl, {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({
                                content: `**Missão de Vídeo Global (SOCKS5)**\n**Jogo:** ${questName}\n**Link Mágico:** https://discord.com/quests/${quest.id}\n*Clique no botão "Watch Video" que aparecerá no card abaixo para concluir a missão usando o proxy americano do Discord!*`
                            })
                        });
                        logP(`[JS] Link enviado para o Webhook com sucesso! Conclua manualmente no chat. Pulando etapa interna.`);
                    } catch(e) {
                        logP(`[JS] Falha ao enviar para o Webhook: ${e}`);
                    }
                    executarDesligamento();
                    return;
                }

                let card = document.getElementById('quest-tile-' + quest.id);
                if(!card) {
                    let questsTab = document.querySelector('a[href="/quest-home"]');
                    if (questsTab) {
                        logP(`[JS] Aba de missões não ativa. Navegando para a aba de Missões...`);
                        questsTab.click();
                        quests.push(quest); // Coloca de volta para tentar de novo
                        setTimeout(doJob, 3000);
                        return;
                    }
                }
                
                if(!card) { logP(`[JS] ALERTA: Card de video nao encontrado (Aba de missoes fechada?). Encerrando bloco.`); executarDesligamento(); return; }
                
                let btns = Array.from(card.querySelectorAll('button'));
                let watchBtn = btns.find(b => /(assistir|continuar|watch|play|jogar)/i.test(b.innerText) && b.classList.contains('primary_a22cb0')) || btns.find(b => b.classList.contains('primary_a22cb0'));
                
                if(watchBtn) {
                    let extractedSeconds = secondsNeeded;
                    let match = watchBtn.innerText.match(/Assistir\s+(\d+)(m|s)/i);
                    if (match) {
                        let val = parseInt(match[1]);
                        if (match[2].toLowerCase() === 'm') extractedSeconds = val * 60;
                        else extractedSeconds = val;
                    }
                    
                    let readDelay = 3000 + Math.floor(Math.random() * 5000);
                    setTimeout(() => {
                        logP(`[JS] Acionando Play no Video... (Duração extraída: ${extractedSeconds}s)`);
                        watchBtn.click();
                        
                        let waitTimeMs = (extractedSeconds + 15) * 1000;
                        logP(`[JS] Aguardando ${extractedSeconds + 15}s (margem de erro) para concluir a missão de vídeo...`);
                        
                        setTimeout(() => {
                            logP(`[JS] Tempo esgotado! Buscando botão de reivindicar recompensa...`);
                            let closeBtn = document.querySelector('button[data-testid="video-quest-close-btn"], button[aria-label="Fechar"], button[aria-label="Close"]');
                            if(closeBtn) closeBtn.click();
                            
                            setTimeout(() => {
                                logP(`[JS] Missão de vídeo concluída! A etapa de reivindicar recompensa foi pulada para evitar bloqueios de hCaptcha.`);
                                executarDesligamento();
                            }, 1000);
                            
                        }, waitTimeMs);
                        
                    }, readDelay);
                } else { 
                    logP(`[JS] Botao Play (Assistir) nao encontrado.`); executarDesligamento(); return; 
                }
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
                
                let completingThisQuest = false;
                let fatTimerStarted = false;
                let fn = data => {
                    if(completingThisQuest) return;
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    if(!fatTimerStarted) logP(`[JS] Tracker Nativo: ${progress} / ${targetTimeWithFat}s`);
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        
                        logP(`[JS] Meta oficial atingida! Mantendo o jogo aberto por mais ${fatRemaining}s (Gordura Stealth)...`);
                        let simulatedProgress = progress;
                        const finishUp = () => {
                            completingThisQuest = true;
                            if (RunningGameStore) { RunningGameStore.getRunningGames = realGetRunningGames; RunningGameStore.getGameForPID = realGetGameForPID; }
                            if (FluxDispatcher) { FluxDispatcher.dispatch({type: "RUNNING_GAMES_CHANGE", removed: [fakeGame], added: [], games: []}); FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn); }
                            executarDesligamento();
                        };

                        if(fatRemaining <= 0) finishUp();
                        else {
                            const queimarGordura = () => {
                                if(simulatedProgress >= targetTimeWithFat) { finishUp(); return; }
                                let ganho = 8 + Math.floor(Math.random() * 12);
                                simulatedProgress += ganho;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                logP(`[JS] Tracker Furtivo: ${simulatedProgress} / ${targetTimeWithFat}s`);
                                setTimeout(queimarGordura, (ganho * 1000) + Math.floor(Math.random() * 2000));
                            };
                            queimarGordura();
                        }
                    }
                };
                if (FluxDispatcher) FluxDispatcher.subscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);
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
                
                let completingThisQuest = false;
                let fatTimerStarted = false;
                let fn = data => {
                    if(completingThisQuest) return;
                    let progress = quest.config.configVersion === 1 ? data.userStatus?.streamProgressSeconds || 0 : Math.floor(data.userStatus?.progress?.[taskName]?.value || 0);
                    if(!fatTimerStarted) logP(`[JS] Stream Nativo: ${progress} / ${targetTimeWithFat}s`);
                    
                    if(!fatTimerStarted && (progress >= secondsNeeded || data.userStatus?.completedAt || data.userStatus?.completed_at)) {
                        fatTimerStarted = true;
                        let fatRemaining = targetTimeWithFat - progress;
                        if(fatRemaining < 0) fatRemaining = 0;
                        logP(`[JS] Meta oficial da Stream atingida! Queimando gordura stealth (${fatRemaining}s)...`);
                        
                        let simulatedProgress = progress;
                        const finishUp = () => {
                            completingThisQuest = true;
                            if (ApplicationStreamingStore) ApplicationStreamingStore.getStreamerActiveStreamMetadata = realFunc;
                            if (FluxDispatcher) FluxDispatcher.unsubscribe("QUESTS_SEND_HEARTBEAT_SUCCESS", fn);
                            executarDesligamento();
                        };

                        if(fatRemaining <= 0) finishUp();
                        else {
                            const queimarGorduraStream = () => {
                                if(simulatedProgress >= targetTimeWithFat) { finishUp(); return; }
                                let ganho = 8 + Math.floor(Math.random() * 12);
                                simulatedProgress += ganho;
                                if(simulatedProgress >= targetTimeWithFat) simulatedProgress = targetTimeWithFat;
                                logP(`[JS] Tracker Furtivo (Stream): ${simulatedProgress} / ${targetTimeWithFat}s`);
                                setTimeout(queimarGorduraStream, (ganho * 1000) + Math.floor(Math.random() * 2000));
                            };
                            queimarGorduraStream();
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
        };
        doJob();

    } catch(err) {
        logP("[JS] Erro critico na espinha dorsal: " + err.message);
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
            RewardsCore.LOGGER("[DISCORD] Update Blocker ativado nativamente.")
    except Exception: pass

def gerenciar_daemon_tor():
    localappdata = os.environ.get('LOCALAPPDATA', '')
    tor_base_dir = os.path.join(localappdata, "RewardBot", "Tor")
    tor_exe = os.path.join(tor_base_dir, "tor", "tor.exe")
    torrc_path = os.path.join(tor_base_dir, "torrc")

    if not os.path.exists(tor_exe):
        RewardsCore.LOGGER("[DISCORD] Baixando pacote oficial do Tor Engine (isso ocorre apenas 1x)...")
        os.makedirs(tor_base_dir, exist_ok=True)
        tar_url = "https://archive.torproject.org/tor-package-archive/torbrowser/13.5/tor-expert-bundle-windows-x86_64-13.5.tar.gz"
        tar_path = os.path.join(tor_base_dir, "tor.tar.gz")
        try:
            urllib.request.urlretrieve(tar_url, tar_path)
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=tor_base_dir)
            os.remove(tar_path)
            RewardsCore.LOGGER("[DISCORD] Tor Engine baixado e extraído com sucesso.")
        except Exception as e:
            RewardsCore.LOGGER(f"[DISCORD] Falha ao baixar Tor: {str(e)}")
            return None

    if not os.path.exists(torrc_path):
        with open(torrc_path, "w") as f:
            f.write("SocksPort 9060\nAvoidDiskWrites 1\n")

    return tor_exe, torrc_path

def verificar_porta_tor():
    try:
        with socket.create_connection(("127.0.0.1", 9060), timeout=1): return True
    except OSError: return False

def iniciar_farm_discord():
    import threading
    if not hasattr(RewardsCore, 'TRAVA_EXECUCAO'):
        RewardsCore.TRAVA_EXECUCAO = threading.Lock()
        
    if RewardsCore.TRAVA_EXECUCAO.locked():
        RewardsCore.LOGGER("\n[SISTEMA] O Bing está usando o motor no momento. Colocando o Discord na fila de espera...", "warning")
        
    with RewardsCore.TRAVA_EXECUCAO:
        if RewardsCore.ABORTAR_PROCESSO: return
        
        cfg = RewardsCore.carregar_config()
        lang = "pt" if cfg.get("language", "pt") == "pt" else "en"
        d_msgs = {
            "en": {"cooldown": "[DISCORD] Cooldown active. Skipping for now.", "not_found": "[DISCORD] ERROR: App not found.", "loop_error": "[DISCORD] Error: {}"},
            "pt": {"cooldown": "[DISCORD] Cooldown ativo. Pulando.", "not_found": "[DISCORD] ERRO: App nao encontrado.", "loop_error": "[DISCORD] Erro: {}"}
        }
        
        cooldown_dias = int(cfg.get("discord_cooldown", 3))
        if cfg.get("do_discord", "n") != "s": return
        if RewardsCore.verificar_se_rodou_hoje("discord", dias_cooldown=cooldown_dias):
            RewardsCore.LOGGER(d_msgs[lang]["cooldown"])
            return

        exe_path, exe_name = localizar_aplicativo_discord()
        if not exe_path: 
            RewardsCore.LOGGER(d_msgs[lang]["not_found"])
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
            RewardsCore.LOGGER(f"[DISCORD] Erro ao consultar a API Global: {e}")

        from datetime import datetime, timezone
        region_batches = {}
        try:
            if isinstance(api_quests, list):
                for q in api_quests:
                    if not is_over_18 and q.get('age_restricted', False): continue
                    
                    cfg_q = q.get('config', {})
                    expires_at = cfg_q.get('expires_at') or cfg_q.get('expiresAt')
                    if expires_at:
                        try:
                            exp_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if exp_date < datetime.now(timezone.utc):
                                continue
                        except:
                            pass

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
                RewardsCore.LOGGER(f"[DISCORD] Resposta inesperada da API: {type(api_quests)}")
        except Exception as e:
            RewardsCore.LOGGER(f"[DISCORD] Erro ao filtrar missões globais: {e}")

        def obter_proxy_socks5_por_pais(country_code):
            import requests
            try:
                api_proxies = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=socks5&proxy_format=protocolipport&format=json&timeout=1500"
                RewardsCore.LOGGER(f"[DISCORD] Transferindo lista de proxies SOCKS5...")
                
                resposta = requests.get(api_proxies, timeout=10).json()
                
                proxies_pais = [
                    p['proxy'] for p in resposta.get('proxies', []) 
                    if p.get('ip_data', {}).get('countryCode') == country_code.upper()
                ]
                
                RewardsCore.LOGGER(f"[DISCORD] Encontrados {len(proxies_pais)} proxies de {country_code.upper()}. Iniciando a varredura...")
                
                for proxy in proxies_pais[:15]:
                    RewardsCore.LOGGER(f"[DISCORD] A testar {proxy}...")
                    proxies_config = {
                        "http": proxy,
                        "https": proxy
                    }
                    try:
                        teste_ip = requests.get("https://api.ipify.org?format=json", proxies=proxies_config, timeout=5)
                        if teste_ip.status_code == 200:
                            ip_camuflado = teste_ip.json().get('ip')
                            RewardsCore.LOGGER("[DISCORD] -> 🟢 LIMPO E RÁPIDO!")
                            RewardsCore.LOGGER(f"[DISCORD] --- SUCESSO ABSOLUTO ---")
                            RewardsCore.LOGGER(f"[DISCORD] O site acha que o nosso IP é: {ip_camuflado}")
                            return proxy.replace('socks5://', '').replace('socks4://', '').replace('http://', '').replace('https://', '')
                    except requests.exceptions.SSLError:
                        RewardsCore.LOGGER("[DISCORD] -> 🔴 SUJO (Certificado Inválido). Saltando...")
                    except requests.exceptions.Timeout:
                        RewardsCore.LOGGER("[DISCORD] -> 🟡 LENTO (Timeout). Saltando...")
                    except requests.exceptions.RequestException:
                        RewardsCore.LOGGER("[DISCORD] -> ⚫ MORTO (Ligação Rejeitada). Saltando...")
                
                RewardsCore.LOGGER("[DISCORD] Nenhum proxy bom encontrado nos primeiros 15.")
            except Exception as e:
                RewardsCore.LOGGER(f"[DISCORD] Erro ao buscar/testar proxy {country_code}: {e}")
            return None

        fases = []
        if not region_batches:
            fases.append({"nome": "Lote Local (Nativo)", "usa_vpn": False, "ids": [], "proxy_host": ""})
        else:
            for region, ids in region_batches.items():
                if region == 'local' or not fazer_globais:
                    fases.append({"nome": f"Lote Local", "usa_vpn": False, "ids": ids, "proxy_host": ""})
                else:
                    RewardsCore.LOGGER(f"[DISCORD] Buscando Proxy SOCKS5 para a região {region.upper()}...")
                    proxy = obter_proxy_socks5_por_pais(region)
                    if proxy:
                        fases.append({
                            "nome": f"Lote Global ({region.upper()})", 
                            "usa_vpn": True, 
                            "ids": ids,
                            "proxy_host": proxy
                        })
                    else:
                        RewardsCore.LOGGER(f"[DISCORD] Nenhum proxy encontrado para {region.upper()}. Convertendo lote para Local.")
                        fases.append({"nome": f"Lote Local (Fallback {region.upper()})", "usa_vpn": False, "ids": ids, "proxy_host": ""})

        for i, fase in enumerate(fases):
            if RewardsCore.ABORTAR_PROCESSO: return
            RewardsCore.LOGGER(f"[DISCORD] >>> INICIANDO {fase['nome'].upper()} <<<")
            RewardsCore.update_ui("discord", fase["nome"], 20 + (i * 30))
            
            args_discord = [
                exe_path, f"--remote-debugging-port={PORTA_DEBUG}",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]

            if fase["usa_vpn"] and fase.get("proxy_host"):
                RewardsCore.LOGGER(f"[DISCORD] Injetando Proxy SOCKS5 Isolado: {fase['proxy_host']}")
                args_discord.append(f"--proxy-server=socks5://{fase['proxy_host']}")
                    
            modo_oculto = cfg.get("modo_oculto", "s") == "s"
            if modo_oculto: args_discord.append("--start-minimized")

            if platform.system().lower() == "windows": subprocess.run(f"taskkill /F /IM \"{exe_name}\" /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
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
                RewardsCore.LOGGER(f"[DISCORD] Aviso: Nao foi possivel injetar ignorar updates: {e}")

            processo = subprocess.Popen(args_discord, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # FASE 4: Workaround Headless (Limbo Renderização Fix)
            if modo_oculto:
                time.sleep(3)
                try: processo.kill()
                except: pass
                if platform.system().lower() == "windows": subprocess.run(f"taskkill /F /PID {processo.pid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)
                processo = subprocess.Popen(args_discord, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            porta_aberta = False
            for _ in range(60): 
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{PORTA_DEBUG}/json/version", timeout=2)
                    porta_aberta = True; break
                except: time.sleep(2)

            if not porta_aberta:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER("[DISCORD] ERRO: Timeout aguardando porta 9222. Fase ignorada.")
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
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER("[DISCORD] ERRO: Falha ao iniciar Selenium.")
                continue

            janela_correta = None
            for _ in range(25):  
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    for handle in driver.window_handles:
                        driver.switch_to.window(handle)
                        if any(x in driver.current_url.lower() for x in ["discord.com/app", "discord.com/channels", "discord.com/login"]):
                            janela_correta = handle; break
                    if janela_correta: break
                except: pass
                time.sleep(2)
                
            if not janela_correta:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER("[DISCORD] ERRO: Timeout ao tentar localizar a aba principal do Discord.")
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
            except: pass
                
            for _ in range(15):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
                    if driver.execute_script("return typeof window.webpackChunkdiscord_app !== 'undefined';"): break
                except: pass
                time.sleep(2)

            try:
                logado = driver.execute_script("return window.location.pathname !== '/login';")
                if not logado:
                    espera = 0
                    while espera < 300: 
                        if RewardsCore.ABORTAR_PROCESSO: return
                        try:
                            if driver.execute_script("return window.location.pathname !== '/login';"):
                                time.sleep(10); break
                        except: pass
                        time.sleep(5); espera += 5
                    else:
                        if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER("[DISCORD] ERRO: App ficou preso na tela de Login.")
                        continue
            except Exception:
                pass
                
            RewardsCore.update_ui("discord", "Sincronizando...", 50)
            
            for _ in range(3):
                if RewardsCore.ABORTAR_PROCESSO: return
                try:
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
                except: pass
                
                time.sleep(6) 
                if RewardsCore.ABORTAR_PROCESSO: return
                
                try:
                    if driver.execute_script("return window.location.pathname.includes('quest') || document.querySelector('[class*=\"questTile\"]') !== null;"): break
                except: pass
                
                try: driver.refresh()
                except: break
                time.sleep(5)

            if RewardsCore.ABORTAR_PROCESSO: return

            ids_globais = fase.get("ids", [])
            quests_webhook_url = cfg.get("quests_webhook_url", "")
            script_injetado = SCRIPT_JS.replace("INJECT_GLOBAL_IDS", json.dumps(ids_globais))
            script_injetado = script_injetado.replace('"INJECT_QUESTS_WEBHOOK"', json.dumps(quests_webhook_url))
            
            try: driver.execute_script(script_injetado)
            except Exception:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER("[DISCORD] ERRO ao injetar Webpack. O aplicativo crashou.")
                return
            
            RewardsCore.update_ui("discord", "Processando Tarefas...", 80)
            
            dummy_processes = []
            try:
                watchdog_timeout = 120 # FASE 4: 2 minutos inativo ao invés de 1 hora fixa
                last_active_time = time.time()
                
                while True:
                    if RewardsCore.ABORTAR_PROCESSO: return
                    
                    time.sleep(2) 
                    
                    try:
                        js_data = driver.execute_script("""
                            let res = { cmd: window.recompensas_cmd, logs: window.recompensas_logs || [] };
                            window.recompensas_cmd = null;
                            window.recompensas_logs = [];
                            return res;
                        """)
                        
                        if js_data and (js_data.get('logs') or js_data.get('cmd')):
                            last_active_time = time.time()
                            
                        if time.time() - last_active_time > watchdog_timeout:
                            RewardsCore.LOGGER("[DISCORD] AVISO: Watchdog de inatividade (2 min) estourou. Encerrando lote para evitar travamento infinito.", "warning")
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
                                        shutil.copy(r"C:\Windows\System32\ping.exe", fake_exe_path)
                                        dp = subprocess.Popen([fake_exe_path, "127.0.0.1", "-n", "3600"], creationflags=subprocess.CREATE_NO_WINDOW)
                                    else:
                                        shutil.copy(shutil.which("sleep") or "/bin/sleep", fake_exe_path)
                                        os.chmod(fake_exe_path, 0o755) 
                                        dp = subprocess.Popen([fake_exe_path, "3600"])

                                    dummy_processes.append((dp, fake_exe_path))
                                    driver.execute_script(f"window.novoPidCamuflado = {dp.pid};") 
                                    
                                elif "REWARDS_KILL:ALL" in cmd:
                                    for dp, path in dummy_processes:
                                        try: dp.kill()
                                        except: pass
                                        try: os.remove(path)
                                        except: pass
                                    dummy_processes.clear()
                    except: pass
                    
                    try:
                        if driver.execute_script("return window.discordQuestsDone === true;"): break
                    except: break
                    
            except Exception as e:
                if not RewardsCore.ABORTAR_PROCESSO: RewardsCore.LOGGER(d_msgs[lang]["loop_error"].format(str(e)[:100]))
                
            for dp, path in dummy_processes:
                try: dp.kill()
                except: pass
                try: os.remove(path)
                except: pass
                
            try:
                driver.execute_script("try { window.DiscordNative.app.quit(); } catch(e) {}")
                time.sleep(4); driver.quit() 
            except: pass
            
            # Morte isolada: matar APENAS o processo do Discord que iniciamos, preservando o Bing.
            try: processo.kill()
            except: pass
            if platform.system().lower() == "windows": subprocess.run(f"taskkill /F /PID {processo.pid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if i < len(fases) - 1: 
                for _ in range(7):
                    if RewardsCore.ABORTAR_PROCESSO: return
                    time.sleep(2)

        if not RewardsCore.ABORTAR_PROCESSO:
            RewardsCore.registrar_data_execucao("discord")
            RewardsCore.update_ui("discord", "Concluído!", 100)
            RewardsCore.LOGGER("[DISCORD] PROCESSO TOTAL FINALIZADO COM SUCESSO!")