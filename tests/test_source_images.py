"""Offline image contract fixtures; no licensed news images or network traffic."""
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT)]
from image_policy import validate_image, public_url


def fixture():
    return {'src':'https://images.example.org/test-fixture.png',
            'source_url':'https://news.example.org/item', 'alt':'离线测试：自有蓝色色块',
            'caption':'自有测试图；不是新闻图片，不用于公开日报。', 'credit':'离线测试作者',
            'license_name':'自有测试授权', 'rights_url':'https://news.example.org/test-permission',
            'rights_statement':'本测试作者拥有此测试图，仅用于离线嵌入测试。',
            'rights_basis':'direct_permission','rights_scope':'this_image','allowed_use':'embed',
            'content_kind':'news_image','verified_at':'2026-10-03T09:00:00+08:00','width':320,'height':180}


class SourceImageTests(unittest.TestCase):
    def validate(self, image):
        return validate_image(image,[{'url':'https://news.example.org/item'}])

    def test_complete_fixture_and_declared_license_types(self):
        image=fixture();self.validate(image)
        for basis in ['open_license','public_domain']:
            image['rights_basis']=basis;self.validate(image)

    def test_og_image_missing_rights_and_wrong_scope_rejected(self):
        with self.assertRaises(ValueError):self.validate({'src':fixture()['src'],'alt':'og:image'})
        for field,value in [('rights_basis','og_image'),('rights_scope','whole_website'),('allowed_use','download_only'),('content_kind','avatar'),('content_kind','advertisement'),('rights_statement','')]:
            image=fixture();image[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(image)

    def test_untrusted_urls_and_signed_addresses_rejected(self):
        for url in ['http://images.example.org/a.png','javascript:alert(1)','data:image/png;base64,AA',
                    'https://127.0.0.1/a.png','https://[::1]/a.png','https://localhost/a.png',
                    'https://host.internal/a.png','https://2130706433/a.png','https://0x7f.0.0.1/a.png',
                    'https://a.example.org:8080/a.png','https://user:pass@images.example.org/a.png',
                    'https://images.example.org/a.svg','https://images.example.org/a.png?width=400',
                    'https://images.example.org/a.png?X-Amz-Signature=SECRET',
                    'https://images.example.org/%61.png','https://images.example.org/a.png#token',
                    'https://images.example.org/a.png\n']:
            image=fixture();image['src']=url
            with self.subTest(url=url),self.assertRaises(ValueError):self.validate(image)

    def test_unrelated_source_dimensions_alt_timestamp_rejected(self):
        for field,value in [('source_url','https://other.example.org/item'),('width',0),('height',True),
                            ('width',10000),('alt',''),('verified_at','2026-10-03')]:
            image=fixture();image[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate(image)

    def test_rights_and_source_links_must_not_contain_credentials(self):
        for field in ['rights_url','source_url']:
            image=fixture();image[field]='https://news.example.org/item?token=SECRET'
            with self.assertRaises(ValueError):self.validate(image)
        self.assertEqual(public_url('https://news.ycombinator.com/item?id=123'), 'https://news.ycombinator.com/item?id=123')


if __name__=='__main__':unittest.main()
