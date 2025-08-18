from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib3, traceback,certifi,os
from urllib.parse import urljoin, urlparse


head = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0', 
    'Connection': 'keep-alive',
}

def url_scraper(start,end):

    for y in range(start,end+1):
        
        isp_url=f"https://www.ispch.gob.cl/biomedico/vigilancia-de-laboratorio/ambitos-de-vigilancia/vigilancia-virus-respiratorios/informes-virus-respiratorios/?y={y}"

        response = requests.get(isp_url, headers=head,verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        report_page_urls = [a["href"] for a in soup.find_all("div",class_="container")[1].find_all("table")[0].find_all("a")]
        
        pdf_urls = []
        pdf_report_names = []

        for page_url in report_page_urls:
            try:
                report_response = requests.get(page_url, headers=head, verify=False)
                report_soup = BeautifulSoup(report_response.text, 'html.parser')
                pdf_link = report_soup.find("a", href=lambda href: href and ".pdf" in href)

                if pdf_link:
                    pdf_url = urljoin(page_url, pdf_link["href"])
                    pdf_urls.append(pdf_url)
                    # Extraer el nombre del informe de la URL del PDF
                    pdf_name = pdf_url.split('/')[-1].replace('.pdf', '')
                    pdf_report_names.append(pdf_name)
                else:
                    print(f"No se encontró un enlace PDF en: {page_url}")
            except Exception as e:
                print(f"Error procesando la página {page_url}: {e}")

    df=pd.DataFrame(zip(pdf_urls, pdf_report_names),columns=["url","report_name"])
    return df 




def smart_get(url, **kwargs):

    try:
        r = requests.get(url, timeout=60, stream=True, **kwargs)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e: 
        print(f"Error HTTP al obtener {url}: {e}")
        return None 
    except requests.exceptions.SSLError:
        pass  

    try:
        r = requests.get(url, timeout=60, stream=True, verify=certifi.where(), **{k:v for k,v in kwargs.items() if k != "verify"})
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e: 
        print(f"Error HTTP al obtener {url}: {e}")
        return None 
    except requests.exceptions.SSLError:
        pass

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(url, timeout=60, stream=True, verify=False, **{k:v for k,v in kwargs.items() if k != "verify"})
    try:
        r.raise_for_status()
        print("  Aviso: usando verify=False (sin validar certificado).")
        return r
    except requests.exceptions.HTTPError as e: 
        print(f"Error HTTP (fallback) al obtener {url}: {e}")
        return None


def download_pdf(pdf_url, save_path, headers=None):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        resp = smart_get(pdf_url, headers=headers)
        if resp and resp.status_code == 200:

            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"PDF descargado en: {save_path}")
        elif resp is None: # Maneja el caso en que smart_get retorna None por HTTPError
            print(f"Error al descargar el PDF de {pdf_url}: El archivo no se encontró o hubo un problema de red.")
        else:
            print(f"Error: No se pudo descargar {pdf_url}. Código de estado: {resp.status_code}")
    except Exception as e:
        print(f" Error al descargar el PDF: {e}")
        traceback.print_exc()



if __name__ == "__main__":
    BASE_DIR = "informes_respiratorios"
    os.makedirs(BASE_DIR, exist_ok=True)
    df=url_scraper(2019,2025)
    
    for x in range(0,len(df)):
        path = os.path.join("informes_respiratorios", df['report_name'][x] + ".pdf")
        download_pdf(df['url'][x],path,head)