import os
import re

DIRECTORY = "informes_respiratorios"

def rename_pdfs():
    print(f"Renombrando PDFs en el directorio: {DIRECTORY}")
    for filename in os.listdir(DIRECTORY):
        if filename.endswith(".pdf"):
            match = re.search(r"SE\.?(\d{1,2})\s+(\d{2}-\d{2}-\d{4})", filename)
            if match:
                se_number = match.group(1)
                date = match.group(2)
                new_filename = f"SE{se_number}_{date}.pdf"
                
                old_filepath = os.path.join(DIRECTORY, filename)
                new_filepath = os.path.join(DIRECTORY, new_filename)

                if old_filepath != new_filepath:
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f"Renombrado: {filename} -> {new_filename}")
                    except OSError as e:
                        print(f"Error al renombrar {filename}: {e}")
                else:
                    print(f"El archivo {filename} ya tiene el formato correcto o no se encontró un patrón coincidente para renombrar.")
            else:
                print(f"No se encontró el patrón para renombrar en: {filename}")

if __name__ == "__main__":
    rename_pdfs()
