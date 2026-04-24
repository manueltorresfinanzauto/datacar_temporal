import pandas as pd
import requests
import re
import os
import pymssql
from bs4 import BeautifulSoup
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class WebScrapinOpinautos:
    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service('/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        "Nos conectamos a nuestra tabla"
        server = os.getenv('DB_NAME_SERVER')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_DATABASE')
        self.conn = pymssql.connect(
            server=server, user=user, password=password, database=database)
        self.cursor = self.conn.cursor()

    def promblem_title(self, suop, tamano_datos=0, clase='align-middle'):
        lis_nombres_problemas = []
        anclaje = suop.find_all(class_=clase)
        inicial = 2
        final = tamano_datos + 2
        for i in anclaje[inicial:final]:
            lis_nombres_problemas.append(i.text)

        return lis_nombres_problemas

    def comment(self, suop, clase='js-report-body Text'):
        lis_comentarios = []
        comentario = suop.find_all(class_=clase)
        for i in comentario:
            lis_comentarios.append(i.text)

        return lis_comentarios

    def time(self, suop, clase='px-15 pt-15 pb-1 max-width-700'):
        lis_tiempo = []
        fecha = []
        raiz_fecha = suop.find_all('div', class_=clase)

        for i in raiz_fecha:
            fecha.append(i.find('span', class_='fecha'))

        for i in fecha:
            lis_tiempo.append(i['title'][:10])

        return lis_tiempo

    def location(self, suop, clase='AuthorShort AuthorShort--right'):
        lis_location = []
        comentario = suop.find_all(class_=clase)

        pais_pattern = re.compile(r'(?<=de\s)([^\s]+)')

        for i in comentario:
            texto = i.text
            # Buscar el país en el texto utilizando la expresión regular
            match = pais_pattern.search(texto)
            if match:
                pais = match.group(1)
                lis_location.append(pais)

        return lis_location

    def info_car(self, suop, clase='text-ellipsis text-normal color-text-gray'):
        lis_info_car = []
        info_car = suop.find_all(class_=clase)
        for i in range(len(info_car)):
            lis_info_car.append(info_car[i].text)

        return lis_info_car

    def extraction_info(self, text):
        "Extraemos el año"
        match_anio = re.search(r'\b(\d{4})\b', text)
        model = match_anio.group(1) if match_anio else 'Desconocido'
        "extraemos el kilometraje"
        match_kms = re.search(r'(\d+)\s*kms?', text)
        kms = match_kms.group(1) if match_kms else 'Desconocido'
        return (model, kms)

    def extraction(self, url, marca, linea, cod_facecolda):
        df_iteracion = None

        "Alistamos las variables principales"
        pagina = '/pag{}'
        url_fin = url+pagina
        res = requests.get(url)
        res.status_code
        code_html = res.text
        soup = BeautifulSoup(code_html, 'html.parser')
        lis_bn = []
        boton = soup.find_all(class_='Button Button--small pagina')

        for i in boton:
            lis_bn.append(i)

        if not lis_bn:
            paginas = 1
        else:
            paginas = int(lis_bn[-1].text)

        paginas = int(paginas)
        lis_link = []

        "Agregamos la lista de las paginas que tenemos"
        for i in range(1, paginas+1):
            lis_link.append(url_fin.format(i))

        for i in lis_link:
            res = requests.get(i)
            estado = res.status_code

            if estado >= 200 and estado < 300:
                code_html = res.text

                # creamos un objetos BeautifulSoup, donde tine parametros (code_html, 'html.parser') parse es el metodo que vamos a usar 
                soup = BeautifulSoup(code_html, 'html.parser')
                can_datos = soup.find_all(
                    class_='WhiteCard mb-3 max-width-700')
                can_datos = len(can_datos)
                list_ubicacion = self.location(soup)
                list_probelmas = self.promblem_title(soup, can_datos)
                list_comentarios = self.comment(soup)
                list_fecha = self.time(soup)
                list_infor_car = self.info_car(soup)

                model, kms = zip(*[self.extraction_info(info)
                                 for info in list_infor_car])
                model = list(model)
                kms = list(kms)

                "Creamos las listas para marca y linea"
                cantidad = len(model)
                list_marca = [marca] * cantidad
                list_linea = [linea] * cantidad
                list_code = [cod_facecolda] * cantidad

                cantidad = len(model)
                df_iteracion = pd.DataFrame({
                    'Cod Fasecolda': list_code,
                    'Marca': list_marca,
                    'Linea': list_linea,
                    'Ubicacion': list_ubicacion,
                    'Fecha': list_fecha,
                    'Problema': list_probelmas,
                    'Comentario': list_comentarios,
                    'Modelo': model,
                    'Kilometraje': kms,
                })

                self.add_df(df_iteracion)

    def eliminamos_filas(self):
        self.cursor.execute("""
            WITH Duplicates AS (
                SELECT 
                    [Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Problema, Comentario, Modelo, Kilometraje,
                    ROW_NUMBER() OVER (
                        PARTITION BY [Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Problema, Comentario, Modelo, Kilometraje
                        ORDER BY (SELECT NULL)
                    ) AS row_num
                FROM [Analitica].[opi].[Opinauto_Defectos]
            )
            DELETE FROM Duplicates
            WHERE row_num > 1;
        """)

        # Commit the transaction
        self.conn.commit()

    def add_df(self, df: pd.DataFrame):
        "Construye la sentencia SQL para insertar múltiples filas"
        values = []

        for index, row in df.iterrows():
            try:
                kilometraje = int(row['Kilometraje'])
            except (ValueError, TypeError):
                kilometraje = None  # O puedes usar un valor predeterminado como 0

            placa = row['Cod Fasecolda'] + '-' + str(row['Modelo'])

            values.append((
                row['Cod Fasecolda'], row['Marca'], row['Linea'], row['Ubicacion'],
                row['Fecha'], row['Problema'], row['Comentario'], row['Modelo'],
                kilometraje, placa  # Asegúrate de que Kilometraje sea numérico
            ))

        # La consulta SQL espera que Kilometraje sea un valor numérico
        sql = """
            INSERT INTO [Analitica].[opi].[Opinauto_Defectos]
            ([Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Problema, Comentario, Modelo, Kilometraje, Placa) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """  # Cambié %d a %s para Kilometraje, porque ya manejamos la conversión en Python
        self.cursor.executemany(sql, values)
        self.conn.commit()

    def opinautos_defectos(self, df_vehiculos: pd.DataFrame):
        "SAcamos los valore unicos de nuestro df_vehiculos"
        df = df_vehiculos.drop_duplicates(subset=['marca', 'linea'])

        "Sacamos la lista de codigos que tenemos"
        self.cursor.execute(
            "SELECT [Placa] FROM [Analitica].[opi].[Opinauto_Defectos]")
        placa_list = [row[0] for row in self.cursor.fetchall()]

        "Creamos nuestro df"
        self.df_final = pd.DataFrame()
        "Es para pasar en cada uno de los elementos de nuestro df"
        for _, row in df.iterrows():
            self.URL = "https://www.opinautos.com/co"
            marca = str(row['marca']).strip().replace(' ', '-')
            linea = str(row['linea']).strip().replace(' ', '-')
            cod_facecolda = str(row['cod fasecolda'])
            placa = str(row['placa'])

            try:
                if placa not in placa_list:
                    "Creamos la url de cada carro y entramos a la pagina"
                    self.URL = self.URL + '/' + \
                        str(marca) + '/' + str(linea) + '/defectos'
                    self.driver.get(self.URL)
                    self.extraction(self.URL, marca, linea, cod_facecolda)

                else:
                    # Sacamos la lista de fechas
                    self.cursor.execute("""
                        SELECT Fecha 
                        FROM [Analitica].[opi].[Opinauto_Defectos]
                        WHERE [Cod Fasecolda] = %s
                    """, (cod_facecolda,))

                    "Obtener la lista de fechas"
                    Fecha_list = [row[0] for row in self.cursor.fetchall()]

                    if Fecha_list:
                        if isinstance(Fecha_list[0], date):
                            "Convertir a datetime.datetime si es necesario"
                            Fecha_list = [datetime.combine(fecha, datetime.min.time()) if isinstance(
                                fecha, date) else fecha for fecha in Fecha_list]

                        fecha_mas_reciente = max(Fecha_list)
                        fecha_actual = datetime.now()
                        diferencia_dias = (
                            fecha_actual - fecha_mas_reciente).days

                        "Se verifica si el ultimo dato esta mas de 60 dias de la fecha actual"
                        if diferencia_dias >= 60:
                            self.URL = self.URL + '/' + \
                                str(marca) + '/' + str(linea) + '/defectos'
                            self.driver.get(self.URL)
                            self.extraction(self.URL, marca,
                                            linea, cod_facecolda)

                        else:
                            print(
                                f'Los datos {marca}-{linea}-{cod_facecolda} estan actualizados: Opinauto_Defectos')
                            pass
            except Exception as e:
                print(
                    f'Los datos {marca}-{linea}-{cod_facecolda}, este esel error: {e}')

        self.eliminamos_filas()
        self.cursor.close()
        self.conn.close()
        self.df_final.to_excel('defectos_opinautos.xlsx', index=False)
        self.driver.quit()


class WebScrapinOpinautosOpiniones:
    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service('/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        "Nos conectamos a nuestra tabla"
        server = os.getenv('DB_NAME_SERVER')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database = os.getenv('DB_DATABASE')
        self.conn = pymssql.connect(
            server=server, user=user, password=password, database=database)
        self.cursor = self.conn.cursor()

    def location(self, soup, clase='WhiteCard margin-top desktop-margin15 js-review'):
        return [
            re.search(r'(?<=de\s)([^\s]+)', box.text).group(1)
            for container in soup.find_all('div', class_=clase)
            for box in container.find_all('div', class_='AuthorShort AuthorShort--right margin-top-small')
            if re.search(r'(?<=de\s)([^\s]+)', box.text)
        ]

    def time(self, soup, clase='WhiteCard margin-top desktop-margin15 js-review'):
        return [
            box.find('span', class_='fecha')['title'][:10]
            for container in soup.find_all('div', class_=clase)
            for box in container.find_all('div', class_='AuthorShort AuthorShort--right margin-top-small')
            if box.find('span', class_='fecha')
        ]

    def info_car(self, soup, clase='WhiteCard margin-top desktop-margin15 js-review'):
        return [
            re.search(r'\b(\d{4})\b', box.text).group(1) if re.search(
                r'\b(\d{4})\b', box.text) else 'Desconocido'
            for container in soup.find_all(class_=clase)
            for box in container.find_all('div', class_='LeftRightBox')
            if box.get('class') == ['LeftRightBox']
        ]

    def calification(self, soup, clase='WhiteCard margin-top desktop-margin15 js-review'):

        gold_star_url = "https://static.opinautos.com/images/design2/icons/icon_star--gold.svg?v=5eb58b"
        return [
            sum(1 for img in box.find_all('img', class_='Icon')
                if img['src'] == gold_star_url)
            for container in soup.find_all(class_=clase)
            for box in container.find_all('div', class_='LeftRightBox__left LeftRightBox__left--noshrink')
        ]

    def extraction(self, url, marca, linea, cod_facecolda):
        res = requests.get(url)

        if 200 <= res.status_code < 300:

            soup = BeautifulSoup(res.text, 'html.parser')

            list_ubicacion = self.location(soup)

            list_time = self.time(soup)
            list_model = self.info_car(soup)
            list_cl = self.calification(soup)
            cantidad = len(list_cl)
            marca_list = [marca] * cantidad
            line_list = [linea] * cantidad
            code_list = [cod_facecolda] * cantidad
            df_iteracion = pd.DataFrame({
                'Cod Fasecolda': code_list,
                'Marca': marca_list,
                'Linea': line_list,
                'Ubicacion': list_ubicacion,
                'Fecha': list_time,
                'Modelo': list_model,
                'Calificacion': list_cl
            })

            self.add_df(df_iteracion)

    def eliminamos_filas(self):
        self.cursor.execute(f"""
            WITH Duplicates AS (
                SELECT 
                    [Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Modelo, Calificacion,
                    ROW_NUMBER() OVER (
                        PARTITION BY [Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Modelo, Calificacion
                        ORDER BY (SELECT NULL)
                    ) AS row_num
                FROM [Analitica].[opi].[Opinautos_Opiniones]
            )
            DELETE FROM Duplicates
            WHERE row_num > 1;
        """)

        # Commit the transaction
        self.conn.commit()

    def add_df(self, df: pd.DataFrame):
        "Construye la sentencia SQL para insertar múltiples filas"
        values = []
        for index, row in df.iterrows():
            placa = row['Cod Fasecolda'] + '-' + str(row['Modelo'])
            values.append((
                row['Cod Fasecolda'], row['Marca'], row['Linea'], row['Ubicacion'],
                row['Fecha'], row['Modelo'], row['Calificacion'], placa))

        sql = """
            INSERT INTO [Analitica].[opi].[Opinautos_Opiniones]
            ([Cod Fasecolda], Marca, Linea, Ubicacion, Fecha, Modelo, Calificacion, Placa) 
            VALUES (%s, %s, %s, %s, %s, %s, %d, %s)
        """
        self.cursor.executemany(
            sql, values)  # Usamos executemany para insertar múltiples filas a la vez
        self.conn.commit()

    def opinautos_opiniones(self, df_vehiculos: pd.DataFrame):
        "SAcamos los valore unicos de nuestro df_vehiculos"
        df = df_vehiculos.drop_duplicates(subset=['marca', 'linea'])

        "Sacamos la lista de codigos que tenemos"
        self.cursor.execute(
            "SELECT [Placa] FROM [Analitica].[opi].[Opinauto_Defectos]")
        placa_list = [row[0] for row in self.cursor.fetchall()]

        "Creamos nuestro df"
        self.df_final = pd.DataFrame()
        "Es para pasar en cada uno de los elementos de nuestro df"
        for _, row in df.iterrows():
            self.URL = "https://www.opinautos.com/co"
            marca = str(row['marca']).strip().replace(' ', '-')
            linea = str(row['linea']).strip().replace(' ', '-')
            cod_facecolda = str(row['cod fasecolda'])
            ID_FacecoldaModelo = str(row['ID_FacecoldaModelo'])

            try:
                if ID_FacecoldaModelo not in placa_list:
                    "Creamos la url de cada carro y entramos a la pagina"
                    self.URL = self.URL + '/' + \
                        str(marca) + '/' + str(linea) + '/opiniones'
                    self.driver.get(self.URL)
                    self.extraction(self.URL, marca, linea, cod_facecolda)

                else:
                    # Sacamos la lista de fechas
                    self.cursor.execute("""
                        SELECT Fecha
                        FROM [Analitica].[opi].[Opinautos_Opiniones]
                        WHERE [Cod Fasecolda] = %s
                    """, (cod_facecolda,))

                    "Obtener la lista de fechas"
                    Fecha_list = [row[0] for row in self.cursor.fetchall()]

                    if Fecha_list:
                        if isinstance(Fecha_list[0], date):
                            "Convertir a datetime.datetime si es necesario"
                            Fecha_list = [datetime.combine(fecha, datetime.min.time()) if isinstance(
                                fecha, date) else fecha for fecha in Fecha_list]

                        fecha_mas_reciente = max(Fecha_list)
                        fecha_actual = datetime.now()
                        diferencia_dias = (
                            fecha_actual - fecha_mas_reciente).days

                        "Se verifica si el ultimo dato esta mas de 60 dias de la fecha actual"
                        if diferencia_dias >= 60:
                            self.URL = self.URL + '/' + \
                                str(marca) + '/' + str(linea) + '/defectos'
                            self.driver.get(self.URL)
                            self.extraction(self.URL, marca,
                                            linea, cod_facecolda)

                        else:
                            print(
                                f'Los datos {marca}-{linea}-{cod_facecolda} estan actualizados : Opinautos_Opiniones')
                            pass
            except Exception as e:
                print(
                    f'Los datos {marca}-{linea}-{cod_facecolda}, este esel error: {e}')

        self.eliminamos_filas()
        self.cursor.close()
        self.conn.close()
        self.df_final.to_excel('opiniones_opinautos.xlsx', index=False)
        self.driver.quit()
