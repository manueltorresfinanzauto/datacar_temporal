import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.utils import resample
from sklearn.linear_model import LinearRegression
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

import joblib
import time
import smogn


#  Clean the dataset
def clean_dataset(df):
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=[np.number]).columns:
        df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
        if df_clean[col].notnull().any():
            q_low = df_clean[col].quantile(0.001)
            q_high = df_clean[col].quantile(0.999)
            df_clean[col] = df_clean[col].clip(lower=q_low, upper=q_high)
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    return df_clean

#  Load and preprocess
file_path = '../../car_data.csv'
df = pd.read_csv(file_path)
df = clean_dataset(df)

selected_columns = ['Cod_fasecolda', 'Modelo', 'Kilometraje', 'Year', 'Month', 'Ubicacion_int', 'Demanda', 'Promedio_estrellas', 'Combustible', 'Descripcion_int', 'Gama', 'Blindaje', 'Estado_vehiculo_int', 'Servicio_int', 'Estado_vitrina','Pricing']
print(df.columns.tolist())

df = df[[col for col in selected_columns if col in df.columns]]

print(df.shape)
# df = df.head(500)
# df = df.astype(float)
df['Estado_vitrina'] = (
    df['Estado_vitrina']
    .str.lower()          # Convierte a minúsculas
    .str.strip()          # Elimina espacios al inicio y final
    .str.replace(r'\s+', '_', regex=True)  # Reemplaza espacios internos por guiones bajos
)
reemplazos = {
    'venta_especial': 'venta_especial',
    'venta_especial_': 'venta_especial',
    'venta_especiales': 'venta_especial',
    'venta espcial' : 'venta_especial',
    'venta_espcial' : 'venta_especial'
    # Agrega más reemplazos según sea necesario
}

df['Estado_vitrina'] = df['Estado_vitrina'].replace(reemplazos)

df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(str).str.zfill(8)
df['Marca_cod'] = df['Cod_fasecolda'].str[:3]
df['Tipolo_cod'] = df['Cod_fasecolda'].str[3:5]
df['Resto_cod'] = df['Cod_fasecolda'].str[5:]

df['Marca_cod'] = df['Marca_cod'].astype(int)
df['Tipolo_cod'] = df['Tipolo_cod'].astype(int)
df['Resto_cod'] = df['Resto_cod'].astype(int)
df['Cod_fasecolda'] = df['Cod_fasecolda'].astype(int)

print(df.columns.tolist())

print(df.shape)
df['Modelo'] = df['Modelo'].replace('-', np.nan)
df = df.dropna(subset=['Modelo'])
df['Kilometraje'] = df['Kilometraje'].replace('-', 0)
df['Kilometraje'] = df['Kilometraje'].replace(r'[^\d.-]', '', regex=True)  # Elimina caracteres no numéricos

df['Kilometraje'] = pd.to_numeric(df['Kilometraje'], errors='coerce').fillna(0)  # Convierte a float
df['Pricing'] = pd.to_numeric(df['Pricing'], errors='coerce')
df = df.dropna(subset=['Pricing'])
for i in selected_columns:
    if i == 'Combustible' or i == 'Gama' or i == 'Estado_vitrina':
        pass
    else:
        df[i] = df[i].astype(float)

df.drop(columns='Cod_fasecolda', inplace=True)
## ------------- categorical --------------------------------------------------------------------------
df = pd.get_dummies(df, columns=['Combustible'], prefix='Combustible')
df = pd.get_dummies(df, columns=['Gama'], prefix='Gama')
df = pd.get_dummies(df, columns=['Estado_vitrina'], prefix='Vitrina')
df.drop(columns=['Gama_De Lujo ', 'Combustible_HBD', 'Vitrina_vitrina', 'Promedio_estrellas'], inplace=True)
print(df.columns.tolist())

df_co = df.drop(columns=['Pricing'])
df_co['Pricing'] = df['Pricing']
corr_matrix = df_co.corr()

plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Correlation Matrix")
plt.show()

X = df.drop(columns=['Pricing'])
y = df['Pricing']
y_log = np.log1p(y)

# Ensure only numeric columns and no NaNs
X_vif = X.select_dtypes(include=[np.number]).copy()
X_vif = X_vif.dropna()  # Optional: or use fillna if needed
X_vif = add_constant(X_vif)  # Required for intercept in VIF

# Compute VIF
vif_data = pd.DataFrame()
vif_data["feature"] = X_vif.columns
vif_data["VIF"] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]

print("\nVariance Inflation Factors (VIF):")
print(vif_data.sort_values("VIF", ascending=False))

model = LinearRegression()
model.fit(X, y)

# Predictions
y_pred = model.predict(X)

# Coefficients
coeffs = pd.Series(model.coef_, index=X.columns)

# R2 and MSE
print("R²:", r2_score(y, y_pred))
print("MSE:", mean_squared_error(y, y_pred))
print("\nCoefficients:")
print(coeffs.sort_values(ascending=False))

residuals = pd.Series(y - y_pred)

sns.residplot(x=y_pred, y=residuals, line_kws={'color': 'red'})
plt.xlabel("Predicted Values")
plt.ylabel("Residuals")
plt.title("Residual Plot (Linear Regression)")
plt.axhline(0, linestyle='--', color='black')
plt.show()
