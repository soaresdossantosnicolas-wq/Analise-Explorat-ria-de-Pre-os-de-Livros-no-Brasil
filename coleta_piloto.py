import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

chave = os.environ.get("GOOGLE_BOOKS_API_KEY")
if not chave:
    raise SystemExit("A chave não está disponível neste terminal.")

pasta = Path("dados_piloto")
pasta.mkdir(exist_ok=True)

consultas = ["literatura brasileira", "romance", "história", "ciência"]
livros = {}
coleta = datetime.now(timezone.utc).isoformat()
sucessos = 0

for numero, consulta in enumerate(consultas, start=1):
    parametros = urllib.parse.urlencode({
        "q": consulta,
        "country": "BR",
        "langRestrict": "pt",
        "printType": "books",
        "maxResults": 40,
    })
    requisicao = urllib.request.Request(
        "https://www.googleapis.com/books/v1/volumes?" + parametros,
        headers={"X-Goog-Api-Key": chave},
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=40) as resposta:
            dados = json.load(resposta)
    except urllib.error.HTTPError as erro:
        print(f"Coleta interrompida: HTTP {erro.code}.")
        print("Confira a ativação da API, as restrições e a cota do projeto.")
        break
    except urllib.error.URLError:
        print("Coleta interrompida por falha de conexão.")
        break

    sucessos += 1
    (pasta / f"resposta_{numero}.json").write_text(
        json.dumps(
            {"consulta": consulta, "coletado_em": coleta, "resposta": dados},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    for item in dados.get("items", []):
        identificador = item.get("id")
        if not identificador or identificador in livros:
            continue

        info = item.get("volumeInfo", {})
        venda = item.get("saleInfo", {})
        preco = venda.get("retailPrice", {})
        tabela = venda.get("listPrice", {})
        isbn = {
            x["type"]: x["identifier"]
            for x in info.get("industryIdentifiers", [])
        }

        livros[identificador] = {
            "google_id": identificador,
            "titulo": info.get("title"),
            "autores": " | ".join(info.get("authors", [])),
            "editora": info.get("publisher"),
            "publicacao": info.get("publishedDate"),
            "paginas": info.get("pageCount"),
            "categorias": " | ".join(info.get("categories", [])),
            "idioma": info.get("language"),
            "isbn13": isbn.get("ISBN_13"),
            "pais_venda": venda.get("country"),
            "situacao_venda": venda.get("saleability"),
            "ebook": venda.get("isEbook"),
            "preco_venda": preco.get("amount"),
            "moeda": preco.get("currencyCode"),
            "preco_tabela": tabela.get("amount"),
            "moeda_tabela": tabela.get("currencyCode"),
            "consulta_origem": consulta,
            "coletado_em_utc": coleta,
        }

    print(f"{consulta}: {len(dados.get('items', []))} registros retornados.")

if not livros:
    raise SystemExit("Nenhum livro coletado. Nenhum CSV foi gerado.")

registros = list(livros.values())
with (pasta / "livros_piloto.csv").open(
    "w", newline="", encoding="utf-8-sig"
) as arquivo:
    escritor = csv.DictWriter(
        arquivo, fieldnames=registros[0].keys(), delimiter=";"
    )
    escritor.writeheader()
    escritor.writerows(registros)

com_preco = [
    livro for livro in registros
    if livro["pais_venda"] == "BR"
    and livro["moeda"] == "BRL"
    and isinstance(livro["preco_venda"], (int, float))
    and livro["preco_venda"] > 0
]

print(f"\nConsultas concluídas: {sucessos}/{len(consultas)}")
print(f"Livros únicos por Google ID: {len(registros)}")
print(f"Com preço de venda positivo em reais: {len(com_preco)}")
print(f"Cobertura de preços: {len(com_preco) / len(registros):.1%}")
print(f"Arquivos salvos em: {pasta.resolve()}")