from functions import load_file, topGames



data = load_file('cos_df.pkl', 'steamcos')

res = topGames(1643320, data, 15)
print(res)
