#!/usr/bin/env python
# coding: utf-8

# # Web Scrapping a tiendas

# web scrapping a Dia

# In[5]:


paginas = {
    'supermercados_dia': {
        'url_base': 'https://diaonline.supermercadosdia.com.ar',
        'selectores': {
            'productos': '#gallery-layout-container div',
            'titulo': 'h3',
            'precio': 'vtex-product-price-1-x-currencyContainer',
            'imagen': 'img',
        },
        'categorias': {
            'bebidas': {
                'gaseosas': ['pomelo', 'cola', 'lima-limon', 'tonica', 'naranja'],
                'cervezas': ['rubia', 'roja', 'negra'],
                'aguas': ['aguas-sin-gas', 'aguas-con-gas', 'aguas-saborizadas'],
                'bodega': ['vino-tinto', 'vino-blanco', 'vino-rosado', 'espumantes', 'sidras'],
                'jugos-e-isotonicas': ['jugos-en-polvo', 'jugos-listos', 'isotonicas-y-energizantes', 'jugos-naturales'],
                'aperitivos': ['amargos', 'vermouth'],
                'bebidas-blancas-y-licores': ['ron-y-vodka', 'whisky', 'licores'],
            },
            'almacen': {
                'conservas': ['conservas-de-pescados', 'conservas-de-vegetales', 'conservas-de-frutas', 'tomates-y-salsas'],
                'aceites-y-aderezos': ['aceites-de-girasol', 'aceites-de-oliva', 'acetos-vinagres-y-limon', 'aceites-de-soja', 'especias', 'sal', 'ketchup', 'mayonesa', 'mostaza', 'salsa-golf'],
                'pastas-secas': ['fideos-largos', 'fideos-para-guiso', 'fideos-para-sopa'],
                'arroz-y-legumbres': ['arroz-doble', 'arroz-integral', 'arroz-largo', 'arroz-parboil', 'arroz-preparado', 'legumbres-y-semillas'],
                'panaderia': ['budines-y-magdalenas', 'facturas-y-medialunas', 'grisines-y-tostadas', 'otras-especialidades', 'panes', 'pan-de-hamburguesa-y-pancho', 'pan-de-molde'],
                'golosinas-y-alfajores': ['alfajores', 'caramelos-y-gomitas', 'chicles-y-chupetines', 'chocolates', 'turrones-obleas-y-confitados'],
                'reposteria': ['bizcochuelos', 'coberturas', 'gelatinas', 'polvo-para-hornear-y-esencias', 'postres-para-preparar', 'premezclas-dulces'],
                'comidas-listas': ['caldos', 'pure', 'sopas'],
                'harinas': ['harinas-de-maiz', 'premezclas-saladas'],
                'picadas': ['aceitunas-y-encurtidos', 'papas-fritas', 'snacks'],
                'pan-rallado-y-rebozadores': [],
            }
        }
    },
    'jumbo': {
        'url_base': 'https://www.jumbo.com.ar',
        'selectores': {
            'productos': '#gallery-layout-container div',
            'titulo': 'h2',
            'precio': 'jumboargentinaio-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'imagen': 'img',
        },
        'categorias': {
            'electro': {
                'calefaccion-calefones-y-termotanques': ['calefaccion', 'calefones', 'termotanques'],
                'cervezas': ['pilsner', 'stout'],
            },
            
        }
    },
    'carrefour': {
        'url_base': 'https://www.carrefour.com.ar',
        'selectores': {
            'titulo': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body',
            'precio': '.valtech-carrefourar-product-price-0-x-currencyContainer',
            'imagen': '.vtex-product-summary-2-x-imageNormal',
        },
        'categorias': {
            'Electro-y-tecnologia': {
                'Lavado': ['Lavarropas', 'Secarropas', 'Lavasecarropas', 'Lavavajillas'],
                'Smart-TV-y-soportes': ['Smart-TV', 'Soportes-y-accesorios'],
            },
            
        }
    },
    'vea': {
        'url_base': 'https://www.vea.com.ar',
        'selectores': {
            'productos': '#gallery-layout-container div',
            'titulo': 'h2',
            'precio': 'veaargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'imagen': 'img',
        },
        'categorias': {
            'electro': {
                'calefaccion-calefones-y-termotanques': ['calefaccion', 'calefones', 'termotanques'],
            },
            
        }
    }
}


# In[8]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import pandas as pd
import time
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def close_overlays(driver):
    """
    Intenta cerrar elementos emergentes que puedan bloquear la interacción
    """
    overlay_selectors = ['.cookie-consent-close', '.close-popup', '#popup-close', '.modal-close']
    for selector in overlay_selectors:
        try:
            overlay = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            overlay.click()
        except TimeoutException:
            pass

def obtener_productos(pagina, categoria, subcategoria=None, subsubcategoria=None):
    """
    Extrae productos de una página con soporte para múltiples sitios, incluyendo Carrefour con paginación.
    """
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Usar si no se necesita la interfaz gráfica
    driver = webdriver.Chrome(options=options)

    try:
        # Configuración específica
        config = paginas[pagina]
        url_base = config['url_base']
        selectores = config['selectores']

        # Construcción de la URL
        if subsubcategoria:
            url = f'{url_base}/{categoria}/{subcategoria}/{subsubcategoria}'
        elif subcategoria:
            url = f'{url_base}/{categoria}/{subcategoria}'
        else:
            url = f'{url_base}/{categoria}'

        driver.get(url)
        time.sleep(5)  # Ajustar según velocidad de la conexión
        close_overlays(driver)

        data = []
        
        if pagina == 'carrefour':
            # Lógica específica para Carrefour con paginación
            pagina_actual = 1
            while True:
                try:
                    # Extraer productos en la página actual
                    nombres = driver.find_elements(By.CSS_SELECTOR, selectores['titulo'])
                    precios = driver.find_elements(By.CSS_SELECTOR, selectores['precio'])
                    imagenes = driver.find_elements(By.CSS_SELECTOR, selectores['imagen'])

                    for i in range(min(len(nombres), len(precios), len(imagenes))):
                        data.append({
                            'Titulo': nombres[i].text.strip(),
                            'Precio': precios[i].text.strip(),
                            'Imagen': imagenes[i].get_attribute('src').strip()
                        })

                    # Navegar a la siguiente página
                    siguiente_boton = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(siguiente_boton)).click()
                    time.sleep(3)  # Pausa breve para estabilidad
                    pagina_actual += 1
                except (NoSuchElementException, TimeoutException):
                    logger.info("No hay más páginas disponibles en Carrefour.")
                    break
        else:
            # Lógica para otras páginas sin paginación
            product_elements = driver.find_elements(By.CSS_SELECTOR, selectores['productos'])
            for element in product_elements:
                try:
                    titulo_element = element.find_element(By.TAG_NAME, selectores['titulo'])
                    precio_element = element.find_element(By.CLASS_NAME, selectores['precio'])
                    imagen_element = element.find_element(By.TAG_NAME, selectores['imagen']).get_attribute('src')

                    data.append({
                        'Titulo': titulo_element.text.strip(),
                        'Precio': precio_element.text.strip(),
                        'Imagen': imagen_element
                    })
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

        # Convertir a DataFrame
        df = pd.DataFrame(data)
        return df

    except Exception as e:
        logger.error(f"Error en obtener_productos: {e}")
        return pd.DataFrame()

    finally:
        driver.quit()


# Ejemplo de uso
def main():
    pagina = 'vea'  # Cambiar por la página que quieras probar
    categoria = 'electro'
    subcategoria = 'calefaccion-calefones-y-termotanques'
    subsubcategoria = 'calefaccion'

    df = obtener_productos(pagina, categoria, subcategoria, subsubcategoria)
    if not df.empty:
        print(df)
        df.to_csv(f'productos_{pagina}_{subcategoria}.csv', index=False, encoding='utf-8-sig')
    else:
        print("No se encontraron productos.")

if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:




