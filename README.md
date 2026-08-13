# CoreNexusBot 
*Advanced Behavioral Evasion & Reward Exploitation Framework*

🌍 **Read in:** [English](#-english) | [Português](#-português)

---

## 🇺🇸 English

### 🎯 Project Overview
**CoreNexusBot** is an advanced, cross-platform automation framework designed to explore and bypass modern behavioral telemetry, anti-bot heuristics, and strict OS-level tracking. Rather than relying on simple DOM interactions, this tool exploits the predictability of security mechanisms by injecting high levels of human entropy into the navigation flow and hijacking internal application states.

The ultimate validation of this stealth architecture is its success rate: by perfectly mimicking organic queues and human pacing, the framework circumvents standard server-side limits, successfully scaling point extraction from the standard 480-point lock to the absolute 2100-point maximum cap without triggering shadowbans.

### 🛡️ Web Telemetry Evasion (Browser Spoofing)
Modern browsers leak a massive amount of fingerprinting data to track automation. This framework neutralizes these trackers at the core:
* **Fingerprint Masking & CDC Evasion:** Bypasses basic Selenium detection by stripping the `navigator.webdriver` flag, disabling WebAuthn APIs, and injecting synthetic hardware parameters (spoofing `hardwareConcurrency`, `deviceMemory`, and `maxTouchPoints`) before the DOM even loads.
* **Algorithmic Humanization:** Defeats cadence-tracking algorithms by implementing "Ghost Clicks" (ActionChains with randomized X/Y pixel offsets) and synthetic typing errors (deliberately typing wrong characters, pausing, backspacing, and correcting them in real-time).
* **Behavioral Entropy Queuing:** Drops static loops in favor of a dynamic state machine. It parses the server's backend limits in real-time and paces the interactions across different environments (PC/Mobile) interlaced with long "idleness" payloads, effectively tricking heuristic algorithms into assigning a high "human trust" score.

### 👾 Discord Quests Exploitation (OS Forging)
Recently, Discord implemented strict anti-bot measures for their Quests system, actively banning accounts that use raw HTTP API token spamming. They introduced active window focus telemetry (`visibilityState`) and native OS process validation to ensure a user is physically playing a game. 
**Our Bypass Architecture:**
* **Webpack Chunk Hijacking:** Instead of sending easily flaggable raw API requests, the bot injects a payload directly into the Discord Electron client. It extracts internal React/Webpack chunks (`webpackChunkdiscord_app`), hijacking the `FluxDispatcher`, `QuestsStore`, and `RunningGameStore` from the inside.
* **DOM Focus Spoofing (Plan B):** Discord checks if the user is actually watching the quest streams. The bot overwrites native Web APIs (`Document.prototype.hasFocus`, `visibilityState`) via `Object.defineProperty`, tricking the client into believing the tab is always visible and focused, even when minimized in the tray.
* **Phantom PID Injection:** To bypass native game tracking, the bot spawns a lightweight, dormant native process (`ping.exe` on Windows, `sleep` on Unix). It captures this authentic Process ID (PID) and forces it into Discord's internal state machine. The client authenticates the fake game via native OS checks, fulfilling the quest 100% headlessly with near-zero RAM footprint.
* **"Fat Timer" Obfuscation:** Prevents robotic exact-second task completions by applying randomized "stealth fat" (keeping the forged process alive for extra, unpredictable minutes after the quest is registered as complete).

### 🖥️ GUI & Core Features
Built with `pywebview` for a seamless front-end to back-end integration:
* **Real-time Console:** Monitor deep DOM injections, payload status, and proxy/4G tunneling directly from the UI.
* **Multi-Profile Sandboxing:** Isolated Chrome profiles preventing cross-contamination of cookies and session tokens.
* **Fail-Fast Defense:** Features proactive memory scraping to detect server-side suspension flags during execution. If a trap is triggered, it aborts instantly to protect proxy integrity.

> **Disclaimer:** This project is for educational and cybersecurity research purposes only. It is intended to study reverse engineering, automated web evasion, and OS integration. The author assumes no liability for account suspensions or TOS violations resulting from the use of this framework.

<br><br>

---

## 🇧🇷 Português

### 🎯 Visão Geral do Projeto
O **CoreNexusBot** é um framework avançado de automação multiplataforma projetado para explorar e contornar a telemetria comportamental moderna, heurísticas anti-bot e rastreamento a nível de Sistema Operacional. Em vez de depender de interações simples no DOM, esta ferramenta explora a previsibilidade dos mecanismos de segurança injetando altos níveis de entropia humana no fluxo e sequestrando estados internos de aplicativos.

A validação definitiva dessa arquitetura furtiva é a sua taxa de sucesso: ao mimetizar perfeitamente filas orgânicas e o ritmo humano, o framework burla as travas padrão do servidor, escalando a extração de pontos do bloqueio padrão de 480 para o teto máximo de 2100 pontos sem acionar *shadowbans*.

### 🛡️ Evasão de Telemetria Web (Browser Spoofing)
Navegadores modernos vazam uma quantidade massiva de dados de *fingerprint* para rastrear automações. Este framework neutraliza esses rastreadores na raiz:
* **Mascaramento de Fingerprint e Evasão CDC:** Bypassa a detecção básica do Selenium removendo a flag `navigator.webdriver`, desativando APIs de WebAuthn e injetando parâmetros sintéticos de hardware (forjando `hardwareConcurrency`, `deviceMemory` e `maxTouchPoints`) antes mesmo do carregamento do DOM.
* **Humanização Algorítmica:** Derrota algoritmos de rastreamento de cadência implementando "Ghost Clicks" (ActionChains com desvios aleatórios de pixels X/Y) e geração de erros de digitação sintéticos (digitando deliberadamente caracteres errados, pausando, apagando e corrigindo-os em tempo real).
* **Fila de Entropia Comportamental:** Substitui loops estáticos por uma máquina de estados dinâmica. O bot lê os limites do servidor em tempo real e divide as interações entre diferentes ambientes (PC/Mobile), intercaladas com *payloads* de ociosidade longa, enganando heurísticas de segurança para conquistar um alto "nível de confiança humano".

### 👾 Exploração do Discord Quests (OS Forging)
Recentemente, o Discord implementou medidas rigorosas anti-bot no sistema de Quests, banindo ativamente contas que usam spam de tokens via API HTTP bruta. Eles introduziram telemetria de foco de janela ativa (`visibilityState`) e validação nativa de processos no SO para garantir que o usuário esteja fisicamente jogando.
**Nossa Arquitetura de Bypass:**
* **Sequestro de Webpack Chunks:** Em vez de enviar requisições de API rastreáveis, o bot injeta um payload diretamente no cliente Electron do Discord. Ele extrai os *chunks* internos do React/Webpack (`webpackChunkdiscord_app`), sequestrando o `FluxDispatcher`, `QuestsStore` e `RunningGameStore` por dentro.
* **Mutação de Foco no DOM (Plano B):** O Discord verifica se o usuário está realmente assistindo às *streams* das missões. O bot sobrescreve APIs nativas da Web (`Document.prototype.hasFocus`, `visibilityState`) via `Object.defineProperty`, enganando o cliente para que acredite que a aba está sempre visível e em foco, mesmo minimizada na bandeja do sistema.
* **Injeção de PID Fantasma:** Para burlar o rastreamento nativo de jogos, o bot inicia um processo nativo leve e dormente (`ping.exe` no Windows, `sleep` no Unix). Ele captura esse Process ID (PID) autêntico e o força para dentro do motor de estados do Discord. O cliente autentica o jogo falso através de checagens do SO, concluindo a missão de forma 100% invisível (Headless) com consumo de RAM quase nulo.
* **Ofuscação "Fat Timer":** Evita conclusões de tarefas exatas (comportamento robótico) aplicando a "gordura stealth" (mantendo o processo forjado ativo por minutos extras e aleatórios após a missão ser registrada como concluída).

### 🖥️ Interface (GUI) e Recursos Essenciais
Construído com `pywebview` para integração fluida entre front-end e back-end:
* **Console em Tempo Real:** Monitore injeções profundas no DOM, status de payloads e túneis de Proxy/4G diretamente na interface.
* **Sandboxing de Múltiplos Perfis:** Perfis isolados do Chrome que impedem a contaminação cruzada de cookies e tokens de sessão.
* **Defesa Fail-Fast:** Possui varredura proativa na memória para detectar *flags* de suspensão do servidor durante a execução. Se uma armadilha for acionada, aborta instantaneamente para proteger o proxy.

> **Aviso Legal:** Este projeto tem fins puramente educacionais e de pesquisa em cibersegurança. Destina-se ao estudo de engenharia reversa, evasão web automatizada e integração com sistemas operacionais. O autor não se responsabiliza por suspensões de contas ou violações dos Termos de Serviço decorrentes do uso deste framework.
