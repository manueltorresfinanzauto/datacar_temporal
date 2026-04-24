# 🚙 Datacarro models 🚗 



## ▶️ Operación 

La operación de esto tiene dos secciones.

### 1. Melollevo brdp con peritaje 

Todos los miércoles por la mañana se corre los 

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

## 🚨⚠️ Posibles errores

El código en sí no presenta errores graves, pero podrían aparecer mensajes relacionados con espacios vacíos en los datos. Usualmente se mostrará un aviso indicando la presencia de valores `NaN` o `inf`.

En estos casos, es importante revisar que las columnas clave (consulta la documentación o el código para identificar cuáles son) no contengan valores vacíos ni caracteres no válidos.


## 🧑‍💻 Desarrollado por

* Manuel Sebastián Torres Hernández
manuel.torres@finanzauto.com.co
