import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
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

class GeoProcessor:
    """
    Processa dados geográficos e aplica restrições espaciais para a otimização de alocação de extensionistas.
    """

    def __init__(self, immutability_rules: list = None, immutable_producers_file: str = None, immutable_extensionists_file: str = None):
        """
        Inicializa o GeoProcessor com regras de imutabilidade e, opcionalmente, arquivos de produtores e extensionistas imutáveis.

        Args:
            immutability_rules (list, optional): Lista de dicionários, onde cada dicionário define uma regra de imutabilidade.
            immutable_producers_file (str, optional): Nome do arquivo CSV em /assets contendo os produtores imutáveis.
            immutable_extensionists_file (str, optional): Nome do arquivo CSV em /assets contendo os extensionistas imutáveis.
        """
        self.immutability_rules = immutability_rules if immutability_rules is not None else []
        self.immutable_producers = []
        self.immutable_extensionists = []

        try:
            from .data_loader import load_list_from_csv
        except ImportError:
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            from src.utils.data_loader import load_list_from_csv

        if immutable_producers_file:
            self.immutable_producers = load_list_from_csv(immutable_producers_file, 'Nome_Produtor', separator=';')
            logger.info(f"Carregados {len(self.immutable_producers)} produtores imutáveis do arquivo {immutable_producers_file}.")

        if immutable_extensionists_file:
            self.immutable_extensionists = load_list_from_csv(immutable_extensionists_file, 'Extensionista_Atual', separator=';')
            logger.info(f"Carregados {len(self.immutable_extensionists)} extensionistas imutáveis do arquivo {immutable_extensionists_file}.")

        logger.info(f"GeoProcessor inicializado com {len(self.immutability_rules)} regras de imutabilidade.")

    def apply_immutability_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica as regras de imutabilidade definidas na inicialização.
        Marca os aviários que não devem ter sua alocação alterada.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados dos aviários.

        Returns:
            pd.DataFrame: DataFrame com uma nova coluna 'immutable_allocation' (True/False).
        """
        df['immutable_allocation'] = False
        combined_condition = pd.Series([False] * len(df))

        for rule in self.immutability_rules:
            rule_type = rule.get('type', 'exact')
            condition = pd.Series([False] * len(df))

            if rule_type == 'compound_and':
                sub_rules = rule.get('sub_rules', [])
                compound_condition = pd.Series([True] * len(df))
                for sub_rule in sub_rules:
                    sub_column = sub_rule.get('column')
                    sub_value = sub_rule.get('value')
                    sub_rule_type = sub_rule.get('type', 'exact')
                    sub_list_name = sub_rule.get('list_name')

                    if sub_column not in df.columns:
                        logger.warning(f"Coluna '{sub_column}' não encontrada no DataFrame para sub-regra de imutabilidade. Sub-regra ignorada.")
                        compound_condition = pd.Series([False] * len(df)) # Se uma coluna não existe, a condição composta é falsa
                        break

                    sub_condition = pd.Series([False] * len(df))
                    if sub_rule_type == 'exact':
                        sub_condition = (df[sub_column] == sub_value)
                    elif sub_rule_type == 'contains':
                        sub_condition = (df[sub_column].str.contains(sub_value, na=False))
                    elif sub_rule_type == 'in_list':
                        if sub_list_name == 'immutable_producers' and self.immutable_producers:
                            sub_condition = (df[sub_column].isin(self.immutable_producers))
                        elif sub_list_name == 'immutable_extensionists' and self.immutable_extensionists:
                            sub_condition = (df[sub_column].isin(self.immutable_extensionists))
                        else:
                            logger.warning(f"Lista de imutabilidade '{sub_list_name}' não encontrada ou vazia para sub-regra. Sub-regra ignorada.")
                            compound_condition = pd.Series([False] * len(df)) # Se a lista não existe, a condição composta é falsa
                            break
                    else:
                        logger.warning(f"Tipo de sub-regra de imutabilidade desconhecido ou incompleto: {sub_rule_type}. Sub-regra ignorada.")
                        compound_condition = pd.Series([False] * len(df)) # Se o tipo é desconhecido, a condição composta é falsa
                        break
                    compound_condition = compound_condition & sub_condition
                condition = compound_condition

            else: # Existing single rules
                column = rule.get('column')
                value = rule.get('value')
                rule_type = rule.get('type', 'exact') # 'exact', 'contains', 'in_list'
                list_name = rule.get('list_name') # Novo para regras in_list fora de compound_and

                if column not in df.columns:
                    logger.warning(f"Coluna '{column}' não encontrada no DataFrame para regra de imutabilidade. Regra ignorada.")
                    continue

                if rule_type == 'exact':
                    condition = (df[column] == value)
                elif rule_type == 'contains':
                    condition = (df[column].str.contains(value, na=False))
                elif rule_type == 'in_list':
                    if list_name == 'immutable_producers' and self.immutable_producers:
                        condition = (df[column].isin(self.immutable_producers))
                    elif list_name == 'immutable_extensionists' and self.immutable_extensionists:
                        condition = (df[column].isin(self.immutable_extensionists))
                    else:
                        logger.warning(f"Lista de imutabilidade '{list_name}' não encontrada ou vazia para regra. Regra ignorada.")
                        continue
                else:
                    logger.warning(f"Tipo de regra de imutabilidade desconhecido ou incompleto: {rule_type}. Regra ignorada.")
                    continue
            
            combined_condition = combined_condition | condition

        df.loc[combined_condition, 'immutable_allocation'] = True
        logger.info(f"Aplicada restrição de imutabilidade. {df['immutable_allocation'].sum()} aviários marcados como imutáveis.")
        return df

    def check_geographical_continuity(self, gdf: gpd.GeoDataFrame) -> bool:
        """
        Verifica a continuidade geográfica das regiões. (Lógica placeholder - a ser desenvolvida).
        Esta é uma função complexa que exigirá algoritmos de análise espacial.

        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame contendo as geometrias das regiões ou aviários.

        Returns:
            bool: True se a continuidade for mantida, False caso contrário.
        """
        logger.warning("Lógica de verificação de continuidade geográfica ainda não implementada. Retornando True por padrão.")
        # TODO: Implementar lógica robusta de verificação de continuidade geográfica usando geopandas/shapely
        return True




if __name__ == "__main__":
    logger.info("Testando a classe GeoProcessor com dados reais e regras de imutabilidade dinâmicas...")
    try:
        from .data_loader import load_exportation_data
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from src.utils.data_loader import load_exportation_data

    df_real = load_exportation_data()

    if df_real is not None:
        # Definir as regras de imutabilidade
        immutability_rules = [
            {'column': 'Extensionista_Atual', 'type': 'in_list'},
            {'column': 'Nome_Produtor', 'type': 'in_list'} # Agora usa a lista carregada do arquivo
        ]
        geo_processor = GeoProcessor(immutability_rules=immutability_rules, immutable_producers_file='PRODUTORES_IMUTAVEIS.csv', immutable_extensionists_file='EXTENSIONISTAS_IMUTAVEIS.csv')

        # Testa a aplicação da imutabilidade
        df_processed = geo_processor.apply_immutability_rules(df_real.copy())
        logger.info("DataFrame após aplicar imutabilidade (primeiras 5 linhas):")
        # Exportar o DataFrame processado para um arquivo CSV na pasta /exports
        exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'exports'))
        os.makedirs(exports_dir, exist_ok=True)
        output_file_path = os.path.join(exports_dir, 'geo_processor_output.csv')
        df_processed.to_csv(output_file_path, sep=';', decimal='.', index=False)
        logger.info(f"DataFrame processado exportado para: {output_file_path}")

        # Teste de continuidade (apenas chamada, pois a lógica é placeholder)
        # Para testar isso, precisaríamos de um GeoDataFrame real
        # geo_processor.check_geographical_continuity(gpd.GeoDataFrame())
    else:
        logger.error("Não foi possível carregar os dados reais para teste do GeoProcessor.")
