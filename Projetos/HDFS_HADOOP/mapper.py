#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import csv


def main():
    # Usamos csv.reader com o delimitador ';'
    reader = csv.reader(sys.stdin, delimiter=';')
    header = True  # para descartar a linha de cabeçalho
    for row in reader:
        # Verifica se é a linha de cabeçalho e pula
        if header:
            header = False
            continue

        # Verifica se a linha tem o número esperado de colunas
        if len(row) < 13:
            continue

        # Indices:
        # row[1]: Estado - Sigla
        # row[10]: Produto
        # row[12]: Valor de Venda
        if row[1].strip().upper() == "SP" and "DIESEL" in row[10].upper():
            try:
                # Converter "Valor de Venda" para float (substituindo vírgula por ponto)
                price = float(row[12].strip().replace(",", "."))
                # Imprime o par key-value: key, price, count (todos separados por tab)
                sys.stdout.write("diesel_sp\t{0}\t{1}\n".format(price, 1))
            except Exception:
                # Se ocorrer erro na conversão, ignora a linha
                continue


if __name__ == '__main__':
    main()
