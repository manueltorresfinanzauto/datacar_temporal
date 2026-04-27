# 🚙 Datacarro models 🚗 



## ▶️ Operación 

La operación de esto tiene dos secciones.

### 1. Melollevo BRDP con peritaje

Todos los miércoles por la mañana se corren los precios de los vehículos registrados en la tabla `[Analitica].[dbo].[peritajes_fasecolda]`.

Para ejecutarlo, correr `pipeline.py` con la función en su forma por defecto:
```python
pipe()
```
Este proceso realiza la descarga, limpieza, predicción y carga a SQL de los precios de referencia.

> Si en algún momento se solicitan precios para placas puntuales por fuera del ciclo semanal, simplemente repetir el mismo proceso.

---

### 2. Solicitud externa

Para solicitudes que **no** provienen de la tabla `peritajes_fasecolda`, se debe colocar el archivo Excel en la carpeta donde se va a correr el código y ejecutar `pipeline.py` así:
```python
pipe(brdp=False, ruta_file="ruta_archivo")
```

Este proceso realiza la limpieza y predicción, y genera un archivo Excel de salida con las siguientes columnas:

| Columna |
|---------|
| `Placa` |
| `Precio_DataCarro` |
| `Precio_Maximo` |
| `Precio_Minimo` |
| `Cod_fasecolda` |
| `Fecha_Precio_DataCarro` |
| `Version_DataCarro` |


### 🚨 Posibles errores

#### 1. Valores vacíos o inválidos (`NaN` / `inf`)
El código maneja la mayoría de estos casos mediante `fillna`, pero en situaciones específicas puede aparecer un error por un valor `NaN` o `inf` no contemplado.

> ⚠️ Esto aplica principalmente al **Caso 2**. El Caso 1 no debería presentar este problema.

#### 2. Nombres de columnas inesperados
Cuando los datos llegan por correo en formato Excel, los nombres de las columnas pueden variar significativamente. El código intenta normalizar estos nombres usando un diccionario de mapeo, pero puede ser insuficiente si el nombre recibido difiere demasiado del esperado.

> ⚠️ Esto aplica principalmente al **Caso 2**. El Caso 1 no debería presentar este problema.

Los nombres de columna que el código espera son:

| Columna esperada |
|-----------------|
| `Placa` |
| `Cod_fasecolda` |
| `Marca` |
| `Linea` |
| `Modelo` |
| `Kilometraje` |
| `Fecha` |
| `Ubicacion` |
| `Realiability` |
| `Blindaje` |
| `Estado` |

Si el archivo Excel trae nombres distintos a estos, revisar y actualizar el diccionario de normalización en el código.



## 🛠️ Requisitos

## Clonar

Debido a que este repositorio tiene un submodulo se tiene que clonar primero este repositorio, `Datacarro_models`, y luego dentro de la carpeta que se creo al clonar `Datacarro_models` se tiene que clonar el repositorio `CleaningData`.



### 📚 Librerias

Este proyecto requiere Python 3.11 (exactamente se usa la versión 3.11.8) o superior y algunas librerias específicas que se pueden instalar de dos formas:

####  Opción 1: Usando Conda 

Si utilizas Anaconda o Miniconda, puedes crear el entorno directamente desde el archivo `.yml`:

```bash
conda env create -f environment_mldata.yml
conda activate nombre_del_entorno
```

#### Opción 2: Instalando los requirements en un ambiente ya existente

Sea con Anaconda o con python puro tocaría correr el siguiente comando para instalar las librerias necesarias

```bash
pip install -r requirements.txt
```


## 🧑‍💻 Desarrollado por

* Manuel Sebastián Torres Hernández
manuel.torres@finanzauto.com.co
