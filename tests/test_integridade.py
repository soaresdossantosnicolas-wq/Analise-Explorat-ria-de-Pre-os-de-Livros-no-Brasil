"""Verificações que protegem a extração e a independência da avaliação."""
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class Integridade(unittest.TestCase):
    def test_catalogos(self):
        for nome,n in [('senac',924),('editora34',677)]:
            d=pd.read_csv(ROOT/f'dados/tratados/{nome}.csv',dtype={'isbn':str})
            self.assertEqual(len(d),n);self.assertTrue(d.isbn.is_unique)
            self.assertTrue(d.isbn_valido.all());self.assertTrue((d.preco_capa>0).all())
    def test_desconto(self):
        d=pd.read_csv(ROOT/'dados/tratados/editora34.csv')
        self.assertTrue(((d.preco_evento-d.preco_capa*.8).abs()<.011).all())
    def test_grupos_independentes(self):
        d=pd.read_csv(ROOT/'relatorios/particoes.csv')
        self.assertFalse(set(d.loc[d.particao=='treino','grupo'])&set(d.loc[d.particao=='teste','grupo']))
        self.assertEqual(len(d),923)
    def test_previsoes(self):
        d=pd.read_csv(ROOT/'relatorios/previsoes_teste.csv');s=pd.read_csv(ROOT/'relatorios/particoes.csv')
        self.assertEqual(set(d.isbn),set(s.loc[s.particao=='teste','isbn']))
        self.assertFalse(d.isna().any().any())
if __name__=='__main__':unittest.main()
