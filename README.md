# Reward Bot - Stealth Architecture

Uma ferramenta avançada de automação multiplataforma desenvolvida para o gerenciamento de tarefas do Microsoft Rewards e Discord Quests. 

## 🎯 O Intuito do Projeto
O objetivo central deste software **não** é a simples repetição de cliques, mas sim a **evasão de telemetria comportamental**. O bot utiliza uma arquitetura baseada no novo motor *Bing Star Engine* para simular padrões de navegação puramente humanos — incluindo erros de digitação, rolagem de tela para leitura, desvio de mira (ghost clicks) e pausas ociosas prolongadas. 

A finalidade é mitigar detecções baseadas em algoritmos (*shadowbans*) e realizar a coleta de pontos e quests diárias de forma 100% autônoma, silenciosa e segura.

---

## ⚙️ Arquitetura e Motores Internos
* **Bing Star Engine (Máquina de Estados):** Substitui limites fixos de pesquisas por uma leitura real do servidor da Microsoft, dividindo a carga organicamente entre PC e Mobile, intercalada por uma "pausa do café" de 40+ minutos para garantir pontos bônus de consistência.
* **Rotina Dinâmica de Pesquisa Visual:** Acionamento do scanner via injeção JavaScript direta no DOM, utilizando sementes randômicas da API *Picsum Photos* para garantir imagens únicas a cada execução.
* **Discord OS Forging:** Motor de camuflagem que simula a presença de executáveis de jogos utilizando processos fantasmas do sistema (`ping.exe` no Windows ou `sleep` no Unix), forjando o rastreamento do Discord Quests com o mínimo de consumo de RAM.
* **Defesa Fail-Fast:** Varredura proativa no aquecimento dos perfis. Caso uma conta seja sinalizada como suspensa, o bot aborta o farm instantaneamente para proteger o IP/Proxy e evitar o desperdício de banda.

---

## 🖥️ Funções da Interface Gráfica (GUI)
A interface foi construída em *AppGUI* (via `pywebview`), garantindo uma aplicação Desktop fluida e unificada com o back-end em Python. 

**Recursos disponíveis no painel:**
* **Terminal Integrado (Console):** Monitoramento em tempo real dos logs de sistema, injeções JS e 4G/Proxy diretamente na UI.
* **Gerenciador de Múltiplos Perfis (Accounts):** Criação, setup guiado, transição e exclusão de contas isoladas via *Chrome Profiles*.
* **Limits & Timers:**
  * Configuração independente de cotas de pesquisa (PC e Mobile).
  * Controle de *Cooldown* para o Discord (evita suspeitas ao espaçar o farm de missões em *X* dias).
* **Behavior & System (Switches):**
  * **Hide Browser (Headless):** Roda o navegador em segundo plano sem interface gráfica.
  * **Do Dashboard Tasks:** Resolve cartões diários, missões extras e tarefas interativas.
  * **Enable Bing Star Bonus (Beta):** Liga o motor furtivo avançado, ignorando os limites manuais e assumindo o controle orgânico do fluxo de pesquisa.
  * **Auto-Farm Discord Quests:** Habilita o módulo nativo do aplicativo do Discord para resolução de *Stream* e *Play* quests.
  * **OS Startup (Boot nativo):** Permite anexar ou remover o bot da inicialização do Windows/Linux/macOS com 1 clique, rodando o bot invisível assim que a máquina liga.
* **Discord Webhook:** Envio de alertas de *Crash* (S.O.S com stack trace) e relatórios de sucesso de farm diretamente para o seu celular.

---

## ⚠️ Aviso Legal e Termos de Uso
Este projeto tem fins **puramente educacionais**, voltado ao estudo de engenharia reversa de telemetria, automação web (Selenium/JavaScript) e integração de sistemas operacionais.

O uso prolongado deste software ou configurações excessivamente agressivas podem violar os Termos de Serviço da Microsoft e do Discord. O autor **não se responsabiliza** por bloqueios, suspensões ou banimentos de contas decorrentes do uso desta ferramenta. Use por sua própria conta e risco.
