# Fontes e referências

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
