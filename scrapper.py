#Import libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests
from time import sleep
import re


# Function to extract numbers from a string
def return_numbers(str_number: str) -> list[int]:
    """ Extract numbers from a string using regex \n
        Returns number digits separated in its whole and decimal parts """

    # Remove "." from the string
    if "." in str_number:
        str_number = str_number.replace(".","")

    # Return the number digits separated in its whole and decimal parts
    return re.findall(r'\d+', str_number)


# Function to extract the value of UF and USD
def extract_valor_UF_USD() -> list:

    # Type in converstion rates
    # UF to CLP
    # USD to CLP

    indicador_UF = 36_720
    indicador_USD = 946

    return [indicador_UF, indicador_USD]


def extract_total_pages() -> int:
    """ Extract the total number of pages from the website """

    # Website URL
    url = f"https://chilepropiedades.cl/propiedades/venta/casa/region-metropolitana-de-santiago-rm/0"


    # Set up custom headers with a User-Agent
    # and make a GET request to the specified URL, storing the response text.
    headers = requests.utils.default_headers()# type: ignore
    headers.update({'User-Agent': 'My User Agent 1.0'})
    html_text = requests.get(url= url, headers=headers).text

    # Parse the HTML content of the website using BeautifulSoup
    soup = BeautifulSoup(html_text, "lxml")

    # Find the <span> element that contains the total number of pages
    total_pages_span = soup.find("div", class_="clp-results-text-container d-none d-sm-block col-sm-6 text-right")
    
    # Parse the content of the div to extract the total number of pages
    max_pages = total_pages_span.text.replace(" ","").replace("\n","")

    return int(return_numbers(max_pages)[0]) + 1


def find_price(casa: str) -> str:
    """ Extract price from the house card """

    price = casa.find("a", class_="d-block text-ellipsis clp-big-value").text.replace(" ","").replace("\n","").replace("$","")

    return price


def find_location(casa: str) -> list[str]:
    """ Extract location from the house card """

    location = casa.h2.a.text.replace(" ","").replace("\n","").split(",")

    comuna = location[0]
    ubicacion = location[1].replace("PublicaciónReciente","")

    return [comuna, ubicacion]


def find_dorms(casa: str) -> int:
    """ Extract number of dorms from the house card """

    dorms = casa.find("span", title="Habitaciones")

    if dorms == None:
        return 0
    
    dorms = dorms.text
    dorms = return_numbers(dorms)
    
    return dorms[0]


def find_baths(casa: str) -> int:
    """ Extract number of baths from the house card """

    baths = casa.find("span", title="Baños")

    if baths == None:
        return 0
    
    baths = baths.text
    baths = return_numbers(baths)
    
    return baths[0]


def find_built_area(casa: str) -> int:
    """ Extract the built area in sqr meters from the house card """

    built_area = casa.find("span", class_="clp-feature-value", title="Superficie Construida")

    if built_area == None:
        return 0
    
    built_area = built_area.text
    built_area = return_numbers(built_area)
    
    return built_area[0]


def find_total_area(casa: str) -> int:
    """ Extract the total area in sqr meters from the house card """

    total_area = casa.find("span", class_="clp-feature-value", title="Superficie Total")

    if total_area == None:
        return 0
    
    total_area = total_area.text
    total_area = return_numbers(total_area)
    
    return total_area[0]


def find_parking(casa: str) -> int:
    """ Extract the number of parking spaces from the house card """

    parking = casa.find("span", title="Estacionamientos")

    if parking == None:
        return 0
    
    parking = parking.text
    parking = return_numbers(parking)
    
    return parking[0]


def find_id(casa: str) -> int:
    """ Extract the id of the house """

    id = casa.find("div", class_="d-md-flex mt-2 align-items-center").div.text
    id = return_numbers(id)
    
    return id[0]

def find_realtor(casa: str) -> str:
    """ Extract the realtor of the house """

    realtor = casa.find("a", class_="imagen-corredora-list-clp")

    if realtor == None:
        return None
    
    else:
        realtor = realtor.find("img")["title"]
        
        return realtor


def extract_data(num_pages: int, start_point: int) -> pd.DataFrame:
    """ Extract data from the website and stores it in a Pandas DataFrame """

    # Setting up DataFrame for storing the extracted data
    columns = ["Price", "Comuna", "Ubicacion", "Dorms", "Baths",
               "Built Area", "Total Area", "Parking","id","Realtor"]

    casas_df = pd.DataFrame(columns=columns)

    # Iterate over the number of pages
    for page in range(start_point, num_pages):

        # According to robots.txt the crawl delay is 2 seconds
        sleep(2)

        print(f"pagina: {page}")
        url = f"https://chilepropiedades.cl/propiedades/venta/casa/region-metropolitana-de-santiago-rm/{page}"

        # Set up custom headers with a User-Agent
        # and make a GET request to the specified URL, storing the response text.
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'My User Agent 1.0'})

        # Try to get the HTML content of the website
        # Possible timeout or connection errors
        try:
            html_text = requests.get(url= url, headers=headers).text
        except:
            print(f"Error en la pagina {page}")
            continue

        # Parse the HTML content of the website using BeautifulSoup
        soup = BeautifulSoup(html_text, "lxml")

        # Find all the <div> elements that contain the house cards
        casa_card = soup.find_all("div", class_="clp-publication-element clp-highlighted-container")

        # Iterate over the house cards
        for casa in casa_card:

            # Setting up list house information
            casa_data = {key: None for key in columns}

            # Extract price
            casa_data["Price"] = find_price(casa)


            # Extract location
            location = find_location(casa)

            casa_data["Comuna"] = location[0]
            casa_data["Ubicacion"] = location[1]


            # Extreact number of dorm
            casa_data["Dorms"] = find_dorms(casa)


            # Extract number of bathrooms
            casa_data["Baths"] = find_baths(casa)


            # Extract Built Area
            casa_data["Built Area"] = find_built_area(casa)


            # Extract Total Area
            casa_data["Total Area"] = find_total_area(casa)
            

            # Extract number of Parking
            casa_data["Parking"] = find_parking(casa)


            # Extract id of the house
            casa_data["id"] = find_id(casa)


            # Extract realtor
            casa_data["Realtor"] = find_realtor(casa)


            # Add the house information dict casa_data into the houses DataFrame casas_df  
            casas_df.loc[len(casas_df)] = casa_data # type: ignore
            
    print("Extraccion Completada!")
    return casas_df


def data_cleaner(casas_df: pd.DataFrame, UFtoCLP: float, USDtoCLP: float) -> pd.DataFrame:
    """ Clean the data extracted from the website \n
        Returns a cleaned DataFrame """

    # Find the index of homes that are listed in USD and UF
    indices_uf = casas_df[casas_df["Price"].str.contains("UF")].index
    indices_usd = casas_df[casas_df["Price"].str.contains("USD")].index

    # Cleaning the 'Price' column in the DataFrame by removing currency symbols and thousands separators
    casas_df.loc[indices_uf, "Price"] = casas_df.loc[indices_uf, "Price"].str.replace("UF","")
    casas_df.loc[indices_usd, "Price"] = casas_df.loc[indices_usd, "Price"].str.replace("USD","")
    casas_df["Price"] = casas_df["Price"].str.replace(".","")

    # Converting the 'Price' column to int64
    casas_df["Price"] = casas_df["Price"].astype("int64")

    # Transforming UF and USD to CLP
    casas_df.loc[indices_uf, "Price"] = casas_df.loc[indices_uf, "Price"] * UFtoCLP
    casas_df.loc[indices_usd, "Price"] = casas_df.loc[indices_usd, "Price"] * USDtoCLP

    # Creating new columns for storing the price in USD 
    casas_df["Price_USD"] = round(casas_df["Price"] / USDtoCLP)
    casas_df["Price_UF"] = round(casas_df["Price"] / UFtoCLP)

    # Renaming "Price" to "Price_CLP"
    casas_df.rename(columns= {"Price":"Price_CLP"}, inplace=True)

    # Rearrenge the columns
    casas_df = casas_df[["Price_CLP","Price_UF","Price_USD",'Comuna', 'Ubicacion', 'Dorms', 'Baths', 'Built Area', 'Total Area', 'Parking', 'id', 'Realtor']]

    # Droping houses that have wrong prices
    bad_data = casas_df[casas_df["Price_UF"] > 100_000]
    indices_malos = bad_data[~bad_data['Comuna'].str.contains('LasCondes|Vitacura|LoBarnechea')].index
    casas_df = casas_df.drop(indices_malos, axis=0)

    bad_data = casas_df[casas_df["Price_UF"] < 1_000]
    casas_df = casas_df.drop(bad_data.index, axis=0)

    # Convert "Parking" column to numeric values
    casas_df["Parking"] = pd.to_numeric(casas_df["Parking"], errors="coerce")

    # Drop houses that have wrong parking values
    bad_data = casas_df[casas_df["Parking"] >= 30]
    casas_df = casas_df.drop(bad_data.index, axis=0)

    print("Limpieza Completada!")
    return casas_df
