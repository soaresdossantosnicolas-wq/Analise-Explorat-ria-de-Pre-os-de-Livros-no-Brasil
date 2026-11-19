"""Análise exploratória e avaliação por grupos de títulos, sem ajustar no teste."""
import json, re, unicodedata
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'relatorios';OUT.mkdir(exist_ok=True)
def grupo(t):
    t=unicodedata.normalize('NFKD',str(t)).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',t).strip()
def tabela_md(df):
    rows=['| '+' | '.join(df.columns)+' |','| '+' | '.join(['---']*len(df.columns))+' |']
    for row in df.itertuples(index=False,name=None):
        rows.append('| '+' | '.join(f'{v:.2f}' if isinstance(v,(float,np.floating)) else str(v) for v in row)+' |')
    return '\n'.join(rows)
def main():
    df=pd.read_csv(ROOT/'dados/tratados/senac.csv',dtype={'isbn':str})
    # Linha com colunas deslocadas fica preservada no bruto, fora da modelagem.
    d=df.loc[~df.revisar_metadados].copy()
    nums=['paginas','largura_cm','altura_cm','espessura_cm','peso_kg','idade_anos']
    cats=['formato','editora']
    d['idade_anos']=(pd.Timestamp('2022-01-07')-pd.to_datetime(d.lancamento,format='%d/%m/%Y',errors='coerce')).dt.days/365.25
    for k in nums:
        d.loc[d[k]<0 if k=='idade_anos' else d[k]<=0,k]=np.nan
    d['grupo']=d.titulo.map(grupo)
    d.to_csv(ROOT/'dados/tratados/senac_modelagem.csv',index=False)
    X=d[nums+cats];y=d.preco_capa;groups=d.grupo
    tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(X,y,groups))
    assert not set(groups.iloc[tr])&set(groups.iloc[te])
    preprocess=ColumnTransformer([
        ('numericas',Pipeline([('imputar',SimpleImputer(strategy='median',add_indicator=True)),('escala',StandardScaler())]),nums),
        ('categoricas',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cats)])
    models={'Mediana':DummyRegressor(strategy='median'),'Ridge':Ridge(alpha=10),'Random Forest':RandomForestRegressor(n_estimators=250,min_samples_leaf=3,max_features=.8,random_state=42,n_jobs=1)}
    fitted={};scores=[]
    for nome,est in models.items():
        from sklearn.base import clone
        pipe=Pipeline([('preparar',clone(preprocess)),('modelo',est)])
        cv=-cross_val_score(pipe,X.iloc[tr],y.iloc[tr],groups=groups.iloc[tr],cv=GroupKFold(5),scoring='neg_mean_absolute_error')
        scores.append({'modelo':nome,'mae_cv':cv.mean(),'desvio_cv':cv.std()})
        fitted[nome]=pipe
    tabela=pd.DataFrame(scores).sort_values('mae_cv');escolhido=tabela.iloc[0].modelo
    # Teste reservado apenas para o escolhido e a referência; não escolher pelo teste.
    resultados=[]
    for nome in dict.fromkeys(['Mediana',escolhido]):
        pipe=fitted[nome].fit(X.iloc[tr],y.iloc[tr]);pred=pipe.predict(X.iloc[te])
        resultados.append({'modelo':nome,'mae':mean_absolute_error(y.iloc[te],pred),'rmse':float(np.sqrt(mean_squared_error(y.iloc[te],pred))),'r2':r2_score(y.iloc[te],pred)})
        if nome==escolhido:pred_final=pred
    tabela.to_csv(OUT/'validacao_cruzada.csv',index=False)
    pd.DataFrame(resultados).to_csv(OUT/'teste_reservado.csv',index=False)
    split=d[['isbn','titulo','grupo']].copy();split['particao']='treino';split.iloc[te,split.columns.get_loc('particao')]='teste';split.to_csv(OUT/'particoes.csv',index=False)
    pd.DataFrame({'isbn':d.isbn.iloc[te].values,'observado':y.iloc[te].values,'previsto':pred_final}).to_csv(OUT/'previsoes_teste.csv',index=False)
    d[nums+['preco_capa']].describe().to_csv(OUT/'estatisticas.csv')
    d[nums+['preco_capa']].corr(method='spearman').to_csv(OUT/'correlacoes_spearman.csv')
    fig,ax=plt.subplots(1,3,figsize=(15,4))
    ax[0].hist(d.preco_capa,bins=30,color='#237f91');ax[0].set(xlabel='Preço de capa (R$)',ylabel='Livros',title='Distribuição — Senac 2022')
    ax[1].scatter(d.paginas,d.preco_capa,alpha=.35,s=12);ax[1].set(xlabel='Páginas',ylabel='Preço de capa (R$)',title='Associação, não causalidade')
    ax[2].scatter(y.iloc[te],pred_final,s=15,alpha=.6);lim=[0,max(y.iloc[te].max(),max(pred_final))];ax[2].plot(lim,lim,'k--');ax[2].set(xlabel='Observado (R$)',ylabel='Previsto (R$)',title=f'Teste: {escolhido}')
    fig.tight_layout();fig.savefig(OUT/'analise.png',dpi=160);plt.close(fig)
    resumo={'registros_originais':len(df),'registros_modelagem':len(d),'treino':len(tr),'n_teste':len(te),'grupos':groups.nunique(),'modelo_selecionado':escolhido,'ausencias_modelagem':d[nums+cats].isna().sum().to_dict(),'metricas_teste':resultados}
    (OUT/'resumo.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2))
    md='# Resultados — preços de capa do catálogo Senac (janeiro de 2022)\n\n'
    md+=f'Amostra: {len(d)} livros; treino: {len(tr)}; teste reservado: {len(te)}. Uma linha com colunas inconsistentes foi excluída. Seleção por MAE médio em cinco folds agrupados no treino.\n\n'
    md+='## Validação cruzada no treino\n\n'+tabela_md(tabela)+'\n\n## Teste reservado\n\n'+tabela_md(pd.DataFrame(resultados))
    md+='\n\n![Gráficos](analise.png)\n\n## Interpretação e limites\n\nO erro absoluto médio (MAE) está em reais de janeiro de 2022. O desvio entre folds não é intervalo de confiança. O teste pertence ao mesmo catálogo: não demonstra generalização para outras editoras ou épocas. Títulos normalizados idênticos permanecem na mesma partição; variantes de título e famílias de edições ainda podem escapar do agrupamento. Não houve busca de hiperparâmetros. Correlação e importância preditiva não demonstram causalidade. Zeros em medidas físicas são ausências, preenchidas somente no treino. A Editora 34 não participa do modelo, pois faltam características e o período é diferente.\n'
    (OUT/'RESULTADOS.md').write_text(md,encoding='utf-8');print(json.dumps(resumo,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
