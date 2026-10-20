import json
import os

FICHIER = "etat.json"


def charger_etat():
    if not os.path.exists(FICHIER):
        return {"position": None}
    with open(FICHIER, encoding="utf-8") as f:
        return json.load(f)


def sauver_etat(etat):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=2)


def ouvrir_position(symbole, quantite, prix_entree, prix_stop, id_stop):
    sauver_etat({
        "position": {
            "symbole": symbole,
            "quantite": quantite,
            "prix_entree": prix_entree,
            "prix_stop": prix_stop,
            "id_stop": id_stop,
        }
    })


def fermer_position():
    sauver_etat({"position": None})


def position_ouverte():
    return charger_etat()["position"]


if __name__ == "__main__":
    print("Position actuelle :", position_ouverte())