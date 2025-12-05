import csv
from pathlib import Path
import re

CSV_PATH = Path('prueba_datos.csv')
TEMPLATE = 'Ve a Google y busca ${busqueda}. Luego realiza ${accion}.'

def interpolate(template: str, row: dict) -> str:
    def repl(match):
        key = match.group(1)
        return row.get(key, '')
    return re.sub(r'\$\{([^}]+)\}', repl, template)


def main():
    if not CSV_PATH.exists():
        print('CSV no encontrado:', CSV_PATH)
        return
    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompt = interpolate(TEMPLATE, row)
            print(f"Prompt generado: {prompt}")

if __name__ == '__main__':
    main()
