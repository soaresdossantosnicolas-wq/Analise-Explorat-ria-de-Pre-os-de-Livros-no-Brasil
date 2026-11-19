"""Reextrai colunas pela posição no PDF, mantendo candidatos para revisão."""
import argparse,re
from pathlib import Path
import pdfplumber
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('pdf');a=p.parse_args();rows=[]
 with pdfplumber.open(a.pdf) as doc:
  for pagina,page in enumerate(doc.pages,1):
   words=page.extract_words();anchors=[w for w in words if w['x0']<150 and re.fullmatch(r'97[89]\d{10}',w['text'])]
   for w in anchors:
    # Cada registro ocupa uma linha visual; texto que invade colunas exige revisão.
    bands=[(150,380),(380,600),(600,669),(669,780)];fields=[]
    for left,right in bands:
     band=page.crop((left,max(0,w['top']-1),right,min(page.height,w['bottom']+1)))
     fields.append((band.extract_text() or '').strip())
    rows.append({'isbn':w['text'],'pagina_pdf':pagina,'titulo_posicional':fields[0],'autor_posicional':fields[1]})
 d=pd.DataFrame(rows);base=pd.read_csv(ROOT/'dados/tratados/editora34.csv',dtype={'isbn':str})
 assert d.isbn.is_unique and set(d.isbn)==set(base.isbn)
 d=base.merge(d,on=['isbn','pagina_pdf'],validate='one_to_one')
 d['titulo_diverge']=d.titulo.str.strip()!=d.titulo_posicional.str.strip();d['autor_diverge']=d.autor.fillna('').str.strip()!=d.autor_posicional.str.strip()
 d['revisar_metadados']=True
 (ROOT/'dados/enriquecidos').mkdir(parents=True,exist_ok=True)
 d.to_csv(ROOT/'dados/enriquecidos/editora34_revisao.csv',index=False)
 print({'registros':len(d),'titulos_divergentes':int(d.titulo_diverge.sum()),'autores_divergentes':int(d.autor_diverge.sum())})
if __name__=='__main__':main()
