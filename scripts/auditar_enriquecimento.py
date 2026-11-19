"""Relaciona catálogo e metadados sem substituir preços ou aprovar títulos."""
from pathlib import Path
from difflib import SequenceMatcher
import unicodedata
import re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def normalizar(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def main():
    pasta=ROOT/'dados/enriquecidos'
    a=pd.read_csv(pasta/'editora34_revisao.csv',dtype={'isbn':str})
    b=pd.read_csv(pasta/'editora34_openlibrary.csv',dtype={'isbn':str})
    d=a.merge(b,on='isbn',how='left',validate='one_to_one')
    d['similaridade_titulo']=[SequenceMatcher(None,normalizar(x),normalizar(y)).ratio() if pd.notna(y) else None for x,y in zip(d.titulo_posicional,d.titulo_openlibrary)]
    d['paginas_validas']=d.paginas_openlibrary.gt(0)&d.paginas_openlibrary.mod(1).eq(0)&d.isbn_confirmado.eq(True)
    # Sinalização para triagem, não aprovação editorial automática.
    d['prioridade_revisao']=d.titulo_diverge|d.autor_diverge|(d.encontrado.eq(True)&d.similaridade_titulo.lt(.8))
    d.to_csv(pasta/'editora34_auditoria.csv',index=False)
    print({'prioridade_revisao':int(d.prioridade_revisao.sum()),'paginas_validas':int(d.paginas_validas.sum()),'titulo_similar_e_paginas':int((d.paginas_validas&d.similaridade_titulo.ge(.8)).sum())})
if __name__=='__main__':main()
