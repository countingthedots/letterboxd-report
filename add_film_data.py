import requests

headers = {
    "accept": "application/json",
    "Authorization" : "", #put you TMDB api key here
}

# Get genres


genres_dict = dict()

genres_json = requests.get("https://api.themoviedb.org/3/genre/movie/list?language=en", headers=headers).json()["genres"]
for genre in genres_json:
    genres_dict[genre["id"]] = genre["name"]

#Get countries
countries_dict = dict()
counties_json = requests.get("https://api.themoviedb.org/3/configuration/countries?language=en-US", headers=headers).json()
for country in counties_json:
    countries_dict[country["iso_3166_1"]] = country["english_name"]


# Get movies
import pandas as pd

df = pd.read_csv("diary.csv")

df["Genre"] = None
df["Language"] = None
df["Country"] = None
df["Director"] = None
df["Revenue"] = None
df["Budget"] = None


for index, row in df.iterrows():
    print(index)
    url = f"https://api.themoviedb.org/3/search/movie?query={row['Name']}&page=1&year={row['Year']}"
    results = requests.get(url, headers=headers).json()["results"]
    if len(results) > 0:
        first_element = results[0]
        id = first_element["id"]

        #get genre
        genres = first_element["genre_ids"]
        if len(genres) > 0:
            df.at[index, "Genre"] = genres_dict[genres[0]]
        else:
            df.at[index, "Genre"] = "Unknown"	
        
        
        movie = requests.get(f"https://api.themoviedb.org/3/movie/{id}", headers=headers).json()

        #get country and language
        countries = movie["origin_country"]
        if len(countries) > 0:
            df.at[index, "Country"] = countries_dict[countries[0]]
        else:
            df.at[index, "Country"] = "Unknown"

        df.at[index, "Language"] = first_element["original_language"]

        #get revenue and budget
        df.at[index, "Revenue"] = movie["revenue"]
        df.at[index, "Budget"] = movie["budget"]

        #get director
        crew = requests.get(f"https://api.themoviedb.org/3/movie/{id}/credits", headers=headers).json()["crew"]
        df.at[index, "Director"] = next((person["name"] for person in crew if person["job"] == "Director"), None)
    
print(df)
df["Rating"].fillna(0, inplace=True)
df['Rating'] = df['Rating'].apply(lambda x: '{:,.2f}'.format(x).replace('.', ','))
df.to_csv("diary_with_genre.tsv", sep="\t", index=False)