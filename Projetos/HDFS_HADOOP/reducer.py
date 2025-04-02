# -*- coding: utf-8 -*-

import sys

total = 0
count = 0

for line in sys.stdin:
    try:
        _, preco = line.strip().split("\t")
        total += float(preco)
        count += 1
    except:
        continue

if count > 0:
    print("Preço médio do diesel em SP: {:.2f}".format(total / count))