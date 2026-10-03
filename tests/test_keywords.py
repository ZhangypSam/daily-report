import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from keyword_policy import validate_keywords
class KeywordsTests(unittest.TestCase):
 def test_three_chinese_and_names(self):
  self.assertEqual(validate_keywords(['llama.cpp','决策模型','预发布']),['llama.cpp','决策模型','预发布'])
 def test_empty_duplicate_wrong_counts_markup(self):
  for v in (None,[],['模型'],['模型','工具','发布','成本'],['模型','模型','发布'],['AI','ａｉ','发布'],['模型','','发布'],[' 模型','工具','发布'],['<img>','工具','发布'],['x'*17,'工具','发布']):
   with self.subTest(v=v),self.assertRaises(ValueError):validate_keywords(v)
