# Remodelação e Otimização Geográfica de Extensionistas (Avicultura)

## 1. Objetivo da Análise

Este projeto visa criar um **modelo de alocação otimizada** para a força de trabalho de extensionistas da avicultura. O objetivo principal é **redesenhar as zonas geográficas (microrregiões)** para atingir uma **carga de trabalho ideal** por técnico (de 50-55 para **40-43 aviários**/extensionista), preparando a estrutura para a expansão da equipe com o mínimo de disrupção.

## 2. Situação Atual e Meta Operacional

| Métrica                 | Situação Atual                               | Meta Operacional                 |
|:------------------------|:---------------------------------------------|:---------------------------------|
| Total de Aviários       | $\approx 1115$ unidades                     | Manter a base.                   |
| Carga Média por Técnico | $50 - 55$ aviários/extensionista             | **$40 - 43$ aviários/extensionista** |
| Ação Esperada           | Redistribuição e Criação de Novas Regiões    |                                  |

Será implementada uma funcionalidade no Streamlit para que o usuário possa ajustar a quantidade meta de aviários por extensionista, permitindo ao modelo recalcular as áreas e a quantidade de extensionistas necessários.

## 3. Premissas e Restrições Mandatórias do Modelo

O modelo de otimização geográfica e a nova divisão de regiões devem aderir estritamente às seguintes premissas e restrições:

*   **Manter a Meta Operacional:** Cada extensionista deverá atender uma quantidade de aviários definida por uma meta (inicialmente 40-43, com slider para ajuste).
*   **Restrição Geográfica de Continuidade (CRÍTICA):** Priorizar a continuidade geográfica das áreas atuais para evitar a descaracterização das regiões de trabalho e a necessidade de realocação de município dos colaboradores.
*   **Imutabilidade de Alocação (Restrição de Negócio):** O raio de atuação do extensionista **Evandro Scheffer**, incluindo todas as **Granjas Paulo Hoffmann**, deve ser mantido intacto. A lista de produtores específicos para esta e outras restrições de imutabilidade é definida externamente em um arquivo CSV (`PRODUTORES_IMUTAVEIS.csv`) na pasta `/assets`. Similarmente, a lista de extensionistas com alocação imutável é definida em (`EXTENSIONISTAS_IMUTAVEIS.csv`). Para os demais, a tendência é manter-se na mesma região, buscando abrir novas regiões na intersecção de regiões para novos extensionistas.
*   **Escopo Geográfico:** A área de análise está delimitada pelos extremos operacionais atuais: **Iporã - Toledo** e **Terra Roxa - Assis Chateaubriand**.
*   **Integralidade de Núcleo:** Os núcleos devem ser atendidos por somente um extensionista, sem divisões.
*   **Priorização por fechar Microrregiões:** Preferência para que um extensionista atenda uma microrregião integralmente, mas não é mandatório. Desconsiderar o valor `PENDENTE`.
*   **Balanceamento da Carga de Demanda:** Tentar balancear o somatório de área dos aviários atendidos (baixa prioridade).

## 4. Requisitos de Dados (Input para a Modelagem)

É essencial o fornecimento da base completa dos aviários em formato **CSV** (localizado em `/assets`), contendo as seguintes colunas obrigatórias:

| Coluna                   | Descrição                                   | Observação (Uso na Análise)                                             |
|:-------------------------|:--------------------------------------------|:------------------------------------------------------------------------|
| `ID_Aviario`             | Código Único (Chave), aviários em núcleos   | Aplicação da Restrição 0.                                               |
| `ID_Nucleo`              | Código Único (Chave), núcleos contêm aviários | Aplicação da Restrição 4.                                               |
| `Nome Proprietario`      | Nome do Responsável do Núcleo               |                                                                         |
| `Nome_Produtor`          | Nome do Produtor.                           |                                                                         |
| `Extensionista_Atual`    | Nome do Técnico responsável hoje.           | Aplicação das Restrições 1 e 2.                                         |
| `Coordenadas`            | Coordenadas Geográficas (Graus Decimais).   | FUNDAMENTAL para cálculo de Proximidade, Clustering e Rota Otimizada.   |
| `Município`              | Localização Administrativa e Física.        | Suporte à validação logística.                                          |
| `Microrregiao`           | Código da Localização / Microrregião        | Aplicação da Restrição 5.                                               |
| `Área`                   | Área em metros Quadrados do aviários        | Aplicação da Premissa 6.                                                |

Ao importar no Streamlit, deverá exibir a quantidade de aviários, núcleos únicos, municípios únicos e extensionistas únicos. Um botão para calcular a nova alocação com um mapa separado para visualização do "antes e depois". Novas regiões serão nomeadas (Região A, Região B, etc.), e a remoção de regiões seguirá a ordem alfabética inversa dos extensionistas.

## 5. Entregáveis do Projeto (Output)

1.  **Dataset de Nova Alocação:** Tabela (CSV) com a base completa dos aviários e uma nova coluna (`Extensionista_Proposto`), exportável pelo Streamlit.
2.  **Relatório Técnico e Proposta de Vagas:** Documento detalhando a metodologia de otimização e o número exato de novas vagas/regiões.
3.  **Mapa Interativo de Visualização (CRÍTICO):** Novo mapa interativo mostrando a **Proposta de Novas Regiões** (coloração por técnico *Proposto*) sobreposta à **Situação Atual** (pontos dos aviários e fronteiras atuais).
4.  **Streamlit Interativo:** Demonstração do antes e depois do cálculo (com mapa e tabelas), com exportação obrigatória em KML para visualização no Google Earth Pro (polígonos das novas áreas e pins com informações dos aviários).

## 6. Premissas Operacionais de Codificação (P.O.C.)

Para formalizar a estrutura e arquitetura de código:

*   **P.O.C. 1: Código Orientado a Objetos (OOP):** Modelagem, pré-processamento de dados e geração de outputs (mapas, KML) devem ser encapsulados em classes Python (`ClusteringModel`, `GeoProcessor`, `KmlExporter`). Garante modularidade, reuso e facilita testes unitários.
*   **P.O.C. 2: Implementação de Logging:** Criação de um módulo de _logging_ (`logger.py`) em `/src/utils/logger.py` para registrar eventos importantes. Substitui `print()` por uma solução auditável e rastreável.
*   **P.O.C. 3: Testes e Docstrings:** Utilização de _docstrings_ (padrão Google ou NumPy) em todas as classes e métodos críticos para suportar a geração automática da documentação via Sphinx. Essencial para o Relatório Técnico e qualidade do código.
*   **P.O.C. 4: Exportação para Troubleshooting:** DataFrames resultantes de etapas críticas devem ser exportados para a pasta `/exports` em formato CSV, sobrescrevendo arquivos existentes. Facilita o troubleshooting e a validação intermediária dos dados.

## 7. Ferramentas Recomendadas

*   **Geopandas / Folium:** Para criação do mapa.
*   **Streamlit:** Para hosting da visualização.
*   **Google Earth Pro:** Para exportação dos dados para os gestores (KML).