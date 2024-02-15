from datetime import date
import scrapper

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


def main():

    print(
        f"""\n
    WEB SCRAPER PROPIEDADES SANTIAGO 2.0
    Desarrollado por: chucrut123
    Fecha de ejecucion: {date.today()}
    Pagina web: https://chilepropiedades.cl/propiedades/venta/casa/region-metropolitana-de-santiago-rm/
    Version: 2.0
    """
    )

    # Gets max number of pages to scrape
    print("Obteniendo numero de propiedades...")
    max_pages = scrapper.extract_total_pages()

    print("Numero de paginas por tipo de propiedad:", *max_pages.items(), sep="\n")

    properties_types_scraped = {}

    for property_type in property_types:

        type_answer = input(
            f"Desea selecionar propiedades del tipo {property_type}?  ([y]: si  [n]: no  [A]: si a todos)\n"
        )

        if type_answer.lower() == "y":
            properties_types_scraped[property_type] = max_pages[property_type]

        elif type_answer == "A":
            properties_types_scraped = max_pages
            break

        elif type_answer.lower() != "n":
            print("Input no valido. Interpretado como [n]: no")

    print(*properties_types_scraped.items(), sep="\n")

    # Ask user for curency exchange rates
    UFtoCLP = round(float(input("Ingrese el valor de la UF en CLP: ")))
    USDtoCLP = round(float(input("Ingrese el valor del USD en CLP: ")))

    data = scrapper.extract_data(property_types=properties_types_scraped)

    while True:
        check_cleaner = input("Desea limpiar los datos? (y/n): ").lower()

        if check_cleaner == "y":
            data = scrapper.data_cleaner(data, UFtoCLP, USDtoCLP)
            break

        elif check_cleaner == "n":
            break

        else:
            pass

    while True:
        csv_save = input("Desea guardar los datos en un archivo csv? (y/n): ").lower()

        if csv_save == "y":
            data.to_csv(f"{date.today()}-Propiedades-Web-Scrape.csv", index=False)
            break

        elif csv_save == "n":
            break

        else:
            pass


main()
