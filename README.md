<div align="center">
  <div style="display:flex; justify-content:center; gap:20px; margin-bottom:15px;">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Banner"/>
    <img src="https://img.shields.io/badge/Microsoft_Rewards-00A4EF?style=for-the-badge&logo=microsoft&logoColor=white" alt="Bing Rewards Banner"/>
  </div>
  <h1>CoreNexusBot</h1>
  <p><strong>Advanced Cross-Platform Evasion Framework for Microsoft Rewards & Discord Quests</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg)]()
</div>

<br>

🌍 **Read in:** [English](#-english) | [Português](#-português)

---

## 🇺🇸 English

### 🎯 Project Overview
**CoreNexusBot** is an advanced, cross-platform automation framework strictly focused on exploiting two specific environments: **Microsoft Rewards** (via heavily modified Google Chrome instances) and **Discord Quests** (via Electron remote debugging).

Rather than relying on basic coordinate clicking, this tool studies and exploits the predictability of telemetry security mechanisms. It injects high levels of human entropy into the navigation flow and hijacks internal application states to operate 100% stealthily.

### ✨ Key Features

#### 🖥️ Modern Web-UI (AppGUI)
The bot no longer relies on a primitive terminal. It spins up a beautiful, responsive **PyWebView-based Graphic Interface**. 
- **Configuration Dashboard:** Tweak search limits, toggle headless modes, switch languages, and manage Webhooks seamlessly.
- **Real-Time Console:** Watch the bot's inner workings through an animated matrix-like console within the app.
- **System Tray Integration (Ghost Mode):** You can set the bot to run at Windows Startup entirely in the background. It will silently dock into your System Tray without interrupting your work.

#### 🌐 Microsoft Rewards & Telemetry Evasion
Microsoft evaluates search quality and consistency through behavioral telemetry. Users demonstrating "robotic" behavior are penalized, often getting stuck in a mid-tier analysis window (e.g., 1800/2100 points). CoreNexusBot bypasses this heuristic lock by acting demonstrably human.

* **Bing Star Engine (Chrono-Gating):** Replaces static loops with a dynamic state machine. It paces interactions across PC and Mobile user agents, interlaced with 40+ minute "Coffee Mode" payloads, effectively tricking heuristic algorithms.
* **Speed Profiles:** Choose how you want the bot to behave:
  * **Stealth:** Paranoia-level simulation. Adds ghost searches and long delays.
  * **Normal:** Simulates an average user with organic typos and standard reading delays.
  * **Turbo:** Skips humanization protocols for blazing-fast points (High Ban Risk).
* **Ultra-Organic Searches:** Powered by a live database fetching real-time queries from Google Trends (RSS) and random Wikipedia articles, diversifying search patterns automatically.
* **Fingerprint Masking:** Utilizes `undetected-chromedriver` to strip the `navigator.webdriver` flag and injects synthetic hardware parameters before the DOM loads.

#### 👾 Discord Quests Exploitation (Webpack State Spoofing)
Discord Quest completion is fully automated via script injection, bypassing the need to actually download or play the required games.
* **Native Background Bypass:** Intercepts Page Visibility APIs (`Document.prototype.hasFocus`, `visibilityState`). The client believes the streaming tab is always focused.
* **Global Quests & VPN Proxying:** The bot fetches free VPN/SOCKS5 IPs and injects them into the session, allowing you to complete exclusive quests from other continents without using Tor!
* **Webpack Chunk Hijacking:** Extracts internal React chunks (`webpackChunkdiscord_app`), hijacking the `FluxDispatcher` to broadcast forged `RUNNING_GAMES_CHANGE` events.
* **Client Support:** Fully supports **Discord Canary** and **Discord PTB** clients.

### ⚙️ Configuration Guide (AppGUI Features)
The AppGUI provides several toggles and settings. Here is how to use them:
* **PC & Mobile Limits:** Sets how many organic searches the bot will perform. (Set to 0 if you only want to do Quests).
* **Headless Mode:** Runs the Chromium browser completely invisibly in the background.
* **Dashboard Tasks:** If enabled, the bot will solve the Daily Set and Extra Activity cards (including the Visual Search mission).
* **Speed Mode:** 
  * `Turbo`: Fast, ignores human pauses. 
  * `Normal`: Balanced with typos and delays. 
  * `Stealth`: Paranoia mode with extreme delays.
* **Discord Global Quests:** Enables spoofing regions for exclusive quests. **Note:** If you enable this, you *must* provide both a `Webhook URL` and a `Trash Channel URL` in the advanced settings to receive the quest links.
* **Discord Webhook:** The bot uses this to send critical updates:
  * ✅ Success reports when a farm finishes.
  * 🚨 SOS Crash logs and suspension warnings.
  * 🎮 Discord Quest cards and progress updates.

### 🛠️ Error Handling & Troubleshooting
If you encounter issues while running the bot, check these common fixes:

* **Bot isn't starting the Chrome browser:** 
  - Ensure you have closed all active instances of Google Chrome before starting the bot.
  - If the profile is corrupted, close the bot, go to the folder where the bot is installed, and delete the `RewardsProfiles` folder.
* **Discord Quests are missing/failing:** 
  - Ensure you have installed [Discord Canary](https://canary.discord.com/) or [Discord PTB](https://ptb.discord.com/). Stable Discord is deliberately unsupported due to API limitations.
* **Crash Logs (`CRASH_LOG_YYYY-MM-DD.txt`):** 
  - The bot features a **Fail-Fast Defense Mechanism**. If a fatal exception occurs (e.g., unexpected DOM changes), the bot automatically generates a detailed crash log file in the root directory containing the full stack trace. Please include this file when reporting bugs!

> **Disclaimer:** This project is for educational and cybersecurity research purposes only. It is intended to study reverse engineering, automated web evasion, and OS integration. The author assumes no liability for account suspensions or TOS violations.

<br><br>

---

## 🇧🇷 Português

### 🎯 Visão Geral do Projeto
O **CoreNexusBot** é um framework avançado de automação multiplataforma focado em explorar dois ambientes principais: **Microsoft Rewards** (via Google Chrome customizado) e **Discord Quests** (via depuração remota do Electron).

Em vez de depender de cliques básicos ou coordenadas, esta ferramenta explora a previsibilidade dos mecanismos de telemetria da Microsoft e do Discord. Ela injeta altos níveis de entropia humana no fluxo de navegação e sequestra o estado interno das aplicações para operar de forma 100% furtiva.

### ✨ Funcionalidades Principais

#### 🖥️ Interface Gráfica Moderna (AppGUI)
O bot abandonou o terminal feio e antiquado. Agora roda numa interface rica e responsiva via **PyWebView**.
- **Painel de Controlo:** Ajuste limites de pesquisa, ligue/desligue o modo invisível (Headless), troque o idioma e configure Webhooks com apenas um clique.
- **Consola em Tempo Real:** Acompanhe a "Mente" do bot a trabalhar numa consola visual embutida.
- **Modo Fantasma (System Tray):** Opção de iniciar automaticamente com o Windows de forma silenciosa. O bot fica escondido na bandeja do sistema a trabalhar sem o incomodar!

#### 🌐 Microsoft Rewards (Evasão de Telemetria no Chrome)
A Microsoft avalia a consistência das pesquisas por meio de telemetria comportamental. Contas "robóticas" ficam travadas na janela média da métrica atual (ex: 1800/2100 pontos). A meta do CoreNexusBot é furar este bloqueio e atingir o limite máximo orgânico.

* **Bing Star Engine (Chrono-Gating):** Cadencia as interações entre PC e Mobile, intercaladas com o famoso "Modo Café" (pausas longas de 40+ minutos para simular rotina).
* **Perfis de Velocidade:**
  * **Stealth (Furtivo):** Simulação paranóica. Passa longos períodos lendo links e adiciona pesquisas fantasmas falsas.
  * **Normal:** Simula um utilizador comum. Comete erros de digitação leves e tem pausas orgânicas padrão.
  * **Turbo:** Velocidade insana ignorando medidas de segurança (Menos Organico, mas rapido).
* **Pesquisas Ultra-Orgânicas:** Usa uma base de dados dinâmica que puxa tópicos reais do Google Trends (RSS) e Wikipedia.
* **Mascaramento de Fingerprint:** Remove a flag `navigator.webdriver` e injeta parâmetros de hardware sintéticos usando `undetected-chromedriver` blindado.

#### 👾 Exploração do Discord Quests (Spoofing de Webpack)
A conclusão das missões do Discord é totalmente automatizada via injeção de JavaScript, sem necessidade de baixar ou jogar nada!
* **Bypass Nativo em Background:** Engana as APIs de visibilidade (`Document.prototype.hasFocus`). O Discord pensa que você está a ver o ecrã do jogo mesmo quando está minimizado.
* **Quests Globais via VPN (SOCKS5):** O bot não usa o Tor! Em vez disso, ele puxa e injeta IPs de VPNs e Proxies SOCKS5 gratuitos de forma dinâmica, permitindo que resgate Missões do Discord exclusivas de outros continentes.
* **Sequestro de Chunks do Webpack:** Extrai blocos internos do React (`webpackChunkdiscord_app`), sequestrando o `FluxDispatcher` para forçar o Discord a reconhecer um jogo fantasma.
* **Suporte Restrito:** Suporta oficialmente apenas o **Discord Canary** e **Discord PTB**.

### ⚙️ Guia de Configurações (AppGUI)
O painel de controlo possui várias opções. Veja o que cada uma faz:
* **Limites PC & Mobile:** Define quantas pesquisas orgânicas o bot fará (Coloque 0 para ignorar pesquisas e fazer só o painel).
* **Modo Headless:** Roda o navegador de forma totalmente invisível para não incomodar.
* **Tarefas do Dashboard:** O bot resolve o Conjunto Diário e as atividades extras (incluindo a Pesquisa Visual).
* **Modos de Velocidade:** 
  * `Turbo`: Muito rápido, ignora pausas longas.
  * `Normal`: Balanceado, com erros de digitação.
  * `Stealth`: Extremo, com imensas pausas e atividades falsas.
* **Missões Globais do Discord (SOCKS5):** Ativa a rotação de IP para Quests gringas. **Atenção:** Se ativar isto, é OBRIGATÓRIO preencher o `Webhook URL` e o `Canal de Lixo (URL)` nas configurações avançadas, para o bot poder enviar-lhe os convites/cards das missões.
* **Sistema de Webhook:** O bot usa o seu Webhook do Discord para enviar:
  * ✅ Relatórios de sucesso quando a conta termina o farm.
  * 🚨 Alertas de suspensão de conta e Crash Logs.
  * 🎮 Cards dinâmicos das missões do Discord e progresso global.

### 🛠️ Solução de Problemas (Troubleshooting)
Se encontrar erros ao rodar o bot, verifique estas soluções comuns:

* **O bot não inicia o Chrome:** 
  - Certifique-se de que fechou todas as instâncias do Google Chrome antes de iniciar o bot.
  - Se o perfil corromper, feche o bot, apague a pasta `RewardsProfiles` e ele criará uma limpa no próximo arranque.
* **As Missões do Discord não aparecem ou falham:** 
  - Verifique se instalou o [Discord Canary](https://canary.discord.com/) ou o [Discord PTB](https://ptb.discord.com/). A versão normal (Stable) não é suportada por limitações da API de debug remoto.
* **Uso dos Crash Logs (`CRASH_LOG_YYYY-MM-DD.txt`):** 
  - O bot possui um **Mecanismo Fail-Fast**. Se ocorrer um erro crítico estrutural, o bot aborta imediatamente e gera um ficheiro de Crash Log contendo o rastreamento do erro. **Sempre** anexe este ficheiro se for reportar um erro!

> **Aviso Legal:** Este projeto tem fins puramente educacionais e de pesquisa em cibersegurança. O autor não se responsabiliza por suspensões de contas decorrentes do uso inadequado deste framework.