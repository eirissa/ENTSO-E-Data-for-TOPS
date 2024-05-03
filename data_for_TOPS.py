from entsoe import EntsoePandasClient
import pandas as pd
from dotenv import load_dotenv
import os

# Set up time range
start = pd.Timestamp('20240414', tz='Europe/Brussels') #yyyymmdd
end = pd.Timestamp('20240415', tz='Europe/Brussels')

# Get the API key
load_dotenv()
client = EntsoePandasClient(api_key=os.environ.get('api_key'))

# Areas of the Nordic 45 model
areas = ['NO_1', 'NO_2', 'NO_3', 'NO_4', 'NO_5', 'SE_1', 'SE_2', 'SE_3', 'SE_4', 'FI']

# International power cable links:
links = ['NO_2-DE', 'NO_2-GB', 'NO_2-DK','NO_2-NL', 'SE_3-DK', 'SE_4-DK', 'SE_4-PL', 'SE_4-DE', 'SE_4-LT', 'FI-EE', 'FI-RU']

# Dictionary to store indexes for each area
exchange_index = {area: [] for area in areas}

# Set to store unique (from_country, to_country) combinations
queried_combinations = set()

# Iterate through areas
for area in areas:
    # Iterate through links
    for index, link in enumerate(links):
        # Check if the area is present in the link
        if area in link:
            exchange_index[area].append(index)

# Initialize empty lists to store data for all areas
generation_data = []
load_data = []
exchange_data = []
hour = 17  #    0<= hour<24

for area in areas:
    index_list = []
    for index, link in enumerate(links):
        # Check if the area is present in the link
        if area in link:
            index_list.append(index)

    generation = client.query_generation(area, start=start, end=end).iloc[[hour]]
    generation['Area Code'] = area

    load = client.query_load(area, start=start, end=end).iloc[[hour]]
    load['Area Code'] = area

    #print(index_list)

    if index_list:
        for index in index_list:
            from_country = area.split('_')[0]
            to_country = links[index].split('-')[1]

            # Check if this combination has already been queried
            combination = (from_country, to_country)
            if combination not in queried_combinations:
                exchange = client.query_crossborder_flows(
                    country_code_from=from_country, country_code_to=to_country, start=start, end=end).iloc[[hour]]
                # Add the combination to the set, so the same query_crossborder_fows is not run multiple times
                queried_combinations.add(combination)

                exchange = exchange.to_frame()
                exchange['Transfer codes'] = area + '-' + to_country
                #exchange = exchange.rename_axis('Transfer codes')
                exchange_data.append(exchange)
            else:
                target_dataframe, idx = next(((df, idx) for idx, df in enumerate(exchange_data) if \
                                         from_country in df['Transfer codes'].values[0] \
                                         and to_country in df['Transfer codes'].values[0]), (None, None))

                if target_dataframe is not None:
                    print('Items\n', target_dataframe['Transfer codes'])
                    print(target_dataframe['Transfer codes'] )
                    target_dataframe['Transfer codes'].values[0]\
                        = target_dataframe['Transfer codes'].values[0].split('_')[0] + '-'\
                        + target_dataframe['Transfer codes'].values[0].split('-')[1]
                    del exchange_data[idx]
                    exchange_data.append(target_dataframe)

    load_data.append(load)
    generation_data.append(generation)
    #print(exchange_data)


# Concatenate DataFrames only once
generation_data = pd.concat(generation_data, ignore_index=True)
load_data = pd.concat(load_data, ignore_index=True)
exchange_data = pd.concat(exchange_data, ignore_index=True)

agr_generation_data = generation_data.groupby("Area Code").sum()
agr_generation_data['Power generation'] = agr_generation_data.sum(axis=1)
agr_generation_data = agr_generation_data[['Power generation']]

agr_load_data = load_data.groupby("Area Code").sum()
agr_load_data['Power consumption'] = agr_load_data.sum(axis=1)
agr_load_data = agr_load_data[['Power consumption']]

agr_exchange_data = exchange_data.groupby("Transfer codes").sum()
agr_exchange_data['Power transfer'] = agr_exchange_data.sum(axis=1)
agr_exchange_data = agr_exchange_data[['Power transfer']]

# Create an ExcelWriter object and specifying location
with pd.ExcelWriter('C:/Users/eirik/OneDrive - NTNU/Master/dataframes_transparency_compare.xlsx',
                        engine='openpyxl') as writer:

    # Save the first DataFrame to the first sheet
    agr_generation_data.to_excel(writer, sheet_name='Aggr_generation', index=True)

    # Save the second DataFrame to a second sheet
    agr_load_data.to_excel(writer, sheet_name='Aggr_load', index=True)

    # Save the third DataFrame to the first sheet
    agr_exchange_data.to_excel(writer, sheet_name='aggr_exchange', index=True)
print('Files to saved to excel successfully')
