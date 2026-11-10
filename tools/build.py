#!/usr/bin/env python3
"""Generate plain, portable HTML from the shared layout and authored articles."""
import html
import json
import posixpath
import re
from pathlib import Path

from content import PAGES

ROOT = Path(__file__).resolve().parents[1]
NAV = [
    ('НАЧАЛО РАБОТЫ', [1, 2, 3]),
    ('ОСНОВЫ ДВИЖКА', [4, 5, 6]),
    ('ИГРОВАЯ ЛОГИКА', [7, 8, 9]),
    ('СОЗДАНИЕ ИГРЫ', [10, 11, 12]),
    ('ПРОЕКТ', [13, 14]),
]


def relative(current, target):
    result = posixpath.relpath(target, posixpath.dirname(current) or '.')
    if result.endswith('/index.html'):
        result = result[:-10]
    return result


def scene(root):
    return f'''<div class="scene-demo" data-scene>
      <div class="scene-caption"><span><i class="live-dot"></i> СЦЕНА 01 / ROTATING CUBE</span><span>CANVAS PREVIEW</span></div>
      <canvas width="960" height="520" aria-label="Трёхмерная иллюстрация вращающегося куба">Для интерактивного просмотра нужен браузер с Canvas.</canvas>
      <div class="scene-controls"><button type="button" data-pause aria-pressed="false">Пауза</button><button type="button" data-wire aria-pressed="false">Каркас</button><label>Скорость <input type="range" data-speed min="0" max="120" value="45" aria-label="Скорость вращения, градусов в секунду"><output>45°/с</output></label></div>
      <noscript><p>Для вращения включите JavaScript. <a href="{root}assets/videos/rotation-demo.mp4">Посмотреть видео сцены</a>.</p></noscript>
    </div>'''


def cards(current, indices):
    icons = ['↗', '⌘', '◇', '⌁', '◈', '▧']
    return '<div class="cards">' + ''.join(
        f'<a class="card" href="{relative(current, PAGES[i]["path"])}"><span class="card-icon">{icons[n % len(icons)]}</span><span class="card-title">{PAGES[i]["title"]}<span aria-hidden="true">↗</span></span><p>{PAGES[i]["intro"]}</p><span class="card-link">Открыть руководство <span aria-hidden="true">→</span></span></a>'
        for n, i in enumerate(indices)
    ) + '</div>'


def homepage(current):
    return f'''<div class="hero">
      <div class="hero-text"><div class="eyebrow"><span class="live-dot"></span> UNREAL ENGINE 5 · УЧЕБНОЕ РУКОВОДСТВО</div>
      <h1>От идеи —<br>к игровому <em>миру.</em></h1>
      <p class="hero-lead">Всё, чтобы сделать первый шаг в разработке игр. От знакомства с редактором до вашей первой 2D- или 3D-сцены.</p>
      <div class="hero-actions"><a class="button primary" href="getting-started/">Начать создавать <span aria-hidden="true">↗</span></a><a class="button secondary" href="examples/">Посмотреть примеры <span aria-hidden="true">→</span></a></div>
      <div class="hero-meta"><span><b>15</b> руководств</span><span><b>2D + 3D</b> разработка</span><span><b>RU</b> на русском</span></div></div>
      <figure class="hero-art"><img src="images/world.svg" width="700" height="700" alt="Изометрический игровой остров: бирюзовые платформы, деревья и парящий куб"><figcaption><span class="live-dot"></span> ВАШ МИР НАЧИНАЕТСЯ ЗДЕСЬ <span>↗</span></figcaption><span class="art-label">WORLD_01<br><b>CREATE. PLAY. ITERATE.</b></span></figure>
    </div>
    <section class="home-section" id="explore"><div class="section-heading"><div><span class="eyebrow">ВАШ СЛЕДУЮЩИЙ ШАГ</span><h2>Исследуйте движок</h2></div><span class="section-note">Учитесь в своём темпе.</span></div>
    {cards(current, [1, 4, 8, 5, 10, 11])}</section>
    <section class="learning-path"><div><span class="eyebrow">ОТ ПЕРВОГО ЗАПУСКА ДО ПЕРВОЙ ИГРЫ</span><h2>Маленькие шаги.<br>Большие возможности.</h2><p>Последовательный маршрут для тех, кто только начинает.</p><a class="text-link" href="getting-started/">Пройти маршрут <span aria-hidden="true">→</span></a></div><ol><li><span>01</span><a href="getting-started/installation.html"><strong>Подготовьте инструменты</strong><small>Установка Unreal Engine 5</small></a></li><li><span>02</span><a href="getting-started/first-project.html"><strong>Создайте первый проект</strong><small>Шаблон, персонаж, первый запуск</small></a></li><li><span>03</span><a href="scenes/"><strong>Оживите свой мир</strong><small>Объекты, свет и игровая логика</small></a></li></ol></section>
    <div class="project-strip"><span class="strip-icon">⌘</span><div><strong>Создано, чтобы разбираться.</strong><p>Учебный проект · Лабораторная работа № 1 · Тема 8</p></div><a href="about/">О руководстве <span aria-hidden="true">↗</span></a></div>'''


SEARCH = [dict(title=p['title'], path=p['path'], group=p['group'], text=re.sub('<[^>]+>', ' ', p['intro'] + ' ' + ' '.join(s[1] for s in p['sections'])).replace('{scene}', 'интерактивное превью сцены')) for p in PAGES]

for index, page in enumerate(PAGES):
    current = page['path']
    root = '../' * (len(Path(current).parts) - 1)
    link = lambda target: relative(current, target)
    sidebar = f'<a class="nav-item {"active" if index == 0 else ""}" href="{link("index.html")}" {"aria-current=\"page\"" if index == 0 else ""}><span class="nav-symbol">◫</span>Обзор документации</a>'
    for group, indices in NAV:
        sidebar += f'<div class="nav-group"><p>{group}</p>'
        for i in indices:
            p = PAGES[i]
            active = ' class="nav-item active" aria-current="page"' if i == index else ' class="nav-item"'
            sidebar += f'<a{active} href="{link(p["path"])}">{p["short"]}</a>'
        sidebar += '</div>'
    toc = ''
    if index == 0:
        body = homepage(current)
    else:
        sections = ''
        for n, (title, content) in enumerate(page['sections'], 1):
            content = content.replace('{root}', root).replace('{scene}', scene(root))
            sections += f'<section id="section-{n}"><h2>{title}</h2>{content}</section>'
        toc = '<aside class="toc" aria-label="Содержание статьи"><p>НА ЭТОЙ СТРАНИЦЕ</p>' + ''.join(f'<a href="#section-{n}">{title}</a>' for n, (title, _) in enumerate(page['sections'], 1)) + f'<div class="toc-note"><span>УЧЕБНОЕ РУКОВОДСТВО</span><p>Практикуйтесь.<br>Экспериментируйте.<br>Создавайте.</p><a href="{link("examples/index.html")}">К примерам →</a></div></aside>'
        prev = PAGES[index - 1]
        nxt = PAGES[index + 1] if index + 1 < len(PAGES) else PAGES[0]
        body = f'''<div class="article-layout"><article><header class="article-header"><div class="eyebrow">{page['group']}</div><h1>{page['title']}</h1><p>{page['intro']}</p><div class="article-meta">UNREAL ENGINE 5 <span>·</span> {max(3, len(re.sub('<[^>]+>', ' ', sections).split()) // 130)} МИН ЧТЕНИЯ</div></header><div class="article-body">{sections}</div><nav class="page-turn" aria-label="Соседние статьи"><a href="{link(prev['path'])}"><small>← ПРЕДЫДУЩАЯ</small><strong>{prev['short']}</strong></a><a href="{link(nxt['path'])}"><small>СЛЕДУЮЩАЯ →</small><strong>{nxt['short']}</strong></a></nav><a class="back-home" href="{link('index.html')}">← Вернуться на главную</a></article>{toc}</div>'''
    document = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(page['intro'], quote=True)}">
  <meta name="theme-color" content="#152725">
  <title>{page['title']} — UE5 Field Guide</title>
  <link rel="icon" type="image/svg+xml" href="{root}images/favicon.svg">
  <link rel="stylesheet" href="{root}style.css">
  <script defer src="{root}assets/js/main.js"></script>
</head>
<body data-root="{root}">
<a class="skip-link" href="#main">Перейти к содержимому</a>
<aside class="sidebar" id="sidebar" aria-label="Навигация по документации">
  <a class="brand" href="{link('index.html')}" aria-label="UE5 Field Guide — главная"><span class="brand-mark">U<span>5</span></span><span>UE5 <b>FIELD GUIDE</b><small>СОЗДАВАЙТЕ НОВЫЕ МИРЫ</small></span></a>
  <div class="version-badge"><span class="live-dot"></span> Unreal Engine <b>5.x</b></div>
  <nav>{sidebar}</nav>
  <div class="sidebar-bottom"><span class="live-dot"></span> Идея. Прототип. Игра.<small>Неофициальное руководство</small></div>
</aside>
<div class="site-content">
  <header class="topbar"><div class="breadcrumbs"><a href="{link('index.html')}">Документация</a><span>/</span><span>{'Обзор' if index == 0 else page['short']}</span></div><div class="topbar-actions"><button type="button" class="search-open" aria-haspopup="dialog"><span aria-hidden="true">⌕</span> Поиск по руководству <kbd>/</kbd></button><a class="official-link" href="https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5-documentation">Epic Docs <span aria-hidden="true">↗</span></a><button type="button" class="menu-toggle" aria-controls="sidebar" aria-expanded="false">Меню</button></div></header>
  <main id="main" tabindex="-1" class="{'home-main' if index == 0 else 'doc-main'}">{body}</main>
  <footer><a href="{link('index.html')}">UE5 <b>FIELD GUIDE</b></a><span>Учиться. Пробовать. Создавать.</span><a href="{link('about/index.html')}">Учебный проект <span aria-hidden="true">↗</span></a></footer>
</div>
<dialog class="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Поиск по руководству</h2><button class="search-close" type="button" aria-label="Закрыть поиск">✕</button></div><label class="sr-only" for="search-input">Название или тема</label><input id="search-input" type="search" placeholder="Например, Blueprints или установка…" autocomplete="off"><p class="search-status" role="status"></p><div class="search-results"></div><div class="search-help">Esc — закрыть <span>15 руководств · поиск по содержимому</span></div></dialog>
<script type="application/json" id="search-fallback">{json.dumps(SEARCH, ensure_ascii=False).replace('</', '<\\/')}</script>
</body>
</html>
'''
    out = ROOT / current
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document, encoding='utf-8')
(ROOT / 'search-index.json').write_text(json.dumps(SEARCH, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Generated {len(PAGES)} HTML pages and search-index.json')
