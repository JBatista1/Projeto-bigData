import sys
import csv

for line in sys.stdin:
    try:
        row = next(csv.reader([line]))
        estado = row[1]
        combustivel = row[2].lower()
        preco_venda = row[8]

        if estado == "SP" and "diesel" in combustivel:
            print(f"{combustivel}\t{preco_venda}")
    except:
        continue
