from fastapi import FastAPI, Query
import logging
import threading
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional
from utils import cargar_datos_1, cargar_datos_2, cargar_datos_3, cargar_datos_4, cargar_datos_5, cargar_datos_6
from constants import CURRENT_YEAR, ALLOWED_ORIGINS
import warnings
warnings.filterwarnings('ignore')

# Create a logger object
logger = logging.getLogger('uvicorn.error')

# Create an instance of FastAPi
app = FastAPI()

# Parsing the allowed origins from the environment variable
allowed_origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_loaded = False

def ensure_data_loaded():
    global data_loaded
    if not data_loaded:
        print("INFO:     Starting loading data.")
        global df_mensual, df_semanal, df_analizado, df_ultimos_6, summary
        global conteo_modelo_bodega, df_abc, df_conteos, df_unido
        global df_periodico, df_EOQ, df_solicitar, conteo_politica_bodega

        df_mensual = cargar_datos_1()
        df_semanal = cargar_datos_2(field='week')
        df_analizado, df_ultimos_6, summary, conteo_modelo_bodega = cargar_datos_3(df_mensual)
        df_abc, df_conteos = cargar_datos_4(df_analizado)
        df_unido = cargar_datos_5(df_ultimos_6, df_abc, summary)
        df_periodico, df_EOQ, df_solicitar, conteo_politica_bodega = cargar_datos_6(df_unido)

        data_loaded = True
        print("INFO:     Finished loading data.")

@app.on_event("startup")
def startup_event():    
    # Run load data in a separate thread to avoid blocking startup
    threading.Thread(target=ensure_data_loaded).start()

@app.get("/health")
def health():
    if not data_loaded:
        return {"status": "initializing"}
    return {"status": "ok"}

@app.get("/api/line-chart-1")
def get_line_chart_1(
    year: Optional[List[int]] = Query(None, alias="anio"),  # Filter by year
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    # Apply filters based on query parameters
    filtered_df = df_mensual
    
    # Filter by year if specified
    if year:
        filtered_df = filtered_df[filtered_df['mes_año'].dt.year.isin(year)]
    
    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]

    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]    
    
    # Group the filtered data by 'mes_año', 'sku', and 'bodega' and sum 'consumo_tm'
    chart_data = filtered_df.groupby(['mes_año', 'sku', 'bodega'])['consumo_tm'].sum().reset_index()

    # Prepare the response format
    response_data = []
    for sku_value in chart_data['sku'].unique():
        sku_data = chart_data[chart_data['sku'] == sku_value]
        sku_data_dict = {
            "name": sku_value, # sku
            "data": [ # values
                {"x": row["mes_año"].strftime('%Y-%m'), "y": round(row["consumo_tm"], 2)}
                for _, row in sku_data.iterrows()
            ]
        }
        response_data.append(sku_data_dict)

    return {"data": response_data}

@app.get("/api/line-chart-2")
def get_line_chart_2(
    year: Optional[List[int]] = Query(None, alias="anio"),  # Filter by year
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    # Apply filters based on query parameters
    filtered_df = df_semanal

    # Filter by year if specified
    if year:
        filtered_df = filtered_df[filtered_df['anio'].isin(year)]

    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]

    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]    

    # Group the filtered data by 'mes_año', 'sku', and 'bodega' and sum 'consumo_tm'
    chart_data = filtered_df.groupby(['semana', 'sku', 'bodega'])['consumo_tm'].sum().reset_index()

    # Prepare the response format
    response_data = []
    for sku_value in chart_data['sku'].unique():
        sku_data = chart_data[chart_data['sku'] == sku_value]
        sku_data_dict = {
            "name": sku_value, # sku
            "data": [ # values
                {"x": row["semana"], "y": round(row["consumo_tm"], 2)}
                for _, row in sku_data.iterrows()
            ]
        }
        response_data.append(sku_data_dict)

    return {"data": response_data}

@app.get("/api/line-chart-3")
def get_line_chart_3(
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    # Seleccionar los últimos 6 registros por SKU
    filtered_df = df_ultimos_6
    # Filter by current year
    filtered_df = filtered_df[filtered_df['mes_año'].dt.year.isin([CURRENT_YEAR])] 
    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]
    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]
    # Split into forecast and consumption data
    # forecast_df = filtered_df[filtered_df['tipo'] == 'pronostico']
    df_consumos = filtered_df[filtered_df['tipo'].isna()]
    # Convert the 'mes_año' column to a list
    last_mes_año = df_consumos['mes_año'].max() if not df_consumos.empty else None
    
    response_data = []
    for sku_value in filtered_df['sku'].unique():
        sku_data = filtered_df[filtered_df['sku'] == sku_value]
        default_dict = { # For standard consumption logic
            "name": sku_value, # SKU name 
            "type": "line",
            "data": []
        }
        forecast_dict = {
            "name": f"{sku_value} - FORECAST", # Adding forecast to SKU name
            "type": "line",
            "data": []
        }
        for _, row in sku_data.iterrows():
            x_value =row["mes_año"].strftime('%Y-%m')
            y_value = round(row["consumo_tm"] if pd.notna(row["consumo_tm"]) else 0, 2)
            if row['tipo'] == 'pronostico': # For forecast data
                # Pronostico logic: 'y' is None for forecast
                default_dict['data'].append({ "x": x_value, "y": None })
                forecast_dict['data'].append({ "x": x_value, "y": y_value })
            elif row['mes_año'] == last_mes_año: # Last month logic (continuity)
                # Copy the last value from filtered to forecast line
                default_dict['data'].append({ "x": x_value, "y": y_value })
                forecast_dict['data'].append({ "x": x_value, "y": y_value })
            else: # For filtered logic
                # Standard filtered data and forecast logicc
                forecast_dict['data'].append({ "x": x_value, "y": None })
                default_dict['data'].append({ "x": x_value, "y": y_value })
        response_data.append(default_dict)
        response_data.append(forecast_dict)

    return {"data": response_data}

@app.get("/api/pie-chart-1")
def get_pie_chart_1(bodega: Optional[List[str]] = Query(None)):
    filtered_df = df_conteos
    print(df_conteos)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]    
    # Example of what to send in the response (using df_conteos for simplicity)
    # This assumes that you want to send the sum of 'consumo_ajustado' for each 'bodega'
    pie_data = {
        "labels": filtered_df['clase_abc'].tolist(),
        "series": filtered_df['conteo'].tolist()
    }
    return {
        "data": pie_data
    }

@app.get("/api/pie-chart-2")
def get_pie_chart_2(bodega: Optional[List[str]] = Query(None)):
    filtered_df = conteo_modelo_bodega
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]    
    # Example of what to send in the response (using df_conteos for simplicity)
    # This assumes that you want to send the sum of 'consumo_ajustado' for each 'bodega'
    pie_data = {
        "labels": filtered_df['mejor_modelo'].tolist(),
        "series": filtered_df['conteo'].tolist()
    }
    return {
        "data": pie_data
    }

@app.get("/api/pie-chart-3")
def get_pie_chart_1(bodega: Optional[List[str]] = Query(None)):
    filtered_df = conteo_politica_bodega
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]    
    # Example of what to send in the response (using df_conteos for simplicity)
    # This assumes that you want to send the sum of 'consumo_ajustado' for each 'bodega'
    pie_data = {
        "labels": filtered_df['politica'].tolist(),
        "series": filtered_df['conteo'].tolist()
    }
    return {
        "data": pie_data
    }

@app.get("/api/table-1")
def get_table_1(
    page: int = Query(1, ge=1),  # Page number, minimum 1
    page_size: int = Query(10, ge=1, le=100),  # Page size, between 1 and 100
    disable_pagination: bool = Query(False),  # Option to disable pagination
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
    clase_abc: Optional[List[str]] = Query(None),  # Filter by clase_abc (default includes both)
    ):
    filtered_df = df_abc.reset_index()
    filtered_df = filtered_df.fillna(0)
    filtered_df = filtered_df[['sku', 'clase_abc', 'bodega']]

    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]
        # Filter by bodega if specified (allow multiple selections)

    if clase_abc:
        filtered_df = filtered_df[filtered_df['clase_abc'].isin(clase_abc)]
        # Filter by bodega if specified (allow multiple selections)

    # Total number of records
    total_records = len(filtered_df)

    filtered_df = filtered_df.to_dict(orient='records')

    # If pagination is disabled, return all data
    if disable_pagination:
        return {
            "data": filtered_df
        }
    
    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Slice the data for the current page
    paginated_data = filtered_df[start_index:end_index]
    
    # Calculate total pages
    total_pages = (total_records + page_size - 1) // page_size
    
    return {
        "data": paginated_data,
        "total": total_records,
        "page": page,
        "total_pages": total_pages
    }

@app.get("/api/table-2")
def get_table_2(
    page: int = Query(1, ge=1),  # Page number, minimum 1
    page_size: int = Query(10, ge=1, le=100),  # Page size, between 1 and 100
    disable_pagination: bool = Query(False),  # Option to disable pagination
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    filtered_df = df_unido.reset_index()
    filtered_df = filtered_df.fillna(0)
    filtered_df = filtered_df[['sku', 'mean', 'std', 'clase_abc', 'bodega', 'variabilidad']]

    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]
    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]

    # Round the numeric columns to 2 decimal places
    filtered_df['mean'] = filtered_df['mean'].round(2)
    filtered_df['std'] = filtered_df['std'].round(2)

    # Total number of records
    total_records = len(filtered_df)

    filtered_df = filtered_df.to_dict(orient='records')

    # If pagination is disabled, return all data
    if disable_pagination:
        return {
            "data": filtered_df
        }
    
    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Slice the data for the current page
    paginated_data = filtered_df[start_index:end_index]
    
    # Calculate total pages
    total_pages = (total_records + page_size - 1) // page_size
    
    return {
        "data": paginated_data,
        "total": total_records,
        "page": page,
        "total_pages": total_pages
    }


@app.get("/api/table-3")
def get_table_3(
    page: int = Query(1, ge=1),  # Page number, minimum 1
    page_size: int = Query(10, ge=1, le=100),  # Page size, between 1 and 100
    disable_pagination: bool = Query(False),  # Option to disable pagination
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    filtered_df = df_periodico.reset_index()
    filtered_df = filtered_df.fillna(0)

    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]
    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]

    # Total number of records
    total_records = len(filtered_df)

    # Apply rounding to relevant fields
    columns_to_round = ['mean', 'costo', 'h', 'demanda_anual', 'SS', 'nivel_objetivo']
    
    for column in columns_to_round:
        filtered_df[column] = filtered_df[column].round(2)
    
    filtered_df = filtered_df.to_dict(orient='records')

    # If pagination is disabled, return all data
    if disable_pagination:
        return {
            "data": filtered_df
        }
    
    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Slice the data for the current page
    paginated_data = filtered_df[start_index:end_index]
    
    # Calculate total pages
    total_pages = (total_records + page_size - 1) // page_size
    
    return {
        "data": paginated_data,
        "total": total_records,
        "page": page,
        "total_pages": total_pages
    }


@app.get("/api/table-4")
def get_table_4(
    page: int = Query(1, ge=1),  # Page number, minimum 1
    page_size: int = Query(10, ge=1, le=100),  # Page size, between 1 and 100
    disable_pagination: bool = Query(False),  # Option to disable pagination
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    filtered_df = df_EOQ.reset_index()
    filtered_df = filtered_df.fillna(0)

    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]
    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]

    # Total number of records
    total_records = len(filtered_df)

    # Columns to round
    columns_to_round = ['mean', 'costo', 'h', 'demanda_anual', 'R', 'EOQ']

    # Apply rounding to each of the columns in the list
    for column in columns_to_round:
        filtered_df[column] = filtered_df[column].round(2)

    # Convert the dataframe to a list of dictionaries
    filtered_df = filtered_df.to_dict(orient='records')

    # If pagination is disabled, return all data
    if disable_pagination:
        return {
            "data": filtered_df
        }

    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Slice the data for the current page
    paginated_data = filtered_df[start_index:end_index]

    # Calculate total pages
    total_pages = (total_records + page_size - 1) // page_size

    return {
        "data": paginated_data,
        "total": total_records,
        "page": page,
        "total_pages": total_pages
    }


@app.get("/api/table-5")
def get_table_5(
    page: int = Query(1, ge=1),  # Page number, minimum 1
    page_size: int = Query(10, ge=1, le=100),  # Page size, between 1 and 100
    disable_pagination: bool = Query(False),  # Option to disable pagination
    sku: Optional[List[str]] = Query(None),  # Filter by sku (allow multiselect)
    bodega: Optional[List[str]] = Query(None),  # Filter by bodega (default includes both)
):
    filtered_df = df_solicitar.reset_index()
    filtered_df = filtered_df.fillna(0)

    # Filter by sku if specified (allow multiple selections)
    if sku:
        filtered_df = filtered_df[filtered_df['sku'].isin(sku)]
    # Filter by bodega if specified (allow multiple selections)
    if bodega:
        filtered_df = filtered_df[filtered_df['bodega'].isin(bodega)]

    # Total number of records
    total_records = len(filtered_df)

    # List of columns to round
    columns_to_round = [
        'mean', 'lead_time', 'SS', 'inventario', 'OCs', 'consumo_ult_sem',
        'Consumo_ult_mes', 'inventario_total', 'solicitar', 'demanda_diaria_promedio',
        'cobertura_dias', 'cobertura_meses'
    ]

    # Apply rounding to the specified columns
    for column in columns_to_round:
        filtered_df[column] = filtered_df[column].round(2)

    # Convert the dataframe to a list of dictionaries
    filtered_df = filtered_df.to_dict(orient='records')

    # If pagination is disabled, return all data
    if disable_pagination:
        return {
            "data": filtered_df
        }

    # Calculate pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Slice the data for the current page
    paginated_data = filtered_df[start_index:end_index]

    # Calculate total pages
    total_pages = (total_records + page_size - 1) // page_size

    return {
        "data": paginated_data,
        "total": total_records,
        "page": page,
        "total_pages": total_pages
    }


@app.get("/api/available-skus")
def get_available_skus(bodega: Optional[str] = Query(None)):
    # If bodega filter is provided, filter by bodega
    if bodega:
        skus = df_mensual[df_mensual['bodega'] == bodega]['sku'].unique().tolist()
    else:
        # If no bodega filter is provided, return all SKUs
        skus = df_mensual['sku'].unique().tolist()
    
    return {"data": skus}

@app.get("/api/available-years")
def get_available_years():
    years = df_mensual['mes_año'].dt.year.unique().astype(str).tolist()  # Convert years to strings
    return {"data": years}

@app.get("/api/available-bodegas")
def get_available_bodegas():
    bodegas = df_mensual['bodega'].unique().tolist()
    return {"data": bodegas}
