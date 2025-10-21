import sys
import pandas as pd
import os

# Adiciona o diretório raiz do projeto ao sys.path para que as importações funcionem
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from src.utils.logger import setup_logger
from src.utils.data_loader import load_exportation_data
from src.utils.geo_processor import GeoProcessor
from src.utils.clustering_model import ClusteringModel
from src.utils.summary_utils import summarize_producers_by_extensionist

logger = setup_logger()

def main():
    logger.info("Iniciando o processo de Remodelação e Otimização Geográfica de Extensionistas...")

    # 1. Carregar os dados
    df_data = load_exportation_data()
    if df_data is None:
        logger.error("Falha ao carregar os dados. Encerrando.")
        return
    logger.info(f"Dados carregados com sucesso. Total de {len(df_data)} registros.")

    # 2. Configurar e aplicar o GeoProcessor
    immutability_rules = [
        {
            'type': 'compound_and',
            'sub_rules': [
                {'column': 'Extensionista_Atual', 'type': 'in_list', 'list_name': 'immutable_extensionists'},
                {'column': 'Nome_Produtor', 'type': 'in_list', 'list_name': 'immutable_producers'}
            ]
        }
    ]
    geo_processor = GeoProcessor(
        immutability_rules=immutability_rules,
        immutable_producers_file='PRODUTORES_IMUTAVEIS.csv',
        immutable_extensionists_file='EXTENSIONISTAS_IMUTAVEIS.csv'
    )
    df_processed = geo_processor.apply_immutability_rules(df_data.copy())
    logger.info(f"GeoProcessor aplicado. {df_processed['immutable_allocation'].sum()} aviários marcados como imutáveis.")

    # 3. Configurar e aplicar o ClusteringModel
    # Extrair extensionistas atuais para o modelo
    current_extensionists = df_processed['Extensionista_Atual'].unique().tolist()

    # Definir a média desejada de aviários por extensionista (exemplo, pode vir de input do usuário)
    desired_avg_aviaries = 40 # Exemplo: 40 aviários por extensionista

    clustering_model = ClusteringModel(
        target_aviaries_min=40,
        target_aviaries_max=43,
        current_extensionists=current_extensionists,
        desired_avg_aviaries_per_extensionist=desired_avg_aviaries
    )
    df_optimized = clustering_model.optimize_allocation(df_processed.copy())
    logger.info("ClusteringModel aplicado. Alocação otimizada gerada.")

    # 4. Exibir e exportar resultados
    logger.info("Primeiras 5 linhas do DataFrame otimizado:")
    print(df_optimized[['ID_Aviario', 'ID_Nucleo', 'Microrregiao', 'Extensionista_Atual', 'Extensionista_Proposto', 'immutable_allocation']].head())

    exports_dir = os.path.join(project_root, 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    output_file_path = os.path.join(exports_dir, 'final_optimized_allocation.csv')
    df_optimized.to_csv(output_file_path, sep=';', decimal='.', index=False)
    logger.info(f"Alocação otimizada final exportada para: {output_file_path}")

    # 5. Sumarizar produtores por extensionista
    summarize_producers_by_extensionist(df_optimized, exports_dir)

if __name__ == "__main__":
    main()
