# Memória do projeto e guia de desenvolvimento

Atualizado em **19/11/2026**. Responsável pelo projeto: **Nicolas Soares dos Santos**. Documento de passagem para o estagiário, baseado no histórico de trabalho, código e resultados disponíveis. Não é uma transcrição das conversas; reúne o contexto relevante para continuar o desenvolvimento. Informações de outros projetos e credenciais foram omitidas.

## 1. Contexto, objetivo e situação atual

Projeto acadêmico de Inteligência Computacional sobre preços de livros. A pergunta inicial era: “Quais características influenciam o preço dos livros comercializados no Brasil e até que ponto é possível prever esses valores utilizando aprendizado de máquina?”.

A formulação operacional adotada é: **quais características estão associadas ao preço de capa dos livros nos catálogos analisados e até que ponto esses preços podem ser previstos por aprendizado de máquina?** A mudança delimita as conclusões ao que os dados sustentam e evita interpretar associação como causalidade.

Já existe uma primeira análise e regressão do catálogo Senac de janeiro de 2022. O catálogo Editora 34 de 2025 foi extraído e enriquecido, mas não participa do modelo. O principal trabalho pendente é conferir metadados e avaliar cobertura, não simplesmente acrescentar algoritmos.

## 2. Repositório e colaboração

- Repositório: https://github.com/soaresdossantosnicolas-wq/Analise-Explorat-ria-de-Pre-os-de-Livros-no-Brasil
- Branch principal: `main`.
- PR #1: primeira análise dos catálogos, integrado anteriormente.
- PR #2: auditoria e enriquecimento da Editora 34 e documentação das etapas; **integrado**, conforme consulta em 19/11/2026.
- PR #2: https://github.com/soaresdossantosnicolas-wq/Analise-Explorat-ria-de-Pre-os-de-Livros-no-Brasil/pull/2
- Trabalhar em uma nova branch a partir da `main` atualizada; revisar mudanças antes de integrar. Não reutilizar cegamente branches antigas já integradas.

O usuário solicita documentação de **cada etapa no README e em DOCUMENTACAO_ETAPAS.txt**. Manter também esta memória atualizada quando houver mudanças de escopo, decisões ou resultados. Usar português claro, apontar limitações e discordar de decisões tecnicamente inadequadas com justificativa e alternativa.

## 3. Linha do tempo técnica e decisões


### 1. DEFINIÇÃO DO PROBLEMA — concluída, com escopo delimitado

Pergunta: quais características estão associadas ao preço de capa dos livros nos catálogos analisados e até que ponto esses preços podem ser previstos por aprendizado de máquina?
O objetivo inicial aborda livros comercializados no Brasil. A amostra disponível permite conclusões sobre os catálogos estudados, sem representatividade nacional demonstrada. Associação não comprova causalidade.


### 2. PROSPECÇÃO DE FONTES E PILOTO — realizada

Foram considerados Google Books, Open Library, fontes de contexto e projetos de referência no GitHub/Kaggle. O piloto Google Books foi preservado; não é a base do modelo atual. Referências e fontes dos PDFs estão em REFERENCIAS.md. Resultados de projetos externos não foram reutilizados como resultados próprios. Não há integração de IBGE ou comércio exterior na regressão atual.
Decisão: usar preços de catálogos brasileiros e consultar metadados por ISBN quando necessário.


### 3. EXTRAÇÃO DOS CATÁLOGOS — concluída, com ressalvas

Script: scripts/extrair.py; saídas: dados/tratados/senac.csv e editora34.csv; auditoria: relatorios/extracao.json.
Senac (janeiro/2022): 924 registros. Editora 34 (ANPOCS/2025): 677 registros. Uma linha representa uma edição no catálogo. ISBN, página do PDF e linha original permitem rastrear a extração.
Preços positivos; ISBNs passam no dígito verificador; nenhum ISBN repetido entre catálogos. Todos os descontos da Editora 34 correspondem a 20%. Essas verificações não comprovam a associação correta entre ISBN e título.


### 4. LIMPEZA E PREPARAÇÃO DO SENAC — concluída para a primeira modelagem

A linha de ISBN 9786555361599 apresenta colunas inconsistentes; permanece na base extraída, mas foi excluída da modelagem. Restaram 923 registros.
Na base extraída: peso tem 1 ausência e 4 valores não positivos; páginas tem 1 valor não positivo; espessura tem 1 ausência e 1 valor não positivo. Largura, altura, medidas, formato, editora, autor e lançamento têm 1 ausência cada. As contagens se sobrepõem.
Valores físicos não positivos são tratados como ausentes. Imputação, escala e codificação são ajustadas dentro do treino de cada partição. Preços não foram imputados nem corrigidos pela inflação. A idade da edição é relativa ao catálogo, não à data atual.


### 5. ANÁLISE E AVALIAÇÃO PREDITIVA DO SENAC — primeira versão concluída

Script: scripts/analisar.py; resultados: relatorios/RESULTADOS.md, métricas e previsões em relatorios/.
Divisão: 738 livros no treino e 185 no teste; grupos por título normalizado, semente 42. Cinco folds agrupados no treino compararam mediana, Ridge e Random Forest com parâmetros fixos, sem busca de hiperparâmetros.
MAE médio na validação cruzada: Ridge R$ 20,02; Random Forest R$ 20,20; mediana R$ 32,46. Ridge foi selecionado pelo treino.
Teste reservado: Ridge MAE R$ 22,60, RMSE R$ 37,46 e R² 0,64; referência de mediana MAE R$ 36,22. Valores monetários referem-se a janeiro/2022. MAE é erro absoluto médio; RMSE penaliza mais os erros grandes. Precisão e F1 não são métricas deste problema de regressão.
Limites: teste do mesmo catálogo; sem validação externa. Variantes de títulos podem escapar do agrupamento. ISBN, preço com desconto e preço por página não devem ser usados como preditores do preço de capa.


### 6. REVISÃO DA EXTRAÇÃO DA EDITORA 34 — triagem concluída; conferência pendente

Script: scripts/revisar_editora34.py. Reextração pelas posições das colunas no PDF identificou divergências em 28 títulos e 30 autores. Ausências de autor: 47 na extração inicial e 29 na extração por posição.
Títulos longos invadem a coluna de autoria; recortes podem truncar palavras. Os novos textos são candidatos para revisão, não correções aprovadas. Originais e preços foram preservados; revisar_metadados permanece verdadeiro.


### 7. ENRIQUECIMENTO POR ISBN — coleta concluída em 19/11/2026

Script: scripts/enriquecer_editora34.py; fonte: Open Library, https://openlibrary.org/dev/docs/api/books .
Consulta dos 677 ISBNs em lotes de 20, com URL, horário UTC e resposta integral armazenados em dados/enriquecidos/openlibrary/. Uma falha de rede foi contornada retomando a coleta pelo cache. Não exige chave de API.
Foram encontrados 235 registros (34,7%), todos com ISBN-13 confirmado diretamente ou por equivalência com ISBN-10 válido. Houve páginas válidas para 158 livros (23,3%). Dos 677 livros, 442 não tiveram registro retornado e 77 tiveram registro sem páginas: total de 519 sem páginas.
A Open Library fornece metadados nesta etapa, não os preços. Ausências não foram inventadas ou preenchidas na base enriquecida.


### 8. AUDITORIA DO ENRIQUECIMENTO — concluída; revisão editorial pendente

Script: scripts/auditar_enriquecimento.py; saída: dados/enriquecidos/editora34_auditoria.csv; relatório: relatorios/ENRIQUECIMENTO_EDITORA34.md.
Junção um a um por ISBN, sem alterar preços. Páginas válidas exigem ISBN confirmado e inteiro positivo. Similaridade de títulos normalizados abaixo de 0,8 e divergências de extração servem para triagem, não como prova de erro.
66 registros receberam prioridade de revisão. 145 possuem páginas válidas e similaridade de título de pelo menos 0,8; isso não equivale a aprovação editorial. Nove testes passaram na implementação desta etapa, incluindo preservação de preços/ISBNs e equivalência ISBN-10/13.


### 9. LIMITAÇÕES E PENDÊNCIAS — em aberto

Conferir os 66 registros prioritários no PDF e em fontes bibliográficas; revisar famílias de obras e variantes de títulos; comparar livros com e sem metadados para investigar viés de cobertura.
A Editora 34 ainda não dispõe de peso, dimensões e acabamento estruturados na base atual. Gênero, assunto e acabamento não estão padronizados entre as fontes.
Faltam séries de preços dos mesmos livros, diversidade de editoras/lojas e preços de transações para sustentar conclusões mais amplas. Catálogos de 2022 e 2025 não constituem uma série temporal comparável.
A Editora 34 permanece fora da regressão e separada do Senac. Não foi treinado modelo novo nesta etapa. Antes disso, é necessário avaliar qualidade, cobertura e viés dos atributos disponíveis.


### 10. REPRODUÇÃO E MANUTENÇÃO

A partir da raiz, em Python 3.12:
python -m pip install -r requirements.txt
python scripts/extrair.py --senac caminho/senac.pdf --editora34 caminho/editora34.pdf
python scripts/analisar.py
python scripts/revisar_editora34.py caminho/editora34.pdf
python scripts/enriquecer_editora34.py
python scripts/auditar_enriquecimento.py
python -m unittest discover -s tests
A extração inicial exige Poppler/pdftotext no PATH. Os PDFs e suas fontes estão descritos em REFERENCIAS.md; não são republicados aqui. O cache permite reproduzir o enriquecimento sem novas consultas. Confira concluido em dados/enriquecidos/resumo.json; com --limite, esse indicador se refere apenas ao limite solicitado.
A cada nova etapa, atualizar este registro e a seção correspondente do README com objetivo, procedimento, arquivos, resultado verificado, decisão e pendências. Diferenciar etapas concluídas de propostas. Não declarar testes ou resultados que não foram executados.


### Transparência

Implementação e documentação elaboradas com auxílio de IA. Dados e métricas foram verificados por execução; a revisão editorial ainda pendente é explicitada. Disponibilidade pública dos catálogos não implica licença aberta.

## 4. Mapa do código e das saídas

| Arquivo ou pasta | Responsabilidade |
|---|---|
| `coleta_piloto.py` | Piloto Google Books; lê chave por variável de ambiente |
| `scripts/extrair.py` | Extração dos dois PDFs e validações iniciais |
| `scripts/analisar.py` | Preparação Senac, EDA, partições, comparação e avaliação de modelos |
| `scripts/revisar_editora34.py` | Candidatos de título/autoria por coordenadas no PDF |
| `scripts/enriquecer_editora34.py` | Consulta Open Library, cache e validação ISBN |
| `scripts/auditar_enriquecimento.py` | Junção de catálogo e metadados, flags para triagem |
| `dados/tratados/` | Catálogos extraídos e Senac preparado para modelagem |
| `dados/enriquecidos/` | Revisão, metadados, auditoria e resumo Editora 34 |
| `dados/enriquecidos/openlibrary/` | Respostas completas, URLs e horários das consultas |
| `relatorios/` | Resultados, métricas, partições, previsões, estatísticas e gráficos |
| `tests/test_integridade.py` | Integridade de catálogos, descontos, partições e previsões |
| `tests/test_enriquecimento.py` | ISBN-10/13, preservação de preços e requisitos das páginas |
| `REFERENCIAS.md` | Origem dos dados e projetos consultados |
| `DOCUMENTACAO_ETAPAS.txt` | Histórico textual das etapas |

### Campos e unidades

ISBN deve permanecer texto. `preco_capa` é o alvo, em BRL da data do catálogo. `preco_evento` é o preço promocional Editora 34. `paginas` conta páginas; largura, altura e espessura são centímetros; peso é quilogramas. `pagina_pdf` e `linha_original` rastreiam a origem. `revisar_metadados` indica necessidade de revisão, não uma correção concluída.

No enriquecimento, `encontrado` indica resposta para a consulta; `isbn_confirmado` verifica os identificadores devolvidos; `paginas_validas` exige inteiro positivo e ISBN confirmado. `prioridade_revisao` indica triagem, não erro comprovado. Similaridade de título não é probabilidade de identidade.

### Preditores e configuração efetivamente usados

- Numéricos: páginas, largura, altura, espessura, peso e idade da edição em anos.
- Categóricos: formato e editora. Autor, título e ISBN não são entradas do modelo atual; título serve ao agrupamento.
- Numéricos: mediana com indicador de ausência e StandardScaler dentro do pipeline.
- Categóricos: OneHotEncoder com categorias desconhecidas ignoradas.
- Ridge: `alpha=10`.
- Random Forest: 250 árvores, `min_samples_leaf=3`, `max_features=0.8`, semente 42, `n_jobs=1`.
- Referência: DummyRegressor com mediana.
- Foram obtidos 923 grupos para 923 registros. O agrupamento atual não demonstrou reunir variantes de uma mesma obra; essa revisão continua necessária.
- Após excluir a linha problemática e invalidar valores físicos: 1 ausência de páginas, 1 de espessura e 4 de peso na modelagem. Não confundir com contagens da base extraída de 924 linhas.
- O script gera previsões e relatórios, mas não exporta um modelo serializado para produção.

## 5. Piloto Google Books e acesso às APIs

O piloto consulta “literatura brasileira”, “romance”, “história” e “ciência”, com país BR, idioma pt, tipo books e até 40 resultados por consulta. Deduplica por Google ID; isso não equivale a deduplicar edições por ISBN. Salva JSONs e CSV separado por ponto e vírgula em `dados_piloto/`.

A chave é lida de `GOOGLE_BOOKS_API_KEY` no ambiente. Não colocar valores de chave em código, documentação, commit ou mensagens. O reconhecimento da variável no terminal do responsável não garante que exista no computador do estagiário. A análise dos catálogos e o enriquecimento Open Library não exigem essa chave.

O piloto distingue preço de venda e de tabela, moeda, país e indicador de ebook. Antes de reutilizar seus dados, conferir cobertura real, BRL, disponibilidade e formato: preços de ebooks e de livros físicos não devem ser misturados sem justificativa. Este documento não atribui ao piloto uma cobertura numérica que não foi revalidada nesta passagem.

## 6. Fontes e materiais de apoio

### Referências registradas

Consulta: 18/11/2026. Resultados próprios foram calculados a partir dos PDFs fornecidos; seus hashes constam em relatorios/extracao.json.

## Dados

- Senac, lista de preços de janeiro de 2022: https://www.editorasenacsp.com.br/Editora/CONTENT/base/arquivos/listapreco/lista_preco_07_01_2022_13_09_30.pdf
- Editora 34, feira virtual ANPOCS 2025: https://sinteseeventos.com/std2/images/Editora_34_-_lista_de_preos_ANPOCS_2025xlsx_-_Sheet1.pdf
- Google Books: https://developers.google.com/books/docs/v1/using — fonte do piloto original, não do modelo de catálogos.

## Projetos consultados

- Nikolas Petrou: https://github.com/nikopetr/Predict-The-Price-Of-Books — organização e comparação de regressões. Revisão estática identificou ajuste de TF-IDF/tópicos após concatenação de treino e teste; não reproduzido.
- Naveen Marthala: https://github.com/naveenmarthala/book-price-prediction — preparação e LightGBM. TF-IDF ajustado antes da separação de validação; não reproduzido.
- Kaggle: https://www.kaggle.com/code/dsxavier/not-only-the-price-of-books/notebook — referência de apresentação e modelos com TensorFlow. Código recebido e inspecionado, mas não executado.

Esses projetos não validam resultados para o mercado brasileiro. As métricas deste repositório são próprias, e sua implementação é independente.

- Open Library: https://openlibrary.org/dev/docs/api/books
- Base bruta MDIC apresentada durante a prospecção: https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta . Não integra a regressão; estatísticas de comércio exterior não fornecem automaticamente preço de varejo por edição.
- Foram enviados materiais de contexto com nomes `PeV_anobase_2024_imprensa_vff.pdf`, `PeV_anobase_2025.pdf`, `Panorama_Consumo_BR_2025-1.pdf` e `preco_livro_nardon.pdf`. Não presumir que seus dados tenham sido integrados; conferir os documentos antes de citar números.
- Os arquivos externos de projetos incluíam `Predict-The-Price-Of-Books-main.zip`, `book-price-prediction-master.zip` e `not-only-the-price-of-books.ipynb`. São referências, não componentes necessários para executar este pipeline.

## 7. Como começar no computador do estagiário

```bash
git clone https://github.com/soaresdossantosnicolas-wq/Analise-Explorat-ria-de-Pre-os-de-Livros-no-Brasil.git
cd Analise-Explorat-ria-de-Pre-os-de-Livros-no-Brasil
git switch -c revisao/metadados-editora34
python -m venv .venv
```

Ativar no PowerShell: `.venv\Scripts\Activate.ps1`. No Linux/macOS: `source .venv/bin/activate`. Usar Python 3.12 como ambiente de referência.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

As nove verificações passaram na etapa de enriquecimento; o estagiário deve executá-las em seu ambiente. Não é necessário refazer consultas ou baixar PDFs para ler as bases já versionadas. Para reextrair, obter os PDFs e instalar Poppler; os comandos completos estão no histórico acima. Executar scripts pode sobrescrever saídas: verificar `git diff` antes de commitar.

Dependências fixadas: numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, matplotlib 3.10.8 e pdfplumber 0.11.9. Não atualizar versões e metodologia ao mesmo tempo sem registrar o impacto.

## 8. Primeiras tarefas recomendadas e critérios de conclusão

1. **Reproduzir a situação atual.** Rodar testes, conferir resumos e documentar divergências de ambiente. Não apresentar uma nova execução como idêntica sem comparar as saídas.
2. **Revisar os 66 casos prioritários.** Criar tabela de decisões por ISBN com campo original, proposta, fonte/página, justificativa, responsável, data e status. Verificar também registros fora da triagem: ausência de flag não é garantia de correção. Não sobrescrever originais.
3. **Investigar viés de cobertura.** Comparar preços e demais atributos disponíveis entre livros com e sem páginas. Relatar tamanhos dos grupos e distribuições, sem declarar representatividade com base apenas em um teste estatístico.
4. **Revisar agrupamento de obras.** Identificar variantes de título/edição e evitar que a mesma família de obra fique em treino e teste. Se mudar a divisão, registrar uma nova versão do experimento e a comparabilidade das métricas.
5. **Decidir sobre Editora 34.** Modelar separadamente apenas se atributos e cobertura forem suficientes. Caso contrário, manter análise descritiva e registrar a limitação.
6. **Atualizar documentação.** README, arquivo de texto e memória devem concordar com código, dados e resultados. Não marcar tarefas planejadas como concluídas.

Cada PR deve explicar problema, mudança, validação e limitações. Alterações de documentação não exigem novo treinamento. Novos testes devem proteger integridade ou comportamento relevante.

## 9. Regras metodológicas para preservar

- Não inventar dados, métricas, resultados, fontes nem revisões humanas.
- Não escolher algoritmos ou ajustar hiperparâmetros a partir do teste reservado. Reutilizá-lo repetidamente para orientar decisões compromete sua independência; novas explorações precisam de protocolo documentado.
- Não ajustar imputação, normalização ou codificação no conjunto completo antes da validação.
- Não usar variáveis derivadas do alvo para prever o próprio alvo.
- Não transformar R² de 0,64 em “64% de precisão”. MAE e RMSE estão em reais; precisão e F1 são métricas de classificação.
- Não dizer que Random Forest venceu: Ridge teve menor MAE médio no protocolo executado. A pequena diferença não demonstra superioridade universal.
- Não interpretar regressão como identificação de causas do preço.
- Não misturar editoras e anos sem controlar e justificar a comparabilidade.
- Não apresentar preços históricos de catálogo como preços atuais ou efetivamente pagos.
- Não afirmar que todas as características foram revisadas só porque nove testes passaram.

## 10. O que ainda não foi estabelecido

Não há evidência de generalização nacional, validação externa, série temporal de preços, modelo de produção ou dashboard neste estágio do projeto. Não há resultado preditivo da Editora 34. As fontes estatísticas de contexto não foram incorporadas à regressão. A identidade dos demais integrantes, tarefas individuais e critérios formais da avaliação devem ser confirmados com o responsável; não foram inferidos de outros projetos.

Esta memória é um retrato datado. Ao retomar o desenvolvimento, conferir a `main`, os PRs e os arquivos de resultados; números podem mudar em etapas posteriores. Preservar registros anteriores e explicar as mudanças.
