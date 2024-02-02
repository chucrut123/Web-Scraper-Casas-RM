from datetime import date
import scrapper

print(f"""\n
WEB SCRAPER PROPIEDADES SANTIAGO 2.0
Desarrollado por: chucrut123
Fecha de ejecucion: {date.today()}
Pagina web: https://chilepropiedades.cl/propiedades/venta/casa/region-metropolitana-de-santiago-rm/
Version: 2.0
""")

# Gets max number of pages to scrape
max_pages = scrapper.extract_total_pages()

# Ask user for curency exchange rates
UFtoCLP = round(float(input("Ingrese el valor de la UF en CLP: ")))
USDtoCLP = round(float(input("Ingrese el valor del USD en CLP: ")))


print(f"\nSe encontraron un total de {max_pages} paginas")
num_pages = int(input("Ingrese el numero de paginas a scrapear: "))
start_point = int(input("Ingrese el numero de pagina donde desea comenzar: "))

if start_point < 0:
    start_point = 0

data = scrapper.extract_data(num_pages, start_point)

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
        data.to_csv(f"{date.today()} Propiedades Web Scrape.csv", index=False)
        break

    elif csv_save == "n":
        break

    else:
        pass