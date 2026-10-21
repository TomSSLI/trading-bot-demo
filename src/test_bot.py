import os
import sys

import bot
from etat import position_ouverte, fermer_position

# On part d'une mémoire propre (le test ne touche qu'à etat.json)
fermer_position()

print("=== TEST 1 : signal ACHAT forcé ===")
bot.decider = lambda df, cfg: "ACHAT"
print(bot.executer())
print("Mémoire :", position_ouverte())

if position_ouverte() is None:
    sys.exit("L'achat n'a pas été mémorisé : on s'arrête.")

print()
print("=== TEST 2 : signal ATTENTE (doit garder la position) ===")
bot.decider = lambda df, cfg: "ATTENTE"
print(bot.executer())

print()
print("=== TEST 3 : signal VENTE forcé ===")
bot.decider = lambda df, cfg: "VENTE"
print(bot.executer())
print("Mémoire :", position_ouverte())