#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

def main():
    current_key = None
    total_price = 0.0
    total_count = 0

    # Cada linha deve estar no formato: key \t price \t count
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split('\t')
        if len(parts) != 3:
            continue

        key, price_str, count_str = parts

        try:
            price = float(price_str)
            count = int(count_str)
        except Exception:
            continue

        # Se for o mesmo key, acumula; senão, emite o resultado do key anterior
        if current_key is None:
            current_key = key

        if key == current_key:
            total_price += price
            total_count += count
        else:
            if total_count != 0:
                average = total_price / total_count
                sys.stdout.write("{0}\t{1:.2f}\n".format(current_key, average))
            # Reinicia para o novo key
            current_key = key
            total_price = price
            total_count = count

    # Emite o último agrupamento
    if current_key is not None and total_count != 0:
        average = total_price / total_count
        sys.stdout.write("{0}\t{1:.2f}\n".format(current_key, average))

if __name__ == '__main__':
    main()
