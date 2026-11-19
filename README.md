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
