import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from enriquecer_editora34 import para13
class ISBN(unittest.TestCase):
 def test_equivalencia(self):self.assertEqual(para13('8573260092'),'9788573260090')
 def test_invalido(self):self.assertEqual(para13('8573260093'),'')
 def test_x(self):self.assertEqual(para13('080442957X'),'9780804429573')

class Preservacao(unittest.TestCase):
 def test_precos_e_isbns_preservados(self):
  import pandas as pd
  root=Path(__file__).resolve().parents[1]
  a=pd.read_csv(root/'dados/tratados/editora34.csv',dtype={'isbn':str}).set_index('isbn')
  b=pd.read_csv(root/'dados/enriquecidos/editora34_auditoria.csv',dtype={'isbn':str}).set_index('isbn')
  self.assertTrue(b.index.is_unique)
  self.assertEqual(set(a.index),set(b.index))
  pd.testing.assert_frame_equal(a[['preco_capa','preco_evento']].sort_index(),b[['preco_capa','preco_evento']].sort_index())
 def test_paginas_exigem_isbn(self):
  import pandas as pd
  d=pd.read_csv(Path(__file__).resolve().parents[1]/'dados/enriquecidos/editora34_auditoria.csv')
  self.assertTrue(d.loc[d.paginas_validas,'isbn_confirmado'].all())
  self.assertTrue(d.loc[~d.isbn_confirmado,'paginas_openlibrary'].isna().all())

if __name__=='__main__':unittest.main()
