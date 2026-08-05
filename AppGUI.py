import webview
import threading
import socket
import os
import platform
import subprocess
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

import RewardsCore 
import DiscordQuests

APP_NAME = "Reward Bot"
APP_VERSION = "v2.1"
APP_CODENAME = "Stealth Architecture"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        :root { 
            --bg-dark: #070b14; 
            --bg-panel: #111827; 
            --text-main: #f1f5f9; 
            --text-muted: #64748b;
            --accent-blue: #0ea5e9; 
            --accent-hover: #0284c7;
            --accent-red: #ef4444; 
            --accent-yellow: #f59e0b;
            --accent-green: #10b981;
            --border-color: #1e293b;
        }

        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

        body { 
            background-color: var(--bg-dark); 
            color: var(--text-main); 
            margin: 0; overflow: hidden; height: 100vh;
        }

        /* =========================================
           CUSTOM TITLEBAR (Transparente e Invisível)
        ========================================= */
        .titlebar {
            height: 32px; display: flex; justify-content: space-between;
            position: absolute; top: 0; width: 100%; z-index: 10000;
            background: transparent;
        }
        .titlebar-drag {
            flex-grow: 1; display: flex; align-items: center; 
            padding-left: 15px; font-size: 11px; color: var(--text-muted); font-weight: bold; letter-spacing: 1px;
            cursor: move;
        }
        /* Classe Mágica do PyWebview para arrastar */
        .pywebview-drag-region { -webkit-app-region: drag; }
        .titlebar-controls { display: flex; -webkit-app-region: no-drag; z-index: 10001; }
        .titlebar-btn {
            width: 46px; height: 100%; background: transparent; border: none; color: var(--text-muted);
            cursor: pointer; transition: 0.2s; font-size: 14px; display: flex; justify-content: center; align-items: center;
        }
        .titlebar-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
        .titlebar-btn.close:hover { background: #e81123; color: #fff; }

        /* =========================================
           BACKGROUND PATTERN (Matrix/Rain)
        ========================================= */
        .rain-bg { position: absolute; inset: 0; z-index: 0; opacity: 0.12; pointer-events: none; overflow: hidden; }
        .rain-bg::before {
            content: ""; position: absolute; inset: -145%; rotate: -45deg; background: transparent;
            background-image: radial-gradient(4px 100px at 0px 235px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 235px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 117.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 252px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 252px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 126px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 150px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 150px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 75px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 253px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 253px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 126.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 204px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 204px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 102px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 134px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 134px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 67px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 179px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 179px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 89.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 299px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 299px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 149.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 215px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 215px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 107.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 281px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 281px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 140.5px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 158px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 158px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 79px, var(--accent-blue) 100%, #0000 150%), radial-gradient(4px 100px at 0px 210px, var(--accent-blue), #0000), radial-gradient(4px 100px at 300px 210px, var(--accent-blue), #0000), radial-gradient(1.5px 1.5px at 150px 105px, var(--accent-blue) 100%, #0000 150%);
            background-size: 300px 235px, 300px 235px, 300px 235px, 300px 252px, 300px 252px, 300px 252px, 300px 150px, 300px 150px, 300px 150px, 300px 253px, 300px 253px, 300px 253px, 300px 204px, 300px 204px, 300px 204px, 300px 134px, 300px 134px, 300px 134px, 300px 179px, 300px 179px, 300px 179px, 300px 299px, 300px 299px, 300px 299px, 300px 215px, 300px 215px, 300px 215px, 300px 281px, 300px 281px, 300px 281px, 300px 158px, 300px 158px, 300px 158px, 300px 210px, 300px 210px, 300px 210px;
            animation: hi 150s linear infinite;
        }
        @keyframes hi {
            0% { background-position: 0px 220px, 3px 220px, 151.5px 337.5px, 25px 24px, 28px 24px, 176.5px 150px, 50px 16px, 53px 16px, 201.5px 91px, 75px 224px, 78px 224px, 226.5px 350.5px, 100px 19px, 103px 19px, 251.5px 121px, 125px 120px, 128px 120px, 276.5px 187px, 150px 31px, 153px 31px, 301.5px 120.5px, 175px 235px, 178px 235px, 326.5px 384.5px, 200px 121px, 203px 121px, 351.5px 228.5px, 225px 224px, 228px 224px, 376.5px 364.5px, 250px 26px, 253px 26px, 401.5px 105px, 275px 75px, 278px 75px, 426.5px 180px; }
            to { background-position: 0px 6800px, 3px 6800px, 151.5px 6917.5px, 25px 13632px, 28px 13632px, 176.5px 13758px, 50px 5416px, 53px 5416px, 201.5px 5491px, 75px 17175px, 78px 17175px, 226.5px 17301.5px, 100px 5119px, 103px 5119px, 251.5px 5221px, 125px 8428px, 128px 8428px, 276.5px 8495px, 150px 9876px, 153px 9876px, 301.5px 9965.5px, 175px 13391px, 178px 13391px, 326.5px 13540.5px, 200px 14741px, 203px 14741px, 351.5px 14848.5px, 225px 18770px, 228px 18770px, 376.5px 18910.5px, 250px 5082px, 253px 5082px, 401.5px 5161px, 275px 6375px, 278px 6375px, 426.5px 6480px; }
        }

        /* =========================================
           TELA DE LOADING (BLACK HOLE ISOLADO)
        ========================================= */
        #loader-wrapper {
            position: fixed; inset: 0; background-color: var(--bg-dark); z-index: 9999;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            animation: fadeOut 1s ease 6s forwards;
        }
        @keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
        
        .loader-box { position: relative; width: 350px; height: 350px; display: flex; align-items: center; justify-content: center; }
        .loader-graphics { position: absolute; animation: shrinkHole 6s cubic-bezier(0.25, 1, 0.5, 1) forwards; display: flex; align-items: center; justify-content: center; }
        @keyframes shrinkHole { 0% { transform: scale(1); } 70% { transform: scale(0.6); } 100% { transform: scale(0); } }
        
        .ring-3 { box-shadow: 0px 0px 10px 15px rgba(14, 165, 233, 0.3); border-radius: 50%; padding: 2px; }
        .ring-2 { box-shadow: 0px 0px 2px 10px #000; border-radius: 50%; padding: 2px; }
        .ring-1 { box-shadow: 0px 0px 10px 15px rgba(14, 165, 233, 0.5); border-radius: 50%; padding: 2px; }
        .black-hole { height: 128px; aspect-ratio: 1; background-color: black; border-radius: 50%; box-shadow: 0px 0px 20px 10px #000, inset 0px 0px 10px rgba(14, 165, 233, 0.5); }
        .glow { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 350px; height: 350px; background: radial-gradient(circle, rgba(14, 165, 233, 0.2) 5%, rgba(14, 165, 233, 0.05) 20%, transparent 70%); border-radius: 50%; z-index: -1; }
        .container-svg { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotateX(75deg); }
        .crescent { position: absolute; top: 50%; left: 50%; transform: rotate(180deg); width: 200px; height: 12px; opacity: 0; filter: drop-shadow(0px 0px 5px var(--accent-blue)) drop-shadow(0px 0px 15px var(--accent-blue)); clip-path: ellipse(60% 100% at 100% 50%); offset-path: path("M 0,-100 A 100,100 0 1,1 0,100 A 100,100 0 1,1 0,-100 Z"); }
        .crescent-1 { animation: moveOval 500ms ease-in-out 0ms infinite; } .crescent-2 { animation: moveOval 500ms ease-in-out 83ms infinite; } .crescent-3 { animation: moveOval 500ms ease-in-out 167ms infinite; } .crescent-4 { animation: moveOval 500ms ease-in-out 250ms infinite; } .crescent-5 { animation: moveOval 500ms ease-in-out 333ms infinite; } .crescent-6 { animation: moveOval 500ms ease-in-out 417ms infinite; }
        
        .loading-text { position: absolute; bottom: 25%; color: var(--accent-blue); font-weight: bold; letter-spacing: 3px; font-size: 0.9em; text-transform: uppercase; }

        /* =========================================
           APP PRINCIPAL E LAYOUT
        ========================================= */
        #app-content { display: flex; height: 100vh; padding-top: 32px; opacity: 0; animation: fadeInApp 1s ease 6s forwards; box-sizing: border-box; }
        @keyframes fadeInApp { to { opacity: 1; } }

        /* SIDEBAR */
        .sidebar {
            width: 240px; background-color: var(--bg-panel); border-right: 1px solid var(--border-color);
            display: flex; flex-direction: column; padding: 20px 15px; z-index: 10; position: relative;
        }
        .brand-container { text-align: center; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
        .brand-name { font-size: 1.3em; font-weight: 800; color: #fff; display: block; margin-bottom: 5px; }
        .brand-version { background: rgba(14, 165, 233, 0.15); color: var(--accent-blue); padding: 2px 8px; border-radius: 4px; font-size: 0.7em; font-weight: bold; border: 1px solid rgba(14, 165, 233, 0.3); }
        .brand-subtitle { font-size: 0.65em; color: var(--text-muted); text-transform: uppercase; letter-spacing: 2px; margin-top: 8px; display: block;}

        .nav-menu { display: flex; flex-direction: column; gap: 8px; flex-grow: 1; margin-bottom: 10px; }
        .nav-item {
            flex: 1; overflow: hidden; cursor: pointer; border-radius: 6px;
            transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
            background: var(--bg-dark); border: 1px solid var(--border-color);
            display: flex; justify-content: center; align-items: center;
        }
        .nav-item:hover, .nav-item.active { flex: 4; border-color: var(--accent-blue); box-shadow: inset 0 0 10px rgba(14, 165, 233, 0.15); }
        .nav-item span {
            transition: all 0.5s; color: var(--text-muted); letter-spacing: 0.15em; font-weight: bold; text-transform: uppercase; font-size: 0.9em;
        }
        .nav-item:hover span, .nav-item.active span { color: var(--accent-blue); }

        .sidebar-bottom { border-top: 1px solid var(--border-color); padding-top: 15px; }
        .diag-header { font-size: 0.75em; color: var(--text-muted); text-transform: uppercase; font-weight: bold; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .mini-diag-item { display: flex; justify-content: space-between; background: transparent; padding: 10px 12px; border-radius: 8px; font-size: 0.75em; border: 1px solid var(--border-color); margin-bottom: 8px; align-items: center; }

        /* AREA DE CONTEUDO E CHUVA (MATRIX) */
        .main-content {
            flex-grow: 1; display: flex; flex-direction: column; padding: 25px 35px; overflow: hidden;
            background: radial-gradient(circle at top right, rgba(15, 23, 42, 0.8), var(--bg-dark));
            position: relative;
        }
        .content-layer { position: relative; z-index: 1; display: flex; flex-direction: column; height: 100%; }
        
        .header-controls { display: flex; gap: 15px; margin-bottom: 20px; flex-shrink: 0; }
        
        /* BOTOES STYLISH CUSTOMIZADOS */
        .btn-stylish {
            padding: 1em 2em; border: none; border-radius: 5px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; cursor: pointer; color: var(--accent-blue); transition: all 500ms; font-size: 14px; position: relative; overflow: hidden; outline: 2px solid var(--accent-blue); background: rgba(14, 165, 233, 0.05); flex-grow: 1;
        }
        .btn-stylish:hover { color: #ffffff; outline: 2px solid #70bdca; box-shadow: 4px 5px 17px -4px rgba(14, 165, 233, 0.6); }
        .btn-stylish::before { content: ""; position: absolute; left: -50px; top: 0; width: 0; height: 100%; background-color: var(--accent-blue); transform: skewX(45deg); z-index: -1; transition: width 500ms; }
        .btn-stylish:hover::before { width: 250%; }

        .btn-stylish.stop { color: var(--accent-red); outline: 2px solid var(--accent-red); background: rgba(239, 68, 68, 0.05); }
        .btn-stylish.stop:hover { color: #ffffff; outline: 2px solid #f87171; box-shadow: 4px 5px 17px -4px rgba(239, 68, 68, 0.6); }
        .btn-stylish.stop::before { background-color: var(--accent-red); }

        .tab-content { display: none; animation: fadeIn 0.3s forwards; height: 100%; overflow-y: auto; padding-right: 5px; }
        .tab-content.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        /* FIX DO CONSOLE SCROLL */
        #console.active { display: flex; flex-direction: column; overflow: hidden; }
        
        /* CARD DE ATUALIZAÇÃO (GITHUB) */
        .update-card {
            flex-shrink: 0; background: linear-gradient(145deg, var(--bg-panel), rgba(14, 165, 233, 0.05));
            border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 20px;
            display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .update-content h3 { margin: 0 0 8px 0; color: #fff; }
        .update-content p { margin: 0; font-size: 0.85em; color: var(--text-muted); line-height: 1.6; }
        .github-btn {
            display: flex; align-items: center; gap: 8px; background: #fff; color: #000; text-decoration: none;
            padding: 8px 16px; border-radius: 6px; font-weight: bold; font-size: 0.85em; transition: 0.2s;
        }
        .github-btn:hover { background: #e2e8f0; transform: scale(1.05); }

        /* TERMINAL DE LOGS */
        #terminal-log { 
            background: rgba(3, 7, 18, 0.9); padding: 20px; flex-grow: 1; border-radius: 12px; height: 100%;
            overflow-y: auto; border: 1px solid var(--border-color); font-family: 'Consolas', monospace;
            font-size: 0.9em; line-height: 1.5; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }
        .log-info { color: var(--accent-blue); }
        .log-success { color: var(--accent-green); }
        .log-warning { color: var(--accent-yellow); }
        .log-error { color: var(--accent-red); }

        /* SETTINGS GRID E COMPONENTES */
        .settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding-bottom: 30px; }
        .card { background-color: rgba(17, 24, 39, 0.95); border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; }
        .card h3 { margin-top: 0; margin-bottom: 20px; font-size: 1.05em; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 10px;}
        
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 0.85em; color: var(--text-muted); font-weight: 500;}
        .form-group input[type="text"] { width: 100%; padding: 10px 12px; background-color: var(--bg-dark); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 6px; outline: none; transition: 0.2s; }
        .form-group input[type="text"]:focus { border-color: var(--accent-blue); }

        /* NUMBER INPUT CUSTOMIZADO (FULL WIDTH) */
        .custom-number-wrapper { display: flex; align-items: center; width: 100%; background: var(--bg-dark); border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }
        .custom-number-wrapper button { background: rgba(255,255,255,0.05); color: var(--text-main); border: none; padding: 12px 0; width: 50px; flex-shrink: 0; cursor: pointer; transition: 0.2s; font-size: 1.2em; font-weight: bold;}
        .custom-number-wrapper button:hover { background: rgba(255,255,255,0.1); }
        .custom-number-wrapper input { flex-grow: 1; background: transparent; border: none; color: var(--text-main); text-align: center; font-size: 0.9em; outline: none; -moz-appearance: textfield; font-weight: bold;}
        .custom-number-wrapper input::-webkit-outer-spin-button, .custom-number-wrapper input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }

        .switch-group { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.02); padding-bottom: 10px;}
        .switch-group label { font-size: 0.85em; color: var(--text-main); }
        .switch { position: relative; display: inline-block; width: 44px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--border-color); transition: .4s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: var(--text-muted); transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: rgba(14, 165, 233, 0.2); border: 1px solid var(--accent-blue); }
        input:checked + .slider:before { transform: translateX(20px); background-color: var(--accent-blue); }

        .btn-save { background: var(--accent-blue); color: #000; border: none; padding: 12px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; margin-top: 15px;}
        .btn-save:hover { background: var(--accent-hover); box-shadow: 0 0 12px rgba(14, 165, 233, 0.4); color: #fff;}
        
        /* BOTAO STARTUP SEPARADO COM CLASSES CLEAN */
        .btn-startup { padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; border: 1px solid transparent; transition: 0.2s; }
        .btn-startup.startup-on { color: var(--accent-green); background: rgba(16, 185, 129, 0.1); border-color: var(--accent-green); }
        .btn-startup.startup-on:hover { background: rgba(16, 185, 129, 0.2); }
        .btn-startup.startup-off { color: var(--accent-red); background: rgba(239, 68, 68, 0.1); border-color: var(--accent-red); }
        .btn-startup.startup-off:hover { background: rgba(239, 68, 68, 0.2); }

        .account-pill { display: inline-flex; align-items: center; background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 20px; margin-right: 10px; margin-bottom: 10px; overflow: hidden; transition: 0.2s; }
        .account-pill:hover { border-color: var(--accent-blue); box-shadow: 0 0 10px rgba(14, 165, 233, 0.3); }
        .account-name { background: transparent; color: var(--accent-blue); border: none; padding: 8px 12px 8px 16px; font-size: 0.9em; font-weight: bold; cursor: pointer; }
        .account-name:hover { color: white; }
        .account-delete { background: rgba(239, 68, 68, 0.1); color: var(--accent-red); border: none; border-left: 1px solid rgba(14, 165, 233, 0.3); padding: 8px 12px; cursor: pointer; transition: 0.2s; }
        .account-delete:hover { background: var(--accent-red); color: white; }
    </style>
</head>
<body>

    <!-- CUSTOM TITLEBAR TRANSPARENTE E ARRASTÁVEL -->
    <div class="titlebar">
        <div class="titlebar-drag pywebview-drag-region"></div>
        <div class="titlebar-controls">
            <button class="titlebar-btn" onclick="pywebview.api.minimizar_janela()">—</button>
            <button class="titlebar-btn close" onclick="pywebview.api.fechar_janela()">✕</button>
        </div>
    </div>

    <!-- LOADER ANIMADO -->
    <div id="loader-wrapper">
        <div class="loader-box">
            <div class="loader-graphics">
                <div class="ring-3"><div class="ring-2"><div class="ring-1">
                    <div class="black-hole"></div><div class="glow"></div>
                </div></div></div>
                <div class="container-svg">
                    <svg class="crescent crescent-1" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                    <svg class="crescent crescent-2" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                    <svg class="crescent crescent-3" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                    <svg class="crescent crescent-4" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                    <svg class="crescent crescent-5" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                    <svg class="crescent crescent-6" viewBox="0 0 50 50"><path d="M 0 0 C 54 50 185 57 226 0 C 198 39 35 32 0 0" fill="#ffffff55"></path></svg>
                </div>
            </div>
        </div>
        <div class="loading-text">Sincronizando Sistema...</div>
    </div>

    <!-- APP PRINCIPAL -->
    <div id="app-content">
        <div class="sidebar">
            <div class="brand-container pywebview-drag-region">
                <span class="brand-name">[APP_NAME] <span class="brand-version">[APP_VERSION]</span></span>
                <span class="brand-subtitle">[APP_CODENAME]</span>
            </div>
            
            <div class="nav-menu">
                <div class="nav-item active" onclick="switchTab('console', this)"><span>Console</span></div>
                <div class="nav-item" onclick="switchTab('accounts', this); atualizarContasUI();"><span>Accounts</span></div>
                <div class="nav-item" onclick="switchTab('settings', this); pywebview.api.carregar_configuracoes_ui();"><span>Settings</span></div>
            </div>
            
            <div class="sidebar-bottom">
                <div class="diag-header">System Status
                    <svg style="width: 14px; cursor: pointer; transition: 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-muted)'" onclick="pywebview.api.rodar_diagnostico_ui()" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
                </div>
                <div id="sidebar-diagnostics">
                    <div class="mini-diag-item" style="justify-content: center; color: var(--text-muted);">Scanning...</div>
                </div>
            </div>
        </div>

        <div class="main-content">
            <!-- CHUVA MATRIX AQUI: Isolada perfeitamente no Main -->
            <div class="rain-bg"></div>

            <div class="content-layer">
                <div class="header-controls">
                    <button class="btn-stylish" onclick="pywebview.api.iniciar()">▶ Run Now</button>
                    <button class="btn-stylish stop" onclick="pywebview.api.parar()">■ Stop Safely</button>
                </div>
                
                <!-- ABA CONSOLE -->
                <div id="console" class="tab-content active">
                    <div class="update-card">
                        <div class="update-content">
                            <h3 id="update-title">O que há de novo na [APP_VERSION]</h3>
                            <p>
                               <span id="update-1">✨ Interface 'Stealth' reformulada com animações dinâmicas.</span><br>
                               <span id="update-2">⚙️ Novo Motor Bing Star Engine.</span><br>
                               <span id="update-3">🔥 Rotina Dinâmica de Pesquisa Visual.</span>
                            </p>
                        </div>
                        <a href="https://github.com/FPGAMESBR/RewardBot" target="_blank" class="github-btn">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57C20.565 21.795 24 17.31 24 12c0-6.63-5.37-12-12-12z"/></svg>
                            <span id="btn-github-text">Ver no GitHub</span>
                        </a>
                    </div>

                    <div id="terminal-log">
                        <span class="log-info">> [APP_NAME] [APP_VERSION] - Engine Connected.</span><br>
                    </div>
                </div>

                <!-- ABA CONTAS -->
                <div id="accounts" class="tab-content">
                    <div class="card" style="margin-bottom: 20px;">
                        <h3>Active Profiles</h3>
                        <div id="account-list" style="margin-bottom: 10px;"><span class="text-muted">Loading profiles...</span></div>
                    </div>
                    <div class="card">
                        <h3>Add New Account</h3>
                        <div class="form-group"><input type="text" id="new-account-name" placeholder="e.g. Account02"></div>
                        <button class="btn-save" onclick="adicionarConta()">+ Launch Setup Browser</button>
                    </div>
                </div>

                <!-- ABA SETTINGS -->
                <div id="settings" class="tab-content">
                    <div class="settings-grid">
                        <div class="card">
                            <h3>Limits & Timers</h3>
                            <div class="form-group">
                                <label>PC Queries</label>
                                <div class="custom-number-wrapper">
                                    <button onclick="changeVal('cfg-pc', -1)">-</button>
                                    <input type="number" id="cfg-pc" value="0">
                                    <button onclick="changeVal('cfg-pc', 1)">+</button>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Mobile Queries</label>
                                <div class="custom-number-wrapper">
                                    <button onclick="changeVal('cfg-mob', -1)">-</button>
                                    <input type="number" id="cfg-mob" value="0">
                                    <button onclick="changeVal('cfg-mob', 1)">+</button>
                                </div>
                            </div>
                            <div class="form-group">
                                <label id="label-cooldown">Discord Cooldown (Days)</label>
                                <div class="custom-number-wrapper">
                                    <button onclick="changeVal('cfg-discord-cooldown', -1)">-</button>
                                    <input type="number" id="cfg-discord-cooldown" value="3">
                                    <button onclick="changeVal('cfg-discord-cooldown', 1)">+</button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>Behavior & System</h3>
                            
                            <div class="switch-group">
                                <label>Hide Browser (Headless)</label>
                                <label class="switch"><input type="checkbox" id="cfg-headless"><span class="slider"></span></label>
                            </div>
                            <div class="switch-group">
                                <label>Do Dashboard Tasks (MS Rewards)</label>
                                <label class="switch"><input type="checkbox" id="cfg-tasks"><span class="slider"></span></label>
                            </div>
                            <!-- NOVO SWITCH: BÔNUS BING STAR -->
                            <div class="switch-group">
                                <label id="label-star-bonus">Enable Bing Star Bonus (Beta)</label>
                                <label class="switch"><input type="checkbox" id="cfg-star-bonus"><span class="slider"></span></label>
                            </div>
                            <div class="switch-group">
                                <label>Auto-Farm Discord Quests</label>
                                <label class="switch"><input type="checkbox" id="cfg-discord"><span class="slider"></span></label>
                            </div>
                            <div class="switch-group" style="border:none;">
                                <label>Enable Multi-Account Profile System</label>
                                <label class="switch"><input type="checkbox" id="cfg-multi"><span class="slider"></span></label>
                            </div>
                        </div>
                        
                        <div class="card" style="grid-column: span 2;">
                            <h3>Integrations & Automation</h3>
                            <div class="form-group" style="margin-bottom: 25px;">
                                <label>Discord Webhook URL (Leave empty to disable)</label>
                                <input type="text" id="cfg-webhook" placeholder="https://discord.com/api/webhooks/...">
                            </div>
                            
                            <h3 style="border-top: 1px solid var(--border-color); padding-top: 20px;">Startup Control</h3>
                            <p style="font-size: 0.85em; color: var(--text-muted); margin-bottom: 15px;">Toggle invisible boot with OS.</p>
                            
                            <!-- Botao Startup com Classes Limpas -->
                            <button id="btn-startup" class="btn-startup startup-off" onclick="pywebview.api.toggle_startup()">OS STARTUP: CHECKING...</button>
                            
                            <button class="btn-save" style="margin-top: 30px;" onclick="salvarConfigUI()">Save All Settings</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const TRANSLATIONS = {
            "en": {
                title: "What's new in [APP_VERSION]",
                item1: "✨ Redesigned 'Stealth' interface with dynamic animations.",
                item2: "⚙️ New Bing Star Engine.",
                item3: "🔥 Dynamic Visual Search Routine.",
                btnGit: "View on GitHub",
                on: "OS STARTUP (ON)",
                off: "OS STARTUP (OFF)",
                cooldownLabel: "Discord Cooldown (Days)",
                starBonusLabel: "Enable Bing Star Bonus (Beta)"
            },
            "pt": {
                title: "O que há de novo na [APP_VERSION]",
                item1: "✨ Interface 'Stealth' reformulada com animações dinâmicas.",
                item2: "⚙️ Novo Motor Bing Star Engine.",
                item3: "🔥 Rotina Dinâmica de Pesquisa Visual.",
                btnGit: "Ver no GitHub",
                on: "OS STARTUP (ON)",
                off: "OS STARTUP (OFF)",
                cooldownLabel: "Discord Cooldown (Dias)",
                starBonusLabel: "Ativar Bônus Bing Star (Beta)"
            }
        };
        let currentLang = "pt";

        setTimeout(() => {
            const loader = document.getElementById('loader-wrapper');
            if(loader) { loader.style.display = 'none'; loader.remove(); }
        }, 7000);

        function log(texto, tipo='info') {
            let logDiv = document.getElementById('terminal-log');
            let txtFormatado = texto.replace(/\\n/g, "<br>");
            logDiv.innerHTML += `<span class="log-${tipo}">> ${txtFormatado}</span><br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function switchTab(tabId, btnElement) {
            document.querySelectorAll('.tab-content').forEach(t => {
                t.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            btnElement.classList.add('active');
        }

        function changeVal(id, step) {
            let el = document.getElementById(id);
            let val = parseInt(el.value) || 0;
            let newVal = val + step;
            if(newVal < 0) newVal = 0;
            el.value = newVal;
        }

        async function atualizarContasUI() {
            let contas = await pywebview.api.listar_contas();
            let html = "";
            contas.forEach(c => { 
                if (c === "DefaultAccount") {
                    html += `<div class="account-pill"><button class="account-name" style="padding-right: 16px;" onclick="abrirConta('${c}')" title="Master Account">${c} ⭐</button></div>`; 
                } else {
                    html += `<div class="account-pill"><button class="account-name" onclick="abrirConta('${c}')">${c}</button><button class="account-delete" onclick="deletarConta('${c}')">🗑️</button></div>`; 
                }
            });
            document.getElementById('account-list').innerHTML = html;
        }

        function abrirConta(nome) { pywebview.api.abrir_setup_conta(nome); switchTab('console', document.querySelectorAll('.nav-item')[0]); }

        async function deletarConta(nome) {
            if(confirm(`Are you sure you want to delete '${nome}'?`)) {
                await pywebview.api.deletar_conta(nome);
                atualizarContasUI();
                pywebview.api.rodar_diagnostico_ui();
            }
        }

        function adicionarConta() {
            let nome = document.getElementById('new-account-name').value.trim();
            if (nome) { abrirConta(nome); document.getElementById('new-account-name').value = ''; }
        }

        // NOVO PARÂMETRO star_bonus
        function popularConfig(pc, mob, headless, tasks, discord, multi, cooldown, webhook, lang, star_bonus) {
            document.getElementById('cfg-pc').value = pc;
            document.getElementById('cfg-mob').value = mob;
            document.getElementById('cfg-headless').checked = (headless === 's');
            document.getElementById('cfg-tasks').checked = (tasks === 's');
            document.getElementById('cfg-discord').checked = (discord === 's');
            document.getElementById('cfg-multi').checked = (multi === 's');
            document.getElementById('cfg-star-bonus').checked = (star_bonus === 's');
            document.getElementById('cfg-discord-cooldown').value = cooldown;
            document.getElementById('cfg-webhook').value = webhook;
            
            // Aplica as Traduções do JSON
            currentLang = (lang === 'en') ? 'en' : 'pt';
            document.getElementById('update-title').innerText = TRANSLATIONS[currentLang].title;
            document.getElementById('update-1').innerText = TRANSLATIONS[currentLang].item1;
            document.getElementById('update-2').innerText = TRANSLATIONS[currentLang].item2;
            document.getElementById('update-3').innerText = TRANSLATIONS[currentLang].item3;
            document.getElementById('btn-github-text').innerText = TRANSLATIONS[currentLang].btnGit;
            document.getElementById('label-cooldown').innerText = TRANSLATIONS[currentLang].cooldownLabel;
            document.getElementById('label-star-bonus').innerText = TRANSLATIONS[currentLang].starBonusLabel;
        }

        function atualizarBotaoStartup(isAtivo) {
            let btn = document.getElementById('btn-startup');
            if (isAtivo) {
                btn.className = 'btn-startup startup-on';
                btn.innerText = TRANSLATIONS[currentLang].on;
            } else {
                btn.className = 'btn-startup startup-off';
                btn.innerText = TRANSLATIONS[currentLang].off;
            }
        }

        function renderDiagnostics(htmlContent) { document.getElementById('sidebar-diagnostics').innerHTML = htmlContent; }

        function salvarConfigUI() {
            let config = {
                pc: document.getElementById('cfg-pc').value,
                mob: document.getElementById('cfg-mob').value,
                headless: document.getElementById('cfg-headless').checked,
                tasks: document.getElementById('cfg-tasks').checked,
                discord: document.getElementById('cfg-discord').checked,
                multi: document.getElementById('cfg-multi').checked,
                ms_new_tasks: document.getElementById('cfg-star-bonus').checked, // Salva na mesma chave antiga pro RewardsCore ler
                discord_cooldown: document.getElementById('cfg-discord-cooldown').value,
                webhook: document.getElementById('cfg-webhook').value
            };
            pywebview.api.salvar_configuracoes_ui(config);
        }

        window.addEventListener('DOMContentLoaded', () => { setTimeout(() => { pywebview.api.rodar_diagnostico_ui(); }, 500); });
    </script>
</body>
</html>
"""

HTML_INTERFACE = HTML_INTERFACE.replace("[APP_NAME]", APP_NAME)
HTML_INTERFACE = HTML_INTERFACE.replace("[APP_VERSION]", APP_VERSION)
HTML_INTERFACE = HTML_INTERFACE.replace("[APP_CODENAME]", APP_CODENAME)

class BotAPI:
    def __init__(self):
        self.rodando = False
        RewardsCore.LOGGER = self.log_ui
        
    def log_ui(self, texto, tipo='info'):
        try:
            t_seguro = str(texto).replace("'", "\\'").replace('"', '\\"')
            webview.windows[0].evaluate_js(f"log('{t_seguro}', '{tipo}')")
        except: print(texto)

    def fechar_janela(self):
        self.parar()
        webview.windows[0].destroy()
        os._exit(0)
        
    def minimizar_janela(self):
        webview.windows[0].minimize()

    def iniciar(self):
        if self.rodando: 
            self.log_ui("System is already running!", "error")
            return
            
        self.rodando = True
        RewardsCore.ABORTAR_PROCESSO = False 
        
        webview.windows[0].evaluate_js("switchTab('console', document.querySelectorAll('.nav-item')[0]);")
        self.log_ui("Initializing Stealth loop...", "info")
        
        threading.Thread(target=self.loop_farm, daemon=True).start()
        threading.Thread(target=DiscordQuests.iniciar_farm_discord, daemon=True).start()

    def parar(self):
        self.log_ui("KILL SWITCH ACTIVATED. Initiating safe shutdown...", "error")
        self.rodando = False
        RewardsCore.ABORTAR_PROCESSO = True 
        
        sistema = platform.system().lower()
        if sistema == "windows":
            subprocess.run("taskkill /F /T /IM chromedriver.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("taskkill /F /T /IM ping.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("taskkill /T /IM DiscordCanary.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("taskkill /T /IM DiscordPTB.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sistema in ["linux", "darwin"]:
            subprocess.run("pkill -f chromedriver", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -f ping", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -15 -f DiscordCanary", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -15 -f DiscordPTB", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        self.log_ui("All background drivers and proxies terminated gracefully.", "warning")

    def loop_farm(self):
        try:
            RewardsCore.preparar_ambiente_adb()
            RewardsCore.iniciar_ciclo_farm()
            
            RewardsCore.registrar_data_execucao("rewards")
            
            self.log_ui("FARM COMPLETED SUCCESSFULLY!", "success")
        except Exception as e:
            self.log_ui(f"Fatal error: {e}", "error")
        finally:
            self.rodando = False

    def listar_contas(self): return RewardsCore.atualizar_lista_contas()
    
    def deletar_conta(self, nome_perfil):
        if nome_perfil == "DefaultAccount":
            self.log_ui("DefaultAccount is the master profile and cannot be deleted.", "error")
            return self.listar_contas()
            
        caminho = RewardsCore.BASE_PROFILES_DIR / nome_perfil
        try:
            if caminho.exists():
                shutil.rmtree(caminho, ignore_errors=True)
            self.log_ui(f"Profile '{nome_perfil}' deleted successfully.", "warning")
        except Exception as e:
            self.log_ui(f"Failed to delete profile: {e}", "error")
        return self.listar_contas()

    def abrir_setup_conta(self, nome_perfil):
        if self.rodando:
            self.log_ui("Stop the bot before opening setup!", "error")
            return
        self.log_ui(f"Opening browser for '{nome_perfil}'...", "warning")
        threading.Thread(target=RewardsCore.modo_configuracao, args=(nome_perfil,), daemon=True).start()

    def obter_status_startup(self):
        sistema = platform.system().lower()
        if sistema == "windows":
            caminho = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "RewardsBot_Startup.vbs")
        elif sistema == "linux":
            caminho = os.path.expanduser("~/.config/autostart/RewardsBot.desktop")
        elif sistema == "darwin":
            caminho = os.path.expanduser("~/Library/LaunchAgents/com.fpg.rewardsbot.plist")
        else: 
            return False
            
        return os.path.exists(caminho)

    def toggle_startup(self):
        RewardsCore.alternar_startup()
        time.sleep(0.5) 
        estado = self.obter_status_startup()
        webview.windows[0].evaluate_js(f"atualizarBotaoStartup({str(estado).lower()})")
        self.rodar_diagnostico_ui()

    def carregar_configuracoes_ui(self):
        cfg = RewardsCore.carregar_config()
        webhook_seguro = json.dumps(cfg.get('webhook_url', ''))
        lang = cfg.get("language", "pt")
        
        js_cmd = f"popularConfig({cfg.get('limite_pc', 30)}, {cfg.get('limite_mobile', 20)}, '{cfg.get('modo_oculto', 's')}', '{cfg.get('fazer_tarefas', 's')}', '{cfg.get('do_discord', 'n')}', '{cfg.get('multi_account', 'n')}', {cfg.get('discord_cooldown', 3)}, {webhook_seguro}, '{lang}', '{cfg.get('ms_new_tasks', 's')}')"
        
        webview.windows[0].evaluate_js(js_cmd)
        estado_startup = self.obter_status_startup()
        webview.windows[0].evaluate_js(f"atualizarBotaoStartup({str(estado_startup).lower()})")

    def salvar_configuracoes_ui(self, dados_html):
        cfg_atual = RewardsCore.carregar_config()
        cfg_atual['limite_pc'] = int(dados_html['pc'])
        cfg_atual['limite_mobile'] = int(dados_html['mob'])
        
        cfg_atual['modo_oculto'] = 's' if dados_html['headless'] else 'n'
        cfg_atual['fazer_tarefas'] = 's' if dados_html['tasks'] else 'n'
        cfg_atual['do_discord'] = 's' if dados_html['discord'] else 'n'
        cfg_atual['multi_account'] = 's' if dados_html['multi'] else 'n'
        cfg_atual['ms_new_tasks'] = 's' if dados_html['ms_new_tasks'] else 'n'
        
        cfg_atual['discord_cooldown'] = int(dados_html['discord_cooldown'])
        cfg_atual['webhook_url'] = dados_html['webhook']
        
        RewardsCore.salvar_config(cfg_atual)
        self.log_ui("Settings saved to disk!", "success")
        webview.windows[0].evaluate_js("switchTab('console', document.querySelectorAll('.nav-item')[0]);")
        self.rodar_diagnostico_ui()

    def rodar_diagnostico_ui(self):
        resultados_html = ""
        def add_item(nome, status, color_type):
            cor = {"green": "var(--accent-green)", "yellow": "var(--accent-yellow)", "red": "var(--accent-red)"}.get(color_type, "var(--accent-red)")
            nonlocal resultados_html 
            resultados_html += f"<div class='mini-diag-item'><span style='color: var(--text-muted);'>{nome}</span><span style='color: {cor}; font-weight: bold;'>● {status}</span></div>"

        v_chrome = RewardsCore.obter_versao_chrome()
        add_item("Chrome", f"v{v_chrome}" if v_chrome else "Error", 'green' if v_chrome else 'red')

        cfg = RewardsCore.carregar_config()
        
        if cfg.get("multi_account", "n") == "s":
            ext = ".exe" if platform.system().lower() == "windows" else ""
            caminho_adb = RewardsCore.BASE_DIR / "platform-tools" / f"adb{ext}"
            add_item("ADB Core", "Ready" if caminho_adb.exists() else "Missing", 'green' if caminho_adb.exists() else 'yellow')
        else:
            add_item("ADB Core", "Not needed", 'green')

        RewardsCore.BASE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        pastas = [p.name for p in RewardsCore.BASE_PROFILES_DIR.iterdir() if p.is_dir()]
        add_item("Profiles", f"{len(pastas)} Found" if pastas else "Empty", 'green' if pastas else 'yellow')

        is_startup_active = self.obter_status_startup()
        add_item("Startup", "ON" if is_startup_active else "OFF", 'green' if is_startup_active else 'yellow')

        if cfg.get("do_discord", "n") != "s":
            add_item("Discord Bot", "Disabled", 'red')
        else:
            exe_path, _ = DiscordQuests.localizar_aplicativo_discord()
            if not exe_path:
                add_item("Discord Bot", "App Missing", 'red')
            else:
                if not RewardsCore.ARQUIVO_LOG.exists():
                    add_item("Discord Bot", "Ready", 'green')
                else:
                    try:
                        with open(RewardsCore.ARQUIVO_LOG, "r", encoding="utf-8") as f:
                            dados_log = json.load(f)
                            hist_discord = dados_log.get("discord", [])
                            if not hist_discord:
                                add_item("Discord Bot", "Ready", 'green')
                            else:
                                ultima_data_str = hist_discord[-1]
                                formato = "%d/%m/%Y" if len(ultima_data_str.split('/')[-1]) == 4 else "%d/%m/%y"
                                ultima_data = datetime.strptime(ultima_data_str, formato)
                                dias_passados = (datetime.now() - ultima_data).days
                                cooldown_dias = int(cfg.get("discord_cooldown", 3))
                                
                                if dias_passados < cooldown_dias:
                                    add_item("Discord Bot", f"Wait {cooldown_dias - dias_passados}d", 'yellow')
                                else:
                                    add_item("Discord Bot", "Ready", 'green')
                    except:
                        add_item("Discord Bot", "Ready", 'green')

        html_seguro = json.dumps(resultados_html)
        webview.windows[0].evaluate_js(f"renderDiagnostics({html_seguro})")

def aguardar_internet(timeout_horas=1):
    """Fica em loop tentando conexão por X horas. Retorna True se conectar, False se falhar."""
    inicio = time.time()
    limite_segundos = timeout_horas * 3600
    
    while (time.time() - inicio) < limite_segundos:
        try:
            # Tenta conectar no DNS do Google
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            time.sleep(30)
    return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # MODO INICIALIZAÇÃO DO SISTEMA OPERACIONAL
        # Trava o bot até ter internet (máximo de 1 hora)
        if not aguardar_internet(timeout_horas=1):
            sys.exit(1) # Desliga silenciosamente se passou 1 hora e nada de internet
            
        rodar_rewards = False
        if not RewardsCore.verificar_se_rodou_hoje("rewards", dias_cooldown=0):
            # REMOVIDO DAQUI: Ele só vai carimbar se chegar até o final sem o PC desligar
            rodar_rewards = True

        threading.Thread(target=DiscordQuests.iniciar_farm_discord, daemon=True).start()
        
        if rodar_rewards:
            RewardsCore.preparar_ambiente_adb()
            RewardsCore.LOGGER = lambda msg, tipo="info": None
            RewardsCore.iniciar_ciclo_farm()
            
            # CARIMBO TRANSFERIDO PARA CÁ: Só registra o dia como concluído se finalizar o ciclo!
            RewardsCore.registrar_data_execucao("rewards")
            
        sys.exit(0)

    api = BotAPI()
    janela = webview.create_window(title=f'{APP_NAME} {APP_VERSION}', html=HTML_INTERFACE, js_api=api, frameless=True, easy_drag=False, width=1050, height=720, background_color='#070b14', resizable=False)
    webview.start()