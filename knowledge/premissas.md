DEMANDA FORMAL DE PROJETO: MODELAGEM DE OTIMIZAÇÃO E REDISTRIBUIÇÃO GEOGRÁFICA DE EXTENSIONISTAS (AVICULTURA)
-------------------------------------------------------------------------------------------------------------

Esse arquivo estará salvo na pasta /knowledge para a documentação do projeto.

| **Origem da Demanda**     | **Jackson**                              | **Data**                                    | **20/10/2025**                 |
|:------------------------- |:---------------------------------------- |:------------------------------------------- |:------------------------------ |
| **Prioridade**            | Média/Alta                               | **Setor Solicitante**                       | Gerência de Campo (Avicultura) |
| **Destinatário Proposto** | TI / Análise de Dados / Geoprocessamento | **Brunão:** Analista de Negócios / Key User |                                |

### 1. Objetivo da Análise

Solicitar a criação de um **modelo de alocação otimizada** para a força de trabalho de extensionistas da avicultura. O objetivo principal é **redesenhar as zonas geográficas (microrregiões)** para atingir uma **carga de trabalho ideal** por técnico (de 50-55 para **40-43 aviários**/extensionista), visando **preparar a estrutura para a expansão** da equipe com o mínimo de disrupção.

### 2. Situação Atual e Meta Operacional

| **Métrica**                 | **Situação Atual**                                                                          | **Meta Operacional**                 |
|:--------------------------- |:------------------------------------------------------------------------------------------- |:------------------------------------ |
| **Total de Aviários**       | $\approx 1115$ unidades                                                                     | Manter a base.                       |
| **Carga Média por Técnico** | $50 - 55$ aviários/extensionista                                                            | **$40 - 43$ aviários/extensionista** |
| **Ação Esperada**           | Redistribuição pontual e Criação de **Novas Regiões Geográficas** (vagas para contratação). |                                      |

Dar a opção para o usuário no streamlit colocar a quantidade de aviários meta por um slide da sidebar. Para proporcionar ao modelo calcular a nova área, para reduzir ou aumentar a quantidade de extensionistas.

### 3. Premissas e Restrições Mandatórias do Modelo

O modelo de otimização geográfica e a nova divisão de regiões devem aderir estritamente às seguintes premissas e restrições:

0. **Manter a Meta Operacional:** Cada extensionista deverá atender uma quantidade de aviários definidos por uma meta (nesta POC em especifico deveremos setar em 40-43, mas eu gostaria de deixar um slider para que eu possa aproveitar o código em ocasiões futuras em um aumento de aviários)
1. **Restrição Geográfica de Continuidade (CRÍTICA):** A criação das novas regiões deve ser feita **priorizando a continuidade geográfica** das áreas atuais dos extensionistas. O objetivo é evitar a **descaracterização** das regiões de trabalho existentes para que a nova alocação não gere a necessidade de **realocação de município** dos colaboradores.
2. **Imutabilidade de Alocação (Restrição de Negócio):** O raio de atuação do extensionista **Evandro Scheffer**, incluindo todas as **Granjas Paulo Hoffmann** sob sua responsabilidade atual, **deve ser mantido intacto**. A lista de produtores específicos para imutabilidade é definida externamente em um arquivo CSV (`PRODUTORES_IMUTAVEIS.csv`) na pasta `/assets`. Similarmente, a lista de extensionistas com alocação imutável é definida em (`EXTENSIONISTAS_IMUTAVEIS.csv`). Para os demais extensionistas deve seguir a tendência de se manterem na mesma região, sem precisar providenciar deslocamentos de municípios. Buscar abrir novas regiões na intersecção de regiões para novos extensionistas.
3. **Escopo Geográfico:** A área de análise está delimitada pelos extremos operacionais atuais: **Iporã - Toledo** e **Terra Roxa - Assis Chateaubriand**. São os limites geográficos da integração, mas não devem limitar o escopo do projeto.
4. **Integralidade de Núcleo:** Os núcleos devem ser atendidos por somente um extensionista, não permitindo que haja divisões entre dois ou mais extensionistas.
5. **Priorização por fechar Microrregiões:** Dar preferências para que um extensionista possa atender uma microrregião integralmente, mas não é mandatório. Desconsiderar o valor `PENDENTE`
6. **Balanceamento da Carga de Demanda:** Tentar Balancear o somatório de área dos aviários atendidos, a fim de evitar vieses e balancear carga de trabalho entre os extensionistas, baixa prioridade.

### 4. Requisitos de Dados (Input para a Modelagem)

Para a execução da modelagem, é essencial o fornecimento da base completa dos aviários em formato **CSV**, contendo as seguintes colunas obrigatórias:

| **Coluna**                   | **Descrição**                             				 | **Observação (Uso na Análise)**                                             |
|:---------------------------- |:------------------------------------------------------- |:----------------------------------------------------------------------------  |
| `ID_Aviario`                 | Código Único (Chave), aviários estão contidos em núcleos| **Aplicação da Restrição 0.**                                                |
| `ID_Nucleo`                  | Código Único (Chave), núcleos contém aviários			 | **Aplicação da Restrição 4.**                                               |
| `Nome Proprietario`          | Nome do Resposável do Núcleo              				 |                                                                             |
| `Nome_Produtor`              | Nome do Produtor.                         				 |                                                                             |
| **`Extensionista_Atual`**    | Nome do Técnico responsável hoje.         				 | **Aplicação das Restrições 1 e 2.**                                         |
| **`Coordenadas`**			   | Coordenadas Geográficas (Graus Decimais). 				 | **FUNDAMENTAL** para cálculo de Proximidade, *Clustering* e Rota Otimizada. |
| `Município`				   | Localização Administrativa e Física.      				 | Suporte à validação logística.                                              |
| `Microrregiao`               | Código da Localização / Microrregião     				 | **Aplicação da Restrição 5.**                                               |
| `Área`                       | Área em metros Quadrados do aviários      				 | **Aplicação da Premissa 6.**                                                |

O arquivo estará em formato `.csv` na pasta `/assets`.
Ao importar o streamlit deverá trazer a quantidade de aviários, núcleos únicos, municípios únicos, extensionistas únicos.
Criação de um botão para calcular a nova aloacação com um outro mapa separado abaixo para ficar explicito o antes e o depois. Nomear novas regiões criadas com (Região A, Região B, Região C), quando for diminuir Regiões retire o último extensionista da lista em ordem alfabética.

### 5. Entregáveis do Projeto (Output)

O projeto de otimização deve resultar nos seguintes entregáveis para a gestão:

1. **Dataset de Nova Alocação:** Uma tabela (CSV) contendo a base completa dos aviários com uma nova coluna (`Extensionista_Proposto`), refletindo a alocação otimizada. Exportado pelo Streamlit.
2. **Relatório Técnico e Proposta de Vagas:** Documento detalhando a metodologia de otimização utilizada e o número exato de novas vagas/regiões a serem criadas para atingir a meta de $40 - 43$ aviários/técnico.
3. **Mapa Interativo de Visualização (CRÍTICO):** Criação de um **novo mapa interativo** que permita a visualização da **Proposta de Novas Regiões** (coloração por técnico *Proposto*), sobrepondo-se à **Situação Atual** (pontos dos aviários e fronteiras atuais).
4. **Streamlit interativo** para demonstrar o antes e o depois da geração do cálculo (com mapa e tabelas). Sendo mandatório a exportação em KML para a visualização pela gestão no Google Earth Pro, com os polígonos da nova área de atendimento e os pins com os núcleos atendidos com a relação de informação dos aviários.

**Ferramentas Recomendadas:** **Geopandas / Folium** (para criação do mapa), **Streamlit** (para hosting da visualização). **Google Earth Pro** (exportação dos dados para os gestores)**


