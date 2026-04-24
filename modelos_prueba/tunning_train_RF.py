import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error, make_scorer, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.utils import resample
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import joblib
import time
from datetime import datetime




def tt_randomforest(df, name_out:str='RF'):
    df = df[df['Pricing'] >= 0] 
    df = df.dropna(subset=['Pricing'])
    X = df.drop(columns=['Pricing'])
    y = df['Pricing']
    y_log = np.log1p(y)

    has_nan_col_a = y_log.isnull().any()
    print('.................................................')
    print(f"Does y have NaN values? {has_nan_col_a}")


    ## -------------- bootstraping ------------------------------------------------------------------------------
    df_bootstrap = pd.concat([X, y_log], axis=1)

    # Bootstrapping: generate a new dataset by sampling with replacement
    df_bootstrap = resample(
        df_bootstrap,
        replace=True,
        n_samples=int(len(df_bootstrap) * 1.5),  # You can increase size; 1.5x is common
        random_state=42
    )

    # Separate the bootstrapped data
    X = df_bootstrap.drop(columns=['Pricing'])
    y_log = df_bootstrap['Pricing']
    ## ..........................................................................................................

    print(df.shape)
    

    # split the data

    X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.3, random_state=42)
    y_test_orig = np.expm1(y_test)
    y_test_orig_log = y_test

    # Tunning grids 

    param_grid = {
        'regressor__n_estimators': [130],
        # 'regressor__max_depth': [15]
        # 'regressor__min_samples_split': [5]
        # 'regressor__min_samples_leaf': [1, 2]
    }

    scoring = {
        'rmse': 'neg_root_mean_squared_error',
        'r2': 'r2'
    }


    # Defining the models
    m_dep : int = 30
    models = {
        'Random Forest' : RandomForestRegressor(random_state=42),
    }

    output_df = X_test.copy()
    output_df['actual_pricing'] = y_test_orig 

    for name, model in models.items():
        print(f'\nTraining {name}...')

        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', model)
        ]) 
        
        grid_search = GridSearchCV(
                                    estimator=pipeline,
                                    param_grid=param_grid,
                                    scoring=scoring,
                                    refit='rmse',  # Metric used to pick best model
                                    cv=5,
                                    n_jobs=-1,
                                    verbose=2,
                                    return_train_score=True
                                    )
        
        print("\nTraining Random Forest with GridSearchCV (5-fold CV)...")
        start = time.time()
        has_nan_col_a = y_train.isnull().any()
        print('.................................................')
        print(f"Does y have NaN values? {has_nan_col_a}")

        grid_search.fit(X_train, y_train)
        print(f"{name} training time: {(time.time() - start):.2f} seconds")

        best_model = grid_search.best_estimator_    
        print("\nBest Parameters:")
        print(grid_search.best_params_)

        # Guardar el modelo ya entrenado
        hoy = datetime.today().strftime("%d_%m_%Y")
        name_out_pkl = f'../{name_out}_model_V1_{hoy}.pkl'
        joblib.dump(best_model, f'{name_out_pkl}')
        print(f"Modelo {name} guardado como {name_out_pkl}")

        y_pred_log = best_model.predict(X_test)
        y_pred = np.expm1(y_pred_log)

        rmse = np.sqrt(mean_squared_error(y_test_orig_log, y_pred_log))
        r2 = r2_score(y_test_orig_log, y_pred_log)
        mape = np.mean(np.abs((y_test_orig_log - y_pred_log)/ y_test_orig_log)) * 100
        
        mae = mean_absolute_error(y_test_orig, y_pred)
        rmse2 = np.sqrt(mean_squared_error(y_test_orig, y_pred))
        media = np.mean(y_test_orig)
        relative_error = rmse2/media
        relative_error_mae = mae / media
        print('---------------------------------------------------------------------')
        print(f" {name}")
        print(f"   RMSE: {rmse:.2f}")
        print(f"   R²: {r2:.4f}")
        # print(f"   MAPE: {mape:.2f}%")
        print(f'   Relative error rmse: {relative_error}')
        print(f'   Relative error mae: {relative_error_mae}')
        pred_col = f"{name.lower().replace(' ', '_')}_pred"
        resid_col = f"{name.lower().replace(' ', '_')}_resid"
        output_df[pred_col] = y_pred 
        output_df[resid_col] = y_test_orig - y_pred 

        #  PLOTS
        plt.figure(figsize=(16, 4))

        # Actual vs Predicted
        plt.subplot(1, 3, 1)
        sns.scatterplot(x=y_test_orig, y=y_pred, alpha=0.6)
        plt.plot([y_test_orig.min(), y_test_orig.max()],
            [y_test_orig.min(), y_test_orig.max()],
            color='red', linestyle='--') 
        plt.xlabel("Actual Price")
        plt.ylabel("Predicted Price")
        plt.title(f"{name} - Actual vs Predicted")

        # Residual Plot
        plt.subplot(1, 3, 2)
        sns.histplot(y_test_orig - y_pred, kde=True, bins=30)
        plt.xlim(-1e8, 1e8)
        plt.title(f"{name} - Residual Distribution")

        # Feature Importance (if available)
        plt.subplot(1, 3, 3)
        try:
            importances = model.feature_importances_
            feature_names = X.columns
            indices = np.argsort(importances)[::-1][:10]
            sns.barplot(x=importances[indices], y=feature_names[indices])
            plt.title(f"{name} - Top 10 Feature Importances")
        except:
            plt.text(0.1, 0.5, "Feature importances not available", fontsize=12)

        plt.tight_layout()
        # plt.savefig(f'plots_best_model_CV.png')
        plt.show()

    # Save final output
    output_df.to_csv("../../car_data_model_results.csv", index=False)
    print(" Output saved as car_data_model_results.csv")

    cv_results = pd.DataFrame(grid_search.cv_results_)
    print(cv_results)
    cv_results.to_csv(f'../../cv_hyperpa{hoy}.csv')
