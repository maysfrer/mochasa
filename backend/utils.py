import pandas as pd
import numpy as np 
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.stats import linregress
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.api import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from constants import EXCEL_FILE_CONSUMPTIONS,EXCEL_FILE_COSTS, MONTHS

def cargar_datos_1(field=None):
    
    # Load the Excel file
    data_0 = pd.read_excel(EXCEL_FILE_CONSUMPTIONS)    

    # Mapping the month names to their corresponding values
    data_0['mes'] = data_0['mes'].map(MONTHS)

    # Combining year, month, and day columns to create a 'fecha' column
    data_0['fecha'] = pd.to_datetime(data_0['anio'].astype(str) + '-' + data_0['mes'].astype(str) + '-' + data_0['dia'].astype(str))

    # Create a 'mes_año' column by extracting the period from the 'date'
    data_0['mes_año'] = data_0['fecha'].dt.to_period('M')

    # Get the latest consumption date for each 'sku'
    ultima_fecha_consumo = data_0.groupby("sku")["fecha"].max().reset_index()
    ultima_fecha_consumo.columns = ["sku", "ultima_fecha"]

    # Get the items that had consumption in the year 2024
    items_consumo_2024 = ultima_fecha_consumo[ultima_fecha_consumo["ultima_fecha"].dt.year == 2024]["sku"]

    # Filter the data to only include items with consumption in 2024
    tabla_consumo_2024 = data_0[data_0["sku"].isin(items_consumo_2024)]

    # Filter the data to only include rows with 'MACROS' or 'MICROS' in the 'bodega' column
    df = tabla_consumo_2024[tabla_consumo_2024['bodega'].isin(['MACROS', 'MICROS'])].reset_index(drop=True)

    if field == 'week':
        return df.groupby(['anio', 'semana', 'sku', 'bodega'])['consumo_tm'].sum().reset_index()
        
    # Return the sum of 'consumo_tm' grouped by 'month_year', 'sku', and 'bodega'
    return df.groupby(['mes_año','sku', 'bodega'])['consumo_tm'].sum().reset_index()

def cargar_datos_2(field=None):
    return cargar_datos_1('week')

def cargar_datos_3(df_mensual): 
    # Obtener df analizado
    df_analizado = analizar_outliers_y_ajustar(df_mensual, 'sku', 'consumo_tm').reset_index(drop=True)
    # Obtener los resultados de tendencia estacionalidad
    resultados_tendencia, summary = analizar_tendencia_estacionalidad(df_analizado, 'sku', 'consumo_tm', ventana=3)
    # Generar los pronósticos basados en el resumen
    df_pronosticos, df_modelos = generar_pronosticos(df_mensual, summary, pasos_pronostico=3)
    # Convertir la columna 'mes_año' a formato de periodo mensual
    df_pronosticos['mes_año'] = df_pronosticos['mes_año'].dt.to_period('M')
    # Combinar los pronósticos con los datos históricos
    df_final = pd.concat([df_mensual, df_pronosticos], ignore_index=True)
    # Ordenar el DataFrame combinado por SKU y mes_año
    df_final = df_final.sort_values(by=['sku', 'mes_año'])
    # Seleccionar los últimos 6 registros de cada SKU
    df_ultimos_6 = df_final.groupby('sku').tail(6)
    # Obtener los resultados de pronostico
    conteo_modelo_bodega = df_modelos.groupby(['mejor_modelo', 'bodega']).size().reset_index(name='conteo')
    return df_analizado, df_ultimos_6, summary, conteo_modelo_bodega

def cargar_datos_4(df_analizado):
    return clasificacion_abc_por_bodega(df=df_analizado,bodega_column='bodega', sku_column='sku',consumo_column='consumo_ajustado')

def cargar_datos_5(ultimos_6, df_abc, summary):
    anl=ultimos_6.groupby('sku')['consumo_tm'].describe().reset_index()
    #Agrupar las tablas de descripción, abc, variabilidad
    df_unido = pd.merge(pd.merge(anl[['sku', 'mean', 'std']], df_abc[['sku', 'clase_abc', 'bodega']], on='sku'), summary[['sku', 'variabilidad']], on='sku')
    return df_unido

def cargar_datos_6(df_unido):
    # Lee las hojas en un diccionario de DataFrames
    lt = pd.read_excel(EXCEL_FILE_COSTS, sheet_name='lt')
    inventario = pd.read_excel(EXCEL_FILE_COSTS, sheet_name='inventario')
    inventario =inventario.groupby('sku')[['inventario', 'OCs', 'consumo_ult_sem', 'Consumo_ult_mes']].sum().reset_index()
    # Dividir las columnas seleccionadas por 1000
    inventario[['inventario', 'OCs', 'consumo_ult_sem', 'Consumo_ult_mes']] /= 1000

    # Carga el archivo Excel
    costo_mp = pd.read_excel(EXCEL_FILE_COSTS, sheet_name='costo_mp')
    costo_mp ['mes'] = costo_mp ['mes'].map(MONTHS)
    costo_mp ['fecha'] = pd.to_datetime(costo_mp ['anio'].astype(str) + '-' + costo_mp ['mes'].astype(str) )
    # Agrupar datos a nivel mensual por SKU, año y bodega
    costo_mp ['mes_año'] = costo_mp ['fecha'].dt.to_period('M')
    costo_promedio = costo_mp.groupby('sku')['costo'].mean().reset_index()

    df_completo = pd.merge(df_unido, costo_promedio[['sku', 'costo']], on='sku', how='left')
    # Rellenar los valores faltantes de costo_promedio con 100
    df_completo['costo'] = df_completo['costo'].fillna(100)
    # Hacer el merge del resultado con lead_time
    df_completo = pd.merge(df_completo, lt[['sku', 'lead_time']], on='sku', how='left')
    # Rellenar los valores faltantes de lead_time con 30
    df_completo['lead_time'] = df_completo['lead_time'].fillna(30)

    #Costos
    costo_mantener = 1.84  # Costo de mantener (por TM)
    costo_recibir = 0.36   # Costo de recibir (por TM)
    costo_pedir = 7.50     # Costo fijo de pedir
    nivel_servicio = {'A': 0.95, 'B': 0.75, 'C': 0.70}  # Niveles de servicio según clase ABC
    z_values = {'A': 1.645, 'B': 0.675, 'C': 0.524}    # Z-scores estándar

    # Calcular h (costo de almacenar)
    df_completo['h'] = 0.12*(df_completo['costo'] + costo_mantener + costo_recibir)
    # Calcular demanda anual (D)
    df_completo['demanda_anual'] = df_completo['mean'] * 12
    # Asignar nivel de servicio (α) y z
    df_completo['alpha'] = df_completo['clase_abc'].map(nivel_servicio)
    df_completo['z'] = df_completo['clase_abc'].map(z_values)
    # Calcular EOQ (Q) para SKUs No Variables
    df_completo['EOQ'] = np.where(
        df_completo['variabilidad'] == 'No Variable',
        np.sqrt((2 * df_completo['demanda_anual'] * costo_pedir) / df_completo['h']),
        np.nan)  # EOQ no aplica para SKUs variables

    df_completo['T'] = np.where(
    df_completo['variabilidad'] == 'Variable',5,np.nan)

    # Calcular stock de seguridad (SS) para todos los SKUs
    df_completo['SS'] = df_completo['z'] * df_completo['std'] * np.sqrt(df_completo['lead_time']/30)

    # Calcular nivel objetivo para Revisión Periódica
    df_completo['SS'] = np.where( df_completo['variabilidad'] == 'Variable',
        df_completo['z'] * df_completo['std'] * np.sqrt((df_completo['lead_time']+df_completo['T'])/30),
        df_completo['z'] * df_completo['std'] * np.sqrt(df_completo['lead_time']/30) )  # Nivel objetivo no aplica para SKUs No Variables

    # Calcular nivel objetivo para Revisión Periódica
    df_completo['nivel_objetivo'] = np.where(
        df_completo['variabilidad'] == 'Variable',
        ((df_completo['mean'])/30 * (df_completo['T'] + df_completo['lead_time'] ) )+ df_completo['SS'],
        np.nan)  # Nivel objetivo no aplica para SKUs No Variables

    # Calcular punto de reorden (R) para EOQ
    df_completo['R'] = np.where(
        df_completo['variabilidad'] == 'No Variable',
        ((df_completo['mean']/30) * df_completo['lead_time']) + df_completo['SS'],
        np.nan)  # Punto de reorden no aplica para SKUs Variables

    # Asignar política sugerida
    df_completo['politica'] = np.where(
        df_completo['variabilidad'] == 'Variable',
        'Revisión Periódica',
        'EOQ')
    
    # Aplicar la lógica para generar pedidos
    # Se une la politica de inventario con la información del inventario.
    df_completo = pd.merge(df_completo, inventario[['inventario','OCs', 'consumo_ult_sem', 'Consumo_ult_mes','sku']], on='sku', how='left')
    # Tabla completa lista para aplicar las politicas
    df_completo[['inventario','OCs', 'consumo_ult_sem', 'Consumo_ult_mes'] ]= df_completo[['inventario','OCs', 'consumo_ult_sem', 'Consumo_ult_mes']].fillna(0)
    df_completo['inventario_total'] = (df_completo['inventario'] + df_completo['OCs'])
    df_completo['solicitar'] = df_completo.apply(generar_pedido, axis=1)

    # Calcular cobertura en días
    df_completo['demanda_diaria_promedio'] = df_completo['mean'] * 12 / 365
    df_completo['cobertura_dias'] = round(df_completo['inventario_total'] / df_completo['demanda_diaria_promedio'],0)
    df_completo['cobertura_meses'] = df_completo['cobertura_dias'] / 30

    df_periodico=df_completo[['sku', 'mean','clase_abc', 'bodega', 'variabilidad', 'costo',
        'lead_time', 'h', 'demanda_anual','T', 'SS',
        'nivel_objetivo','politica']][df_completo.politica=='Revisión Periódica']
    df_EOQ=df_completo[['sku', 'mean','clase_abc', 'bodega', 'variabilidad', 'costo',
        'lead_time', 'h', 'demanda_anual','R', 'EOQ',
        'politica']][df_completo.politica=='EOQ']

    df_solicitar = df_completo[['sku', 'mean','clase_abc', 'bodega', 'variabilidad',
        'lead_time','SS','politica', 'inventario', 'OCs',
    'consumo_ult_sem', 'Consumo_ult_mes', 'inventario_total', 'solicitar',
    'demanda_diaria_promedio', 'cobertura_dias', 'cobertura_meses']][( df_completo['Consumo_ult_mes'] >0 )
                                        & ( df_completo['solicitar'] >0) ].sort_values('cobertura_dias', ascending=True)

    conteo_politica_bodega = df_completo.groupby(['politica', 'bodega']).size().reset_index(name='conteo')

    return df_periodico, df_EOQ, df_solicitar, conteo_politica_bodega

def clasificacion_abc_por_bodega(df, bodega_column, sku_column, consumo_column):
    resultados = []
    conteos_abc = []

    # Agrupar por bodega
    for bodega, datos_bodega in df.groupby(bodega_column):
        # Calcular el consumo total por SKU dentro de la bodega
        consumo_por_sku = datos_bodega.groupby(sku_column)[consumo_column].sum().reset_index()
        consumo_por_sku = consumo_por_sku.sort_values(by=consumo_column, ascending=False)

        # Calcular el porcentaje acumulado
        consumo_por_sku['porcentaje'] = 100 * consumo_por_sku[consumo_column] / consumo_por_sku[consumo_column].sum()
        consumo_por_sku['porcentaje_acumulado'] = consumo_por_sku['porcentaje'].cumsum()

        # Asignar la categoría ABC
        def asignar_clase(pct_acum):
            if pct_acum <= 80:
                return 'A'
            elif pct_acum <= 95:
                return 'B'
            else:
                return 'C'

        consumo_por_sku['clase_abc'] = consumo_por_sku['porcentaje_acumulado'].apply(asignar_clase)

        # Agregar la columna de bodega para mantener el contexto
        consumo_por_sku[bodega_column] = bodega

        # Agregar a los resultados
        resultados.append(consumo_por_sku)

        # Calcular conteo de SKUs por clase ABC en esta bodega
        conteo = consumo_por_sku['clase_abc'].value_counts().reset_index()
        conteo.columns = ['clase_abc', 'conteo']
        conteo[bodega_column] = bodega
        conteos_abc.append(conteo)

    # Combinar los resultados en un solo DataFrame
    df_clasificacion_abc = pd.concat(resultados, ignore_index=True)

    # Combinar los conteos de SKUs por clase y bodega
    df_conteos_abc = pd.concat(conteos_abc, ignore_index=True)

    return df_clasificacion_abc, df_conteos_abc

def analizar_outliers_y_ajustar(data, grupo, columna):
    result = []
    for item, subset in data.groupby(grupo):
        # Calcular límites usando IQR
        Q1 = subset[columna].quantile(0.25)
        Q3 = subset[columna].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        # limite_superior = Q3 + 1.5 * IQR

        # Detectar outliers
        #subset['es_outlier'] = (subset[columna] < limite_inferior) | (subset[columna] > limite_superior)
        subset['es_outlier'] = subset[columna] < limite_inferior
        # Reemplazar valores de consumo_tm para los outliers con el promedio de los datos no outliers
        promedio_no_outliers = subset[~subset['es_outlier']][columna].mean()
        subset['consumo_ajustado'] = subset.apply(
            lambda row: promedio_no_outliers if row['es_outlier'] else row[columna], axis=1
        )

        result.append(subset)

    # Combinar resultados
    return pd.concat(result)

def analizar_tendencia_estacionalidad(df, sku_column, consumo_column, ventana=3):
    resultados_tendencia = {}
    resumen = []

    for sku, datos_sku in df.groupby(sku_column):
        datos_sku = datos_sku.sort_values(by='mes_año').set_index('mes_año')

        # Convertir el índice 'mes_año' a tipo datetime si es de tipo PeriodIndex
        if isinstance(datos_sku.index, pd.PeriodIndex):
            datos_sku.index = datos_sku.index.to_timestamp()

        # Calcular media móvil
        datos_sku['media_movil'] = datos_sku[consumo_column].rolling(window=ventana).mean()

        # Calcular coeficiente de variación (CV)
        cv = np.std(datos_sku[consumo_column]) / np.mean(datos_sku[consumo_column]) if np.mean(datos_sku[consumo_column]) != 0 else 0
        variabilidad = "Variable" if cv > 0.5 else "No Variable"

        # Análisis de tendencia con regresión lineal
        try:
            x = np.arange(len(datos_sku))
            y = datos_sku[consumo_column].values
            slope, intercept, _, _, _ = linregress(x, y)
            tendencia = "Ascendente" if slope > 0 else "Descendente" if slope < 0 else "No Tiene Tendencia"
        except ValueError:
            tendencia = "Datos insuficientes"

        # Análisis de estacionalidad y meses estacionales
        try:
            descomposicion = seasonal_decompose(datos_sku[consumo_column], model='additive', period=12)
            var_estacional = np.var(descomposicion.seasonal.dropna())
            var_residuo = np.var(descomposicion.resid.dropna())
            estacionalidad = "Estacional" if var_estacional > var_residuo else "No Estacional"

            # Identificar los meses estacionales si la serie es estacional
            if estacionalidad == "Estacional":
                meses_estacionales = descomposicion.seasonal.groupby(descomposicion.seasonal.index.month).mean()
                meses_altos = meses_estacionales[meses_estacionales > meses_estacionales.mean()].index.tolist()
                meses_estacionales = [f'Mes {mes}' for mes in meses_altos]
            else:
                meses_estacionales = []

        except ValueError:
            estacionalidad = "Datos insuficientes"
            meses_estacionales = []

        # Guardar resultados en el diccionario
        resultados_tendencia[sku] = {
            'cv': cv,
            'variabilidad': variabilidad,
            'tendencia': tendencia,
            'estacionalidad': estacionalidad,
            'meses_estacionales': meses_estacionales,
            'datos_sku': datos_sku,
            'descomposicion': descomposicion if estacionalidad == "Estacional" else None
        }

        # Agregar a la lista para el DataFrame resumen
        resumen.append({
            'sku': sku,
            'estacionalidad': estacionalidad,
            'variabilidad': variabilidad,
            'tendencia': tendencia
        })

    # Crear el DataFrame resumen
    df_resumen = pd.DataFrame(resumen)

    return resultados_tendencia, df_resumen

def generar_pronosticos(df_mensual, summary, pasos_pronostico=3):
    resultados = []
    pronosticos_finales = []

    for sku in summary['sku']:
        # Filtrar la serie histórica para el SKU
        serie_historica = df_mensual[df_mensual['sku'] == sku].sort_values(by='mes_año')
        serie_historica.set_index('mes_año', inplace=True)
        consumo_tm = serie_historica['consumo_tm']

        # Dividir en entrenamiento y prueba
        entrenamiento = consumo_tm[:-pasos_pronostico]
        prueba = consumo_tm[-pasos_pronostico:]

        # Evaluar todos los modelos y seleccionar el mejor
        mejor_modelo, predicciones, evaluaciones = evaluar_modelos(entrenamiento, prueba, pasos_pronostico)
        bodega = serie_historica['bodega'].iloc[0] 
        # Agregar predicciones al DataFrame final
        for i in range(pasos_pronostico):
            nueva_fecha = consumo_tm.index[-1].to_timestamp() + pd.DateOffset(months=i+1)
            valor_pronosticado = predicciones[i] if predicciones is not None else np.nan
            pronosticos_finales.append({
                'mes_año': nueva_fecha,
                'sku': sku,
                'bodega': bodega,
                'consumo_tm': valor_pronosticado,
                'tipo': 'pronostico'
            })

        # Guardar los resultados del modelo y errores
       

        resultados.append({
            'sku': sku,
            'bodega': bodega,
            'mejor_modelo': mejor_modelo[0],
            'mae': mejor_modelo[1],
            'evaluaciones': evaluaciones
        })

    # Crear DataFrames finales
    df_pronosticos = pd.DataFrame(pronosticos_finales)
    df_modelos = pd.DataFrame(resultados)

    return df_pronosticos, df_modelos

def evaluar_modelos(serie_entrenamiento, serie_prueba, pasos_pronostico):
    """
    Prueba diferentes modelos de pronóstico y selecciona el mejor según MAE en la prueba.
    """
    resultados_modelos = []
    predicciones_modelos = {}

    # Modelo 1: SARIMA
    try:
        sarima = SARIMAX(serie_entrenamiento, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)).fit(disp=False)
        pred_sarima = sarima.get_forecast(steps=pasos_pronostico).predicted_mean
        mae_sarima = mean_absolute_error(serie_prueba, pred_sarima[:len(serie_prueba)])
        resultados_modelos.append(('SARIMA', mae_sarima))
        predicciones_modelos['SARIMA'] = pred_sarima
    except:
        pass

    # Modelo 2: Holt-Winters
    try:
        hw = ExponentialSmoothing(serie_entrenamiento, seasonal='add', seasonal_periods=12).fit()
        pred_hw = hw.forecast(steps=pasos_pronostico)
        mae_hw = mean_absolute_error(serie_prueba, pred_hw[:len(serie_prueba)])
        resultados_modelos.append(('Holt-Winters', mae_hw))
        predicciones_modelos['Holt-Winters'] = pred_hw
    except:
        pass

    # Modelo 3: ARIMA
    try:
        arima = SARIMAX(serie_entrenamiento, order=(1, 1, 1)).fit(disp=False)
        pred_arima = arima.get_forecast(steps=pasos_pronostico).predicted_mean
        mae_arima = mean_absolute_error(serie_prueba, pred_arima[:len(serie_prueba)])
        resultados_modelos.append(('ARIMA', mae_arima))
        predicciones_modelos['ARIMA'] = pred_arima
    except:
        pass

    # Modelo 4: Regresión Lineal
    try:
        x = np.arange(len(serie_entrenamiento)).reshape(-1, 1)
        y = serie_entrenamiento.values
        reg = LinearRegression().fit(x, y)
        x_future = np.arange(len(serie_entrenamiento), len(serie_entrenamiento) + pasos_pronostico).reshape(-1, 1)
        pred_lr = reg.predict(x_future)
        mae_lr = mean_absolute_error(serie_prueba, reg.predict(np.arange(len(serie_entrenamiento)-len(serie_prueba), len(serie_entrenamiento)).reshape(-1, 1)))
        resultados_modelos.append(('Regresión Lineal', mae_lr))
        predicciones_modelos['Regresión Lineal'] = pred_lr
    except:
        pass

    # Seleccionar el mejor modelo
    mejor_modelo = min(resultados_modelos, key=lambda x: x[1]) if resultados_modelos else (None, None)

    return mejor_modelo, predicciones_modelos.get(mejor_modelo[0], None), resultados_modelos

# Calcular si se debe solicitar según la política de inventario
def generar_pedido(row):
    if row['politica'] == 'EOQ':
        # Si el inventario total está por debajo del punto de reorden (R)
        if row['inventario_total'] < row['R']:
            return row['EOQ']  # Pedido por EOQ
        else:
            return 0  # No se necesita pedido
    elif row['politica'] == 'Revisión Periódica':
        # Pedido para alcanzar el nivel objetivo
        return max(row['nivel_objetivo'] - row['inventario_total'], 0)
    else:
        return 0  # No se aplica ninguna política
