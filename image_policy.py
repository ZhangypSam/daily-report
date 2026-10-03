"""Offline contract for optional, explicitly reviewed original-source images."""
from datetime import datetime
import ipaddress
import re
from urllib.parse import urlsplit, parse_qsl

FIELDS = {'src', 'source_url', 'alt', 'caption', 'credit', 'license_name',
          'rights_url', 'rights_statement', 'rights_basis', 'rights_scope',
          'allowed_use', 'content_kind', 'verified_at', 'width', 'height'}


def public_url(value, *, image=False):
    if not isinstance(value, str) or not 1 <= len(value) <= 2048:
        raise ValueError('public URL required')
    if any(ord(c) <= 32 or ord(c) == 127 for c in value) or '\\' in value:
        raise ValueError('unsafe URL characters')
    url = urlsplit(value)
    host = (url.hostname or '').lower().rstrip('.')
    if url.scheme != 'https' or not host or url.username or url.password or url.fragment:
        raise ValueError('credential-free HTTPS URL required')
    if url.port not in (None, 443) or '%' in url.netloc or '%' in url.path:
        raise ValueError('unsupported URL form')
    if not host.isascii() or not re.fullmatch(r'[a-z0-9-]+(?:\.[a-z0-9-]+)+', host):
        raise ValueError('public DNS hostname required')
    if host.endswith(('.localhost', '.local', '.internal', '.home', '.test', '.invalid')) or host == 'localhost':
        raise ValueError('local hostname prohibited')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP image/source addresses prohibited')
    # Reject alternative numeric host spellings as well as dotted IP literals.
    if all(re.fullmatch(r'(?:[0-9]+|0x[0-9a-f]+)', part) for part in host.split('.')):
        raise ValueError('numeric host prohibited')
    if re.search(r'SCT[A-Za-z0-9]{15,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}', value):
        raise ValueError('secret-shaped URL prohibited')
    if image:
        if url.query or not re.search(r'\.(?:png|jpe?g|webp|avif)$', url.path, re.I):
            raise ValueError('stable query-free raster image URL required')
    elif any(key != 'id' or not val.isdigit() for key, val in parse_qsl(url.query, keep_blank_values=True)):
        raise ValueError('only public numeric id query is supported')
    return value


def validate_image(image, sources):
    if not isinstance(image, dict) or set(image) != FIELDS:
        raise ValueError('image needs complete, explicitly reviewed rights/provenance fields')
    if image['allowed_use'] != 'embed' or image['rights_scope'] != 'this_image':
        raise ValueError('permission must cover embedding this specific image')
    if image['rights_basis'] not in {'direct_permission', 'open_license', 'public_domain'}:
        raise ValueError('explicit image rights basis required; og:image is not permission')
    if image['content_kind'] != 'news_image':
        raise ValueError('only relevant source news images; no avatars or ads')
    for key in FIELDS - {'width', 'height'}:
        value = image[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 2048:
            raise ValueError('image fields must be nonempty bounded text')
        if re.search(r'SCT[A-Za-z0-9]{15,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|-----BEGIN .*PRIVATE KEY', value):
            raise ValueError('secret-shaped image field prohibited')
    if len(image['alt']) > 240 or len(image['caption']) > 600:
        raise ValueError('concise alt and caption required')
    for dimension in ('width', 'height'):
        if type(image[dimension]) is not int or not 1 <= image[dimension] <= 8192:
            raise ValueError('verified positive image dimensions required')
    if image['width'] * image['height'] > 40_000_000:
        raise ValueError('image dimensions exceed review limit')
    public_url(image['src'], image=True)
    public_url(image['source_url'])
    public_url(image['rights_url'])
    if image['source_url'] not in {s['url'] for s in sources}:
        raise ValueError('image must reference a source of this news item')
    checked = datetime.fromisoformat(image['verified_at'].replace('Z', '+00:00'))
    if checked.tzinfo is None:
        raise ValueError('rights check timestamp requires timezone')
    # This contract checks recorded evidence, not the legal validity of a grant.
    return image
