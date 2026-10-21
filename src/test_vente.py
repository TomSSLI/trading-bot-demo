import bot

bot.decider = lambda df, cfg: "VENTE"
print(bot.executer())