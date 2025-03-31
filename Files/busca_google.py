#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import glob

# Criando pasta para salvar cvs
download_dir = os.path.join(os.getcwd(), "cvs")
os.makedirs(download_dir, exist_ok=True)

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

navegador = webdriver.Chrome()
navegador.maximize_window()
navegador.get("https://dados.gov.br/dados/conjuntos-dados/serie-historica-de-precos-de-combustiveis-e-de-glp")

# expande
recursos = navegador.find_element(By.CLASS_NAME, "botao-collapse-Recursos")
recursos.click()

all_titulos = []  # Lista para armazenar todos os títulos encontrados

def aguarda_download(download_dir, timeout=30):
    """
    Aguarda até que um novo arquivo seja baixado na pasta download_dir ou até atingir o timeout.
    Retorna o caminho do arquivo baixado ou None caso não encontre.
    """
    tempo_inicial = time.time()
    while True:
        arquivos = glob.glob(os.path.join(download_dir, '*'))
        if arquivos:
            # Retorna o arquivo mais recente (com base na data de criação)
            return max(arquivos, key=os.path.getctime)
        if time.time() - tempo_inicial > timeout:
            break
        time.sleep(1)
    return None

def sanitiza_nome(nome):
    """
    Remove ou substitui caracteres que não são permitidos em nomes de arquivos.
    """
    caracteres_invalidos = '<>:"/\\|?*'
    for char in caracteres_invalidos:
        nome = nome.replace(char, '_')
    return nome.strip()

for ano in range(2020, 2026):
    xpath = f"//h4[contains(text(), '{ano}') and contains(text(), 'Combustíveis Automotivos')]"
    titulos = navegador.find_elements(By.XPATH, xpath)
    # Adiciona os títulos encontrados à lista
    all_titulos.extend(titulos)


for titulo in all_titulos:
    try:
        # A partir do <h4>, sobe para o container pai que deve conter o botão desejado
        container = titulo.find_element(By.XPATH, "./ancestor::div[1]")
        # Dentro do container, localiza o botão que contenha o texto "Recursos"
        container = titulo.find_element(By.XPATH, "./ancestor::div[1]")
        # Dentro do container, localiza o botão que contenha o texto "Recursos"
        botao = container.find_element(By.XPATH, ".//button[contains(., 'Acessar o recurso')]")
        botao.click()
        time.sleep(2)  # Aguarda


    except Exception as e:
        print(f"Erro ao clicar no botão para o título '{titulo.text}': {e}")

time.sleep(20)
