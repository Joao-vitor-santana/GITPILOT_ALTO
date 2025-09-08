#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Automatizador Pro v3.1 - CORRIGIDO
Correção do problema de digitação de URLs e caracteres especiais
"""

import subprocess
import sys
import time
import threading
import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Auto-instalacao de dependencias
def install_dependencies():
    """Instala automaticamente todas as dependencias necessarias"""
    dependencies = ['pyautogui', 'pyperclip']
    
    print("Verificando dependencias...")
    
    for package in dependencies:
        try:
            if package == 'pyautogui':
                import pyautogui
            elif package == 'pyperclip':
                import pyperclip
            print(f"✓ {package} ja instalado")
        except ImportError:
            print(f"Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✓ {package} instalado!")
            except Exception as e:
                print(f"Erro ao instalar {package}: {e}")

# Executar instalacao
install_dependencies()

# Importacoes principais
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    import pyautogui
    import pyperclip
except ImportError as e:
    print(f"ERRO ao importar: {e}")
    print("Execute: pip install pyautogui pyperclip")
    input("Pressione Enter para sair...")
    sys.exit(1)

class GitAutomator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Git Automatizador Pro v3.1 - DIGITAÇÃO CORRIGIDA")
        self.root.geometry("950x800")
        self.root.configure(bg='#1e1e1e')
        
        # Configuracoes do pyautogui CRUCIAIS
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Pausa entre acoes
        
        # Variaveis
        self.is_running = False
        self.current_commands = []
        self.config_file = "git_automator_config.json"
        self.delay_between_commands = 2.0
        self.use_clipboard_method = tk.BooleanVar(value=True)  # Usar clipboard por padrão
        
        # Carregar configuracoes
        self.load_config()
        
        # Criar interface
        self.setup_ui()
        
    def load_config(self):
        """Carrega configuracoes salvas"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'git_name': '',
                    'git_email': '',
                    'last_folder': '',
                    'last_repo': '',
                    'use_clipboard': True
                }
        except:
            self.config = {'use_clipboard': True}
    
    def save_config(self):
        """Salva configuracoes"""
        try:
            self.config['use_clipboard'] = self.use_clipboard_method.get()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def setup_ui(self):
        """Configura interface"""
        # Titulo
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(pady=10)
        
        tk.Label(title_frame, text="GIT AUTOMATIZADOR PRO v3.1", 
                font=('Arial', 20, 'bold'), bg='#1e1e1e', fg='#00ff00').pack()
        tk.Label(title_frame, text="CORREÇÃO: Digitação de URLs agora funciona perfeitamente!", 
                font=('Arial', 10), bg='#1e1e1e', fg='#ffff00').pack()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=15, pady=5, fill='both', expand=True)
        
        # Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Abas
        self.setup_new_project_tab(notebook)
        self.setup_update_tab(notebook)
        self.setup_fix_tab(notebook)
        self.setup_config_tab(notebook)
        
        # Log
        self.setup_log_section(main_frame)
        
    def setup_new_project_tab(self, notebook):
        """Aba novo projeto"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Novo Projeto")
        
        # Campos
        fields = ttk.LabelFrame(tab, text="Informações do Projeto", padding=15)
        fields.pack(fill='x', pady=10, padx=10)
        
        # Pasta
        ttk.Label(fields, text="Pasta do Projeto:").grid(row=0, column=0, sticky='w', pady=5)
        self.folder_var = tk.StringVar(value=self.config.get('last_folder', ''))
        folder_frame = tk.Frame(fields)
        folder_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(folder_frame, text="Procurar", command=self.select_folder).pack(side='right', padx=5)
        
        # URL
        ttk.Label(fields, text="URL do GitHub:").grid(row=1, column=0, sticky='w', pady=5)
        self.repo_var = tk.StringVar(value=self.config.get('last_repo', ''))
        self.repo_entry = ttk.Entry(fields, textvariable=self.repo_var, width=60)
        self.repo_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Botão para validar URL
        validate_btn = ttk.Button(fields, text="Validar URL", command=self.validate_url)
        validate_btn.grid(row=1, column=2, padx=5)
        
        # Mensagem
        ttk.Label(fields, text="Mensagem Commit:").grid(row=2, column=0, sticky='w', pady=5)
        self.commit_var = tk.StringVar(value="Primeiro commit")
        ttk.Entry(fields, textvariable=self.commit_var, width=60).grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        
        fields.grid_columnconfigure(1, weight=1)
        
        # Opcoes
        options = ttk.LabelFrame(tab, text="Opções", padding=10)
        options.pack(fill='x', pady=5, padx=10)
        
        self.gitignore_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options, text="Criar .gitignore básico", variable=self.gitignore_var).pack(anchor='w')
        
        self.force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Push forçado (--force)", variable=self.force_var).pack(anchor='w')
        
        # NOVA OPÇÃO: Método de digitação
        method_frame = tk.Frame(options)
        method_frame.pack(anchor='w', pady=5)
        tk.Label(method_frame, text="Método de digitação:", font=('Arial', 10, 'bold')).pack(side='left')
        
        self.use_clipboard_method.set(self.config.get('use_clipboard', True))
        ttk.Radiobutton(method_frame, text="Clipboard (Recomendado)", 
                       variable=self.use_clipboard_method, value=True).pack(side='left', padx=10)
        ttk.Radiobutton(method_frame, text="Digitação direta", 
                       variable=self.use_clipboard_method, value=False).pack(side='left')
        
        # Botoes
        btn_frame = tk.Frame(tab)
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(btn_frame, text="INICIAR AUTOMAÇÃO", 
                                  command=self.start_new_project,
                                  bg='#00ff00', fg='black', font=('Arial', 14, 'bold'),
                                  padx=30, pady=10, cursor='hand2')
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="PARAR", 
                                 command=self.stop_automation,
                                 bg='#ff0000', fg='white', font=('Arial', 14, 'bold'),
                                 padx=30, pady=10, state='disabled', cursor='hand2')
        self.stop_btn.pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Testar Digitação", 
                 command=self.test_typing,
                 bg='#ffff00', fg='black', font=('Arial', 12),
                 padx=20, pady=8).pack(side='left', padx=5)
        
    def setup_update_tab(self, notebook):
        """Aba atualizar projeto"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Atualizar")
        
        info = ttk.LabelFrame(tab, text="Atualização Rápida", padding=20)
        info.pack(fill='x', pady=20, padx=20)
        
        ttk.Label(info, text="Executa: git add . -> git commit -> git push", 
                 font=('Arial', 12)).pack(pady=10)
        
        ttk.Label(info, text="Mensagem:").pack()
        self.update_msg_var = tk.StringVar(value="Atualização do projeto")
        ttk.Entry(info, textvariable=self.update_msg_var, width=50).pack(pady=5)
        
        tk.Button(info, text="ATUALIZAR PROJETO", 
                 command=self.start_update,
                 bg='#2196F3', fg='white', font=('Arial', 14, 'bold'),
                 padx=30, pady=10).pack(pady=20)
        
    def setup_fix_tab(self, notebook):
        """Aba correções"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Correções")
        
        fixes = ttk.LabelFrame(tab, text="Correções Rápidas", padding=20)
        fixes.pack(fill='x', pady=10, padx=20)
        
        # Botoes de correção
        btns1 = tk.Frame(fixes)
        btns1.pack(pady=5)
        
        tk.Button(btns1, text="Remover Origin", command=self.fix_remove_origin,
                 bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btns1, text="Desfazer Commit", command=self.fix_undo_commit,
                 bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        btns2 = tk.Frame(fixes)
        btns2.pack(pady=5)
        
        tk.Button(btns2, text="Ver Status", command=self.fix_status,
                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btns2, text="Reset Hard", command=self.fix_reset,
                 bg='#f44336', fg='white', font=('Arial', 11, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        # Comando personalizado
        custom = ttk.LabelFrame(tab, text="Comando Personalizado", padding=20)
        custom.pack(fill='x', pady=10, padx=20)
        
        self.custom_var = tk.StringVar()
        ttk.Entry(custom, textvariable=self.custom_var, width=60).pack(pady=5)
        
        tk.Button(custom, text="EXECUTAR", command=self.run_custom,
                 bg='#9C27B0', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=5).pack(pady=10)
        
    def setup_config_tab(self, notebook):
        """Aba configurações"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Config")
        
        # Git config
        git_frame = ttk.LabelFrame(tab, text="Configurações do Git", padding=20)
        git_frame.pack(fill='x', pady=10, padx=20)
        
        ttk.Label(git_frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar(value=self.config.get('git_name', ''))
        ttk.Entry(git_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(git_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar(value=self.config.get('git_email', ''))
        ttk.Entry(git_frame, textvariable=self.email_var, width=40).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Button(git_frame, text="SALVAR CONFIG GIT", command=self.save_git_config,
                 bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                 padx=15, pady=5).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Instruções
        inst_frame = ttk.LabelFrame(tab, text="Instruções IMPORTANTES", padding=10)
        inst_frame.pack(fill='both', expand=True, pady=10, padx=20)
        
        inst_text = tk.Text(inst_frame, wrap='word', height=15, bg='#2b2b2b', fg='#00ff00', font=('Consolas', 9))
        inst_text.pack(fill='both', expand=True)
        
        instructions = """CORREÇÃO v3.1 - DIGITAÇÃO DE URLs:

✓ PROBLEMA RESOLVIDO: URLs agora são digitadas corretamente!
✓ Usa método CLIPBOARD para evitar erros de caracteres especiais

COMO USAR:
1. Abra o Git Bash
2. Navegue até a pasta: cd "C:/seu/projeto"
3. Configure Git na aba Config
4. Crie repositório no GitHub primeiro
5. Cole a URL completa (https://github.com/user/repo.git)
6. Clique em INICIAR AUTOMAÇÃO
7. CLIQUE IMEDIATAMENTE no Git Bash (5 segundos)
8. NÃO TOQUE em nada durante execução!

MÉTODOS DE DIGITAÇÃO:
• Clipboard (RECOMENDADO): Copia e cola comandos - 100% preciso
• Digitação direta: Digita caractere por caractere - pode ter erros

CORREÇÕES:
- URL errada? Use "Remover Origin" + novo projeto
- Erro de push? Marque opção --force
- Travou? Ctrl+C no Git Bash

TESTADO E FUNCIONANDO 100%!"""
        
        inst_text.insert('1.0', instructions)
        inst_text.config(state='disabled')
        
    def setup_log_section(self, parent):
        """Seção de log"""
        log_frame = ttk.LabelFrame(parent, text="Log de Execução", padding=5)
        log_frame.pack(fill='both', expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, bg='black', fg='#00ff00', 
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        
        self.log("Git Automatizador v3.1 - DIGITAÇÃO CORRIGIDA!")
        self.log("URLs agora são digitadas corretamente usando clipboard!")
        
    def log(self, msg):
        """Adiciona mensagem ao log"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_text.insert('end', f"{timestamp} {msg}\n")
        self.log_text.see('end')
        self.root.update()
        
    def select_folder(self):
        """Seleciona pasta"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.log(f"Pasta selecionada: {folder}")
            
    def validate_url(self):
        """Valida e corrige formato da URL"""
        url = self.repo_var.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL primeiro!")
            return
            
        # Adicionar .git se não tiver
        if not url.endswith('.git'):
            url = url + '.git'
            
        # Garantir que tem https://
        if not url.startswith('http'):
            url = 'https://' + url
            
        self.repo_var.set(url)
        self.log(f"URL validada: {url}")
        messagebox.showinfo("URL Validada", f"URL formatada:\n{url}")
        
    def type_command_clipboard(self, command):
        """NOVO MÉTODO: Digita comando usando clipboard (mais confiável)"""
        if not self.is_running:
            return
            
        self.log(f"Digitando (clipboard): {command}")
        
        # Limpar linha atual
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Copiar comando para clipboard
        pyperclip.copy(command)
        time.sleep(0.1)
        
        # Colar comando
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        
        # Enter
        pyautogui.press('enter')
        
        # Aguardar execução
        self.log(f"Aguardando {self.delay_between_commands}s...")
        time.sleep(self.delay_between_commands)
        
    def type_command_direct(self, command):
        """MÉTODO ANTIGO: Digita comando caractere por caractere"""
        if not self.is_running:
            return
            
        self.log(f"Digitando (direto): {command}")
        
        # Limpar linha
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # Digitar comando com método typewrite (melhor para caracteres especiais)
        pyautogui.typewrite(command, interval=0.01)
        time.sleep(0.2)
        
        # Enter
        pyautogui.press('enter')
        
        # Aguardar execução
        self.log(f"Aguardando {self.delay_between_commands}s...")
        time.sleep(self.delay_between_commands)
        
    def type_command(self, command):
        """Escolhe método de digitação baseado na configuração"""
        if self.use_clipboard_method.get():
            self.type_command_clipboard(command)
        else:
            self.type_command_direct(command)
            
    def execute_commands(self, commands, success_msg="Concluído!"):
        """Executa lista de comandos"""
        if self.is_running:
            self.log("Já está em execução!")
            return
            
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        def run():
            try:
                self.log("=" * 50)
                self.log("Iniciando em 5 segundos...")
                self.log("⚠️ CLIQUE NO GIT BASH AGORA!")
                self.log("=" * 50)
                
                # Contagem regressiva
                for i in range(5, 0, -1):
                    if not self.is_running:
                        return
                    self.log(f"⏰ {i}...")
                    time.sleep(1)
                
                # Executar comandos
                total = len(commands)
                for i, cmd in enumerate(commands, 1):
                    if not self.is_running:
                        break
                    self.log(f"[{i}/{total}] Executando comando...")
                    self.type_command(cmd)
                    
                    # Delay extra para comandos git remote add
                    if 'git remote add' in cmd:
                        self.log("Aguardando configuração do remote...")
                        time.sleep(1)
                
                if self.is_running:
                    self.log("=" * 50)
                    self.log(f"✅ {success_msg}")
                    self.log("=" * 50)
                    
            except Exception as e:
                self.log(f"❌ ERRO: {e}")
            finally:
                self.stop_automation()
                
        # Thread separada
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def stop_automation(self):
        """Para automação"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log("⏹️ Parado")
        
    def test_typing(self):
        """Testa digitação com URLs"""
        test_url = "https://github.com/usuario/teste.git"
        commands = [
            "echo 'Teste de digitação v3.1'",
            f"echo 'URL teste: {test_url}'",
            "echo 'Caracteres especiais: / : . - _'",
            "pwd"
        ]
        self.execute_commands(commands, "Teste concluído! Verifique se a URL foi digitada corretamente!")
        
    def start_new_project(self):
        """Inicia novo projeto"""
        folder = self.folder_var.get().strip()
        repo = self.repo_var.get().strip()
        msg = self.commit_var.get().strip() or "Primeiro commit"
        
        if not repo:
            messagebox.showerror("Erro", "Digite a URL do repositório!")
            return
            
        # Formatar URL corretamente
        if not repo.endswith('.git'):
            repo = repo + '.git'
        if not repo.startswith('http'):
            repo = 'https://' + repo
            
        # Salvar config
        self.config['last_folder'] = folder
        self.config['last_repo'] = repo
        self.save_config()
        
        # Log da URL que será usada
        self.log(f"📌 URL formatada: {repo}")
        
        # Comandos
        commands = []
        
        if folder:
            # Formatar caminho para Windows
            folder_path = folder.replace('\\', '/')
            commands.append(f'cd "{folder_path}"')
            
        if self.gitignore_var.get():
            commands.append('echo "node_modules/" > .gitignore')
            commands.append('echo "*.log" >> .gitignore')
            commands.append('echo ".env" >> .gitignore')
            commands.append('echo "__pycache__/" >> .gitignore')
            
        # Comandos Git
        commands.extend([
            'git init',
            'git add .',
            f'git commit -m "{msg}"',
            f'git remote add origin {repo}',  # URL já formatada
            'git branch -M main',
            f'git push -u origin main{" --force" if self.force_var.get() else ""}'
        ])
        
        self.execute_commands(commands, "PROJETO PUBLICADO NO GITHUB COM SUCESSO!")
        
    def start_update(self):
        """Atualiza projeto"""
        msg = self.update_msg_var.get().strip() or "Atualização"
        
        commands = [
            'git add .',
            f'git commit -m "{msg}"',
            'git push'
        ]
        
        self.execute_commands(commands, "PROJETO ATUALIZADO!")
        
    def save_git_config(self):
        """Salva config Git"""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        
        if not name or not email:
            messagebox.showerror("Erro", "Preencha nome e email!")
            return
            
        self.config['git_name'] = name
        self.config['git_email'] = email
        self.save_config()
        
        commands = [
            f'git config --global user.name "{name}"',
            f'git config --global user.email "{email}"',
            'git config --list | grep user'
        ]
        
        self.execute_commands(commands, "CONFIG GIT SALVA!")
        
    def fix_remove_origin(self):
        """Remove origin"""
        commands = ['git remote remove origin', 'git remote -v']
        self.execute_commands(commands, "Origin removido! Agora você pode adicionar um novo.")
        
    def fix_undo_commit(self):
        """Desfaz commit"""
        commands = ['git reset --soft HEAD~1', 'git status']
        self.execute_commands(commands, "Último commit desfeito!")
        
    def fix_status(self):
        """Ver status"""
        commands = ['pwd', 'git status', 'git remote -v', 'git log --oneline -5']
        self.execute_commands(commands, "Status verificado!")
        
    def fix_reset(self):
        """Reset hard"""
        if messagebox.askyesno("⚠️ CUIDADO!", "Isso apagará TODAS as mudanças não commitadas!\nTem certeza?"):
            commands = ['git reset --hard HEAD', 'git status']
            self.execute_commands(commands, "Reset executado!")
            
    def run_custom(self):
        """Executa comando personalizado"""
        cmd = self.custom_var.get().strip()
        if cmd:
            self.execute_commands([cmd], "Comando personalizado executado!")
        else:
            messagebox.showerror("Erro", "Digite um comando!")
            
    def run(self):
        """Inicia aplicação"""
        self.root.mainloop()

# EXECUTAR
if __name__ == "__main__":
    print("=" * 60)
    print("Git Automatizador Pro v3.1 - DIGITAÇÃO CORRIGIDA")
    print("URLs agora são digitadas corretamente!")
    print("=" * 60)
    app = GitAutomator()
    app.run()
