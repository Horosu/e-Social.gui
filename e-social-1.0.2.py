import threading
import multiprocessing
import requests
import re
import os
import pandas as pd
import pdfkit
import json
import bcrypt
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import sys
from io import StringIO
from customtkinter import CTkImage

def ler_arquivo_publico(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erro ao acessar o arquivo: {e}")
        exit()

def verificar_credenciais(usuario, senha, credenciais):
    senha_hash = credenciais.get(usuario)
    if senha_hash is None:
        return False
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())

class RedirectText(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, text):
        super().write(text)
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

def login():
    global usuario
    usuario = entry_usuario.get()
    senha = entry_senha.get()

    if not usuario or not senha:
        messagebox.showwarning("Login", "Por favor, preencha todos os campos.")
        return

    if 'atualizado' not in credenciais:
        messagebox.showinfo("Atualização Necessária", "Foi encontrado uma versão mais recente deste software, por favor entre em contanto com sua equiipe de T.I !! ")
        sys.exit()  # Fecha o programa

    if verificar_credenciais(usuario, senha, credenciais):
        progress_bar.start()
        root.after(1000, lambda: (messagebox.showinfo("Login", "Login bem-sucedido!"), 
                                  root.withdraw(), 
                                  abrir_painel()))
    else:
        messagebox.showerror("Login", "Credênciais inválidas!")

def processar_dados(periodo_apuracao):
    try:
        print(f"Processando dados com o período: {periodo_apuracao}")

        messagebox.showinfo("Processar Dados", "Dados processados com sucesso!")
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        messagebox.showerror("Erro", f"Erro ao processar dados: {e}")

    file_path = "dados.xlsx"
    
    headers_file = "headers.txt"
    with open(headers_file, 'r') as f:
        headers_str = f.read()
    
    headers = eval('{' + headers_str + '}')
    
    threaded_process_sheets(file_path, periodo_apuracao, headers)

def sanitize_filename(name):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def include_external_css(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    css_links = [link['href'] for link in soup.find_all('link', rel='stylesheet') if link.has_attr('href')]
    
    css_content = ""
    for css_url in css_links:
        css_url_absolute = urljoin(base_url, css_url)
        try:
            response = requests.get(css_url_absolute)
            response.raise_for_status()
            css_content += response.text
        except requests.RequestException as e:
            print(f"Erro ao baixar CSS de {css_url_absolute}: {e}")
    
    style_tag = soup.new_tag('style')
    style_tag.string = css_content
    soup.head.append(style_tag)
    
    return str(soup)

def threaded_fetch_and_save_as_pdf(url, payload, file_name, base_folder, headers, create_folder=False):
    print(f"Enviando POST para URL: {url}")

    response = requests.request("POST", url, data=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro ao se comunicar com o e-Social. Status Code: {response.status_code}")
        return None

    print(f"Resposta recebida com sucesso. Status Code: {response.status_code}")

    html_with_css = include_external_css(response.text, url)

    if create_folder:
        regex2 = r'id="Nome".*?value="([^"]*)"'
        match2 = re.search(regex2, response.text)
        if match2:
            nome = match2.group(1)
            print(f"Nome capturado de {url}: {nome}")
            base_folder = os.path.join(base_folder, sanitize_filename(nome))
            os.makedirs(base_folder, exist_ok=True)
        else:
            print(f"Nada encontrado para nome em {url}")
            return None

    if base_folder is None:
        print(f"Base folder é None para {url}")
        return None

    sanitized_file_name = sanitize_filename(file_name) + ".pdf"
    file_path = os.path.join(base_folder, sanitized_file_name)

    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    options = {
        'no-outline': None,
        'disable-javascript': None,
        'zoom': '1.3'
    }
    
    try:
        print(f"Salvando a página como PDF em: {file_path}")
        pdfkit.from_string(html_with_css, file_path, configuration=config, options=options)
        print(f"Página salva como PDF em {file_path}")
    except Exception as e:
        print(f"Erro ao salvar PDF: {e}")

    return base_folder

def threaded_process_sheets(file_path, periodo_apuracao, headers):
    df = pd.read_excel(file_path, sheet_name=None)
    for sheet_name, data in df.items():
        folder_name = sanitize_filename(sheet_name)
        os.makedirs(folder_name, exist_ok=True)
        for cpf in data['CPF']:
            cpf = re.sub(r'\D', '', str(cpf))
            periodo_apuracao_encoded = periodo_apuracao.replace('/', '%2F')
            cpf_base_folder = folder_name
            urls_payloads_filenames = [
                ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorContribuicaoPrevidenciaria", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorContribuicaoPrevidenciaria", True),
                ("https://www.esocial.gov.br/portal/Totalizador/FGTSPorTrabalhador", f"HabilitarPesquisaParcialCpf=False&PeriodoApuracao={periodo_apuracao_encoded}&Cpf={cpf}", "FgtsPorTrabalhador", False),
                ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorImpostoRenda", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorImpostoRenda", False)
            ]
            for url, payload, file_name, create_folder in urls_payloads_filenames:
                cpf_base_folder = threaded_fetch_and_save_as_pdf(url, payload, file_name, cpf_base_folder, headers, create_folder)


def threaded_fetch_and_download_link(url, payload, file_name, base_folder, headers, create_folder=False):
    response = requests.request("POST", url, data=payload, headers=headers)
    regex = r'href="([^"]*)">Baixar XML'
    regex2 = r'id="Nome".*?value="([^"]*)"'

    if create_folder:
        match2 = re.search(regex2, response.text)
        if match2:
            nome = match2.group(1)
            print(f"Nome capturado de {url}: {nome}")
            base_folder = os.path.join(base_folder, sanitize_filename(nome))
            os.makedirs(base_folder, exist_ok=True)
        else:
            print(f"Nada encontrado para nome em {url}")
            return None

    match = re.search(regex, response.text)
    if match:
        link = match.group(1)
        print(f"Link capturado de {url}: {link}")
        download_response = requests.get(link, headers=headers)
        if download_response.status_code == 200:
            sanitized_link = sanitize_filename(file_name)
            file_path = os.path.join(base_folder, sanitized_link)
            with open(file_path, 'wb') as file:
                file.write(download_response.content)
            print(f"Arquivo salvo em {file_path}")
        else:
            print(f"Falha de download no link {link}")
    else:
        print(f"Nada encontrado no link {url}")

    return base_folder

def process_sheets_xml(file_path, periodo_apuracao, headers):
    df = pd.read_excel(file_path, sheet_name=None)
    for sheet_name, data in df.items():
        folder_name = sanitize_filename(sheet_name)
        os.makedirs(folder_name, exist_ok=True)
        for cpf in data['CPF']:
            cpf = re.sub(r'\D', '', str(cpf))  
            periodo_apuracao_encoded = periodo_apuracao.replace('/', '%2F')
            cpf_base_folder = folder_name
            urls_payloads_filenames = [
                ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorContribuicaoPrevidenciaria", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorContribuicaoPrevidenciaria.xml", True),
                ("https://www.esocial.gov.br/portal/Totalizador/FGTSPorTrabalhador", f"HabilitarPesquisaParcialCpf=False&PeriodoApuracao={periodo_apuracao_encoded}&Cpf={cpf}", "FgtsPorTrabalhador.xml", False),
                ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorImpostoRenda", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorImpostoRenda.xml", False)
            ]
            for url, payload, file_name, create_folder in urls_payloads_filenames:
                cpf_base_folder = threaded_fetch_and_download_link(url, payload, file_name, cpf_base_folder, headers, create_folder)

def executar_extrair_xml():
    def sanitize_filename(name):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name

    def threaded_fetch_and_download_link(url, payload, file_name, base_folder, headers, create_folder=False):
        response = requests.request("POST", url, data=payload, headers=headers)
        regex = r'href="([^"]*)">Baixar XML'
        regex2 = r'id="Nome".*?value="([^"]*)"'

        if create_folder:
            match2 = re.search(regex2, response.text)
            if match2:
                nome = match2.group(1)
                print(f"Nome capturado de {url}: {nome}")
                base_folder = os.path.join(base_folder, sanitize_filename(nome))
                os.makedirs(base_folder, exist_ok=True)
            else:
                print(f"Nada encontrado para nome em {url}")
                return None

        match = re.search(regex, response.text)
        if match:
            link = match.group(1)
            print(f"Link capturado de {url}: {link}")
            download_response = requests.get(link, headers=headers)
            if download_response.status_code == 200:
                sanitized_link = sanitize_filename(file_name)
                file_path = os.path.join(base_folder, sanitized_link)
                with open(file_path, 'wb') as file:
                    file.write(download_response.content)
                print(f"Arquivo salvo em {file_path}")
            else:
                print(f"Falha de download no link {link}")
        else:
            print(f"Nada encontrado no link {url}")

        return base_folder

    def threaded_process_sheets(file_path, periodo_apuracao, headers):
        df = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, data in df.items():
            folder_name = sanitize_filename(sheet_name)
            os.makedirs(folder_name, exist_ok=True)
            for cpf in data['CPF']:
                cpf = re.sub(r'\D', '', str(cpf)) 
                periodo_apuracao_encoded = periodo_apuracao.replace('/', '%2F')
                cpf_base_folder = folder_name
                urls_payloads_filenames = [
                    ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorContribuicaoPrevidenciaria", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorContribuicaoPrevidenciaria.xml", True),
                    ("https://www.esocial.gov.br/portal/Totalizador/FGTSPorTrabalhador", f"HabilitarPesquisaParcialCpf=False&PeriodoApuracao={periodo_apuracao_encoded}&Cpf={cpf}", "FgtsPorTrabalhador.xml", False),
                    ("https://www.esocial.gov.br/portal/Totalizador/TotalizadorImpostoRenda", f"PeriodoApuracaoPesquisa={periodo_apuracao_encoded}&CpfPesquisa={cpf}", "TotalizadorImpostoRenda.xml", False)
                ]
                for url, payload, file_name, create_folder in urls_payloads_filenames:
                    cpf_base_folder = threaded_fetch_and_download_link(url, payload, file_name, cpf_base_folder, headers, create_folder)

    file_path = "dados.xlsx"
    periodo_apuracao = entry_periodo_apuracao_xml.get()

    headers_file = "headers.txt"
    with open(headers_file, 'r') as f:
        headers_str = f.read()

    headers = eval('{' + headers_str + '}')

    threaded_process_sheets(file_path, periodo_apuracao, headers)

def executar_codigo_xml(periodo_apuracao):
    file_path = "dados.xlsx"
    try:
        print(f"Executando XML com o período: {periodo_apuracao}")
        
        messagebox.showinfo("Executar XML", "XML processado com sucesso!")
    except Exception as e:
        print(f"Erro ao executar XML: {e}")
        messagebox.showerror("Erro", f"Erro ao executar XML: {e}")
    
    headers_file = "headers.txt"
    with open(headers_file, 'r') as f:
        headers_str = f.read()

    headers = eval('{' + headers_str + '}')

    process_sheets_xml(file_path, periodo_apuracao, headers)

class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert('end', string)
        self.widget.yview('end')

def atualizar_referer(referer):
    with open("headers.txt", "r") as file:
        linhas = file.readlines()

    for i, linha in enumerate(linhas):
        if '"Referer":' in linha:
            linhas[i] = f'"Referer": "{referer}",\n'
            break

    with open("headers.txt", "w") as file:
        file.writelines(linhas)

def atualizar_header(chave, valor):
    with open("headers.txt", "r") as file:
        linhas = file.readlines()

    for i, linha in enumerate(linhas):
        if f'"{chave}":' in linha:
            linhas[i] = f'"{chave}": "{valor}",\n'
            break

    with open("headers.txt", "w") as file:
        file.writelines(linhas)

def inserir_referer():
    referer_window = ctk.CTkToplevel(root)
    referer_window.title("Entrada de Referer")
    referer_window.geometry("300x150") 
    referer_window.attributes('-topmost', True)

    window_width = 300
    window_height = 150

    screen_width = referer_window.winfo_screenwidth()
    screen_height = referer_window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    referer_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    label = ctk.CTkLabel(referer_window, text="Insira o novo Referer:")
    label.pack(pady=10)

    entry = ctk.CTkEntry(referer_window)
    entry.pack(pady=10)

    def on_submit():
        referer = entry.get()
        if referer:
            atualizar_referer(referer)
            label_feedback.configure(text="Referer atualizado com sucesso!")
        referer_window.destroy()

    submit_button = ctk.CTkButton(referer_window, text="Confirmar", command=on_submit)
    submit_button.pack(pady=10)
        

def inserir_cookie():
    cookie_window = ctk.CTkToplevel(root)
    cookie_window.title("Entrada de Cookie")
    cookie_window.geometry("300x150")  
    cookie_window.attributes('-topmost', True)

    window_width = 300
    window_height = 150
    
    screen_width = cookie_window.winfo_screenwidth()
    screen_height = cookie_window.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    cookie_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    

    label = ctk.CTkLabel(cookie_window, text="Insira o novo Cookie:")
    label.pack(pady=10)

    entry = ctk.CTkEntry(cookie_window)
    entry.pack(pady=10)

    def on_submit():
        cookie = entry.get()
        if cookie:
            atualizar_header("Cookie", cookie)
            label_feedback.configure(text="Cookie atualizado com sucesso!")
        cookie_window.destroy()

    submit_button = ctk.CTkButton(cookie_window, text="Confirmar", command=on_submit)
    submit_button.pack(pady=10)


def abrir_painel():
    global root, text_console, text_headers, entry_periodo_apuracao_xml, entry_periodo_apuracao_pdf, label_feedback, notebook, usuario


    root = ctk.CTk()
    root.title("e-Social | V:1.0.2 ")
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Configura a aparência e o fundo da janela
    root.configure(bg='#1F1F1F')

    # Criar o Notebook usando CTkTabview
    notebook = ctk.CTkTabview(root)
    notebook.pack(fill='both', expand=True)

    # Aba Console
    notebook.add("Console")
    frame_console = notebook.tab("Console")

    # Área de texto para o Console
    text_console = ctk.CTkTextbox(frame_console, wrap='word', bg_color='#1E1E1E', text_color='#CCCCCC', font=("Arial", 12), padx=10, pady=10)
    text_console.pack(fill='both', expand=True, padx=10, pady=10)

    # Barra de rolagem para o console
    scrollbar = ctk.CTkScrollbar(frame_console, orientation='vertical', command=text_console.yview)
    scrollbar.pack(side='right', fill='y')
    text_console.configure(yscrollcommand=scrollbar.set)

    # Redirecionar prints para a área de texto
    sys.stdout = RedirectText(text_console)

    # Aba Headers

    ctk.set_appearance_mode('dark')

    notebook.add("Headers")
    frame_headers = notebook.tab("Headers")

    label_instrucao = ctk.CTkLabel(frame_headers, text="Clique no botão abaixo para inserir um novo Referer ou Cookie:", 
                               font=("Arial", 12), bg_color='#1F1F1F', text_color='#CCCCCC')
    label_instrucao.pack(pady=10)
    
    botao_inserir_cookie = ctk.CTkButton(frame_headers, text="Inserir Cookie", 
                                     font=("Arial", 12, "bold"), 
                                     command=inserir_cookie, 
                                     bg_color='#007BFF', text_color='#FFFFFF')
    botao_inserir_cookie.pack(pady=25)

    botao_inserir_referer = ctk.CTkButton(frame_headers, text="Inserir Referer", 
                                      font=("Arial", 12, "bold"), 
                                      command=inserir_referer, 
                                      bg_color='#28A745', text_color='#FFFFFF')
    botao_inserir_referer.pack(pady=10)

    label_feedback = ctk.CTkLabel(frame_headers, text="")
    label_feedback.pack(pady=25)

    notebook.set("Headers")

    # Área de texto para editar os headers
    text_headers = ctk.CTkTextbox(frame_headers, wrap='word', bg_color='#1E1E1E', text_color='#CCCCCC', font=("Arial", 12), padx=10, pady=10)
    text_headers.pack(fill='both', expand=True, padx=10, pady=10)
    

    # Barra de rolagem para o editor de headers
    scrollbar_headers = ctk.CTkScrollbar(frame_headers, orientation='vertical', command=text_headers.yview)
    scrollbar_headers.pack(side='right', fill='y')
    text_headers.configure(yscrollcommand=scrollbar_headers.set)


    # Aba Extrair XML
    notebook.add("Extrair XML")
    frame_xml = notebook.tab("Extrair XML")

    ctk.CTkLabel(frame_xml, text="Periodo de apuração:", font=("Arial", 12), bg_color='#1F1F1F', text_color='#CCCCCC').pack(pady=10)
    entry_periodo_apuracao_xml = ctk.CTkEntry(frame_xml, font=("Arial", 12))
    entry_periodo_apuracao_xml.pack(pady=10)

    botao_executar_xml = ctk.CTkButton(frame_xml, text="Extrair XML", font=("Arial", 12, "bold"), command=lambda: executar_codigo_xml(entry_periodo_apuracao_xml.get()), bg_color='#28A745', text_color='#FFFFFF')
    botao_executar_xml.pack(pady=10)

    # Aba Extrair PDF
    notebook.add("Extrair PDF")
    frame_pdf = notebook.tab("Extrair PDF")

    ctk.CTkLabel(frame_pdf, text="Periodo de apuração:", font=("Arial", 12), bg_color='#1F1F1F', text_color='#CCCCCC').pack(pady=10)
    entry_periodo_apuracao_pdf = ctk.CTkEntry(frame_pdf, font=("Arial", 12))
    entry_periodo_apuracao_pdf.pack(pady=10)

    botao_executar_pdf = ctk.CTkButton(frame_pdf, text="Extrair PDF", font=("Arial", 12, "bold"), command=lambda: processar_dados(entry_periodo_apuracao_pdf.get()), bg_color='#28A745', text_color='#FFFFFF')
    botao_executar_pdf.pack(pady=10)

    print(r""" Versão 1.0.2 
               
        Thermica Refrigeração e Ar condicionado LTDA
        Last Updated: 08/2024
          
By:Guilherme Gonçalves """
    )

    def criar_frame_usuario(usuario):
        frame_usuario = ctk.CTkFrame(notebook,
                                    corner_radius=11,  
                                    border_width=0,   
                                    bg_color="#003366")  

        label_usuario = ctk.CTkLabel(frame_usuario,
                                    text=f" user:  {usuario} ",  
                                    font=("Arial", 11, "bold"),  
                                    text_color="#FFFFFF",  
                                    bg_color="#003366")  #

        label_usuario.pack(padx=5, pady=5, fill="both", expand=True)

        frame_usuario.update_idletasks()
        frame_usuario.configure(width=label_usuario.winfo_width() + 20)  
        frame_usuario.configure(height=label_usuario.winfo_height() + 10)  

        return frame_usuario

        usuario  
    frame_usuario = criar_frame_usuario(usuario)
    frame_usuario.place(x=10, y=5)  

    # Carregar o conteúdo do headers.txt
    carregar_headers()

    root.mainloop()

def carregar_headers():
    headers_file = "headers.txt"
    try:
        with open(headers_file, 'r') as f:
            headers_content = f.read()
            text_headers.delete('1.0', ctk.END)
            text_headers.insert(ctk.END, headers_content)
    except FileNotFoundError:
        text_headers.insert(ctk.END, "{}")
        print(f"Arquivo {headers_file} não encontrado. Criado um novo arquivo vazio.")

def centralizar_janela(root, largura, altura):
    # Obtém a largura e altura da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    # Calcula as coordenadas para centralizar a janela
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2

    # Define a geometria da janela
    root.geometry(f"{largura}x{altura}+{x}+{y}")

def configurar_gui():
    global root, entry_usuario, entry_senha, credenciais, progress_bar

    # Criar ou reescrever o arquivo headers.txt com o conteúdo padrão
    conteudo_padrao = r"""
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Content-Type": "application/x-www-form-urlencoded",
"Cookie": "TipoAcessoGovBr=x509; SeloGovBr=3; Origem=govbr; __AntiXsrfToken=9abaaf4558f44070a14256feafb21c9f; s=a0db0a8d1b97c8f6b47d31052b2d592b4440fb6ecb7dc74a253ef5956340cb16; assinadoc_cert_type=A1; ASP.NET_SessionId=c2smjwqha0kly1i1x0f3i1mn; usuario_logado_ws=32.454.894/0001-86; ASP.NET_SessionId=favfamctvjkzlqzve3eehyn; usuario_logado_ws=32.454.894/0001-86",
"Origin": "https://www.esocial.gov.br",
"Referer": "https://www.esocial.gov.br/portal/Totalizador/FGTSPorTrabalhador?id=d51a2a4f-6663-4232-9a31-27a685b9c7cb",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "same-origin",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
"sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": '"Windows"'
"""

    headers_file = "headers.txt"
    with open(headers_file, 'w') as f:
        f.write(conteudo_padrao)

    # URL para download de credenciais
    url = 'https://drive.google.com/uc?export=download&id=1qPhU7olM4hIBo1rYlSHnmvimv3odEND0'
    conteudo = ler_arquivo_publico(url)

    try:
        credenciais = json.loads(conteudo)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        exit()

    # Estilo e aparência do CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()

    # Centraliza e define o tamanho da janela
    largura_janela = 400
    altura_janela = 300
    centralizar_janela(root, largura_janela, altura_janela)
   
    root.title("e-Social | V:1.0.2 ")

    # Configura o grid para a janela principal
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame = ctk.CTkFrame(root, corner_radius=15)
    frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Configura o grid dentro do frame
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    try:
        logo_img = Image.open("logo.png")
        logo_img = logo_img.resize((100, 100), Image.ANTIALIAS)
        logo_image = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(frame, image=logo_image, text="")
        logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    except Exception as e:
        print(f"Erro ao carregar imagem do logo: {e}")

    ctk.CTkLabel(frame, text="Bem-vindo de volta!", font=("Arial", 20, "bold")).grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky="n")

    ctk.CTkLabel(frame, text="Usuário:", font=("Arial", 12)).grid(row=2, column=0, padx=(0, 10), pady=10, sticky='e')
    entry_usuario = ctk.CTkEntry(frame, placeholder_text="Digite seu usuário", font=("Arial", 12))
    entry_usuario.grid(row=2, column=1, padx=(0, 10), pady=10, sticky='w')

    ctk.CTkLabel(frame, text="Senha:", font=("Arial", 12)).grid(row=3, column=0, padx=(0, 10), pady=10, sticky='e')
    entry_senha = ctk.CTkEntry(frame, placeholder_text="Digite sua senha", show='*', font=("Arial", 12))
    entry_senha.grid(row=3, column=1, padx=(0, 10), pady=10, sticky='w')

    ctk.CTkButton(frame, text="Entrar", font=("Arial", 12, "bold"), command=login).grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="ew")

    progress_bar = ctk.CTkProgressBar(frame, orientation='horizontal', mode='indeterminate')
    progress_bar.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="ew")

    root.mainloop()

configurar_gui()