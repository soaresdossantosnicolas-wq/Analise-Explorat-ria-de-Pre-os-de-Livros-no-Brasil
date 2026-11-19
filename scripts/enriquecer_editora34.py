"""Consulta metadados por ISBN em lotes; preserva respostas e não altera preços."""
import argparse,json,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from datetime import datetime,timezone
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def para13(s):
 s=s.replace('-', '').replace(' ', '')
 if len(s)!=10 or not s[:9].isdigit() or s[-1] not in '0123456789X':return ''
 if (sum(int(v)*(10-i) for i,v in enumerate(s[:9]))+(10 if s[-1]=='X' else int(s[-1])))%11:return ''
 v='978'+s[:9];return v+str((-sum(int(n)*(1 if i%2==0 else 3) for i,n in enumerate(v)))%10)
def main():
 p=argparse.ArgumentParser();p.add_argument('--limite',type=int,default=677);a=p.parse_args()
 d=pd.read_csv(ROOT/'dados/tratados/editora34.csv',dtype={'isbn':str}).head(a.limite)
 out=ROOT/'dados/enriquecidos';cache=out/'openlibrary';cache.mkdir(parents=True,exist_ok=True);rows=[]
 for i in range(0,len(d),20):
  lote=d.iloc[i:i+20];arquivo=cache/f'lote_{i:04d}_{len(lote)}.json'
  url='https://openlibrary.org/api/books?'+urllib.parse.urlencode({'bibkeys':','.join('ISBN:'+x for x in lote.isbn),'format':'json','jscmd':'data'})
  if arquivo.exists():
   pack=json.loads(arquivo.read_text(encoding="utf-8"))
   if pack['url']!=url:raise ValueError('Cache incompatível com o lote consultado')
  else:
   try:
    req=urllib.request.Request(url,headers={'User-Agent':'PesquisaAcademicaLivros/1.0'})
    with urllib.request.urlopen(req,timeout=40) as r: data=json.load(r)
    pack={'consultado_em':datetime.now(timezone.utc).isoformat(),'url':url,'resposta':data}
    arquivo.write_text(json.dumps(pack,ensure_ascii=False,indent=2),encoding="utf-8")
   except (urllib.error.URLError,TimeoutError) as e:
    print('Lote interrompido',i,type(e).__name__,flush=True);break
   time.sleep(1)
  for isbn in lote.isbn:
   b=pack['resposta'].get('ISBN:'+isbn,{})
   ids=b.get('identifiers',{});exato=isbn in ids.get('isbn_13',[])+[para13(s) for s in ids.get('isbn_10',[])]
   # Correspondência por chave consultada não basta para aceitar metadados.
   rows.append({'isbn':isbn,'encontrado':bool(b),'isbn_confirmado':exato,'titulo_openlibrary':b.get('title'),'paginas_openlibrary':b.get('number_of_pages') if exato else None,'autores_openlibrary':' | '.join(x['name'] for x in b.get('authors',[])),'editoras_openlibrary':' | '.join(x['name'] for x in b.get('publishers',[])),'publicacao_openlibrary':b.get('publish_date'),'url_openlibrary':b.get('url'),'consultado_em':pack['consultado_em']})
  print('Consultados',len(rows),flush=True)
 if rows:
  result=pd.DataFrame(rows);result.to_csv(out/'editora34_openlibrary.csv',index=False)
  summary={'consultados':len(rows),'encontrados':int(result.encontrado.sum()),'isbn_confirmados':int(result.isbn_confirmado.sum()),'com_paginas_confirmadas':int(result.paginas_openlibrary.notna().sum()),'concluido':len(rows)==len(d)}
  (out/'resumo.json').write_text(json.dumps(summary,indent=2),encoding="utf-8");print(summary)
if __name__=='__main__':main()
