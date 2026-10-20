def calculer_quantite(capital, prix, cfg):
    """Quantité de BTC à acheter pour risquer ~1 % du capital si le stop (2 %) est touché."""
    risque_max = capital * cfg["risk_per_trade_pct"] / 100
    perte_par_unite = prix * cfg["stop_loss_pct"] / 100
    quantite = risque_max / perte_par_unite
    # Plafond d'exposition : jamais plus de 30 % du capital engagé
    quantite_max = capital * cfg["max_total_exposure_pct"] / 100 / prix
    return round(min(quantite, quantite_max), 5)


def prix_stop_loss(prix, cfg):
    return round(prix * (1 - cfg["stop_loss_pct"] / 100), 2)


def peut_acheter(position_ouverte, quantite):
    """On n'achète pas si on est déjà en position ou si la quantité est nulle."""
    return (not position_ouverte) and quantite > 0


if __name__ == "__main__":
    from analyse import charger_config

    cfg = charger_config()
    capital, prix = 10000.0, 81500.0
    q = calculer_quantite(capital, prix, cfg)
    print(f"Quantité : {q} BTC (~{q * prix:.2f} USDT)")
    print(f"Stop loss : {prix_stop_loss(prix, cfg)}")