"""Extrai catálogos com Poppler (pdftotext), preservando linhas e inconsistências."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
def numero(s): return float(s.replace(' ', '').replace('.', '').replace(',', '.'))
def isbn_valido(s): return len(s)==13 and s.isdigit() and sum(int(n)*(1 if i%2==0 else 3) for i,n in enumerate(s))%10==0

def extrair(pdf, fonte):
    text = subprocess.check_output(['pdftotext','-layout',str(pdf),'-'], text=True)
    rows=[]
    for pagina, texto in enumerate(text.split('\f'),1):
        for bloco in re.split(r'(?=\b97[89]\d{10}\b)',texto)[1:]:
            linhas=bloco.strip().splitlines(); linha=linhas[0]; isbn=linha[:13]
            row={'isbn':isbn,'fonte':fonte,'pagina_pdf':pagina,'linha_original':bloco.strip(),'isbn_valido':isbn_valido(isbn)}
            if fonte=='senac':
                m=re.match(r'\d{13}\s+(.*?)\s*R\$\s*([\d.,]+)\s+(\d+)\s+(.*)',linha)
                if not m: raise ValueError(f'Preço/páginas não identificados: {isbn}')
                titulo,preco,paginas,resto=m.groups()
                row.update(titulo=titulo,preco_capa=numero(preco),paginas=int(paginas),data_catalogo='2022-01-07')
                # Extrair a partir de marcadores explícitos; nunca inferir preços ausentes.
                tail=re.match(r'(.*?)\s+(BROCHURA|CAPA DURA|ESPIRAL|FLEX[IÍ]VEL|ENCADERNADO|CARTONADO)\s+(.*?)\s+(\d+[,.]\d+)\s+(.*?)\s+(\d{2}/\d{2}/\d{4})\s*$',resto)
                if tail:
                    medidas,formato,editora,peso,autor,data=tail.groups()
                    row.update(medidas=medidas,formato=formato,editora=editora,peso_kg=numero(peso),autor=autor,lancamento=data)
                    dims=re.fullmatch(r'\s*(\d+(?:[,.]\d+)?)\s*[xX]\s*(\d+(?:[,.]\d+)?)\s*[xX]\s*(\d+(?:[,.]\d+)?)\s*',medidas)
                    if dims:
                        for k,v in zip(['largura_cm','altura_cm','espessura_cm'],dims.groups()):row[k]=numero(v.replace('.',','))
                row['revisar_metadados']=not bool(tail)
            else:
                vals=re.findall(r'R\$\s*([\d,.]+)',bloco)
                if len(vals)!=2: raise ValueError(f'Preços ambíguos: {isbn}: {vals}')
                row.update(preco_capa=float(vals[0]),preco_evento=float(vals[1]),ano_catalogo=2025)
                prefix=bloco[13:bloco.index('R$')].strip(' -\n')
                parts=re.split(r'\s{2,}',prefix,maxsplit=1)
                row.update(titulo=parts[0],autor=parts[1] if len(parts)>1 else '',revisar_metadados=True)
                row['desconto_20_confere']=abs(row['preco_evento']-row['preco_capa']*.8)<.011
            rows.append(row)
    df=pd.DataFrame(rows)
    assert df.isbn.is_unique and df.isbn_valido.all() and (df.preco_capa>0).all()
    out=ROOT/'dados/tratados';out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/f'{fonte}.csv',index=False)
    return {'arquivo':pdf.name,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'registros':len(df),'metadados_a_revisar':int(df.revisar_metadados.sum())}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--senac',type=Path,required=True);p.add_argument('--editora34',type=Path,required=True);a=p.parse_args()
    resumo=[extrair(a.senac,'senac'),extrair(a.editora34,'editora34')]
    (ROOT/'relatorios').mkdir(exist_ok=True)
    (ROOT/'relatorios/extracao.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2))
    print(resumo)
