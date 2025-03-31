from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import glob
from download_manager import DownloadManager
from zip_extractor import ZipExtractor

class Scraper:
    def __init__(self, download_manager, zip_extractor, url, chrome_options):
        self.download_manager = download_manager
        self.zip_extractor = zip_extractor
        self.url = url
        self.chrome_options = chrome_options
        self.navegador = None

    def inicia_navegador(self):
        self.navegador = webdriver.Chrome(options=self.chrome_options)
        self.navegador.maximize_window()
        self.navegador.get(self.url)

    def fecha_navegador(self):
        if self.navegador:
            self.navegador.quit()

    def expandir_recursos(self):
        recursos = self.navegador.find_element(By.CLASS_NAME, "botao-collapse-Recursos")
        recursos.click()

    def obter_titulos(self):
        titulos = []
        for ano in range(2020, 2026):
            xpath = f"//h4[contains(text(), '{ano}') and contains(text(), 'Combustíveis Automotivos')]"
            titulos.extend(self.navegador.find_elements(By.XPATH, xpath))
        return titulos

    def inicia_scraping(self):
        self.inicia_navegador()
        self.expandir_recursos()
        titulos = self.obter_titulos()

        for titulo in titulos:
            sucesso = False
            tentativa = 0
            while not sucesso and tentativa < self.download_manager.max_attempts:
                tentativa += 1
                try:
                    print(f"Iniciando tentativa {tentativa} para o título: {titulo.text}")
                    self.download_manager.remove_downloads_incompletos()

                    while not self.download_manager.downloads_finalizados():
                        print("Aguardando que o download anterior termine...")
                        time.sleep(2)

                    arquivos_anteriores = set(glob.glob(os.path.join(self.download_manager.download_dir, '*')))

                    container = titulo.find_element(By.XPATH, "./ancestor::div[1]")
                    botao = container.find_element(By.XPATH, ".//button[contains(., 'Acessar o recurso')]")
                    botao.click()
                    time.sleep(2)

                    novo_arquivo = self.download_manager.aguarda_novo_arquivo(arquivos_anteriores, minutes=3)
                    if not novo_arquivo:
                        raise Exception("Arquivo não foi baixado no tempo esperado.")

                    self.download_manager.aguarda_download_finalizado(novo_arquivo, espera=2)

                    _, extensao = os.path.splitext(novo_arquivo)
                    novo_nome = self.download_manager.sanitiza_nome(titulo.text) + extensao
                    novo_caminho = os.path.join(self.download_manager.download_dir, novo_nome)
                    os.rename(novo_arquivo, novo_caminho)
                    print(f"Arquivo renomeado para: {novo_caminho}")
                    sucesso = True
                except Exception as e:
                    print(f"Tentativa {tentativa} para o título '{titulo.text}' falhou: {e}")
                    time.sleep(2)
            if not sucesso:
                print(f"Falha ao baixar o arquivo para o título '{titulo.text}' após {self.download_manager.max_attempts} tentativas.")
            time.sleep(2)

        while not self.download_manager.downloads_finalizados():
            print("Aguardando downloads finalizarem...")
            time.sleep(2)

        self.zip_extractor.extrai_arquivos_zip(self.download_manager.download_dir)
        print("Todos os downloads foram concluídos e os arquivos ZIP foram extraídos.")
        self.fecha_navegador()
