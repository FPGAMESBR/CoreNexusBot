# CoreNexusBot 
*Cross-Platform Evasion Framework for Microsoft Rewards & Discord Quests*

🌍 **Read in:** [English](#-english) | [Português](#-português)

---

## 🇺🇸 English

### 🎯 Project Overview
**CoreNexusBot** is an advanced, cross-platform automation framework strictly focused on exploiting two specific environments: **Microsoft Rewards** (via heavily modified Google Chrome instances) and **Discord Quests** (via Electron remote debugging). 

Rather than relying on basic coordinate clicking, this tool studies and exploits the predictability of telemetry security mechanisms. It injects high levels of human entropy into the navigation flow and hijacks internal application states to operate 100% stealthily.

### 🌐 Microsoft Rewards (Chrome Telemetry Evasion)
Microsoft evaluates search quality and consistency through behavioral telemetry. Users demonstrating "robotic" behavior — such as firing simultaneous requests without pauses — are penalized in the monthly **Bing Star Bonus**, often getting stuck at baseline rewards (e.g., 480/2100 points). Our ultimate goal with CoreNexusBot is to bypass this heuristic lock and reach the absolute 2100-point organic cap by acting demonstrably human.
* **Bing Star Queuing (Beta):** Replaces static loops with a dynamic state machine. It paces interactions across PC and Mobile user agents, interlaced with 40+ minute "idleness" payloads, effectively tricking heuristic algorithms into assigning a high "human trust" score. *(Note: This entropy injection module is currently in testing to validate our stealth capabilities and can be toggled on/off in the settings).*
* **Fingerprint Masking:** Utilizes `undetected-chromedriver` to strip the `navigator.webdriver` flag, disabling WebAuthn APIs, and injecting synthetic hardware parameters before the DOM loads.
* **Algorithmic Humanization:** Defeats cadence-tracking algorithms by implementing "Ghost Clicks" (ActionChains with randomized X/Y pixel offsets), synthetic typing errors (deliberately typing wrong characters, pausing, backspacing, and correcting them), and erratic scrolling.
* **Aggressive DOM Manipulation:** Bypasses UI traps by scanning deep DOM elements for incomplete tasks and using JavaScript Promises to force visual searches and ad clicks even when the visual interface lags.

### 👾 Discord Quests Exploitation (Webpack State Spoofing)
Discord Quest completion is fully automated via script injection, bypassing the need to actually download or play the required games. 
* **Webpack Chunk Hijacking:** The bot injects a payload directly into the Discord Electron client via Chrome DevTools Protocol. It extracts internal React/Webpack chunks (`webpackChunkdiscord_app`), hijacking the `FluxDispatcher` and `RunningGameStore` to broadcast forged `RUNNING_GAMES_CHANGE` events.
* **Proactive PID Forging (Countermeasure):** While the spoofing is handled purely via script, the bot implements an advanced countermeasure against potential deep-client heuristics. It spawns a dormant, native OS process (`ping.exe` on Windows, `sleep` on Unix) just to harvest an authentic Process ID (PID). This real PID is injected into Discord’s fake game payload, creating a bulletproof, verifiable state in memory should Discord decide to cross-reference active tasks with the OS process tree in the future.
* **DOM Focus Spoofing:** Overwrites native Web APIs (`Document.prototype.hasFocus`, `visibilityState`) tricking the client into believing the streaming tab is always visible and focused.

### 🚨 Error Handling, Crash Logs & Reporting
The bot features a **Fail-Fast Defense Mechanism** to protect proxy integrity and account standing. If a suspension flag (shadowban) is detected in the HTML during execution, the bot immediately aborts.
* **Crash Logs:** If a fatal exception occurs (e.g., unexpected DOM changes, complete network failure), the bot generates a detailed `CRASH_LOG_YYYY-MM-DD.txt` file in the root directory containing the full stack trace.
* **Discord Webhook SOS:** Critical errors and successful completion stamps can be broadcasted directly to a personal Discord channel via Webhook.
* **Bug Reporting:** If you encounter repetitive logic loops or unhandled exceptions, please open an **Issue** on GitHub. Include the `CRASH_LOG` file and a brief description of what triggered the failure.

> **Disclaimer:** This project is for educational and cybersecurity research purposes only. It is intended to study reverse engineering, automated web evasion, and OS integration. The author assumes no liability for account suspensions or TOS violations resulting from the use of this framework.

<br><br>

---

## 🇧🇷 Português

### 🎯 Visão Geral do Projeto
O **CoreNexusBot** é um framework avançado de automação multiplataforma estritamente focado em explorar dois ambientes específicos: **Microsoft Rewards** (via instâncias profundamente modificadas do Google Chrome) e **Discord Quests** (via depuração remota do Electron).

Em vez de depender de cliques básicos por coordenadas, esta ferramenta estuda e explora a previsibilidade dos mecanismos de telemetria de segurança. Ela injeta altos níveis de entropia humana no fluxo de navegação e sequestra estados internos de aplicativos para operar de forma 100% furtiva.

### 🌐 Microsoft Rewards (Evasão de Telemetria no Chrome)
A Microsoft avalia a qualidade e a consistência das pesquisas por meio de telemetria comportamental. Usuários que demonstram comportamento "robótico" — como o disparo de requisições ininterruptas sem pausas — são penalizados no **Bônus Bing Star**, muitas vezes ficando travados na pontuação base (ex: 480/2100 pontos). A nossa meta atual com o CoreNexusBot é contornar essa trava heurística e buscar o teto orgânico máximo de 2100 pontos agindo de forma comprovadamente humana.
* **Fila do Bônus Bing Star (Beta):** Substitui loops estáticos por uma máquina de estados dinâmica. Ele cadencia as interações entre *user-agents* de PC e Mobile, intercaladas com *payloads* de ociosidade de 40+ minutos. *(Nota: Este módulo focado no bônus encontra-se atualmente em fase de testes para validar a nossa furtividade, podendo ser ativado ou desativado livremente no painel de configurações).*
* **Mascaramento de Fingerprint:** Utiliza o `undetected-chromedriver` para remover a flag `navigator.webdriver`, desativar APIs WebAuthn e injetar parâmetros sintéticos de hardware antes do carregamento do DOM.
* **Humanização Algorítmica:** Derrota algoritmos de rastreamento de cadência implementando "Ghost Clicks" (ActionChains com desvios aleatórios de pixels X/Y), erros sintéticos de digitação (digitando caracteres errados, pausando, apagando e corrigindo) e rolagens de tela erráticas.
* **Manipulação Agressiva de DOM:** Contorna armadilhas de interface (UI) escaneando elementos profundos do DOM em busca de tarefas incompletas e utilizando *Promises* em JavaScript para forçar o envio de pesquisas visuais e propagandas, mesmo quando a renderização da página trava.

### 👾 Exploração do Discord Quests (Spoofing de Webpack)
A conclusão das missões do Discord é totalmente automatizada via injeção de script, eliminando a necessidade de baixar ou jogar os jogos exigidos.
* **Sequestro de Chunks do Webpack:** O bot injeta um payload diretamente no cliente Electron do Discord via protocolo DevTools. Ele extrai blocos internos do React/Webpack (`webpackChunkdiscord_app`), sequestrando o `FluxDispatcher` e o `RunningGameStore` para transmitir eventos forjados de `RUNNING_GAMES_CHANGE`.
* **Forja Proativa de PID (Contramedida):** Embora a falsificação do jogo seja tratada puramente via script, o bot implementa uma contramedida avançada contra possíveis heurísticas profundas do cliente. Ele inicia um processo dormente nativo no SO (`ping.exe` no Windows, `sleep` no Unix) apenas para colher um Process ID (PID) autêntico. Esse PID real é injetado no payload do jogo falso dentro do Discord, criando um estado verificável na memória, prevenindo detecções caso o Discord decida, no futuro, cruzar os dados da tarefa ativa com a árvore de processos do sistema operacional.
* **Spoofing de Foco no DOM:** Sobrescreve APIs nativas da Web (`Document.prototype.hasFocus`, `visibilityState`), enganando o cliente para que acredite que a aba da *stream* está sempre visível e focada.

### 🚨 Tratamento de Erros, Crash Logs e Reportes
O bot possui um **Mecanismo de Defesa Fail-Fast** para proteger a integridade do proxy e a saúde da conta. Se uma *flag* de suspensão (banimento) for detectada no HTML durante a execução, o bot aborta imediatamente.
* **Crash Logs:** Se ocorrer uma exceção fatal (ex: mudanças inesperadas no DOM do Bing, falha de rede), o bot gera um arquivo detalhado `CRASH_LOG_YYYY-MM-DD.txt` no diretório raiz contendo o rastreamento completo do erro (*stack trace*).
* **Discord Webhook SOS:** Erros críticos e carimbos de conclusão bem-sucedida podem ser transmitidos diretamente para o seu canal privado no Discord via Webhook.
* **Reporte de Bugs:** Se você encontrar *loops* lógicos repetitivos ou exceções não tratadas, por favor, abra uma **Issue** no GitHub. Anexe o arquivo `CRASH_LOG` e uma breve descrição do que acionou a falha.

> **Aviso Legal:** Este projeto tem fins puramente educacionais e de pesquisa em cibersegurança. Destina-se ao estudo de engenharia reversa, evasão web automatizada e integração com sistemas operacionais. O autor não se responsabiliza por suspensões de contas ou violações dos Termos de Serviço decorrentes do uso deste framework.
