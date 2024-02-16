# Import libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests
from time import sleep
import re

# Global tuple
property_types = (
    "bodega",
    "casa",
    "departamento",
    "estacionamiento",
    "estudio",
    "hotel",
    "local-comercial",
    "loft",
    "lote-de-cementerio",
    "oficina",
    "parcela",
    "sitio",
    "terreno",
    "terreno-agricola",
    "terreno-forestal",
    "terreno-industrial",
)


# Function to extract numbers from a string
def return_numbers(str_number: str) -> list[int]:
    """Extract numbers from a string using regex \n
    Returns number digits separated in its whole and decimal parts"""

    # Remove "." from the string
    if "." in str_number:
        str_number = str_number.replace(".", "")

    # Return the number digits separated in its whole and decimal parts
    return re.findall(r"\d+", str_number)


def extract_total_pages() -> dict[str, int]:
    """Extract the total number of pages from the website"""

    max_pages_per_type = {}

    for property_type in property_types:

        # Website URL
        url = f"https://chilepropiedades.cl/propiedades/venta/{property_type}/region-metropolitana-de-santiago-rm/0"

        # Set up custom headers with a User-Agent
        # and make a GET request to the specified URL, storing the response text.
        headers = requests.utils.default_headers()  # type: ignore
        headers.update({"User-Agent": "My User Agent 1.0"})
        html_text = requests.get(url=url, headers=headers).text

        # Parse the HTML content of the website using BeautifulSoup
        soup = BeautifulSoup(html_text, "lxml")

        # Find the <span> element that contains the total number of pages
        total_pages_span = soup.find(
            "div",
            class_="clp-results-text-container d-none d-sm-block col-sm-6 text-right",
        )

        # Parse the content of the div to extract the total number of pages
        try:
            max_pages = total_pages_span.text.replace(" ", "").replace("\n", "")
            max_pages = int(return_numbers(max_pages)[0]) + 1
        except AttributeError:
            max_pages = 0

        max_pages_per_type[property_type] = max_pages

    return max_pages_per_type


def find_price(property: str) -> str:
    """Extract price from the house card"""

    price = (
        property.find("a", class_="d-block text-ellipsis clp-big-value")
        .text.replace(" ", "")
        .replace("\n", "")
        .replace("$", "")
    )

    return price


def find_location(property: str) -> list[str]:
    """Extract location from the house card"""

    location = property.h2.a.text.replace(" ", "").replace("\n", "").split(",")

    comuna = location[0]
    ubicacion = location[1].replace("PublicaciónReciente", "")

    return [comuna, ubicacion]


def find_dorms(property: str) -> int:
    """Extract number of dorms from the house card"""

    dorms = property.find("span", title="Habitaciones")

    if dorms == None:
        return 0

    dorms = dorms.text
    dorms = return_numbers(dorms)

    return dorms[0]


def find_baths(property: str) -> int:
    """Extract number of baths from the house card"""

    baths = property.find("span", title="Baños")

    if baths == None:
        return 0

    baths = baths.text
    baths = return_numbers(baths)

    return baths[0]


def find_built_area(property: str) -> int:
    """Extract the built area in sqr meters from the house card"""

    built_area = property.find(
        "span", class_="clp-feature-value", title="Superficie Construida"
    )

    if built_area == None:
        return 0

    built_area = built_area.text
    built_area = return_numbers(built_area)

    return built_area[0]


def find_total_area(property: str) -> int:
    """Extract the total area in sqr meters from the house card"""

    total_area = property.find(
        "span", class_="clp-feature-value", title="Superficie Total"
    )

    if total_area == None:
        return 0

    total_area = total_area.text
    total_area = return_numbers(total_area)

    return total_area[0]


def find_parking(property: str) -> int:
    """Extract the number of parking spaces from the house card"""

    parking = property.find("span", title="Estacionamientos")

    if parking == None:
        return 0

    parking = parking.text
    parking = return_numbers(parking)

    return parking[0]


def find_id(property: str) -> int:
    """Extract the id of the house"""

    id = property.find("div", class_="d-md-flex mt-2 align-items-center").div.text
    id = return_numbers(id)

    return id[0]


def find_realtor(property: str) -> str:
    """Extract the realtor of the house"""

    realtor = property.find("a", class_="imagen-corredora-list-clp")

    if realtor == None:
        return None

    else:
        realtor = realtor.find("img")["title"]

        return realtor


def extract_data(property_types: dict[str, int]) -> pd.DataFrame:
    """Extract data from the website and stores it in a Pandas DataFrame"""

    # Setting up DataFrame for storing the extracted data
    columns = [
        "price",
        "comuna",
        "ubicacion",
        "dorms",
        "baths",
        "built_area",
        "total_area",
        "parking",
        "id",
        "realtor",
        "property_type",
    ]

    properties_df = pd.DataFrame(columns=columns)

    for property_type, num_pages in property_types.items():
        print(f"Extracting property type: {property_type}\n")

        # Iterate over the number of pages
        for page in range(num_pages):

            # According to robots.txt the crawl delay is 2 seconds
            sleep(2)

            print(f"pagina: {page}", end="\r")
            url = f"https://chilepropiedades.cl/propiedades/venta/{property_type}/region-metropolitana-de-santiago-rm/{page}"

            # Set up custom headers with a User-Agent
            # and make a GET request to the specified URL, storing the response text.
            headers = requests.utils.default_headers()
            headers.update({"User-Agent": "My User Agent 1.0"})

            # Try to get the HTML content of the website
            # Possible timeout or connection errors
            try:
                html_text = requests.get(url=url, headers=headers).text
            except:
                print(f"Error en la pagina {page}")
                continue

            # Parse the HTML content of the website using BeautifulSoup
            soup = BeautifulSoup(html_text, "lxml")

            # Find all the <div> elements that contain the house cards
            property_card = soup.find_all(
                "div", class_="clp-publication-element clp-highlighted-container"
            )

            # Iterate over the house cards
            for property in property_card:

                # Setting up list house information
                property_data = {key: None for key in columns}

                # Set up property type
                property_data["property_type"] = property_type

                # Extract price
                property_data["price"] = find_price(property)

                # Extract location
                location = find_location(property)

                property_data["comuna"] = location[0]
                property_data["ubicacion"] = location[1]

                # Extreact number of dorm
                property_data["dorms"] = find_dorms(property)

                # Extract number of bathrooms
                property_data["baths"] = find_baths(property)

                # Extract Built Area
                property_data["built_area"] = find_built_area(property)

                # Extract Total Area
                property_data["total_area"] = find_total_area(property)

                # Extract number of parking
                property_data["parking"] = find_parking(property)

                # Extract id of the house
                property_data["id"] = find_id(property)

                # Extract realtor
                property_data["realtor"] = find_realtor(property)

                # Add the house information dict casa_data into the houses DataFrame casas_df
                properties_df.loc[len(properties_df)] = property_data  # type: ignore

    print("Extraccion Completada!")
    return properties_df


def data_cleaner(
    properties_df: pd.DataFrame, UFtoCLP: float, USDtoCLP: float
) -> pd.DataFrame:
    """
    Clean the data extracted from the website
    Returns a cleaned DataFrame
    """

    # Find the index of homes that are listed in USD and UF
    indices_uf = properties_df[properties_df["price"].str.contains("UF")].index
    indices_usd = properties_df[properties_df["price"].str.contains("USD")].index

    # Cleaning the 'Price' column in the DataFrame by removing currency symbols and thousands separators
    properties_df.loc[indices_uf, "price"] = properties_df.loc[
        indices_uf, "price"
    ].str.replace("UF", "")
    properties_df.loc[indices_usd, "price"] = properties_df.loc[
        indices_usd, "price"
    ].str.replace("USD", "")
    properties_df["price"] = properties_df["price"].str.replace(".", "")

    # Converting the 'Price' column to int64
    properties_df["price"] = properties_df["price"].astype("float64")

    # Transforming UF and USD to CLP
    properties_df.loc[indices_uf, "price"] = (
        properties_df.loc[indices_uf, "price"] * UFtoCLP
    )
    properties_df.loc[indices_usd, "price"] = (
        properties_df.loc[indices_usd, "price"] * USDtoCLP
    )

    # Creating new columns for storing the price in USD
    properties_df["price_USD"] = round(properties_df["price"] / USDtoCLP)
    properties_df["price_UF"] = round(properties_df["price"] / UFtoCLP)

    # Renaming "Price" to "Price_CLP"
    properties_df.rename(columns={"price": "price_CLP"}, inplace=True)
    properties_df["price_CLP"] = round(properties_df["price_CLP"])

    # Rearrenge the columns
    properties_df = properties_df[
        [
            "price_CLP",
            "price_UF",
            "price_USD",
            "comuna",
            "ubicacion",
            "dorms",
            "baths",
            "built_area",
            "total_area",
            "parking",
            "id",
            "realtor",
            "property_type",
        ]
    ]

    # Droping houses that have wrong prices
    bad_data = properties_df[
        (properties_df["price_UF"] > 100_000)
        & (properties_df["property_type"] == "casa")
    ]
    indices_malos = bad_data[
        ~bad_data["comuna"].str.contains("LasCondes|Vitacura|LoBarnechea")
    ].index
    properties_df = properties_df.drop(indices_malos, axis=0)

    bad_data = properties_df[properties_df["price_UF"] < 1_000]
    properties_df = properties_df.drop(bad_data.index, axis=0)

    # Drop houses that have wrong parking values
    bad_data = properties_df[properties_df["parking"] >= 30]
    properties_df = properties_df.drop(bad_data.index, axis=0)

    print("Limpieza Completada!")
    return properties_df
