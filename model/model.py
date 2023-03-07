from functions import load_file, topGames



# Load the matrix from S3 bucket
data = load_file('cos_df.pkl', 'steamcos')

# Request top 15 games
res = topGames(1643320, data, 15)
print(res)
