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

#### 🌐 Microsoft Rewards & Organic Search Engine
Microsoft evaluates search quality and consistency through behavioral patterns. CoreNexusBot keeps daily activity organic so you can reach the full **Bing Star Bonus** (2,100/2,100 points) in **Normal** mode without needing extra slowdowns.

* **Bing Star Engine (Smart Coffee Mode):** Paces searches across PC and Mobile sessions split by an organic Coffee Mode break. If **50% or more** of the daily searches are already completed at session start (for example, resuming an interrupted morning run at night), Coffee Mode is automatically skipped.
* **Daily Execution Lock:** Prevents duplicate same-day Bing runs on both manual launch and Windows Startup (stored in `Exe.json`), while preserving retry ability if a run is stopped or fails mid-way.
* **Speed Profiles:**
  * **Normal:** Recommended default. Balanced organic pacing, subtle typos, and Smart Coffee Mode.
  * **Turbo:** Skips organic delays and Coffee Mode for maximum speed (Higher Risk).
* **Dynamic Search Topics:** Fetches fresh queries from Google Trends (RSS) and random Wikipedia articles so search sessions stay varied.
* **Browser Profile Isolation:** Persists dedicated Chrome profiles (`RewardsProfiles`) and hardware fingerprints per account.

#### 👾 Discord Quests Automation
* **Native Video Player UI:** Video quests are watched directly through Discord's real `<video>` UI modal (`Assistir` / `Continuar`) with DevTools focus emulation — zero forged `/video-progress` API calls.
* **Strict Quests Navigation & DM Safety:** Navigates strictly to `/quest-home` (avoiding `/message-requests`) and protects the Direct Messages sidebar from accidental close clicks.
* **Automatic Startup Retry:** If Discord Canary/PTB hangs during startup or updates, the launcher cleanly terminates, re-resolves the latest app directory, and retries up to 3 times.
* **Global Quests & SOCKS5 Proxying:** Supports region-targeted batches via SOCKS5 proxies and isolated session cloning.
* **Client Support:** Officially supports **Discord Canary** and **Discord PTB**.

### ⚙️ Configuration Guide (AppGUI Features)
The AppGUI provides several toggles and settings. Here is how to use them:
* **PC & Mobile Limits:** Sets how many organic searches the bot will perform. (Set to 0 if you only want to do Quests or Dashboard tasks).
* **Headless Mode:** Runs the browser invisibly in the background.
* **Dashboard Tasks:** Solves the Daily Set and Extra Activity cards (including the Bing Visual Search streak).
* **Speed Mode:**
  * `Normal`: Balanced organic pacing with Smart Coffee Mode (auto-skipped at ≥ 50% initial progress).
  * `Turbo`: Fast mode, skips organic delays and Coffee Mode.
* **Discord Global Quests:** Enables region batches for global quests. **Note:** If you enable this, provide both a `Quests Webhook URL` and a `Trash Channel URL` in Settings.
* **Discord Webhook:** Sends status reports, crash logs, and quest notifications.

### 🛠️ Error Handling & Troubleshooting
If you encounter issues while running the bot, check these common fixes:

* **Bot isn't starting the Chrome browser:** 
  - Ensure you have closed all active instances of Google Chrome before starting the bot.
  - If the profile is corrupted, close the bot, go to the folder where the bot is installed, and delete the `RewardsProfiles` folder.
* **Discord Quests are missing/failing:** 
  - Ensure you have installed [Discord Canary](https://canary.discord.com/) or [Discord PTB](https://ptb.discord.com/). Stable Discord is unsupported due to remote debugging limitations.
* **Crash Logs (`crash_YYYY-MM-DD_HH-MM-SS.txt`):** 
  - If a fatal exception occurs, the bot automatically writes a detailed crash log inside the `logs/` directory containing the full stack trace. Please include this file when reporting bugs.

> **Disclaimer:** This project is for educational and automation research purposes only. The author assumes no liability for account restrictions or terms of service violations.

<br><br>

---

## 🇧🇷 Português

### 🎯 Visão Geral do Projeto
O **CoreNexusBot** é um framework avançado de automação multiplataforma focado em explorar dois ambientes principais: **Microsoft Rewards** (via Google Chrome customizado) e **Discord Quests** (via depuração remota do Electron).

Em vez de depender de cliques básicos ou coordenadas, esta ferramenta explora a previsibilidade dos mecanismos de telemetria da Microsoft e do Discord. Ela injeta altos níveis de entropia humana no fluxo de navegação e sequestra o estado interno das aplicações para operar de forma 100% furtiva.

### ✨ Funcionalidades Principais

#### 🖥️ Interface Gráfica Moderna (AppGUI)
O bot abandonou o terminal feio e antiquado. Agora roda numa interface rica e responsiva via **PyWebView**.
- **Painel de Controle:** Ajuste limites de pesquisa, ligue/desligue o modo invisível (Headless), troque o idioma e configure Webhooks com apenas um clique.
- **Consola em Tempo Real:** Acompanhe a "Mente" do bot a trabalhar numa consola visual embutida.
- **Modo Fantasma (System Tray):** Opção de iniciar automaticamente com o Windows de forma silenciosa. O bot fica escondido na bandeja do sistema a trabalhar sem o incomodar!

#### 🌐 Microsoft Rewards (Motor Orgânico Bing Star)
A Microsoft avalia a consistência das pesquisas ao longo do mês. O CoreNexusBot mantém uma cadência orgânica que permite atingir o máximo do **Bônus Bing Star** (2.100/2.100 pontos) diretamente no modo **Normal**, sem precisar de travas extras.

* **Bing Star Engine (Modo Café Inteligente):** Divide as pesquisas entre PC e Mobile com uma pausa orgânica no meio (Modo Café). Se **50% ou mais** das pesquisas do dia já estiverem concluídas ao iniciar (ex.: iniciou de manhã, pausou e retomou à noite), o Modo Café é pulado automaticamente.
* **Trava Diária Automática:** Impede reexecução duplicada do Bing no mesmo dia tanto no botão manual quanto no Startup do Windows (`Exe.json`), preservando a retomada caso uma execução seja interrompida ou falhe antes de terminar.
* **Perfis de Velocidade:**
  * **Normal:** Padrão recomendado. Ritmo orgânico balanceado, erros leves de digitação e Modo Café Inteligente.
  * **Turbo:** Velocidade máxima, pulando pausas longas e Modo Café (maior risco).
* **Pesquisas Orgânicas Dinâmicas:** Usa tópicos atualizados do Google Trends (RSS) e artigos aleatórios da Wikipedia.
* **Isolamento de Perfis:** Mantém perfis dedicados do Chrome (`RewardsProfiles`) e fingerprint consistente por conta.

#### 👾 Automação do Discord Quests
* **Player Nativo Real para Vídeos:** As missões de vídeo são assistidas diretamente pelo player `<video>` oficial da interface (`Assistir` / `Continuar`) com emulação de foco via DevTools — sem chamadas diretas forjadas à API `/video-progress`.
* **Navegação Estrita e Proteção das DMs:** Abre exclusivamente a aba `/quest-home` (sem cair em `Solicitações de mensagens`) e bloqueia cliques de fechamento dentro da barra lateral de Mensagens Diretas.
* **Retentativa Automática na Abertura:** Se o Discord Canary/PTB travar na splash screen ou durante uma atualização, o bot encerra o processo limpo, relocaliza o binário atualizado e tenta novamente até 3 vezes.
* **Quests Globais via SOCKS5:** Suporta lotes globais por região usando proxies SOCKS5 isolados.
* **Suporte Oficial:** **Discord Canary** e **Discord PTB**.

### ⚙️ Guia de Configurações (AppGUI)
O painel de controle possui as seguintes opções principais:
* **Limites PC & Mobile:** Define quantas pesquisas orgânicas o bot fará (coloque `0` para pular pesquisas e rodar apenas tarefas ou Discord).
* **Modo Headless:** Roda o navegador de forma invisível em segundo plano.
* **Tarefas do Dashboard:** Resolve o Conjunto Diário e atividades extras (incluindo a série de Pesquisa Visual do Bing).
* **Modos de Velocidade:**
  * `Normal`: Balanceado e orgânico, com Modo Café Inteligente (pulado automaticamente quando ≥ 50% já foi concluído).
  * `Turbo`: Rápido, ignora pausas longas e Modo Café.
* **Missões Globais do Discord (SOCKS5):** Ativa lotes de Quests por região. **Atenção:** se ativar, preencha o `Webhook de Quests` e o `Canal de Descarte (URL)` nas configurações.
* **Sistema de Webhook:** Envia relatórios de conclusão, alertas de erro/crash e notificações de Quests.

### 🛠️ Solução de Problemas (Troubleshooting)
Se encontrar erros ao rodar o bot, verifique estas soluções comuns:

* **O bot não inicia o Chrome:** 
  - Certifique-se de que fechou todas as instâncias do Google Chrome antes de iniciar o bot.
  - Se o perfil corromper, feche o bot, apague a pasta `RewardsProfiles` e ele criará uma limpa na próxima execução.
* **As Missões do Discord não aparecem ou falham:** 
  - Verifique se instalou o [Discord Canary](https://canary.discord.com/) ou o [Discord PTB](https://ptb.discord.com/). A versão Stable não é suportada por limitações do debug remoto.
* **Crash Logs (`crash_YYYY-MM-DD_HH-MM-SS.txt`):** 
  - Caso ocorra um erro fatal, o bot grava automaticamente o rastreamento completo dentro da pasta `logs/`. Anexe esse arquivo ao reportar um problema.

> **Aviso Legal:** Este projeto tem fins educacionais e de estudo de automação. O autor não se responsabiliza por eventuais restrições de conta decorrentes do uso.