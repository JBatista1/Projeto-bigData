import os
import glob
import time

class DownloadManager:
    def __init__(self, download_dir, max_attempts=3, seconds_in_minute=60):
        self.download_dir = download_dir
        self.max_attempts = max_attempts
        self.seconds_in_minute = seconds_in_minute

    def aguarda_novo_arquivo(self, arquivos_anteriores, minutes=3):
        timeout = minutes * self.seconds_in_minute
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < timeout:
            atuais = set(glob.glob(os.path.join(self.download_dir, '*')))
            novos = atuais - arquivos_anteriores
            novos = {a for a in novos if not a.endswith('.crdownload')}
            if novos:
                return max(novos, key=os.path.getctime)
            time.sleep(1)
        return None

    def aguarda_download_finalizado(self, arquivo, espera=2):
        stable = False
        while not stable:
            tamanho_inicial = os.path.getsize(arquivo)
            time.sleep(espera)
            tamanho_final = os.path.getsize(arquivo)
            if tamanho_inicial == tamanho_final:
                stable = True

    def sanitiza_nome(self, nome):
        caracteres_invalidos = '<>:"/\\|?*'
        for char in caracteres_invalidos:
            nome = nome.replace(char, '_')
        return nome.strip()

    def downloads_finalizados(self):
        crdownload_files = glob.glob(os.path.join(self.download_dir, '*.crdownload'))
        return len(crdownload_files) == 0

    def remove_downloads_incompletos(self):
        arquivos_incompletos = glob.glob(os.path.join(self.download_dir, '*.crdownload'))
        for arquivo in arquivos_incompletos:
            try:
                os.remove(arquivo)
            except Exception as e:
                print(f"Erro ao remover arquivo incompleto {arquivo}: {e}")
