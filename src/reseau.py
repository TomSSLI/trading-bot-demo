import time

import requests


def get_avec_reessai(url, essais=3, pause=3, **kwargs):
    """GET avec quelques nouvelles tentatives en cas de coupure réseau."""
    for i in range(essais):
        try:
            reponse = requests.get(url, **kwargs)
            reponse.raise_for_status()
            return reponse
        except requests.exceptions.RequestException:
            if i == essais - 1:
                raise
            time.sleep(pause)