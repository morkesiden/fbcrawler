import sys
from lib.m_sql import stats_
from lib.m_tools import reaction2name

max = sys.argv[1] if len(sys.argv) > 1 else 5

class Colores:
    AZUL = "\033[94m"
    AMARILLO = "\033[93m"
    ROJO = "\033[91m"
    MORADO = "\033[95m"
    MORADO2 = "\033[95m"
    RESET = "\033[0m"  


def color_reaction(reaction):

    reaction_name = reaction2name(reaction)

    if reaction_name == 'Like':  return Colores.AZUL + reaction_name + Colores.RESET
    if reaction_name == 'Love':  return Colores.MORADO + reaction_name + Colores.RESET
    if reaction_name == 'Angry':  return Colores.ROJO + reaction_name + Colores.RESET
    if reaction_name == 'Care':  return Colores.MORADO2 + reaction_name + Colores.RESET
    if reaction_name == 'Haha':  return Colores.AMARILLO + reaction_name + Colores.RESET

    return reaction_name
    

print('\n')
rows = stats_(max)

for row in rows:
    print(f"reactions_count: {row[2]}\tprefer: {color_reaction(row[1])}\tprofile_url: {row[0]}")

