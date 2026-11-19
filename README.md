# Preços de livros em catálogos brasileiros

Projeto de Inteligência Computacional: quais características estão associadas ao preço dos livros nos catálogos analisados e até que ponto é possível prever esses valores com aprendizado de máquina?

Primeira análise: **preço de capa do catálogo Senac de janeiro de 2022**. Não representa o preço atual, o valor efetivamente pago ou todo o mercado brasileiro.

## Resultados e execução

Veja [resultados calculados](relatorios/RESULTADOS.md), [auditoria de extração](relatorios/extracao.json) e [referências](REFERENCIAS.md).

Python 3.12. A partir da raiz do repositório:

```bash
python -m pip install -r requirements.txt
python scripts/analisar.py
python -m unittest discover -s tests
```

Os CSVs extraídos estão em `dados/tratados/`; não é preciso uma chave de API para esta análise. O piloto Google Books original foi preservado.

Para refazer a extração, baixe os PDFs nos links de REFERENCIAS.md e instale Poppler, deixando `pdftotext` no PATH (Windows: instale uma distribuição de Poppler e adicione a pasta bin ao PATH; Linux: pacote poppler-utils):

```bash
python scripts/extrair.py --senac caminho/senac.pdf --editora34 caminho/editora34.pdf
```

## Dados e decisões

- Senac: 924 ISBNs distintos com preço de capa; 923 registros na modelagem. A linha `9786555361599` apresenta colunas inconsistentes no documento e foi preservada para auditoria, mas excluída do modelo.
- Editora 34: 677 ISBNs distintos, todos com desconto equivalente a 20%. Preços validados, mas título e autor extraídos automaticamente permanecem sinalizados para revisão. Esta base não participa da regressão.
- Nenhum ISBN repetido entre os catálogos; todos passam no dígito verificador. Isto não prova que cada ISBN esteja corretamente atribuído ao título.
- Campos físicos nulos ou não positivos são tratados como ausentes; não alteramos o dado original. Preços não foram corrigidos pela inflação nem imputados.
- A data do catálogo Senac é obtida do nome da lista publicada; idade da edição usa essa data, não a data atual.
- Uma linha representa uma edição no catálogo. Campos: ISBN (texto), preço de capa (BRL), páginas, largura/altura/espessura (cm), peso (kg), formato, editora, autor, lançamento e rastreabilidade (página e linha original).
- Títulos podem estar truncados no PDF. Não são usados como variáveis preditoras; servem somente para agrupar títulos normalizados idênticos na separação.

## Revisão da Editora 34

A etapa de enriquecimento por ISBN e suas limitações estão em [revisão e cobertura](relatorios/ENRIQUECIMENTO_EDITORA34.md). Os dados auditáveis ficam em `dados/enriquecidos/`. Metadados não substituem os preços do catálogo nem entram automaticamente no modelo.

## Avaliação

Teste de aproximadamente 20%, separado por grupos de títulos normalizados, semente 42. Cinco folds por grupo no treino selecionam o menor MAE entre mediana, Ridge e Random Forest com parâmetros fixos. Todos os ajustes de imputação, escala e codificação acontecem dentro do pipeline em cada fold. O teste só avalia a referência e o modelo escolhido; não seleciona modelos.

MAE e RMSE estão em reais de janeiro de 2022. R² mede desempenho relativo à média do teste. Gráficos e correlações são descritivos e não estabelecem causalidade. Não há validação externa em outros catálogos. Títulos variantes podem escapar do agrupamento; falta revisão editorial de famílias de obras.

Não incluir preço com desconto ou preço por página entre as entradas: derivam do alvo. ISBN não é preditor. A base da Editora 34 não foi misturada à do Senac, pois período e editora ficariam confundidos.

## Transparência

Implementação e documentação elaboradas com auxílio de IA. Referências externas inspiram o desenho do trabalho; seus notebooks não foram copiados nem suas métricas reutilizadas. Os direitos sobre os catálogos permanecem com seus titulares; disponibilidade pública não implica licença aberta. Os PDFs não foram republicados nesta alteração.

## Histórico documentado das etapas

Versão em texto: [DOCUMENTACAO_ETAPAS.txt](DOCUMENTACAO_ETAPAS.txt).

DOCUMENTAÇÃO DAS ETAPAS DO PROJETO
Atualização: 19/11/2026

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

### TRANSPARÊNCIA
Implementação e documentação elaboradas com auxílio de IA. Dados e métricas foram verificados por execução; a revisão editorial ainda pendente é explicitada. Disponibilidade pública dos catálogos não implica licença aberta.
