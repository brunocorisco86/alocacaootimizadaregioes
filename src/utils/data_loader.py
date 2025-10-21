import pandas as pd
import os
try:
    from .logger import setup_logger
except ImportError:
    # Fallback for direct execution (e.g., python data_loader.py)
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.utils.logger import setup_logger

logger = setup_logger()

def load_exportation_data(file_name="exportation.csv"):
    """
    Carrega o arquivo CSV de exportação de dados de aviários.

    Args:
        file_name (str): O nome do arquivo CSV a ser carregado. Padrão é "exportation.csv".

    Returns:
        pd.DataFrame: Um DataFrame do pandas contendo os dados do arquivo CSV.
                      Retorna None se o arquivo não for encontrado ou ocorrer um erro.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(base_path, '..', '..', 'assets')
    file_path = os.path.join(assets_path, file_name)

    try:
        df = pd.read_csv(file_path, sep=';', decimal=',')
        logger.info(f"Arquivo '{file_name}' carregado com sucesso. {len(df)} registros encontrados.")

        # Criar a coluna 'Coordenadas' no formato 'latitude,longitude' com ponto como separador decimal
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            df['Coordenadas'] = df['Latitude'].astype(str) + ',' + df['Longitude'].astype(str)
            # Ensure Latitude and Longitude are float for later use if needed, and convert back to string for Coordenadas
            df['Latitude'] = df['Latitude'].astype(float)
            df['Longitude'] = df['Longitude'].astype(float)
        else:
            logger.warning("Colunas 'Latitude' ou 'Longitude' não encontradas para criar 'Coordenadas'.")

        # Renomear a coluna 'Extensionista' para 'Extensionista_Atual'
        if 'Extensionista' in df.columns:
            df.rename(columns={'Extensionista': 'Extensionista_Atual'}, inplace=True)
        else:
            logger.warning("Coluna 'Extensionista' não encontrada para renomear para 'Extensionista_Atual'.")

        return df
    except FileNotFoundError:
        logger.error(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo '{file_path}': {e}")
        return None

def load_list_from_csv(file_name: str, column_name: str, separator: str = ';') -> list:
    """
    Carrega uma lista de valores de uma coluna específica de um arquivo CSV.

    Args:
        file_name (str): O nome do arquivo CSV a ser carregado da pasta /assets.
        column_name (str): O nome da coluna de onde os valores devem ser extraídos.
        separator (str): O delimitador do arquivo CSV. Padrão é ';'.

    Returns:
        list: Uma lista de strings contendo os valores da coluna especificada.
              Retorna uma lista vazia se o arquivo não for encontrado, a coluna não existir ou ocorrer um erro.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(base_path, '..', '..', 'assets')
    file_path = os.path.join(assets_path, file_name)

    try:
        df = pd.read_csv(file_path, sep=separator)
        if column_name in df.columns:
            logger.info(f"Arquivo '{file_name}' carregado com sucesso. {len(df)} registros encontrados na coluna '{column_name}'.")
            return df[column_name].astype(str).tolist()
        else:
            logger.warning(f"Coluna '{column_name}' não encontrada no arquivo '{file_name}'. Retornando lista vazia.")
            return []
    except FileNotFoundError:
        logger.error(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return []
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo '{file_path}': {e}")
        return []


if __name__ == "__main__":
    logger.info("Testando a função load_exportation_data...")
    df_data = load_exportation_data()

    if df_data is not None:
        logger.info("Primeiras 5 linhas do DataFrame:")
        print(df_data.head())
        logger.info(f"Colunas do DataFrame: {df_data.columns.tolist()}")
    else:
        logger.warning("Não foi possível carregar os dados para teste.")