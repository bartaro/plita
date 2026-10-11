"""Render the eight Markdown manuals as offline HTML; Python 3, stdlib only.

Run `python docs/manual/build.py` from the repository root to regenerate.
Run with --check to verify that committed HTML matches the Markdown sources.
"""
from pathlib import Path
import argparse
import html
import re

ROOT = Path(__file__).resolve().parent
LANGUAGES = [
    ('en', 'English', 'Contents', 'Skip to content', 'Read on GitHub or open the HTML files locally.'),
    ('ja', '日本語', '目次', '本文へ', 'GitHubではMarkdown版を、ローカルではHTML版を開いてください。'),
    ('ko', '한국어', '목차', '본문으로 이동', 'GitHub에서는 Markdown을, 로컬에서는 HTML 파일을 여세요.'),
    ('zh-CN', '简体中文', '目录', '跳转到正文', '在 GitHub 阅读 Markdown 版，或在本地打开 HTML 文件。'),
    ('zh-TW', '繁體中文', '目錄', '跳至正文', '在 GitHub 閱讀 Markdown 版，或在本機開啟 HTML 檔案。'),
    ('fr', 'Français', 'Sommaire', 'Aller au contenu', 'Lisez la version Markdown sur GitHub ou ouvrez les fichiers HTML localement.'),
    ('es', 'Español', 'Contenido', 'Ir al contenido', 'Lea Markdown en GitHub o abra los archivos HTML localmente.'),
    ('de', 'Deutsch', 'Inhalt', 'Zum Inhalt', 'Lesen Sie Markdown auf GitHub oder öffnen Sie die HTML-Dateien lokal.'),
]


def inline(value):
    pattern = r'`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)'
    parts = []
    cursor = 0
    for match in re.finditer(pattern, value):
        parts.append(html.escape(value[cursor:match.start()]))
        if match.group(1) is not None:
            parts.append('<code>' + html.escape(match.group(1)) + '</code>')
        else:
            href = match.group(3)
            assert not href.lower().startswith(('javascript:', 'data:')), href
            parts.append('<a href="' + html.escape(href, quote=True) + '">' + html.escape(match.group(2)) + '</a>')
        cursor = match.end()
    parts.append(html.escape(value[cursor:]))
    return ''.join(parts)


def render(markdown):
    body, headings, paragraph, code = [], [], [], None
    language = ''
    in_list = False

    def flush():
        if paragraph:
            body.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()

    for line in markdown.splitlines():
        if code is not None:
            if line == '```':
                body.append('<pre><code class="language-' + html.escape(language) + '">' + html.escape('\n'.join(code)) + '\n</code></pre>')
                code = None
            else:
                code.append(line)
            continue
        if line.startswith('```'):
            flush()
            if in_list:
                body.append('</ul>')
                in_list = False
            language, code = line[3:], []
        elif line.startswith('- '):
            flush()
            if not in_list:
                body.append('<ul>')
                in_list = True
            body.append('<li>' + inline(line[2:]) + '</li>')
        else:
            if in_list:
                body.append('</ul>')
                in_list = False
            if line.startswith('## '):
                flush()
                anchor = 'section-' + str(len(headings) + 1)
                title = line[3:]
                headings.append((anchor, title))
                body.append('<h2 id="' + anchor + '">' + inline(title) + '</h2>')
            elif line.startswith('# '):
                flush()
                body.append('<h1>' + inline(line[2:]) + '</h1>')
            elif line.strip():
                paragraph.append(line)
            else:
                flush()
    flush()
    if in_list:
        body.append('</ul>')
    assert code is None, 'Unclosed code fence'
    return '\n'.join(body), headings


def navigation(current):
    return ' '.join(
        '<a href="' + lang + '.html" lang="' + lang + '" hreflang="' + lang + '"'
        + (' aria-current="page"' if lang == current else '') + '>' + name + '</a>'
        for lang, name, *_ in LANGUAGES
    )


def page(lang, title, body, toc='', skip='Skip to content'):
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="manual.css">
</head>
<body>
<a class="skip" href="#main">{html.escape(skip)}</a>
<header><a class="brand" href="index.html">PLITA</a><span>2026-10-11 · 0.0.1</span></header>
<nav class="languages" aria-label="Language">{navigation(lang)}</nav>
<div class="layout">{toc}<main id="main">{body}
<footer>Copyright (c) 2026 DAISUKE OBA · <a href="../../LICENSE">MIT</a></footer>
</main></div>
</body>
</html>
'''


def outputs():
    cards = []
    for lang, name, contents, skip, guidance in LANGUAGES:
        source = (ROOT / (lang + '.md')).read_text(encoding='utf-8')
        # The Markdown edition has its own language selector. HTML uses the nav above.
        source = '\n'.join(line for line in source.splitlines() if not line.startswith('[English](en.md)'))
        body, headings = render(source)
        title = source.splitlines()[0][2:]
        toc = '<aside><nav aria-label="' + contents + '"><h2>' + contents + '</h2>'
        toc += ''.join('<a href="#' + anchor + '">' + inline(text) + '</a>' for anchor, text in headings)
        toc += '</nav><p><a href="' + lang + '.md">Markdown</a></p></aside>'
        yield ROOT / (lang + '.html'), page(lang, title, body, toc, skip)
        cards.append(f'<article><h2 lang="{lang}">{name}</h2><p lang="{lang}">{guidance}</p><p><a href="{lang}.html">HTML</a> · <a href="{lang}.md">Markdown</a></p></article>')
    body = '<h1>PLITA Manuals / マニュアル</h1><p>8 languages · HTML + Markdown · Offline HTML, no external assets.</p><div class="cards">' + ''.join(cards) + '</div>'
    yield ROOT / 'index.html', page('en', 'PLITA Manuals', body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    count = 0
    for path, content in outputs():
        count += 1
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(path.name)
        else:
            path.write_text(content, encoding='utf-8', newline='\n')
    if stale:
        raise SystemExit('Regenerate HTML: ' + ', '.join(stale))
    print(f'{count} HTML pages: ' + ('up to date' if args.check else 'generated'))


if __name__ == '__main__':
    main()
