# Fila de Desenvolvimento - Remodelação e Otimização Geográfica de Extensionistas (Avicultura)

Este documento descreve a fila de desenvolvimento proposta para o projeto, organizada por fases e prioridades, com base nos requisitos e premissas estabelecidos.

## Fase 1: Configuração e Carregamento Inicial de Dados

*   **Configuração do Ambiente:**
    *   Criar `requirements.txt` com todas as dependências do projeto.
    *   Estruturar o projeto com as pastas `src`, `assets`, `docs`, `plots`, `knowledge`, `tests`.
*   **Utilitário de Carregamento de Dados:**
    *   Desenvolver função/módulo para ler o arquivo `exportation.csv` da pasta `/assets`.
    *   Validar a estrutura e as colunas obrigatórias do dataset.

## Fase 2: Lógica Central - Pré-processamento e Modelagem

*   **Classe `GeoProcessor`:**
    *   Implementar funcionalidades para manipulação de coordenadas geográficas.
    *   Desenvolver lógica para garantir a continuidade geográfica (Restrição 1).
    *   Tratar a imutabilidade de alocação do extensionista Evandro Scheffer (Restrição 2).
    *   Definir os limites geográficos de Iporã-Toledo e Terra Roxa-Assis Chateaubriand (Restrição 3).
*   **Classe `ClusteringModel`:**
    *   Implementar o algoritmo de otimização para alocação de aviários.
    *   Aplicar a meta operacional de aviários por extensionista (Premissa 0).
    *   Garantir a integralidade dos núcleos (Restrição 4).
    *   Priorizar o fechamento de microrregiões (Restrição 5).
    *   Implementar balanceamento da carga de demanda (Restrição 6 - baixa prioridade).

## Fase 3: Saída e Visualização

*   **Classe `KmlExporter`:**
    *   Desenvolver funcionalidade para exportar os resultados da nova alocação em formato KML.
    *   Incluir polígonos das novas áreas de atendimento e pins com informações dos núcleos/aviários.
*   **Aplicação Streamlit:**
    *   Criar a interface do usuário para demonstrar o "antes e depois" da alocação.
    *   Implementar slider na sidebar para ajuste da meta de aviários por extensionista.
    *   Exibir quantidade de aviários, núcleos, municípios e extensionistas únicos.
    *   Integrar mapas interativos (Folium/Geopandas) para visualização da situação atual e proposta.
    *   Exibir tabelas com o dataset de nova alocação.
    *   Botão para calcular a nova alocação e gerar o dataset de saída.
    *   Funcionalidade de exportação do dataset de nova alocação (CSV) e KML.

## Fase 4: Testes e Logging

*   **Testes Unitários:**
    *   Escrever testes unitários para as classes `GeoProcessor`, `ClusteringModel`, `KmlExporter` e utilitários de dados.
    *   Garantir cobertura adequada para as lógicas críticas e restrições.
*   **Integração de Logging:**
    *   Integrar o módulo `logger.py` em todas as classes e funções relevantes.
    *   Registrar eventos importantes, violações de restrições e resultados finais.

## Fase 5: Documentação

*   **Docstrings:**
    *   Adicionar docstrings (padrão Google ou NumPy) a todas as classes, métodos e funções críticas.
    *   Configurar Sphinx para geração automática da documentação.
*   **Relatório Técnico:**
    *   Elaborar o relatório técnico detalhando a metodologia de otimização e a proposta de vagas (Entregável 2).
