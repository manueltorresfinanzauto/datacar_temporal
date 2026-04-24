# 🚙 Datacarro models 🚗 




## 🛠️ Requisitos

## Clonar

Debido a que este repositorio tiene un submodulo se tiene que clonar primero este repositorio, `Datacarro_models`, y luego dentro de la carpeta que se creo al clonar `Datacarro_models` se tiene que clonar el repositorio `CleaningData`.



### 📚 Librerias

Este proyecto requiere Python 3.11 o superior y algunas librerias específicas que se pueden instalar de dos formas:

####  Opción 1: Usando Conda (recomendado)

Si utilizas Anaconda o Miniconda, puedes crear el entorno directamente desde el archivo `.yml`:

```bash
conda env create -f environment_mldata.yml
conda activate nombre_del_entorno
```

#### Opción 2: Instalando los requirements en un ambiente ya existente

Sea con Anaconda o con python puro tocaria correr el siguiente comando para instalar las librerias necesarias

```
pip install -r requirements.txt
```

### 🐧 Instalación de WSL

Para la instalcación de WSL se puede seguir las instrucciones dadas desde la página de microsoft en el siguiente link: 
>  https://learn.microsoft.com/en-us/windows/wsl/install

Cabe aclarar que para esa instalación toca tener permisos de administrador, por lo que toca crear un ticket con TI. Además, en algunos casos puede se necesario instalar Ubuntu (SO recomendado, pero también puede ser Debian) desde la Microsoft store.

### ☁️ Configuración del LLM de AWS

Para este proyecto necesitamos el acceso y unos modelos pertenecientes a AWS, para esto toca configurar ese acceso corriendo los siguientes comandos en el wsl (para instalar el cli):

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install && rm -rf awscliv2.zip aws
aws --version
```

deberia aparecer algo como la siguiente información, luego de correr el comando de version,

```
aws-cli/2.24.10 Python/3.12.9 Linux/5.15.167.4-microsoft-standard-WSL2 exe/x86_64.ubuntu.24
```

y luego de eso toca hacer el aws configure


finalmente se necesita tener ciertas credenciales, estas se pueden solicitar con el responsable, los cuale son los del equipo de IA. 

a

## 🚧 Consideraciones de ejecución en entornos de 16 GB de RAM y sistema operativo Windows

Esto se debe a dos razones principales:

1. **El modelo LLM de AWS requiere un entorno Linux** para su ejecución, lo que hace necesario el uso de WSL.
2. **Las limitaciones de memoria en este tipo de configuración** (Windows + WSL con 16 GB de RAM) impiden ejecutar todo el proyecto dentro de WSL. Esto se debe a que:
   - Windows consume una parte significativa de la memoria disponible.
   - WSL introduce una capa adicional de uso de memoria.
   - Además, WSL impone un límite sobre la cantidad de memoria que puede utilizar.

> En sistemas con mayor capacidad de RAM, es posible ejecutar todo el proyecto dentro de WSL sin necesidad de dividirlo entre entornos.

### 🐧 WSL

Toca correr todo lo que es de la carpeta `CleaningData`, es decir todo lo que sea código de limpieza de datos; el cual se corre desde el archivo `clean_main.py`. Como se explicó esto es debido a las condiciones para correr los modelos de LLM. Estos se pueden encontar en al archivo `cleaners/__init__.py` y `limpieza_datos.py`.

### 🪟 Windows

Ya luego de tener los datos limpios por parte del `clean_main.py` ya se puede proceder al entrenamiento del modelo, en el cual se va a correr en Windows ya que se tiene acceso a más memoria ram. Para esto se utiliza el archivo que tenemos de datos y entrenar en el archivo de `modelos_prueba/RF_tunning.py`, `Trainning_RF.py` y `Pricing_RF.py`.


# 🚀 Cómo ejecutar el proyecto

Para ejecutar el proyecto, es necesario correr diferentes scripts dependiendo de la parte que se desea utilizar. Por ello, la ejecución se divide en dos secciones:

1. Predicción del precio

2. Entrenamiento del modelo

### 💰 Predicción de precios

Para predecir los precios, primero se debe realizar una limpieza de datos. Este proceso se ejecuta en **WSL** mediante el script `limpieza_datos.py`, donde debes especificar la **ruta del archivo Excel** que deseas limpiar.

Una vez obtenidos los datos limpios, puedes ejecutar el script `Pricing_RF.py` en **Windows**.  
*(Para más detalles sobre qué sistema operativo utilizar, consulta la sección [🚧 Consideraciones de ejecución en entornos de 16 GB de RAM y sistema operativo Windows](#-consideraciones-de-ejecución-en-entornos-de-16-gb-de-ram-y-sistema-operativo-windows)).*

Este script requiere:


- La **ruta del archivo limpio** generado por `limpieza_datos.py`.
- El archivo `.pkl` con el modelo entrenado, que se genera al ejecutar `Training_RF.py` (explicado en la siguiente sección).

### 🧠 Entrenamiento del modelo


Para entrenar el modelo, se parte de un archivo llamado `car_data_v1.csv`, que contiene los datos base.  
Si deseas agregar nuevos datos, puedes concatenarlos utilizando el script `concatenar_datos.py` como ejemplo.

Una vez que tienes el archivo completo con los datos que deseas usar para el entrenamiento, se debe realizar una limpieza previa.  
Esta limpieza se lleva a cabo mediante el script `limpieza_datos.py`, el cual genera un nuevo archivo limpio que será utilizado por `Trainning_RF.py`.

El script `Trainning_RF.py` toma los datos limpios y entrena un modelo de **Random Forest**, generando un archivo `.pkl` que contiene el modelo entrenado.  
Este archivo será utilizado posteriormente en la etapa de predicción de precios.

## 🚨⚠️ Posibles errores

El código en sí no presenta errores graves, pero podrían aparecer mensajes relacionados con espacios vacíos en los datos. Usualmente se mostrará un aviso indicando la presencia de valores `NaN` o `inf`.

En estos casos, es importante revisar que las columnas clave (consulta la documentación o el código para identificar cuáles son) no contengan valores vacíos ni caracteres no válidos.


## 🧑‍💻 Desarrollado por

* Manuel Sebastián Torres Hernández
manuel.torres@finanzauto.com.co
