import pandas as pd
import numpy as np
from sklearn.cluster import KMeans # Exemplo de algoritmo de clustering
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

class ClusteringModel:
    """
    Implementa o algoritmo de otimização para alocação de aviários, aplicando as premissas e restrições.
    """

    def __init__(self, target_aviaries_min: int = 40, target_aviaries_max: int = 43, current_extensionists: list = None, desired_avg_aviaries_per_extensionist: int = None):
        """
        Inicializa o modelo de clustering com a meta operacional de aviários por extensionista.

        Args:
            target_aviaries_min (int): Número mínimo de aviários por extensionista.
            target_aviaries_max (int): Número máximo de aviários por extensionista.
            current_extensionists (list, optional): Lista de nomes dos extensionistas atuais.
            desired_avg_aviaries_per_extensionist (int, optional): Média desejada de aviários por extensionista, se fornecida pelo usuário.
        """
        self.target_aviaries_min = target_aviaries_min
        self.target_aviaries_max = target_aviaries_max
        self.current_extensionists = sorted(current_extensionists) if current_extensionists is not None else []
        self.desired_avg_aviaries_per_extensionist = desired_avg_aviaries_per_extensionist
        logger.info(f"ClusteringModel inicializado com meta de aviários por extensionista: {target_aviaries_min}-{target_aviaries_max}. Desejado: {desired_avg_aviaries_per_extensionist}.")

    def _calculate_num_extensionists(self, total_aviaries: int) -> int:
        """
        Calcula o número ideal de extensionistas com base na meta operacional ou na média desejada.
        """
        if self.desired_avg_aviaries_per_extensionist is not None and self.desired_avg_aviaries_per_extensionist > 0:
            num_ext = int(np.ceil(total_aviaries / self.desired_avg_aviaries_per_extensionist))
            logger.info(f"Calculado número ideal de extensionistas: {num_ext} para {total_aviaries} aviários, usando média desejada de {self.desired_avg_aviaries_per_extensionist}.")
        else:
            if self.target_aviaries_max <= 0:
                logger.error("target_aviaries_max deve ser maior que zero para calcular o número de extensionistas.")
                return 1 # Fallback
            num_ext = int(np.ceil(total_aviaries / ((self.target_aviaries_min + self.target_aviaries_max) / 2)))
            logger.info(f"Calculado número ideal de extensionistas: {num_ext} para {total_aviaries} aviários, usando meta min/max.")
        return num_ext

    def optimize_allocation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implementa o algoritmo de otimização para alocação de aviários.

        Args:
            df (pd.DataFrame): DataFrame contendo os dados dos aviários, incluindo 'Coordenadas',
                               'ID_Nucleo', 'Microrregiao', 'Área' e 'immutable_allocation'.

        Returns:
            pd.DataFrame: DataFrame com uma nova coluna 'Extensionista_Proposto'.
        """
        if df.empty:
            logger.warning("DataFrame vazio fornecido para otimização. Retornando DataFrame vazio.")
            return df

        df_result = df.copy()

        # 0. Aplicar imutabilidade (se já não foi aplicada pelo GeoProcessor)
        # Assumimos que a coluna 'immutable_allocation' já existe e foi tratada pelo GeoProcessor

        # Extrair coordenadas para clustering
        if 'Coordenadas' not in df_result.columns:
            logger.error("Coluna 'Coordenadas' não encontrada para clustering.")
            df_result['Extensionista_Proposto'] = None
            return df_result

        # Converter coordenadas para formato numérico
        coords = df_result['Coordenadas'].str.split(',', expand=True).astype(float).values

        # 1. Calcular número de extensionistas necessários
        total_aviaries = len(df_result)
        num_extensionists = self._calculate_num_extensionists(total_aviaries)

        # 2. Aplicar algoritmo de clustering (KMeans como exemplo)
        # TODO: A escolha do algoritmo e a integração das restrições (continuidade, núcleos) é complexa.
        # KMeans é um placeholder e não garante continuidade ou integralidade de núcleos diretamente.
        if num_extensionists > 0 and len(coords) >= num_extensionists:
            kmeans = KMeans(n_clusters=num_extensionists, random_state=42, n_init=10) # n_init para evitar warnings
            df_result['cluster'] = kmeans.fit_predict(coords)
            logger.info(f"Clustering inicial com {num_extensionists} clusters realizado.")
        else:
            logger.warning(f"Não foi possível realizar clustering. num_extensionists={num_extensionists}, len(coords)={len(coords)}.")
            df_result['cluster'] = -1 # Indicar que não houve clustering

        # 3. Garantir a integralidade dos núcleos (Restrição 4)
        # Se um núcleo for dividido entre clusters, reatribuir todos os aviários do núcleo ao cluster majoritário.
        if 'ID_Nucleo' in df_result.columns:
            for nucleo_id in df_result['ID_Nucleo'].unique():
                nucleo_aviaries = df_result[df_result['ID_Nucleo'] == nucleo_id]
                if not nucleo_aviaries.empty:
                    # Encontra o cluster mais comum para este núcleo
                    most_common_cluster = nucleo_aviaries['cluster'].mode()[0]
                    df_result.loc[df_result['ID_Nucleo'] == nucleo_id, 'cluster'] = most_common_cluster
            logger.info("Integralidade dos núcleos garantida.")

        # 4. Priorizar o fechamento de microrregiões (Restrição 5)
        # Similar à integralidade dos núcleos, mas para microrregiões. Pode ser mais complexo.
        if 'Microrregiao' in df_result.columns:
            for microrregiao_id in df_result['Microrregiao'].unique():
                if microrregiao_id == 'PENDENTE': # Ignorar PENDENTE conforme premissa
                    continue
                microrregiao_aviaries = df_result[df_result['Microrregiao'] == microrregiao_id]
                if not microrregiao_aviaries.empty:
                    most_common_cluster = microrregiao_aviaries['cluster'].mode()[0]
                    df_result.loc[df_result['Microrregiao'] == microrregiao_id, 'cluster'] = most_common_cluster
            logger.info("Priorização de fechamento de microrregiões aplicada.")

        # 5. Balanceamento da carga de demanda (Restrição 6 - baixa prioridade)
        # Isso pode ser feito ajustando os clusters após a atribuição inicial ou como parte do objetivo do clustering.
        # Por enquanto, é um placeholder.
        logger.warning("Balanceamento da carga de demanda (Restrição 6) ainda não implementado.")

        # 1. Calcular número de extensionistas necessários (target)
        total_aviaries = len(df_result)
        target_num_extensionists = self._calculate_num_extensionists(total_aviaries)

        # 2. Ajustar n_clusters iterativamente para tentar atingir a meta de aviários por extensionista
        current_n_clusters = target_num_extensionists
        best_df_result = df_result.copy()
        best_avg_aviaries_per_ext = 0
        best_n_clusters = current_n_clusters

        # Limites para n_clusters
        min_clusters = max(1, len(self.current_extensionists)) # Pelo menos o número de extensionistas atuais
        max_clusters = total_aviaries // self.target_aviaries_min + 5 # Um pouco acima do máximo teórico

        # Loop de ajuste
        for iteration in range(20): # Limitar iterações para evitar loops infinitos
            if current_n_clusters <= 0 or current_n_clusters > total_aviaries:
                logger.warning(f"Número de clusters inválido: {current_n_clusters}. Ajustando para {max(1, min(total_aviaries, current_n_clusters))}.")
                current_n_clusters = max(1, min(total_aviaries, current_n_clusters))

            if len(coords) < current_n_clusters:
                logger.warning(f"Não há aviários suficientes ({len(coords)}) para {current_n_clusters} clusters. Reduzindo clusters para {len(coords)}.")
                current_n_clusters = len(coords)
                if current_n_clusters == 0: # Evitar KMeans com 0 clusters
                    break

            kmeans = KMeans(n_clusters=current_n_clusters, random_state=42, n_init=10) # n_init para evitar warnings
            df_temp = df_result.copy()
            df_temp['cluster'] = kmeans.fit_predict(coords)

            avg_aviaries_per_ext = total_aviaries / current_n_clusters
            logger.info(f"Iteração {iteration}: n_clusters={current_n_clusters}, Avg Aviaries={avg_aviaries_per_ext:.2f}")

            # Verificar se a média está dentro do range desejado
            if self.target_aviaries_min <= avg_aviaries_per_ext <= self.target_aviaries_max:
                best_df_result = df_temp
                best_n_clusters = current_n_clusters
                logger.info(f"Meta de aviários por extensionista atingida com {current_n_clusters} clusters.")
                break

            # Ajustar n_clusters para a próxima iteração
            if avg_aviaries_per_ext < self.target_aviaries_min:
                current_n_clusters = min(max_clusters, current_n_clusters + 1) # Aumentar clusters
            else: # avg_aviaries_per_ext > self.target_aviaries_max
                current_n_clusters = max(min_clusters, current_n_clusters - 1) # Diminuir clusters

            # Se não houver mudança no número de clusters, sair para evitar loop infinito
            if current_n_clusters == best_n_clusters and iteration > 0:
                logger.warning("Não foi possível atingir a meta de aviários por extensionista dentro das iterações. Usando o melhor resultado encontrado.")
                break
            best_n_clusters = current_n_clusters # Atualizar para a próxima comparação

        df_result = best_df_result
        logger.info(f"Clustering final com {best_n_clusters} clusters realizado. Média de aviários por extensionista: {total_aviaries / best_n_clusters:.2f}")

        # 3. Garantir a integralidade dos núcleos (Restrição 4)
        # Se um núcleo for dividido entre clusters, reatribuir todos os aviários do núcleo ao cluster majoritário.
        if 'ID_Nucleo' in df_result.columns:
            for nucleo_id in df_result['ID_Nucleo'].unique():
                nucleo_aviaries = df_result[df_result['ID_Nucleo'] == nucleo_id]
                if not nucleo_aviaries.empty:
                    # Encontra o cluster mais comum para este núcleo
                    # Excluir -1 (não clusterizado) se houver
                    valid_clusters = nucleo_aviaries[nucleo_aviaries['cluster'] != -1]['cluster']
                    if not valid_clusters.empty:
                        most_common_cluster = valid_clusters.mode()[0]
                        df_result.loc[df_result['ID_Nucleo'] == nucleo_id, 'cluster'] = most_common_cluster
                    else:
                        logger.warning(f"Núcleo {nucleo_id} não possui aviários clusterizados. Mantendo cluster original ou -1.")
            logger.info("Integralidade dos núcleos garantida.")

        # 4. Priorizar o fechamento de microrregiões (Restrição 5)
        # Similar à integralidade dos núcleos, mas para microrregiões. Pode ser mais complexo.
        if 'Microrregiao' in df_result.columns:
            for microrregiao_id in df_result['Microrregiao'].unique():
                if microrregiao_id == 'PENDENTE': # Ignorar PENDENTE conforme premissa
                    continue
                microrregiao_aviaries = df_result[df_result['Microrregiao'] == microrregiao_id]
                if not microrregiao_aviaries.empty:
                    # Excluir -1 (não clusterizado) se houver
                    valid_clusters = microrregiao_aviaries[microrregiao_aviaries['cluster'] != -1]['cluster']
                    if not valid_clusters.empty:
                        most_common_cluster = valid_clusters.mode()[0]
                        df_result.loc[df_result['Microrregiao'] == microrregiao_id, 'cluster'] = most_common_cluster
                    else:
                        logger.warning(f"Microrregião {microrregiao_id} não possui aviários clusterizados. Mantendo cluster original ou -1.")
            logger.info("Priorização de fechamento de microrregiões aplicada.")

        # 5. Balanceamento da carga de demanda (Restrição 6 - baixa prioridade)
        # Esta restrição não é ativamente balanceada além da meta de aviários por extensionista.
        logger.info("Balanceamento da carga de demanda (Restrição 6) não é ativamente balanceado além da meta de aviários por extensionista.")

        # Mapear clusters para nomes de extensionistas
        final_extensionist_mapping = {}
        assigned_current_extensionists = set()

        # Tentar mapear clusters para extensionistas atuais
        if self.current_extensionists:
            # Para cada cluster, encontrar o extensionista atual mais frequente
            for cluster_id in df_result['cluster'].unique():
                cluster_df = df_result[df_result['cluster'] == cluster_id]
                if not cluster_df.empty:
                    # Excluir aviários imutáveis para não influenciar a decisão de mapeamento do cluster
                    mappable_aviaries = cluster_df[~cluster_df['immutable_allocation']]
                    if not mappable_aviaries.empty:
                        most_common_ext = mappable_aviaries['Extensionista_Atual'].mode()[0]
                        # Se o extensionista mais comum ainda não foi atribuído a um cluster
                        if most_common_ext in self.current_extensionists and most_common_ext not in assigned_current_extensionists:
                            final_extensionist_mapping[cluster_id] = most_common_ext
                            assigned_current_extensionists.add(most_common_ext)
                            logger.info(f"Cluster {cluster_id} mapeado para extensionista atual: {most_common_ext}")

        # Preencher os clusters restantes e lidar com excesso/déficit de extensionistas
        remaining_clusters = sorted([c for c in df_result['cluster'].unique() if c not in final_extensionist_mapping])
        available_current_extensionists = sorted([ext for ext in self.current_extensionists if ext not in assigned_current_extensionists])

        # Se houver mais clusters do que extensionistas atuais disponíveis, criar novas regiões
        new_region_counter = 0
        for cluster_id in remaining_clusters:
            if available_current_extensionists:
                # Atribuir clusters restantes a extensionistas atuais não atribuídos
                ext_to_assign = available_current_extensionists.pop(0)
                final_extensionist_mapping[cluster_id] = ext_to_assign
                logger.info(f"Cluster {cluster_id} mapeado para extensionista atual restante: {ext_to_assign}")
            else:
                # Criar novas regiões para clusters sem extensionista atual
                new_region_name = f"Região {chr(65 + new_region_counter)}"
                final_extensionist_mapping[cluster_id] = new_region_name
                new_region_counter += 1
                logger.info(f"Cluster {cluster_id} mapeado para nova região: {new_region_name}")

        # Atribuir nomes aos novos extensionistas propostos
        df_result['Extensionista_Proposto'] = df_result['cluster'].map(final_extensionist_mapping)

        # Manter alocação imutável
        df_result.loc[df_result['immutable_allocation'] == True, 'Extensionista_Proposto'] = \
            df_result.loc[df_result['immutable_allocation'] == True, 'Extensionista_Atual']
        logger.info("Alocação finalizada com 'Extensionista_Proposto'.")

        return df_result.drop(columns=['cluster'])


if __name__ == "__main__":
    logger.info("Testando a classe ClusteringModel com dados reais...")
    try:
        from .data_loader import load_exportation_data
        from .geo_processor import GeoProcessor
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
        from src.utils.data_loader import load_exportation_data
        from src.utils.geo_processor import GeoProcessor

    df_real = load_exportation_data()

    if df_real is not None:
        # Aplicar pré-processamento do GeoProcessor
        immutability_rules = [
            {'column': 'Extensionista_Atual', 'type': 'in_list'},
            {'column': 'Nome_Produtor', 'type': 'in_list'}
        ]
        geo_processor = GeoProcessor(immutability_rules=immutability_rules, immutable_producers_file='PRODUTORES_IMUTAVEIS.csv', immutable_extensionists_file='EXTENSIONISTAS_IMUTAVEIS.csv')
        df_processed = geo_processor.apply_immutability_rules(df_real.copy())

        # Inicializa o ClusteringModel com valores de exemplo para min/max aviários
        clustering_model = ClusteringModel(target_aviaries_min=40, target_aviaries_max=43)

        # Otimiza a alocação
        df_optimized = clustering_model.optimize_allocation(df_processed.copy())

        logger.info("DataFrame após otimização (primeiras 5 linhas):")
        # Exportar o DataFrame otimizado para um arquivo CSV na pasta /exports
        exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'exports'))
        os.makedirs(exports_dir, exist_ok=True)
        output_file_path = os.path.join(exports_dir, 'clustering_model_output.csv')
        df_optimized.to_csv(output_file_path, sep=';', decimal='.', index=False)
        logger.info(f"DataFrame otimizado exportado para: {output_file_path}")
    else:
        logger.error("Não foi possível carregar os dados reais para teste do ClusteringModel.")
