import pandas as pd
import os

# Importa o logger
try:
    from .logger import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.utils.logger import setup_logger

logger = setup_logger()

def summarize_producers_by_extensionist(df: pd.DataFrame, output_dir: str, file_name: str = 'producers_by_extensionist_summary.csv') -> None:
    """
    Sumariza a quantidade de produtores únicos atendidos por cada Extensionista_Proposto
    e exporta o resultado para um arquivo CSV.

    Args:
        df (pd.DataFrame): DataFrame otimizado contendo a coluna 'Extensionista_Proposto' e 'Nome_Produtor'.
        output_dir (str): Diretório onde o arquivo CSV de sumarização será salvo.
        file_name (str): Nome do arquivo CSV de saída.
    """
    if 'Extensionista_Proposto' not in df.columns or 'Nome_Produtor' not in df.columns or 'ID_Aviario' not in df.columns or 'Extensionista_Atual' not in df.columns:
        logger.error("DataFrame não contém as colunas necessárias para sumarização (Extensionista_Proposto, Nome_Produtor, ID_Aviario, Extensionista_Atual).")
        return

    # Sumário de produtores e aviários propostos
    proposed_summary_df = df.groupby('Extensionista_Proposto').agg(
        Total_Produtores_Propostos=('Nome_Produtor', 'nunique'),
        Total_Aviarios_Propostos=('ID_Aviario', 'count')
    ).reset_index()

    # Sumário de aviários atuais por extensionista atual
    current_aviaries_df = df.groupby('Extensionista_Atual')['ID_Aviario'].count().reset_index()
    current_aviaries_df.rename(columns={'ID_Aviario': 'Total_Aviarios_Atuais'}, inplace=True)

    # Mapear os aviários atuais para os extensionistas propostos
    # Isso é um pouco complexo, pois um Extensionista_Atual pode se tornar um Extensionista_Proposto
    # ou ser substituído por uma 'Região X'.
    # Para simplificar, vamos tentar mapear diretamente onde os nomes coincidem.
    # Para os que não coincidem, teremos que deixar como NaN ou 0.

    # Criar um DataFrame para o resultado final
    final_summary_df = proposed_summary_df.copy()

    # Adicionar a coluna de aviários atuais, tentando corresponder os nomes
    # Se um Extensionista_Proposto é um Extensionista_Atual existente, trazemos seus aviários atuais.
    # Caso contrário, será NaN.
    final_summary_df = pd.merge(
        final_summary_df,
        current_aviaries_df,
        left_on='Extensionista_Proposto',
        right_on='Extensionista_Atual',
        how='left'
    )
    final_summary_df.drop(columns=['Extensionista_Atual'], inplace=True)
    final_summary_df['Total_Aviarios_Atuais'] = final_summary_df['Total_Aviarios_Atuais'].fillna(0).astype(int)

    # Calcular a diferença
    final_summary_df['Diferenca_Aviarios'] = final_summary_df['Total_Aviarios_Propostos'] - final_summary_df['Total_Aviarios_Atuais']

    final_summary_df = final_summary_df.sort_values(by='Total_Produtores_Propostos', ascending=False)

    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, file_name)
    final_summary_df.to_csv(output_file_path, sep=';', decimal='.', index=False)
    logger.info(f"Sumário de produtores e aviários por extensionista exportado para: {output_file_path}")

if __name__ == "__main__":
    logger.info("Este módulo é destinado a ser importado e usado por outros scripts.")
    logger.info("Para testar a funcionalidade, execute main.py.")
