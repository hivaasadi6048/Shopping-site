import bleach

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i',
    'ul', 'ol', 'li',
    'blockquote',
    'a',
    'h1', 'h2', 'h3', 'h4',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
}

def sanitize_html(html):
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )