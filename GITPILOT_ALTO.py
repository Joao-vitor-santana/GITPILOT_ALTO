#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Automatizador Pro - Automatiza comandos Git via interface gráfica
Autor: Criado para facilitar publicação de projetos no GitHub
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Auto-instalação de dependências
def install_dependencies():
    """Instala automaticamente todas as dependências necessárias"""
    dependencies = [
        'pyautogui',
        'keyboard',
        'psutil'
    ]
    
    print("Verificando e instalando dependencias...")
    
    for package in dependencies:
        try:
            if package == 'pyautogui':
                import pyautogui
            elif package == 'keyboard':
                import keyboard
            elif package == 'psutil':
                import psutil
            print(f"OK {package} ja esta instalado")
        except ImportError:
            print(f"Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"OK {package} instalado com sucesso!")
            except Exception as install_error:
                print(f"ERRO ao instalar {package}: {install_error}")

# Executar auto-instalação
try:
    install_dependencies()
except Exception as e:
    print(f"AVISO: Erro na instalacao automatica: {e}")
    print("Tentando continuar mesmo assim...")

# Importações principais
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    import pyautogui
    # keyboard e psutil são opcionais para funcionalidade básica
    try:
        import keyboard
        import psutil
        HAS_ADVANCED_FEATURES = True
    except ImportError:
        HAS_ADVANCED_FEATURES = False
        print("Recursos avancados desabilitados (keyboard/psutil nao encontrados)")
        
except ImportError as e:
    print(f"ERRO ao importar bibliotecas essenciais: {e}")
    print("Execute manualmente: pip install pyautogui")
    input("Pressione Enter para sair...")
    sys.exit(1)

class GitAutomator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Git Automatizador Pro v2.0")
        self.root.geometry("900x750")
        self.root.configure(bg='#2b2b2b')
        
        # Configurações do pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Variáveis
        self.is_running = False
        self.git_process = None
        self.current_commands = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface gráfica"""
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(pady=15)
        
        tk.Label(title_frame, text="Git Automatizador Pro v2.0", 
                font=('Arial', 18, 'bold'), bg='#2b2b2b', fg='#4CAF50').pack()
        tk.Label(title_frame, text="Automatize seus comandos Git sem erros!", 
                font=('Arial', 10), bg='#2b2b2b', fg='#cccccc').pack()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=15, pady=10, fill='both', expand=True)
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Aba 1: Novo Projeto
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Novo Projeto")
        self.setup_new_project_tab(tab1)
        
        # Aba 2: Projeto Existente
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Atualizar Projeto")
        self.setup_update_project_tab(tab2)
        
        # Aba 3: Correções e Limpeza
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Correcoes/Limpeza")
        self.setup_fix_tab(tab3)
        
        # Aba 4: Configurações
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Configuracoes")
        self.setup_config_tab(tab4)
        
        # Status e Log
        self.setup_status_section(main_frame)
        
    def setup_new_project_tab(self, parent):
        """Configura a aba de novo projeto"""
        
        # Frame para campos
        fields_frame = ttk.LabelFrame(parent, text="Informacoes do Projeto", padding=15)
        fields_frame.pack(fill='x', pady=10)
        
        # Pasta do projeto
        ttk.Label(fields_frame, text="Pasta do Projeto:").grid(row=0, column=0, sticky='w', pady=5)
        self.folder_var = tk.StringVar()
        folder_frame = tk.Frame(fields_frame)
        folder_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_var, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(folder_frame, text="Procurar", width=10, 
                  command=self.select_folder).pack(side='right', padx=(5,0))
        
        # URL do repositório GitHub
        ttk.Label(fields_frame, text="URL do Repositorio GitHub:").grid(row=1, column=0, sticky='w', pady=5)
        self.repo_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.repo_var, width=70).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Mensagem do commit
        ttk.Label(fields_frame, text="Mensagem do Commit:").grid(row=2, column=0, sticky='w', pady=5)
        self.commit_var = tk.StringVar(value="Primeiro commit")
        ttk.Entry(fields_frame, textvariable=self.commit_var, width=70).grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        
        # Configurar grid
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Opções avançadas
        options_frame = ttk.LabelFrame(parent, text="Opcoes Avancadas", padding=15)
        options_frame.pack(fill='x', pady=10)
        
        self.auto_add_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Adicionar todos os arquivos automaticamente (git add .)", 
                       variable=self.auto_add_var).pack(anchor='w', pady=2)
        
        self.create_gitignore_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Criar arquivo .gitignore basico", 
                       variable=self.create_gitignore_var).pack(anchor='w', pady=2)
        
        self.force_push_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Usar push forcado (--force) - CUIDADO!", 
                       variable=self.force_push_var).pack(anchor='w', pady=2)
        
        # Velocidade de digitação
        speed_frame = tk.Frame(options_frame)
        speed_frame.pack(fill='x', pady=5)
        
        ttk.Label(speed_frame, text="Velocidade de digitacao:").pack(side='left')
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["Muito Lenta", "Lenta", "Normal", "Rapida", "Muito Rapida"], 
                                  state="readonly", width=12)
        speed_combo.pack(side='left', padx=10)
        
        # Preview de comandos
        preview_frame = ttk.LabelFrame(parent, text="Preview dos Comandos", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=8, bg='#f0f0f0', font=('Consolas', 9))
        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scroll.pack(side="right", fill="y")
        
        # Botão para gerar preview
        ttk.Button(preview_frame, text="Gerar Preview", 
                  command=self.generate_preview).pack(pady=5)
        
        # Botões
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=15)
        
        self.start_btn = tk.Button(button_frame, text="INICIAR AUTOMATIZACAO", 
                                  command=self.start_new_project_automation,
                                  bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'),
                                  padx=20, pady=8)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="PARAR", 
                                 command=self.stop_automation,
                                 bg='#f44336', fg='white', font=('Arial', 12, 'bold'),
                                 padx=20, pady=8, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
    def setup_update_project_tab(self, parent):
        """Configura a aba de atualização de projeto"""
        
        info_frame = ttk.LabelFrame(parent, text="Atualizacao Rapida", padding=15)
        info_frame.pack(fill='x', pady=10)
        
        ttk.Label(info_frame, text="Esta opcao executa: git add . -> git commit -> git push").pack(anchor='w', pady=5)
        
        # Mensagem do commit
        ttk.Label(info_frame, text="Mensagem do Commit:").pack(anchor='w', pady=(10,5))
        self.update_commit_var = tk.StringVar(value="Atualizacao do projeto")
        ttk.Entry(info_frame, textvariable=self.update_commit_var, width=60).pack(fill='x', pady=5)
        
        # Opções para update
        self.update_force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(info_frame, text="Push forcado (--force)", 
                       variable=self.update_force_var).pack(anchor='w', pady=5)
        
        # Botão de atualização
        update_btn = tk.Button(parent, text="ATUALIZAR PROJETO", 
                              command=self.start_update_automation,
                              bg='#2196F3', fg='white', font=('Arial', 12, 'bold'),
                              padx=20, pady=10)
        update_btn.pack(pady=20)
        
    def setup_fix_tab(self, parent):
        """Configura a aba de correções e limpeza"""
        
        fix_frame = ttk.LabelFrame(parent, text="Correcoes Automaticas", padding=15)
        fix_frame.pack(fill='x', pady=10)
        
        ttk.Label(fix_frame, text="Use estas opcoes quando algo der errado:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0,10))
        
        # Botões de correção
        btn_frame1 = tk.Frame(fix_frame)
        btn_frame1.pack(fill='x', pady=5)
        
        tk.Button(btn_frame1, text="Remover Remote Origin", 
                 command=self.fix_remove_origin,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame1, text="Desfazer Ultimo Commit", 
                 command=self.fix_undo_commit,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        btn_frame2 = tk.Frame(fix_frame)
        btn_frame2.pack(fill='x', pady=5)
        
        tk.Button(btn_frame2, text="Reset Hard (CUIDADO!)", 
                 command=self.fix_reset_hard,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame2, text="Verificar Status", 
                 command=self.fix_check_status,
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        # Correção manual de URL
        manual_frame = ttk.LabelFrame(parent, text="Correcao Manual de Remote", padding=15)
        manual_frame.pack(fill='x', pady=10)
        
        ttk.Label(manual_frame, text="Nova URL do repositorio:").pack(anchor='w', pady=5)
        self.new_repo_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.new_repo_var, width=70).pack(fill='x', pady=5)
        
        tk.Button(manual_frame, text="Corrigir URL do Remote", 
                 command=self.fix_remote_url,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(pady=10)
        
        # Comandos personalizados
        custom_frame = ttk.LabelFrame(parent, text="Comando Personalizado", padding=15)
        custom_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(custom_frame, text="Digite um comando Git personalizado:").pack(anchor='w', pady=5)
        self.custom_cmd_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=self.custom_cmd_var, width=70).pack(fill='x', pady=5)
        
        tk.Button(custom_frame, text="Executar Comando", 
                 command=self.execute_custom_command,
                 bg='#9C27B0', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(pady=10)
        
    def setup_config_tab(self, parent):
        """Configura a aba de configurações"""
        
        # Configurações do Git
        git_frame = ttk.LabelFrame(parent, text="Configuracoes do Git", padding=15)
        git_frame.pack(fill='x', pady=10)
        
        ttk.Label(git_frame, text="Nome de usuario:").grid(row=0, column=0, sticky='w', pady=5)
        self.git_name_var = tk.StringVar()
        ttk.Entry(git_frame, textvariable=self.git_name_var, width=40).grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        ttk.Label(git_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        self.git_email_var = tk.StringVar()
        ttk.Entry(git_frame, textvariable=self.git_email_var, width=40).grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        git_frame.grid_columnconfigure(1, weight=1)
        
        config_btn = tk.Button(git_frame, text="Salvar Configuracoes Git", 
                              command=self.save_git_config,
                              bg='#FF9800', fg='white', font=('Arial', 10, 'bold'))
        config_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Verificar configurações atuais
        check_btn = tk.Button(git_frame, text="Verificar Config Atual", 
                             command=self.check_git_config,
                             bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        check_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Informações
        info_frame = ttk.LabelFrame(parent, text="Instrucoes", padding=15)
        info_frame.pack(fill='both', expand=True, pady=10)
        
        instructions = """COMO USAR:

1. Certifique-se de que o Git Bash esteja ABERTO e ativo
2. Navegue ate a pasta do seu projeto no Git Bash usando: cd "caminho/da/pasta"
3. Preencha as informacoes na aba "Novo Projeto"
4. Use "Gerar Preview" para ver os comandos que serao executados
5. Clique em "INICIAR AUTOMATIZACAO"
6. RAPIDAMENTE clique na janela do Git Bash
7. Aguarde a automatizacao terminar!

IMPORTANTE:
- Mantenha o Git Bash sempre visivel
- Nao mova o mouse durante a automatizacao
- Para emergencias, mova o mouse para o canto superior esquerdo
- Use a aba "Correcoes/Limpeza" se algo der errado

CONFIGURACAO INICIAL:
- Configure seu nome e email do Git na aba "Configuracoes"
- Crie o repositorio no GitHub ANTES de usar o automatizador
- Sempre verifique a URL do repositorio antes de executar

DICAS DE CORRECAO:
- Se errar a URL: use "Corrigir URL do Remote"
- Se der erro de push: tente com "--force" nas opcoes
- Se travou: use "Reset Hard" (CUIDADO - apaga mudancas nao commitadas)
"""
        
        text_widget = tk.Text(info_frame, wrap='word', height=20, bg='#f5f5f5', font=('Arial', 9))
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill='both', expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert('1.0', instructions)
        text_widget.configure(state='disabled')
        
    def setup_status_section(self, parent):
        """Configura a seção de status e log"""
        
        status_frame = ttk.LabelFrame(parent, text="Status e Log", padding=10)
        status_frame.pack(fill='both', expand=True, pady=(10,0))
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para usar!")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        status_label.pack(anchor='w', pady=5)
        
        # Log
        log_frame = tk.Frame(status_frame)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, bg='#1e1e1e', fg='#00ff00', 
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        self.log("Git Automatizador Pro v2.0 iniciado!")
        self.log("Recursos de correcao automatica adicionados!")
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_text.insert('end', f"{timestamp} {message}\n")
        self.log_text.see('end')
        self.root.update()
        
    def select_folder(self):
        """Seleciona pasta do projeto"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.generate_preview()
            
    def save_git_config(self):
        """Salva configurações do Git"""
        name = self.git_name_var.get().strip()
        email = self.git_email_var.get().strip()
        
        if not name or not email:
            messagebox.showerror("Erro", "Preencha nome e email!")
            return
            
        commands = [
            f'git config --global user.name "{name}"',
            f'git config --global user.email "{email}"'
        ]
        
        self.execute_commands(commands, "Configuracoes do Git salvas!")
        
    def check_git_config(self):
        """Verifica configurações atuais do Git"""
        commands = [
            'git config user.name',
            'git config user.email',
            'git config --list'
        ]
        
        self.execute_commands(commands, "Verificacao de configuracoes concluida!")
        
    def generate_preview(self):
        """Gera preview dos comandos que serão executados"""
        folder = self.folder_var.get().strip()
        repo_url = self.repo_var.get().strip()
        commit_msg = self.commit_var.get().strip() or "Primeiro commit"
        
        commands = []
        
        if folder:
            commands.append(f'cd "{folder}"')
            
        if self.create_gitignore_var.get():
            commands.append('echo "# Gitignore automatico" > .gitignore')
        
        commands.extend([
            'git init',
            'git add .' if self.auto_add_var.get() else 'git add <arquivos>',
            f'git commit -m "{commit_msg}"'
        ])
        
        if repo_url:
            commands.append(f'git remote add origin {repo_url}')
        else:
            commands.append('git remote add origin <URL_DO_REPOSITORIO>')
            
        commands.extend([
            'git branch -M main',
            'git push -u origin main' + (' --force' if self.force_push_var.get() else '')
        ])
        
        # Mostrar no preview
        self.preview_text.delete('1.0', 'end')
        self.preview_text.insert('1.0', '\n'.join(commands))
        
    def get_typing_speed(self):
        """Retorna velocidade de digitação"""
        speed_map = {
            "Muito Lenta": 0.5,
            "Lenta": 0.3,
            "Normal": 0.1,
            "Rapida": 0.05,
            "Muito Rapida": 0.01
        }
        return speed_map.get(self.speed_var.get(), 0.1)
        
    def type_command(self, command):
        """Digita comando no terminal ativo"""
        if not self.is_running:
            return
            
        speed = self.get_typing_speed()
        self.log(f"Digitando: {command}")
        
        # Limpar linha atual primeiro
        pyautogui.keyDown('ctrl')
        pyautogui.press('c')
        pyautogui.keyUp('ctrl')
        time.sleep(0.1)
        
        for char in command:
            if not self.is_running:
                break
            pyautogui.typewrite(char, interval=speed)
            
        pyautogui.press('enter')
        time.sleep(3)  # Aguarda comando executar
        
    def start_new_project_automation(self):
        """Inicia automatização para novo projeto"""
        
        # Validações
        folder = self.folder_var.get().strip()
        repo_url = self.repo_var.get().strip()
        commit_msg = self.commit_var.get().strip() or "Primeiro commit"
        
        if not repo_url:
            messagebox.showerror("Erro", "Digite a URL do repositorio!")
            return
        
        # Preparar comandos
        commands = []
        
        if folder:
            commands.append(f'cd "{folder}"')
            
        if self.create_gitignore_var.get():
            commands.append('echo "__pycache__/\n*.pyc\n*.pyo\n.env\nnode_modules/\n.DS_Store" > .gitignore')
        
        commands.extend([
            'git init',
            'git add .' if self.auto_add_var.get() else f'git add .',
            f'git commit -m "{commit_msg}"',
            f'git remote add origin {repo_url}',
            'git branch -M main',
            f'git push -u origin main{" --force" if self.force_push_var.get() else ""}'
        ])
        
        self.current_commands = commands
        self.execute_commands(commands, "Projeto publicado no GitHub!")
        
    def start_update_automation(self):
        """Inicia automatização para atualização"""
        commit_msg = self.update_commit_var.get().strip() or "Atualizacao do projeto"
        
        commands = [
            'git add .',
            f'git commit -m "{commit_msg}"',
            f'git push{" --force" if self.update_force_var.get() else ""}'
        ]
        
        self.current_commands = commands
        self.execute_commands(commands, "Projeto atualizado!")
        
    # Funções de correção
    def fix_remove_origin(self):
        """Remove origin atual"""
        commands = ['git remote remove origin']
        self.execute_commands(commands, "Remote origin removido!")
        
    def fix_undo_commit(self):
        """Desfaz último commit"""
        commands = ['git reset --soft HEAD~1']
        self.execute_commands(commands, "Ultimo commit desfeito!")
        
    def fix_reset_hard(self):
        """Reset hard - CUIDADO!"""
        result = messagebox.askyesno("CUIDADO!", 
                                   "Reset hard ira APAGAR todas as mudancas nao commitadas!\n\nTem certeza?")
        if result:
            commands = ['git reset --hard HEAD']
            self.execute_commands(commands, "Reset hard executado!")
            
    def fix_check_status(self):
        """Verifica status do repositório"""
        commands = [
            'git status',
            'git remote -v',
            'git branch'
        ]
        self.execute_commands(commands, "Status verificado!")
        
    def fix_remote_url(self):
        """Corrige URL do remote"""
        new_url = self.new_repo_var.get().strip()
        if not new_url:
            messagebox.showerror("Erro", "Digite a nova URL!")
            return
            
        commands = [
            'git remote remove origin',
            f'git remote add origin {new_url}',
            'git remote -v'
        ]
        self.execute_commands(commands, "URL do remote corrigida!")
        
    def execute_custom_command(self):
        """Executa comando personalizado"""
        cmd = self.custom_cmd_var.get().strip()
        if not cmd:
            messagebox.showerror("Erro", "Digite um comando!")
            return
            
        if not cmd.startswith('git '):
            cmd = 'git ' + cmd
            
        commands = [cmd]
        self.execute_commands(commands, "Comando personalizado executado!")
        
    def execute_commands(self, commands, success_msg="Comandos executados!"):
        """Executa lista de comandos"""
        self.is_running = True
        self.start_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.status_var.set("Executando automatizacao...")
        
        def run():
            try:
                self.log("Iniciando em 5 segundos...")
                self.log("CLIQUE RAPIDAMENTE NA JANELA DO GIT BASH!")
                
                for i in range(5, 0, -1):
                    if not self.is_running:
                        return
                    self.status_var.set(f"Iniciando em {i}...")
                    time.sleep(1)
                
                if not self.is_running:
                    return
                
                # Executar comandos
                for i, cmd in enumerate(commands, 1):
                    if not self.is_running:
                        break
                        
                    self.status_var.set(f"Executando comando {i}/{len(commands)}")
                    self.type_command(cmd)
                    
                self.log(f"SUCESSO: {success_msg}")
                self.status_var.set("Concluido com sucesso!")
                
            except Exception as e:
                self.log(f"ERRO: {e}")
                self.status_var.set("Erro na execucao!")
                
            finally:
                self.stop_automation()
        
        # Executar em thread separada
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
    def stop_automation(self):
        """Para a automatização"""
        self.is_running = False
        self.start_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.status_var.set("Pronto para usar!")
        self.log("Automatizacao interrompida")
        
    def run(self):
        """Executa a aplicação"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Função chamada ao fechar a aplicação"""
        self.stop_automation()
        self.root.destroy()

def main():
    """Função principal"""
    print("Iniciando Git Automatizador Pro v2.0...")
    
    try:
        app = GitAutomator()
        app.run()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuario")
    except Exception as e:
        print(f"ERRO inesperado: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
