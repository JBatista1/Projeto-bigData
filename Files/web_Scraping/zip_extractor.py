import os
import zipfile

class ZipExtractor:
    def extrai_arquivos_zip(self, diretorio_zip, diretorio_saida=None):
        if diretorio_saida is None:
            diretorio_saida = diretorio_zip

        arquivos_zip = [arquivo for arquivo in os.listdir(diretorio_zip) if arquivo.lower().endswith('.zip')]
        if not arquivos_zip:
            print("Nenhum arquivo ZIP encontrado em", diretorio_zip)
            return

        for arquivo_zip in arquivos_zip:
            caminho_zip = os.path.join(diretorio_zip, arquivo_zip)
            base_nome = os.path.splitext(arquivo_zip)[0]
            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    infos = [info for info in zip_ref.infolist() if not info.is_dir()]
                    total = len(infos)
                    if total == 0:
                        print(f"O arquivo ZIP {arquivo_zip} não contém arquivos para extração.")
                        continue

                    for idx, info in enumerate(infos, start=1):
                        nome_original = os.path.basename(info.filename)
                        _, ext = os.path.splitext(nome_original)
                        if total == 1:
                            novo_nome = base_nome + ext
                        else:
                            novo_nome = f"{base_nome}_{idx}{ext}"
                        caminho_saida = os.path.join(diretorio_saida, novo_nome)

                        with zip_ref.open(info) as origem, open(caminho_saida, 'wb') as destino:
                            destino.write(origem.read())
                        print(f"Extraído e renomeado: {novo_nome}")
                os.remove(caminho_zip)
                print(f"Arquivo ZIP {arquivo_zip} removido após extração.")
            except Exception as e:
                print(f"Erro ao extrair {arquivo_zip}: {e}")
