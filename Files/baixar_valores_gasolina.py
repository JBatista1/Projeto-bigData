from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import glob


def aguarda_novo_arquivo(download_dir, arquivos_anteriores, minutes=3):
    """
    Aguarda que um novo arquivo seja criado na pasta de download que não esteja em 'arquivos_anteriores',
    ignorando arquivos com extensão .crdownload.
    Retorna o caminho do novo arquivo ou None se o tempo limite for atingido.
    """
    timeout = minutes * 60
    tempo_inicial = time.time()
    while time.time() - tempo_inicial < timeout:
        atuais = set(glob.glob(os.path.join(download_dir, '*')))
        novos = atuais - arquivos_anteriores
        # Filtra arquivos que não estejam em download (sem .crdownload)
        novos = {a for a in novos if not a.endswith('.crdownload')}
        if novos:
            return max(novos, key=os.path.getctime)
        time.sleep(1)
    return None


def aguarda_download_finalizado(arquivo, espera=2):
    """
    Aguarda até que o arquivo esteja estável (tamanho não muda por 'espera' segundos).
    """
    stable = False
    while not stable:
        tamanho_inicial = os.path.getsize(arquivo)
        time.sleep(espera)
        tamanho_final = os.path.getsize(arquivo)
        if tamanho_inicial == tamanho_final:
            stable = True


def sanitiza_nome(nome):
    """
    Remove ou substitui caracteres inválidos para nomes de arquivos.
    """
    caracteres_invalidos = '<>:"/\\|?*'
    for char in caracteres_invalidos:
        nome = nome.replace(char, '_')
    return nome.strip()


def downloads_finalizados(download_dir):
    """
    Retorna True se não houver arquivos com extensão .crdownload (downloads em andamento)
    """
    crdownload_files = glob.glob(os.path.join(download_dir, '*.crdownload'))
    return len(crdownload_files) == 0


def remove_downloads_incompletos(download_dir):
    """
    Remove arquivos com extensão .crdownload da pasta de download.
    """
    arquivos_incompletos = glob.glob(os.path.join(download_dir, '*.crdownload'))
    for arquivo in arquivos_incompletos:
        try:
            os.remove(arquivo)
        except Exception as e:
            print(f"Erro ao remover arquivo incompleto {arquivo}: {e}")


# Criando pasta para salvar CSVs
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

navegador = webdriver.Chrome(options=chrome_options)
navegador.maximize_window()
navegador.get("https://dados.gov.br/dados/conjuntos-dados/serie-historica-de-precos-de-combustiveis-e-de-glp")

# Expande a seção de recursos
recursos = navegador.find_element(By.CLASS_NAME, "botao-collapse-Recursos")
recursos.click()

all_titulos = []
for ano in range(2020, 2026):
    xpath = f"//h4[contains(text(), '{ano}') and contains(text(), 'Combustíveis Automotivos')]"
    titulos = navegador.find_elements(By.XPATH, xpath)
    all_titulos.extend(titulos)

max_attempts = 3  # Número máximo de tentativas por arquivo

for titulo in all_titulos:
    sucesso = False
    tentativa = 0
    while not sucesso and tentativa < max_attempts:
        tentativa += 1
        try:
            print(f"Iniciando tentativa {tentativa} para o título: {titulo.text}")
            # Remove downloads incompletos antes de iniciar nova tentativa
            remove_downloads_incompletos(download_dir)

            # Aguarda que não haja downloads em andamento
            while not downloads_finalizados(download_dir):
                print("Aguardando que o download anterior termine...")
                time.sleep(2)

            # Registra os arquivos existentes antes de iniciar o download
            arquivos_anteriores = set(glob.glob(os.path.join(download_dir, '*')))

            # Localiza o container pai do título e o botão para acessar o recurso
            container = titulo.find_element(By.XPATH, "./ancestor::div[1]")
            botao = container.find_element(By.XPATH, ".//button[contains(., 'Acessar o recurso')]")
            botao.click()
            time.sleep(2)  # Aguarda o início do download

            # Aguarda que um novo arquivo apareça
            novo_arquivo = aguarda_novo_arquivo(download_dir, arquivos_anteriores, minutes=3)
            if not novo_arquivo:
                raise Exception("Arquivo não foi baixado no tempo esperado.")

            # Aguarda que o arquivo esteja estável (download concluído)
            aguarda_download_finalizado(novo_arquivo, espera=2)

            # Extrai a extensão e define o novo nome do arquivo
            _, extensao = os.path.splitext(novo_arquivo)
            novo_nome = sanitiza_nome(titulo.text) + extensao
            novo_caminho = os.path.join(download_dir, novo_nome)
            os.rename(novo_arquivo, novo_caminho)
            print(f"Arquivo renomeado para: {novo_caminho}")
            sucesso = True
        except Exception as e:
            print(f"Tentativa {tentativa} para o título '{titulo.text}' falhou: {e}")
            time.sleep(2)  # Aguarda antes de tentar novamente

    if not sucesso:
        print(f"Falha ao baixar o arquivo para o título '{titulo.text}' após {max_attempts} tentativas.")
    time.sleep(2)  # Aguarda antes de passar para o próximo título

# Aguarda que todos os downloads sejam finalizados antes de fechar o navegador
while not downloads_finalizados(download_dir):
    print("Aguardando downloads finalizarem...")
    time.sleep(2)

print("Todos os downloads foram concluídos. O navegador será fechado.")
navegador.quit()
