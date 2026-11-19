# Revisão e enriquecimento — Editora 34

## Objetivo e procedimento

Verificar a extração do catálogo ANPOCS 2025 e buscar páginas, título, autoria e editora por ISBN na Open Library. Os preços continuam sendo os do PDF; a Open Library não é fonte de preços nesta etapa.

A reextração por coordenadas preservou os 677 ISBNs e seus preços, identificando divergências em 28 títulos e 30 autores em relação à extração inicial. Os textos por posição são **candidatos para conferência**, não substituições aprovadas: títulos extensos invadem a coluna de autores, e o recorte pode cortar palavras. A flag `revisar_metadados` permanece verdadeira.

As consultas foram realizadas em lotes de 20 ISBNs. Respostas completas, URL e horário UTC estão em `dados/enriquecidos/openlibrary/`. O script reutiliza esses arquivos para reprodução sem novas chamadas; remova-os apenas se desejar uma nova consulta. Não exige chave de API.

O identificador devolvido precisa conter o ISBN-13 consultado ou ISBN-10 válido equivalente. Só então o número de páginas pode ser aproveitado. A auditoria ainda verifica se páginas é um inteiro positivo. Correspondência de ISBN não equivale a revisão bibliográfica humana: registros colaborativos podem conter erros.

## Arquivos

- `editora34_revisao.csv`: dados originais e candidatos extraídos por posição.
- `editora34_openlibrary.csv`: metadados retornados, identidade confirmada e rastreabilidade.
- `editora34_auditoria.csv`: junção um a um, com preços preservados e flags.
- `resumo.json`: cobertura das consultas.

Todos estão em `dados/enriquecidos/`. A similaridade de títulos usa SequenceMatcher sobre letras sem acentos, números e espaços; 0,8 é apenas limiar de triagem, não uma probabilidade de acerto. Prioridade de revisão reúne divergências de extração e títulos retornados com similaridade abaixo desse limiar. Ausências não são imputadas.

## Reproduzir

```bash
python -m pip install -r requirements.txt
python scripts/revisar_editora34.py caminho/editora34.pdf
python scripts/enriquecer_editora34.py
python scripts/auditar_enriquecimento.py
python -m unittest discover -s tests
```

Uma interrupção de rede gera saída parcial; confira `concluido` no resumo e execute novamente para continuar a partir do cache. `--limite` permite um piloto menor; `concluido` refere-se ao conjunto solicitado pelo limite.

## Limites para modelagem

Nenhuma regressão foi treinada nesta etapa. A Editora 34 permanece separada do Senac: os catálogos têm editoras, datas e composições diferentes. Antes de modelar, conferir as divergências no PDF, avaliar cobertura e viés dos metadados ausentes e escolher atributos com qualidade suficiente. Não usar desconto, preço do evento ou preço por página para prever preço de capa: derivam do alvo.

Fonte da API: https://openlibrary.org/dev/docs/api/books . Fonte dos preços: catálogo da Editora 34 em REFERENCIAS.md.

## Cobertura observada — coleta de 19/11/2026

- ISBNs consultados: 677 (coleta completa).
- Registros encontrados e com ISBN confirmado: 235 (34,7%).
- Registros com páginas retornadas e válidas: 158 (23,3%).
- Sem registro retornado: 442 (65,3%).
- Com registro, mas sem páginas: 77.
- Prioridade de revisão: 66.
- Com páginas válidas e similaridade de título ≥ 0,8: 145.

A baixa cobertura impede tratar esse subconjunto como representativo de todo o catálogo sem investigar o viés de disponibilidade. O próximo passo recomendado é a conferência dos casos prioritários e a comparação entre registros com e sem páginas, antes de decidir uma regressão específica para a Editora 34.
