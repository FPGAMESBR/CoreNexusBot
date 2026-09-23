# CoreNexusBot 
*Cross-Platform Evasion Framework for Microsoft Rewards & Discord Quests*

🌍 **Read in:** [English](#-english) | [Português](#-português)

---

## 🇺🇸 English

### 🎯 Project Overview
**CoreNexusBot** is an advanced, cross-platform automation framework strictly focused on exploiting two specific environments: **Microsoft Rewards** (via heavily modified Google Chrome instances) and **Discord Quests** (via Electron remote debugging). 

Rather than relying on basic coordinate clicking, this tool studies and exploits the predictability of telemetry security mechanisms. It injects high levels of human entropy into the navigation flow and hijacks internal application states to operate 100% stealthily.

### 🌐 Microsoft Rewards (Chrome Telemetry Evasion)
Microsoft evaluates search quality and consistency through behavioral telemetry. Users demonstrating "robotic" behavior are penalized in the **Bing Star Bonus**, often getting stuck at baseline rewards or flagged in the mid-tier analysis window (e.g., 1200/2100 points). Our ultimate goal with CoreNexusBot is to bypass this heuristic lock and reach the absolute 2100-point organic cap by acting demonstrably human.
* **Bing Star Queuing:** Replaces static loops with a dynamic state machine. It paces interactions across PC and Mobile user agents, interlaced with 40+ minute "idleness" payloads, effectively tricking heuristic algorithms into assigning a high "human trust" score.
* **Smart Start & Execution:** Skips the "Cafe Mode" organic pause if only dashboard tasks are required and searches are disabled, launching straight into action.
* **Ultra-Organic Searches:** Powered by a live database fetching real-time queries from Google Trends (RSS) and random Wikipedia articles, diversifying search patterns automatically.
* **Fingerprint Masking:** Utilizes `undetected-chromedriver` to strip the `navigator.webdriver` flag, disabling WebAuthn APIs, and injecting synthetic hardware parameters before the DOM loads.
* **Algorithmic Humanization:** Defeats cadence-tracking algorithms by implementing "Ghost Clicks", synthetic typing errors (deliberately typing wrong characters, pausing, backspacing, and correcting them), and erratic scrolling.

### 👾 Discord Quests Exploitation (Webpack State Spoofing)
Discord Quest completion is fully automated via script injection, bypassing the need to actually download or play the required games. 
* **Native Discord Bypass:** Runs 100% in the background. The bot intercepts Page Visibility APIs (`Document.prototype.hasFocus`, `visibilityState` and `hidden`), tricking the client into believing the streaming tab is always visible and focused, preventing the quest timer from pausing when you click away.
* **Webpack Chunk Hijacking:** Extracts internal React/Webpack chunks (`webpackChunkdiscord_app`), hijacking the `FluxDispatcher` and `RunningGameStore` to broadcast forged `RUNNING_GAMES_CHANGE` events.
* **Parallel Execution Engine:** Bing and Discord modules run concurrently. You no longer need to wait for one task to finish to start the other, heavily optimizing your farming speed.

### 🛠️ Troubleshooting & Support
If you encounter issues while running the bot, check these common fixes before opening an issue on GitHub:
* **Bot isn't starting the Chrome browser:** 
  - Ensure you have closed all active instances of Google Chrome before starting the bot.
  - If the profile is corrupted, close the bot, go to the folder where the bot is installed, and delete the `RewardsProfiles` folder. The bot will automatically create a fresh, clean profile on the next run.
* **Discord Quests are stuck at 0%:** 
  - Check if you are logged into Discord via your standard DiscordCanary/PTB program.
* **Crash Logs (`CRASH_LOG_YYYY-MM-DD.txt`):** 
  - The bot features a **Fail-Fast Defense Mechanism** to protect proxy integrity and account standing. If a fatal exception occurs (e.g., unexpected DOM changes, complete network failure), the bot generates a detailed crash log file in the root directory containing the full stack trace. Please include this file when reporting bugs.

### 🚨 Fail-Fast & Reporting
* **Crash Logs:** Generates detailed `CRASH_LOG_YYYY-MM-DD.txt` on fatal exceptions.
* **Discord Webhook SOS:** Critical errors and successful completion stamps can be broadcasted directly to a personal Discord channel via Webhook.

> **Disclaimer:** This project is for educational and cybersecurity research purposes only. It is intended to study reverse engineering, automated web evasion, and OS integration. The author assumes no liability for account suspensions or TOS violations resulting from the use of this framework.

<br><br>

---

## 🇧🇷 Português

### 🎯 Visão Geral do Projeto
O **CoreNexusBot** é um framework avançado de automação multiplataforma focado em explorar dois ambientes: **Microsoft Rewards** e **Discord Quests**.

Em vez de depender de cliques básicos, esta ferramenta explora a previsibilidade dos mecanismos de telemetria. Ela injeta altos níveis de entropia humana no fluxo de navegação e sequestra estados internos dos aplicativos para operar de forma 100% furtiva.

### 🌐 Microsoft Rewards (Evasão de Telemetria no Chrome)
A Microsoft avalia a consistência das pesquisas por meio de telemetria comportamental. Usuários que demonstram comportamento "robótico" são penalizados no **Bônus Bing Star**, muitas vezes caindo no filtro de análise e ficando travados na janela média (ex: 1200/2100 pontos). A meta do CoreNexusBot é contornar essa trava heurística e buscar o teto orgânico máximo de 2100 pontos agindo de forma comprovadamente humana.
* **Fila do Bônus Bing Star:** Cadencia as interações entre PC e Mobile, intercaladas com o "Modo Café" (pausas de 40+ minutos).
* **Smart Start & Execução Inteligente:** O bot ignora o Modo Café e vai direto ao ponto se você não estiver rodando pesquisas (ex: apenas tarefas do painel).
* **Pesquisas Ultra-Orgânicas:** Alimentado por uma base de dados dinâmica que puxa tópicos reais do Google Trends (RSS) e artigos aleatórios da Wikipedia, diversificando os padrões de busca automaticamente.
* **Mascaramento de Fingerprint:** Remove a flag `navigator.webdriver` e injeta parâmetros sintéticos de hardware antes do carregamento do DOM usando `undetected-chromedriver`.
* **Humanização Algorítmica:** Derrota algoritmos de cadência com "Ghost Clicks", erros sintéticos de digitação (digitando, pausando, apagando e corrigindo) e rolagens erráticas.

### 👾 Exploração do Discord Quests (Spoofing de Webpack)
A conclusão das missões do Discord é totalmente automatizada via injeção de script.
* **Bypass Nativo do Discord:** Roda 100% em background. O bot intercepta as APIs de visibilidade (`Document.prototype.hasFocus`, `visibilityState` e `hidden`), enganando o cliente para que acredite que a aba está sempre visível e focada, impedindo que o contador da missão pause quando você minimiza ou muda de janela.
* **Sequestro de Chunks do Webpack:** Extrai blocos internos do React (`webpackChunkdiscord_app`), sequestrando o `FluxDispatcher` para transmitir eventos forjados de jogos.
* **Motor de Execução Paralela:** Bing e Discord agora rodam simultaneamente. Você não precisa mais esperar um bot terminar para iniciar o outro, otimizando muito o seu tempo de farm.

### 🛠️ Solução de Problemas (Troubleshooting)
Se você encontrar erros ao rodar o bot, verifique estas soluções comuns antes de abrir uma Issue no GitHub:
* **Bot não inicia o navegador Chrome:** 
  - Certifique-se de fechar todas as instâncias e abas do Google Chrome antes de dar "Run" no bot.
  - Se o seu perfil de usuário corrompeu, feche o bot, vá até a pasta onde ele está instalado e apague a pasta `RewardsProfiles`. O bot criará um perfil totalmente novo, limpo e sem erros na próxima vez que você abri-lo.
* **Missões do Discord travadas em 0%:** 
  - Verifique se você está logado no Discord através do seu Programa DiscordCanary/PTB padrão.
* **Uso dos Crash Logs (`CRASH_LOG_YYYY-MM-DD.txt`):** 
  - O bot possui um **Mecanismo de Defesa Fail-Fast**. Se ocorrer um erro crítico ou uma exceção não tratada (ex: Microsoft mudou a página de recompensas do nada, ou sua internet caiu), o bot desliga sozinho e gera um arquivo de Crash Log contendo todas as linhas e causas do erro. Sempre anexe esse arquivo quando for reportar um erro no GitHub.

### 🚨 Tratamento de Erros e Logs
* **Crash Logs:** Gera arquivos `CRASH_LOG_YYYY-MM-DD.txt` em caso de falhas fatais ou mudanças imprevistas no DOM.
* **Discord Webhook SOS:** Envia logs de sucesso e erros críticos direto para o seu servidor do Discord via Webhook.

> **Aviso Legal:** Este projeto tem fins puramente educacionais e de pesquisa em cibersegurança. O autor não se responsabiliza por suspensões de contas decorrentes do uso deste framework.