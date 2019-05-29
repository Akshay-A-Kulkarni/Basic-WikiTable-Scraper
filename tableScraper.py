import wikipedia as wiki
import string
import pandas as pd
from pandas.io.html import read_html

seedpage = wiki.page("List of United States cities by population")

url = seedpage.url

wikitables = read_html(url,  attrs={"class":"wikitable sortable"})

print ("Extracted {num} wikitables".format(num=len(wikitables)))
print (url)
table_df = wikitables[0]


def removecite(x):
    ''' Simple fucntion to remove citations from scraped table'''
    if type(x) == str:
        return x.partition('[')[0]
    else:
        return x
    
def getsummary(x):
    summaries = []
    for city in list(x):
        try:
            summary = wiki.page(city,auto_suggest=True, redirect=True).summary
        except (wikipedia.exceptions.DisambiguationError) as e:
            summary = "Summary not fetched due to disambiguation"
        summaries.append(summary)
    return summaries
    

table_df = table_df.applymap(removecite) # mapping removecite function on all values to clean text.

table_df = table_df.rename(columns=table_df.iloc[0])
table_df = table_df.drop([0])
col_names = ["2018 Rank","City","State","2018 Estimate","2010 Census","Change %","2016 land area(sq mi)","2016 land area (km sq)",
             "2016 population density (/sq mi)","2016 population density (/km sq)","Location"] # changing column names.
table_df = table_df.set_axis(col_names, axis=1, inplace=False)

# gathering all summaries.
all_summs = getsummary(table_df["City"])

table_df["Summary"] = all_summs


## CLEANING DATA ##

# Stripping % symbol from values 
table_df["Change %"] = table_df['Change %'].str.replace("%","")

# Stripping units from area metrics

table_df['2016 land area(sq mi)'] = table_df['2016 land area(sq mi)'].str.replace('([sq mi])', '')
table_df['2016 population density (/sq mi)'] = table_df['2016 population density (/sq mi)'].str.replace('([/sq mi])', '')

table_df['2016 land area (km sq)'] = table_df['2016 land area (km sq)'].str.replace('km2', '')
table_df['2016 population density (/km sq)'] = table_df['2016 population density (/km sq)'].str.replace('/km2', '')


# splitting the location cols for individual lats and longs 
table_df["Location"] = table_df['Location'].str.rpartition('/')[2]   # removing redundancy

table_df['Latitude'] = table_df['Location'].str.rpartition(' ')[0].str.replace("([°,N,W])", "") # strip °N & °W from lat and long.
table_df['Longitude'] = table_df['Location'].str.rpartition(' ')[2].str.replace("([°,N,W])", "")



table_df.to_csv("scraped_data.csv",encoding='utf-8-sig',index=False) # using utf-8-sig encoding to strip off the UTF-8 Byte Order Mark

