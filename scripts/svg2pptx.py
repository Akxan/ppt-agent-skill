#!/usr/bin/env python3
"""SVG -> PPTX：把 dom-to-svg 产出的 SVG 逐元素翻成原生 OOXML 形状

支持:
  rect / circle / ellipse / line / polygon / polyline / path（含 A/S/Q/T 命令）
  text + tspan（字距、斜体、竖排）、image（data URI + 本地文件）
  linearGradient / radialGradient、完整仿射变换（matrix/translate/scale/rotate）
  group opacity、首个全屏矩形或图片 -> 幻灯片背景
  class 含 pptx-card 的分组 -> PowerPoint 组合（可整体移动、可做入场动画）
  页间切换（默认淡入）与卡片入场动画（默认关闭）

用法:
  python svg2pptx.py <svg_dir_or_file> -o output.pptx
      [--transition fade|push|wipe|cover|split|zoom|dissolve|none]
      [--animate none|fade|wipe|rise|zoom] [--animate-trigger click|auto]
"""

import argparse
import base64
import io
import math
import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.util import Emu

from pptx_motion import ENTRANCE_EFFECTS, TRANSITIONS, TRANSITION_SPEEDS, apply_entrance, apply_transition

# -------------------------------------------------------------------
# 常量
# -------------------------------------------------------------------
SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}
EMU_PX = 9525
SLIDE_W = 12192000
SLIDE_H = 6858000
CANVAS_W, CANVAS_H = 1280, 720
CARD_CLASS = 'pptx-card'

CSS_COLORS = {
    'aliceblue': 'f0f8ff', 'antiquewhite': 'faebd7', 'aqua': '00ffff',
    'aquamarine': '7fffd4', 'azure': 'f0ffff', 'beige': 'f5f5dc',
    'bisque': 'ffe4c4', 'black': '000000', 'blanchedalmond': 'ffebcd',
    'blue': '0000ff', 'blueviolet': '8a2be2', 'brown': 'a52a2a',
    'burlywood': 'deb887', 'cadetblue': '5f9ea0', 'chartreuse': '7fff00',
    'chocolate': 'd2691e', 'coral': 'ff7f50', 'cornflowerblue': '6495ed',
    'cornsilk': 'fff8dc', 'crimson': 'dc143c', 'cyan': '00ffff',
    'darkblue': '00008b', 'darkcyan': '008b8b', 'darkgoldenrod': 'b8860b',
    'darkgray': 'a9a9a9', 'darkgreen': '006400', 'darkgrey': 'a9a9a9',
    'darkkhaki': 'bdb76b', 'darkmagenta': '8b008b', 'darkolivegreen': '556b2f',
    'darkorange': 'ff8c00', 'darkorchid': '9932cc', 'darkred': '8b0000',
    'darksalmon': 'e9967a', 'darkseagreen': '8fbc8f', 'darkslateblue': '483d8b',
    'darkslategray': '2f4f4f', 'darkturquoise': '00ced1', 'darkviolet': '9400d3',
    'deeppink': 'ff1493', 'deepskyblue': '00bfff', 'dimgray': '696969',
    'dodgerblue': '1e90ff', 'firebrick': 'b22222', 'floralwhite': 'fffaf0',
    'forestgreen': '228b22', 'fuchsia': 'ff00ff', 'gainsboro': 'dcdcdc',
    'ghostwhite': 'f8f8ff', 'gold': 'ffd700', 'goldenrod': 'daa520',
    'gray': '808080', 'green': '008000', 'greenyellow': 'adff2f',
    'grey': '808080', 'honeydew': 'f0fff0', 'hotpink': 'ff69b4',
    'indianred': 'cd5c5c', 'indigo': '4b0082', 'ivory': 'fffff0',
    'khaki': 'f0e68c', 'lavender': 'e6e6fa', 'lawngreen': '7cfc00',
    'lemonchiffon': 'fffacd', 'lightblue': 'add8e6', 'lightcoral': 'f08080',
    'lightcyan': 'e0ffff', 'lightgoldenrodyellow': 'fafad2', 'lightgray': 'd3d3d3',
    'lightgreen': '90ee90', 'lightpink': 'ffb6c1', 'lightsalmon': 'ffa07a',
    'lightseagreen': '20b2aa', 'lightskyblue': '87cefa', 'lightslategray': '778899',
    'lightsteelblue': 'b0c4de', 'lightyellow': 'ffffe0', 'lime': '00ff00',
    'limegreen': '32cd32', 'linen': 'faf0e6', 'magenta': 'ff00ff',
    'maroon': '800000', 'mediumaquamarine': '66cdaa', 'mediumblue': '0000cd',
    'mediumorchid': 'ba55d3', 'mediumpurple': '9370db', 'mediumseagreen': '3cb371',
    'mediumslateblue': '7b68ee', 'mediumspringgreen': '00fa9a',
    'mediumturquoise': '48d1cc', 'mediumvioletred': 'c71585', 'midnightblue': '191970',
    'mintcream': 'f5fffa', 'mistyrose': 'ffe4e1', 'moccasin': 'ffe4b5',
    'navajowhite': 'ffdead', 'navy': '000080', 'oldlace': 'fdf5e6',
    'olive': '808000', 'olivedrab': '6b8e23', 'orange': 'ffa500',
    'orangered': 'ff4500', 'orchid': 'da70d6', 'palegoldenrod': 'eee8aa',
    'palegreen': '98fb98', 'paleturquoise': 'afeeee', 'palevioletred': 'db7093',
    'papayawhip': 'ffefd5', 'peachpuff': 'ffdab9', 'peru': 'cd853f',
    'pink': 'ffc0cb', 'plum': 'dda0dd', 'powderblue': 'b0e0e6',
    'purple': '800080', 'rebeccapurple': '663399', 'red': 'ff0000',
    'rosybrown': 'bc8f8f', 'royalblue': '4169e1', 'saddlebrown': '8b4513',
    'salmon': 'fa8072', 'sandybrown': 'f4a460', 'seagreen': '2e8b57',
    'seashell': 'fff5ee', 'sienna': 'a0522d', 'silver': 'c0c0c0',
    'skyblue': '87ceeb', 'slateblue': '6a5acd', 'slategray': '708090',
    'snow': 'fffafa', 'springgreen': '00ff7f', 'steelblue': '4682b4',
    'tan': 'd2b48c', 'teal': '008080', 'thistle': 'd8bfd8',
    'tomato': 'ff6347', 'turquoise': '40e0d0', 'violet': 'ee82ee',
    'wheat': 'f5deb3', 'white': 'ffffff', 'whitesmoke': 'f5f5f5',
    'yellow': 'ffff00', 'yellowgreen': '9acd32',
}

# 字体策略
#   safe（默认）：把设计字体映射到 Windows/macOS 版 Office 都自带的字体，保证衬线/无衬线/等宽/
#                 粗黑的区分与斜体不丢；收件人没装 Google Fonts 时版面仍可预期
#   design      ：保留字体栈里的第一个字体名，仅当打开 PPTX 的机器装了这些字体时才正确
SAFE_FONTS = {'Arial', 'Arial Black', 'Georgia', 'Times New Roman', 'Courier New', 'Verdana', 'Tahoma',
              'Trebuchet MS', 'Impact', 'Microsoft YaHei', 'SimSun', 'SimHei', 'KaiTi', 'FangSong'}
DESIGN_ALIASES = {'PingFang SC': 'Microsoft YaHei', 'SF Pro Display': 'Arial', 'SF Pro Text': 'Arial',
                  'Helvetica Neue': 'Arial', 'Helvetica': 'Arial'}
GENERIC_FONTS = {'sans-serif', 'serif', 'monospace', 'system-ui', '-apple-system',
                 'BlinkMacSystemFont', 'cursive', 'fantasy', 'ui-sans-serif', 'ui-serif'}
_HEAVY = re.compile(r'bagel|bowlby|black|impact|ultra', re.I)
_MONO = re.compile(r'mono|courier|consolas|menlo', re.I)
_SERIF = re.compile(r'serif|playfair|fraunces|bodoni|didot|garamond|tiempos|georgia|times|song|mincho|'
                    r'cheltenham|iowan|sangbleu|editorial', re.I)
_SANS = re.compile(r'sans|inter|helvetica|arial|grotesk|yahei|hei|pingfang|quicksand|nunito|orbitron|system', re.I)
_KAI = re.compile(r'kai|楷', re.I)
_CJK_NAME = re.compile(r'SC|TC|JP|CJK|Song|Hei|YaHei|PingFang|Hiragino|Mincho|Kaiti|Han |SimSun', re.I)


def px(v):
    return int(round(float(v) * EMU_PX))


def font_sz(svg_px):
    return max(100, int(float(svg_px) * 75))


def num(v, default=0.0):
    """'12.5px' / '50%' / 12 -> 12.5（单位直接丢弃）"""
    if v is None:
        return default
    m = re.match(r'\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)', str(v))
    return float(m.group(1)) if m else default


def natural_key(path):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', path.name)]


def _font_class(names):
    """字体栈 -> heavy / mono / serif / sans：先看首个具体字体名，再看栈尾的通用族。"""
    concrete = [n for n in names if n not in GENERIC_FONTS]
    for name in concrete[:1]:
        for kind, pattern in (('heavy', _HEAVY), ('mono', _MONO), ('serif', _SERIF), ('sans', _SANS)):
            if pattern.search(name):
                return kind
    if 'monospace' in names:
        return 'mono'
    return 'serif' if 'serif' in names and 'sans-serif' not in names else 'sans'


def resolve_fonts(ff_str, mode='safe'):
    """font-family 字体栈 -> (latin 字体, 东亚字体)"""
    names = [f.strip().strip('"\'') for f in ff_str.replace('&quot;', '').split(',') if f.strip()]
    concrete = [n for n in names if n not in GENERIC_FONTS]
    kind = _font_class(names)
    east_asian = 'KaiTi' if any(_KAI.search(n) for n in concrete[:2]) else \
        'SimSun' if kind == 'serif' else 'Microsoft YaHei'
    if mode == 'design':
        latin = DESIGN_ALIASES.get(concrete[0], concrete[0]) if concrete else 'Microsoft YaHei'
        named = next((n for n in concrete if _CJK_NAME.search(n)), None)
        return latin, DESIGN_ALIASES.get(named, named) if named else east_asian
    if concrete and concrete[0] in SAFE_FONTS:
        return concrete[0], east_asian
    return {'heavy': 'Arial Black', 'mono': 'Courier New', 'serif': 'Georgia'}.get(kind, 'Arial'), east_asian


# safe 字体的字宽与网页字体不同。用本机字体文件量出替换后的宽度，超出浏览器实测宽度时等比缩小字号，
# 避免相邻文本框互相压住。找不到字体文件时不缩放。
_FONT_DIRS = ['/System/Library/Fonts/Supplemental', '/Library/Fonts', 'C:/Windows/Fonts',
              '/usr/share/fonts/truetype/msttcorefonts', '/usr/share/fonts/truetype/liberation']
_FONT_FILES = {
    ('Arial', False, False): ['Arial.ttf', 'arial.ttf', 'LiberationSans-Regular.ttf'],
    ('Arial', True, False): ['Arial Bold.ttf', 'arialbd.ttf', 'LiberationSans-Bold.ttf'],
    ('Arial', False, True): ['Arial Italic.ttf', 'ariali.ttf', 'LiberationSans-Italic.ttf'],
    ('Arial', True, True): ['Arial Bold Italic.ttf', 'arialbi.ttf', 'LiberationSans-BoldItalic.ttf'],
    ('Arial Black', False, False): ['Arial Black.ttf', 'ariblk.ttf'],
    ('Georgia', False, False): ['Georgia.ttf', 'georgia.ttf', 'LiberationSerif-Regular.ttf'],
    ('Georgia', True, False): ['Georgia Bold.ttf', 'georgiab.ttf', 'LiberationSerif-Bold.ttf'],
    ('Georgia', False, True): ['Georgia Italic.ttf', 'georgiai.ttf', 'LiberationSerif-Italic.ttf'],
    ('Georgia', True, True): ['Georgia Bold Italic.ttf', 'georgiaz.ttf', 'LiberationSerif-BoldItalic.ttf'],
    ('Courier New', False, False): ['Courier New.ttf', 'cour.ttf', 'LiberationMono-Regular.ttf'],
    ('Courier New', True, False): ['Courier New Bold.ttf', 'courbd.ttf', 'LiberationMono-Bold.ttf'],
}
_font_cache = {}


def _metric_font(name, bold, italic):
    key = (name, bold, italic)
    if key not in _font_cache:
        font = None
        candidates = _FONT_FILES.get(key) or _FONT_FILES.get((name, bold, False)) or \
            _FONT_FILES.get((name, False, False)) or []
        try:
            from PIL import ImageFont
            for directory in _FONT_DIRS:
                for filename in candidates:
                    path = Path(directory) / filename
                    if path.exists():
                        font = ImageFont.truetype(str(path), 100)
                        break
                if font:
                    break
        except Exception:
            font = None
        _font_cache[key] = font
    return _font_cache[key]


def fit_scale(text, font_name, bold, italic, size, spacing, measured_width):
    """替换字体后需要的字号缩放系数（0.75~1.0）；无法测量时返回 1。"""
    font = _metric_font(font_name, bold, italic)
    if font is None or measured_width <= 0 or size <= 0:
        return 1.0
    latin = ''.join(ch for ch in text if ord(ch) <= 0x2E7F)
    cjk = len(text) - len(latin)
    natural = font.getlength(latin) / 100 * size + cjk * size
    available = measured_width - spacing * len(text)
    if natural <= 0 or available <= 0 or natural <= available * 1.01:
        return 1.0
    return max(0.75, available / natural)


# -------------------------------------------------------------------
# 仿射变换 (a, b, c, d, e, f)：x' = a*x + c*y + e, y' = b*x + d*y + f
# -------------------------------------------------------------------
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
_TRANSFORM_RE = re.compile(r'(matrix|translate|scale|rotate)\s*\(([^)]*)\)')


def mat_mul(m, n):
    """先应用 n 再应用 m"""
    return (m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1],
            m[0] * n[2] + m[2] * n[3], m[1] * n[2] + m[3] * n[3],
            m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5])


def mat_apply(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def mat_scale(m):
    return math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0


def mat_rotation(m):
    return math.degrees(math.atan2(m[1], m[0]))


def mat_axis_aligned(m):
    return abs(m[1]) < 1e-6 and abs(m[2]) < 1e-6


def parse_transform(text):
    m = IDENTITY
    for name, args in _TRANSFORM_RE.findall(text or ''):
        v = [float(x) for x in re.split(r'[\s,]+', args.strip()) if x]
        if name == 'matrix' and len(v) == 6:
            t = tuple(v)
        elif name == 'translate' and v:
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == 'scale' and v:
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == 'rotate' and v:
            r = math.radians(v[0])
            t = (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), 0, 0)
            if len(v) == 3:
                t = mat_mul(mat_mul((1, 0, 0, 1, v[1], v[2]), t), (1, 0, 0, 1, -v[1], -v[2]))
        else:
            continue
        m = mat_mul(m, t)
    return m


# -------------------------------------------------------------------
# 颜色
# -------------------------------------------------------------------
def parse_color(s):
    """-> (hex6, alpha 0-100000) / ('grad', id) / None"""
    if not s or s.strip() in ('none', 'transparent'):
        return None
    s = s.strip()
    if s.startswith('url('):
        m = re.search(r'#([\w-]+)', s)
        return ('grad', m.group(1)) if m else None
    m = re.match(r'rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*(?:[,/]\s*([\d.]+%?))?\s*\)', s)
    if m:
        r, g, b = (min(255, int(round(float(m.group(i))))) for i in (1, 2, 3))
        a = 1.0
        if m.group(4):
            a = float(m.group(4).rstrip('%')) / (100 if m.group(4).endswith('%') else 1)
        return (f'{r:02x}{g:02x}{b:02x}', int(a * 100000))
    if s.startswith('#'):
        h = s[1:]
        if len(h) in (3, 4):
            h = ''.join(ch * 2 for ch in h)
        alpha = int(int(h[6:8], 16) / 255 * 100000) if len(h) == 8 else 100000
        return (h.lower().ljust(6, '0')[:6], alpha)
    c = CSS_COLORS.get(s.lower())
    return (c, 100000) if c else None


# -------------------------------------------------------------------
# OOXML 元素构造
# -------------------------------------------------------------------
def _el(tag, attrib=None, text=None, children=None):
    pre, local = tag.split(':') if ':' in tag else ('a', tag)
    el = etree.Element(f'{{{NS[pre]}}}{local}')
    for k, v in (attrib or {}).items():
        el.set(k, str(v))
    if text is not None:
        el.text = str(text)
    for c in (children or []):
        if c is not None:
            el.append(c)
    return el


def _srgb(hex6, alpha=100000):
    el = _el('a:srgbClr', {'val': hex6})
    if alpha < 100000:
        el.append(_el('a:alpha', {'val': str(max(0, alpha))}))
    return el


def _make_grad(gdef, opacity=1.0):
    gs_lst = _el('a:gsLst')
    for stop in sorted(gdef['stops'], key=lambda s: s['offset']):
        sc = parse_color(stop['color_str'])
        if not sc or sc[0] == 'grad':
            continue
        alpha = int(sc[1] * stop.get('opacity', 1.0) * opacity)
        pos = int(min(100, max(0, stop['offset'])) * 1000)
        gs_lst.append(_el('a:gs', {'pos': str(pos)}, children=[_srgb(sc[0], alpha)]))
    if len(gs_lst) < 2:
        return None
    if gdef.get('type') == 'radial':
        path = _el('a:path', {'path': 'circle'}, children=[
            _el('a:fillToRect', {'l': '50000', 't': '50000', 'r': '50000', 'b': '50000'})])
        return _el('a:gradFill', {'rotWithShape': '1'}, children=[gs_lst, path])
    dx = gdef.get('x2', 1) - gdef.get('x1', 0)
    dy = gdef.get('y2', 0) - gdef.get('y1', 0)
    ang = int(math.degrees(math.atan2(dy, dx)) * 60000) % 21600000
    return _el('a:gradFill', children=[gs_lst, _el('a:lin', {'ang': str(ang), 'scaled': '0'})])


def make_fill(fill_str, grads, opacity=1.0):
    c = parse_color(fill_str)
    if c is None:
        return _el('a:noFill')
    if c[0] == 'grad':
        gdef = grads.get(c[1])
        grad = _make_grad(gdef, opacity) if gdef else None
        return grad if grad is not None else _el('a:noFill')
    return _el('a:solidFill', children=[_srgb(c[0], int(c[1] * opacity))])


def make_line(stroke_str, width_px, grads, opacity=1.0, cap=None, dash=None):
    """SVG 描边 -> a:ln；渐变描边取首个色标。无有效颜色返回 None。"""
    c = parse_color(stroke_str)
    if c and c[0] == 'grad':
        gdef = grads.get(c[1])
        c = parse_color(gdef['stops'][0]['color_str']) if gdef and gdef.get('stops') else None
        if c and c[0] == 'grad':
            c = None
    if not c or width_px <= 0:
        return None
    attrib = {'w': str(max(1, int(width_px * 12700 * 0.75)))}
    if cap == 'round':
        attrib['cap'] = 'rnd'
    elif cap == 'square':
        attrib['cap'] = 'sq'
    ln = _el('a:ln', attrib, children=[_el('a:solidFill', children=[_srgb(c[0], int(c[1] * opacity))])])
    if dash:
        ln.append(_el('a:prstDash', {'val': dash}))
    ln.append(_el('a:round'))
    return ln


def _xfrm(x, y, cx, cy, flip_h=False, flip_v=False):
    xfrm = _el('a:xfrm', children=[
        _el('a:off', {'x': str(int(x)), 'y': str(int(y))}),
        _el('a:ext', {'cx': str(max(0, int(cx))), 'cy': str(max(0, int(cy)))}),
    ])
    if flip_h:
        xfrm.set('flipH', '1')
    if flip_v:
        xfrm.set('flipV', '1')
    return xfrm


def make_shape(sid, name, x, y, cx, cy, preset='rect', fill_el=None, line_el=None,
               rx=0, geom_el=None, adjustments=None, flip_h=False, flip_v=False):
    sp = _el('p:sp')
    sp.append(_el('p:nvSpPr', children=[
        _el('p:cNvPr', {'id': str(sid), 'name': name}), _el('p:cNvSpPr'), _el('p:nvPr')]))
    sp_pr = _el('p:spPr', children=[_xfrm(x, y, cx, cy, flip_h, flip_v)])
    if geom_el is not None:
        sp_pr.append(geom_el)
    else:
        av = _el('a:avLst')
        if preset == 'roundRect' and rx > 0:
            shorter = max(min(cx, cy), 1)
            adj = min(50000, int(rx / shorter * 100000))
            av.append(_el('a:gd', {'name': 'adj', 'fmla': f'val {adj}'}))
        for name_, value in (adjustments or {}).items():
            av.append(_el('a:gd', {'name': name_, 'fmla': f'val {value}'}))
        sp_pr.append(_el('a:prstGeom', {'prst': preset}, children=[av]))
    sp_pr.append(fill_el if fill_el is not None else _el('a:noFill'))
    if line_el is not None:
        sp_pr.append(line_el)
    sp.append(sp_pr)
    return sp


def make_textbox(sid, name, x, y, cx, cy, run, align=None, vertical=False):
    """run = {text, sz, bold, italic, spc, hex, alpha, latin, ea}"""
    sp = _el('p:sp')
    sp.append(_el('p:nvSpPr', children=[
        _el('p:cNvPr', {'id': str(sid), 'name': name}), _el('p:cNvSpPr', {'txBox': '1'}), _el('p:nvPr')]))
    sp.append(_el('p:spPr', children=[
        _xfrm(x, y, cx, cy),
        _el('a:prstGeom', {'prst': 'rect'}, children=[_el('a:avLst')]),
        _el('a:noFill'), _el('a:ln', children=[_el('a:noFill')]),
    ]))
    body_attr = {'wrap': 'none', 'lIns': '0', 'tIns': '0', 'rIns': '0', 'bIns': '0', 'anchor': 't'}
    if vertical:
        body_attr['vert'] = 'eaVert'
    rpr_attr = {'lang': 'zh-CN', 'dirty': '0', 'sz': str(run['sz'])}
    if run.get('bold'):
        rpr_attr['b'] = '1'
    if run.get('italic'):
        rpr_attr['i'] = '1'
    if run.get('spc'):
        rpr_attr['spc'] = str(run['spc'])
    rpr = _el('a:rPr', rpr_attr, children=[
        _el('a:solidFill', children=[_srgb(run.get('hex', '000000'), run.get('alpha', 100000))]),
        _el('a:latin', {'typeface': run['latin']}),
        _el('a:ea', {'typeface': run['ea']}),
    ])
    paragraph = _el('a:p')
    if align:
        paragraph.append(_el('a:pPr', {'algn': align}))
    paragraph.append(_el('a:r', children=[rpr, _el('a:t', text=run['text'])]))
    sp.append(_el('p:txBody', children=[_el('a:bodyPr', body_attr), _el('a:lstStyle'), paragraph]))
    return sp


def make_group(sid, name):
    return _el('p:grpSp', children=[
        _el('p:nvGrpSpPr', children=[
            _el('p:cNvPr', {'id': str(sid), 'name': name}), _el('p:cNvGrpSpPr'), _el('p:nvPr')]),
        _el('p:grpSpPr'),
    ])


def fit_group(group):
    """按子形状包围盒设置组合的 xfrm；空组返回 False。"""
    boxes = []
    for off in group.iter(f'{{{NS["a"]}}}off'):
        ext = off.getnext()
        if ext is None or not ext.tag.endswith('}ext'):
            continue
        x, y = int(off.get('x')), int(off.get('y'))
        boxes.append((x, y, x + int(ext.get('cx')), y + int(ext.get('cy'))))
    if not boxes:
        return False
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    group.find(f'{{{NS["p"]}}}grpSpPr').append(_el('a:xfrm', children=[
        _el('a:off', {'x': str(x0), 'y': str(y0)}),
        _el('a:ext', {'cx': str(x1 - x0), 'cy': str(y1 - y0)}),
        _el('a:chOff', {'x': str(x0), 'y': str(y0)}),
        _el('a:chExt', {'cx': str(x1 - x0), 'cy': str(y1 - y0)}),
    ]))
    return True


# -------------------------------------------------------------------
# SVG path -> 绝对坐标段 [('M', [pt]), ('L', [pt]), ('C', [c1, c2, pt]), ('Z', [])]
# -------------------------------------------------------------------
_PATH_TOKEN = re.compile(r'([MmZzLlHhVvCcSsQqTtAa])|([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)')
_PATH_ARGC = {'m': 2, 'l': 2, 'h': 1, 'v': 1, 'c': 6, 's': 4, 'q': 4, 't': 2, 'a': 7}


def _arc_to_cubics(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """SVG 端点参数化椭圆弧 -> 若干三次贝塞尔 [(c1, c2, end), ...]"""
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [((x1, y1), (x2, y2), (x2, y2))]
    phi = math.radians(phi_deg % 360)
    cos_p, sin_p = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cos_p * dx + sin_p * dy, -sin_p * dx + cos_p * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    coef = math.sqrt(max(0.0, (rx ** 2 * ry ** 2 - den) / den)) if den else 0.0
    if bool(large) == bool(sweep):
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    ux, uy = (x1p - cxp) / rx, (y1p - cyp) / ry
    theta = angle(1, 0, ux, uy)
    delta = angle(ux, uy, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi

    count = max(1, math.ceil(abs(delta) / (math.pi / 2) - 1e-9))
    step = delta / count
    t = 4 / 3 * math.tan(step / 4)

    def place(ux_, uy_):
        x, y = rx * ux_, ry * uy_
        return (cos_p * x - sin_p * y + cx, sin_p * x + cos_p * y + cy)

    cubics = []
    for _ in range(count):
        c1, s1 = math.cos(theta), math.sin(theta)
        theta += step
        c2, s2 = math.cos(theta), math.sin(theta)
        cubics.append((place(c1 - t * s1, s1 + t * c1), place(c2 + t * s2, s2 - t * c2), place(c2, s2)))
    return cubics


def parse_path(d):
    items = [m.group(1) or float(m.group(2)) for m in _PATH_TOKEN.finditer(d)]
    segments = []
    cur = start = (0.0, 0.0)
    last_ctrl = None           # 上一段的控制点，供 S/T 镜像
    last_cmd = ''
    i, cmd = 0, None
    while i < len(items):
        if isinstance(items[i], str):
            cmd = items[i]
            i += 1
            if cmd in 'Zz':
                segments.append(('Z', []))
                cur, last_ctrl, last_cmd = start, None, 'z'
                continue
        if cmd is None:
            i += 1
            continue
        low, rel = cmd.lower(), cmd.islower()
        argc = _PATH_ARGC.get(low)
        if argc is None or i + argc > len(items) or any(isinstance(v, str) for v in items[i:i + argc]):
            break
        a = items[i:i + argc]
        i += argc
        ox, oy = cur if rel else (0.0, 0.0)

        if low == 'm':
            cur = start = (a[0] + ox, a[1] + oy)
            segments.append(('M', [cur]))
            cmd = 'l' if rel else 'L'              # 后续坐标对视为 lineTo
            last_ctrl = None
        elif low == 'l':
            cur = (a[0] + ox, a[1] + oy)
            segments.append(('L', [cur]))
            last_ctrl = None
        elif low == 'h':
            cur = (a[0] + ox, cur[1])
            segments.append(('L', [cur]))
            last_ctrl = None
        elif low == 'v':
            cur = (cur[0], a[0] + oy)
            segments.append(('L', [cur]))
            last_ctrl = None
        elif low in ('c', 's'):
            if low == 'c':
                c1 = (a[0] + ox, a[1] + oy)
                c2, end = (a[2] + ox, a[3] + oy), (a[4] + ox, a[5] + oy)
            else:
                c1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) \
                    if last_ctrl and last_cmd in 'cs' else cur
                c2, end = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            segments.append(('C', [c1, c2, end]))
            cur, last_ctrl = end, c2
        elif low in ('q', 't'):
            if low == 'q':
                ctrl, end = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            else:
                ctrl = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) \
                    if last_ctrl and last_cmd in 'qt' else cur
                end = (a[0] + ox, a[1] + oy)
            c1 = (cur[0] + 2 / 3 * (ctrl[0] - cur[0]), cur[1] + 2 / 3 * (ctrl[1] - cur[1]))
            c2 = (end[0] + 2 / 3 * (ctrl[0] - end[0]), end[1] + 2 / 3 * (ctrl[1] - end[1]))
            segments.append(('C', [c1, c2, end]))
            cur, last_ctrl = end, ctrl
        elif low == 'a':
            end = (a[5] + ox, a[6] + oy)
            for cubic in _arc_to_cubics(cur[0], cur[1], a[0], a[1], a[2], a[3], a[4], end[0], end[1]):
                segments.append(('C', list(cubic)))
            cur, last_ctrl = end, None
        last_cmd = low
    return segments


def segments_to_geometry(segments, matrix):
    """变换后的路径段 -> (custGeom, bbox)；无有效点返回 (None, None)"""
    moved = [(cmd, [mat_apply(matrix, *p) for p in pts]) for cmd, pts in segments]
    points = [p for _, pts in moved for p in pts]
    if len(points) < 2:
        return None, None
    x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
    x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
    width, height = max(x1 - x0, 0.01), max(y1 - y0, 0.01)

    def pt(p):
        return _el('a:pt', {'x': str(px(p[0] - x0)), 'y': str(px(p[1] - y0))})

    path = _el('a:path', {'w': str(max(1, px(width))), 'h': str(max(1, px(height)))})
    for cmd, pts in moved:
        if cmd == 'M':
            path.append(_el('a:moveTo', children=[pt(pts[0])]))
        elif cmd == 'L':
            path.append(_el('a:lnTo', children=[pt(pts[0])]))
        elif cmd == 'C':
            path.append(_el('a:cubicBezTo', children=[pt(p) for p in pts]))
        else:
            path.append(_el('a:close'))
    geom = _el('a:custGeom', children=[
        _el('a:avLst'), _el('a:gdLst'), _el('a:ahLst'), _el('a:cxnLst'),
        _el('a:rect', {'l': 'l', 't': 't', 'r': 'r', 'b': 'b'}),
        _el('a:pathLst', children=[path]),
    ])
    return geom, (x0, y0, width, height)


# -------------------------------------------------------------------
# SVG -> PPTX 转换器
# -------------------------------------------------------------------
class SvgConverter:
    SKIP_TAGS = {'defs', 'style', 'linearGradient', 'radialGradient', 'stop', 'pattern',
                 'clipPath', 'filter', 'mask', 'title', 'desc', 'metadata', 'marker', 'symbol'}

    def __init__(self, group_cards=True, fonts='safe'):
        self.group_cards = group_cards
        self.fonts = fonts
        self.sid = 100
        self.grads = {}
        self.painted = 0          # 已输出的可见元素数，用于判定"首个全屏元素 = 背景"
        self.card_ids = []        # 本页卡片组合的 shape id，按文档顺序
        self.stats = {'shapes': 0, 'skipped': 0, 'errors': 0}

    def _id(self):
        self.sid += 1
        return self.sid

    def convert(self, svg_path, slide):
        self.sid = 100
        self.painted = 0
        self.card_ids = []
        self.stats = {'shapes': 0, 'skipped': 0, 'errors': 0}
        # huge_tree：内嵌的 base64 图层单个属性可超过 libxml2 默认的 10MB 上限
        root = etree.parse(str(svg_path), etree.XMLParser(huge_tree=True)).getroot()
        self._parse_grads(root)
        sp_tree = slide.shapes._spTree
        self._walk(root, sp_tree, IDENTITY, 1.0, slide, in_card=False)

    # ---- 渐变定义 ----
    def _parse_grads(self, root):
        self.grads = {}

        def pct(v, default):
            v = v if v is not None else default
            return float(v.rstrip('%')) / 100 if '%' in str(v) else float(v)

        for kind in ('linear', 'radial'):
            for g in root.iter(f'{{{SVG_NS}}}{kind}Gradient'):
                gid = g.get('id')
                if not gid:
                    continue
                stops = []
                for s in g.findall(f'{{{SVG_NS}}}stop'):
                    off = s.get('offset', '0%')
                    stops.append({
                        'offset': float(off.rstrip('%')) if '%' in off else float(off) * 100,
                        'color_str': s.get('stop-color', '#000'),
                        'opacity': float(s.get('stop-opacity', '1')),
                    })
                gdef = {'type': kind, 'stops': stops}
                if kind == 'linear':
                    gdef.update(x1=pct(g.get('x1'), '0%'), y1=pct(g.get('y1'), '0%'),
                                x2=pct(g.get('x2'), '100%'), y2=pct(g.get('y2'), '0%'))
                self.grads[gid] = gdef

    # ---- 遍历 ----
    @staticmethod
    def _tag(el):
        return etree.QName(el).localname if isinstance(el.tag, str) else ''

    def _walk(self, el, container, matrix, opacity, slide, in_card):
        tag = self._tag(el)
        if not tag or tag in self.SKIP_TAGS:
            return
        handler = getattr(self, f'_draw_{tag}', None)
        if handler is not None:
            try:
                handler(el, container, mat_mul(matrix, parse_transform(el.get('transform'))),
                        opacity * num(el.get('opacity'), 1.0), slide)
            except Exception as exc:      # 单个元素失败不影响整页
                self.stats['errors'] += 1
                print(f"    Warning: <{tag}> failed: {exc}", file=sys.stderr)
            return

        child_matrix = mat_mul(matrix, parse_transform(el.get('transform'))) if tag == 'g' else matrix
        child_opacity = opacity * num(el.get('opacity'), 1.0) if tag == 'g' else opacity
        is_card = (self.group_cards and not in_card and tag == 'g'
                   and CARD_CLASS in (el.get('class') or '').split())
        target = container
        if is_card:
            target = make_group(self._id(), f'Card {len(self.card_ids) + 1}')
            container.append(target)
        for child in el:
            self._walk(child, target, child_matrix, child_opacity, slide, in_card or is_card)
        if is_card:
            if fit_group(target):
                self.card_ids.append(int(target.find(f'.//{{{NS["p"]}}}cNvPr').get('id')))
            else:
                container.remove(target)

    def _add(self, container, shape):
        container.append(shape)
        self.painted += 1
        self.stats['shapes'] += 1

    def _stroke(self, el, matrix, opacity):
        stroke = el.get('stroke', '')
        if not stroke or stroke == 'none':
            return None
        width = num(el.get('stroke-width'), 1.0) * mat_scale(matrix)
        dash = None
        dasharray = el.get('stroke-dasharray', '')
        if dasharray and dasharray != 'none':
            first = num(re.split(r'[\s,]+', dasharray.strip())[0], 0)
            dash = 'sysDot' if first <= num(el.get('stroke-width'), 1.0) * 2 else 'dash'
        return make_line(stroke, width, self.grads, opacity * num(el.get('stroke-opacity'), 1.0),
                         cap=el.get('stroke-linecap'), dash=dash)

    def _fill(self, el, opacity):
        return make_fill(el.get('fill', ''), self.grads, opacity * num(el.get('fill-opacity'), 1.0))

    # ---- 各元素 ----
    def _draw_rect(self, el, container, matrix, opacity, slide):
        w, h = num(el.get('width')), num(el.get('height'))
        if w <= 0 or h <= 0:
            return
        x, y = num(el.get('x')), num(el.get('y'))
        fill_s, stroke_s = el.get('fill', ''), el.get('stroke', '')
        color = parse_color(fill_s)
        if color and color[0] != 'grad' and color[1] == 0 and (not stroke_s or stroke_s == 'none'):
            return                                    # 全透明无边框：不可见

        if not mat_axis_aligned(matrix):              # 旋转/斜切的矩形按多边形处理
            corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            self._draw_segments([('M', [corners[0]])] + [('L', [c]) for c in corners[1:]] + [('Z', [])],
                                el, container, matrix, opacity, 'R')
            return

        x0, y0 = mat_apply(matrix, x, y)
        x1, y1 = mat_apply(matrix, x + w, y + h)
        x, y, w, h = min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)
        if w < 4 and h < 4:
            self.stats['skipped'] += 1                # 亚像素级装饰点
            return

        # 首个可见元素若为不透明全屏矩形 -> 幻灯片背景
        opaque = opacity >= 0.99 and color is not None and (
            self._grad_opaque(color[1]) if color[0] == 'grad' else color[1] >= 99000)
        if self.painted == 0 and opaque and w >= CANVAS_W - 10 and h >= CANVAS_H - 10:
            self._set_background(slide, make_fill(fill_s, self.grads, 1.0))
            self.painted += 1
            return

        radius = max(num(el.get('rx')), num(el.get('ry'))) * mat_scale(matrix)
        self._add(container, make_shape(
            self._id(), f'R{self.sid}', px(x), px(y), px(w), px(h),
            preset='roundRect' if radius > 0 else 'rect', rx=px(radius),
            fill_el=self._fill(el, opacity), line_el=self._stroke(el, matrix, opacity)))

    def _grad_opaque(self, grad_id):
        gdef = self.grads.get(grad_id)
        if not gdef or not gdef['stops']:
            return False
        for stop in gdef['stops']:
            color = parse_color(stop['color_str'])
            if not color or color[0] == 'grad' or color[1] * stop.get('opacity', 1.0) < 99000:
                return False
        return True

    def _set_background(self, slide, fill_el):
        c_sld = slide._element.find(f'{{{NS["p"]}}}cSld')
        for old in c_sld.findall(f'{{{NS["p"]}}}bg'):
            c_sld.remove(old)
        c_sld.insert(0, _el('p:bg', children=[_el('p:bgPr', children=[fill_el, _el('a:effectLst')])]))

    def _draw_circle(self, el, container, matrix, opacity, slide):
        self._ellipse(el, container, matrix, opacity, num(el.get('r')), num(el.get('r')))

    def _draw_ellipse(self, el, container, matrix, opacity, slide):
        self._ellipse(el, container, matrix, opacity, num(el.get('rx')), num(el.get('ry')))

    def _ellipse(self, el, container, matrix, opacity, rx, ry):
        scale = mat_scale(matrix)
        rx, ry = rx * scale, ry * scale
        if rx < 1 or ry < 1:
            self.stats['skipped'] += 1
            return
        cx, cy = mat_apply(matrix, num(el.get('cx')), num(el.get('cy')))
        box = (px(cx - rx), px(cy - ry), px(2 * rx), px(2 * ry))
        fill_s, stroke_s = el.get('fill', ''), el.get('stroke', '')
        hollow = not fill_s or fill_s == 'none'

        # 环形进度：fill=none + stroke-dasharray="弧长 间隔" -> arc 预设 + 粗描边
        dash = [num(p) for p in re.split(r'[\s,]+', el.get('stroke-dasharray', '').strip()) if p]
        # （虚线圆的 dasharray 会沿圆周重复，弧长+间隔远小于周长，不走这个分支）
        circumference = 2 * math.pi * num(el.get('r') or el.get('rx'))
        is_progress = len(dash) >= 2 and dash[0] > 0 and dash[0] + dash[1] >= circumference * 0.98
        if hollow and stroke_s and is_progress:
            sweep = min(dash[0] / circumference, 1.0) * 360
            line = make_line(stroke_s, num(el.get('stroke-width'), 1.0) * scale, self.grads, opacity,
                             cap=el.get('stroke-linecap'))
            if line is not None and sweep < 359.5:
                # SVG 圆从 3 点钟方向顺时针起笔；arc 的角度同为自 3 点钟顺时针
                start = mat_rotation(matrix) % 360
                self._add(container, make_shape(
                    self._id(), f'Arc{self.sid}', *box, preset='arc', line_el=line,
                    adjustments={'adj1': int(start * 60000),
                                 'adj2': int(((start + sweep) % 360) * 60000)}))
                return
        line = make_line(stroke_s, num(el.get('stroke-width'), 1.0) * scale, self.grads, opacity) \
            if is_progress else self._stroke(el, matrix, opacity)
        self._add(container, make_shape(
            self._id(), f'C{self.sid}', *box, preset='ellipse',
            fill_el=_el('a:noFill') if hollow else self._fill(el, opacity), line_el=line))

    def _draw_line(self, el, container, matrix, opacity, slide):
        x1, y1 = mat_apply(matrix, num(el.get('x1')), num(el.get('y1')))
        x2, y2 = mat_apply(matrix, num(el.get('x2')), num(el.get('y2')))
        line = self._stroke(el, matrix, opacity) if el.get('stroke') else \
            make_line('#000', mat_scale(matrix), self.grads, opacity)
        if line is None:
            return
        self._add(container, make_shape(
            self._id(), f'L{self.sid}', px(min(x1, x2)), px(min(y1, y2)),
            px(abs(x2 - x1)), px(abs(y2 - y1)), preset='line', line_el=line,
            flip_h=x1 > x2, flip_v=y1 > y2))

    def _draw_polygon(self, el, container, matrix, opacity, slide):
        self._poly(el, container, matrix, opacity, closed=True)

    def _draw_polyline(self, el, container, matrix, opacity, slide):
        self._poly(el, container, matrix, opacity, closed=False)

    def _poly(self, el, container, matrix, opacity, closed):
        values = [float(v) for v in re.findall(r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?', el.get('points', ''))]
        points = list(zip(values[0::2], values[1::2]))
        if len(points) < 2:
            return
        segments = [('M', [points[0]])] + [('L', [p]) for p in points[1:]]
        if closed:
            segments.append(('Z', []))
        self._draw_segments(segments, el, container, matrix, opacity, 'P')

    def _draw_path(self, el, container, matrix, opacity, slide):
        d = el.get('d', '')
        if not d or 'nan' in d.lower():
            return
        self._draw_segments(parse_path(d), el, container, matrix, opacity, 'P')

    def _draw_segments(self, segments, el, container, matrix, opacity, prefix):
        geom, bbox = segments_to_geometry(segments, matrix)
        if geom is None:
            return
        x, y, w, h = bbox
        if w < 2 and h < 2:
            self.stats['skipped'] += 1
            return
        self._add(container, make_shape(
            self._id(), f'{prefix}{self.sid}', px(x), px(y), max(1, px(w)), max(1, px(h)),
            geom_el=geom, fill_el=self._fill(el, opacity), line_el=self._stroke(el, matrix, opacity)))

    def _draw_text(self, el, container, matrix, opacity, slide):
        """每个 tspan 一个文本框，保留精确坐标。"""
        scale = mat_scale(matrix)
        base = {key: el.get(key, '') for key in
                ('fill', 'font-size', 'font-weight', 'font-style', 'font-family', 'letter-spacing')}
        base['fill'] = base['fill'] or el.get('color', '')
        after_edge = 'after-edge' in el.get('dominant-baseline', '')
        anchor = el.get('text-anchor', 'start')
        vertical = el.get('writing-mode', '').startswith('vertical')

        tspans = el.findall(f'{{{SVG_NS}}}tspan')
        pieces = [(ts, ts.text) for ts in tspans] if tspans else [(el, el.text)]
        for node, text in pieces:
            if not text or not text.strip():
                continue
            text = text.strip()
            attr = {key: node.get(key) or value for key, value in base.items()}
            size = num(attr['font-size'], 14.0) * scale
            spacing = num(attr['letter-spacing'], 0.0) * scale
            x, y = mat_apply(matrix, num(node.get('x')), num(node.get('y')))
            color = parse_color(attr['fill'])
            if color and color[0] != 'grad' and color[1] == 0:
                continue                              # 全透明文字（已烘焙进位图的元素）
            if not color or color[0] == 'grad':
                color = ('000000', 100000)
            latin, east_asian = resolve_fonts(attr['font-family'], self.fonts)
            weight = attr['font-weight']
            run = {
                'text': text, 'sz': font_sz(size),
                'bold': weight in ('bold', 'bolder') or num(weight, 400) >= 600,
                'italic': attr['font-style'] in ('italic', 'oblique'),
                'spc': int(round(spacing * 75)),
                'hex': color[0], 'alpha': int(color[1] * opacity),
                'latin': latin, 'ea': east_asian,
            }

            measured = num(node.get('textLength')) * scale
            if self.fonts == 'safe' and not vertical:
                run['sz'] = font_sz(size * fit_scale(text, latin, run['bold'], run['italic'],
                                                     size, spacing, measured))

            if vertical:
                # 竖排：x 为列左缘，y 为文字块底缘
                height = len(text) * (size + spacing)
                width = max(num(node.get('textLength')) * scale, size * 1.2)
                box = (x, y - height, width, height + size * 0.2)
                align = None
            else:
                width = measured if measured > 0 else sum(
                    size * (1.0 if ord(ch) > 0x2E7F else 0.55) + spacing for ch in text)
                top = y - size if after_edge else y - size * 0.85
                left = x - width / 2 if anchor == 'middle' else x - width if anchor == 'end' else x
                box = (left, top, width, size * 1.5)
                align = {'middle': 'ctr', 'end': 'r'}.get(anchor)
            self._add(container, make_textbox(
                self._id(), f'T{self.sid}', px(box[0]), px(box[1]), px(box[2]), px(box[3]),
                run, align=align, vertical=vertical))

    def _draw_image(self, el, container, matrix, opacity, slide):
        href = el.get(f'{{{XLINK_NS}}}href') or el.get('href', '')
        w, h = num(el.get('width')), num(el.get('height'))
        if not href or w <= 0 or h <= 0:
            return
        x0, y0 = mat_apply(matrix, num(el.get('x')), num(el.get('y')))
        x1, y1 = mat_apply(matrix, num(el.get('x')) + w, num(el.get('y')) + h)
        x, y, w, h = min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)

        source = None
        if href.startswith('data:'):
            m = re.match(r'data:image/[\w+.-]+;base64,(.*)', href, re.DOTALL)
            if m:
                source = io.BytesIO(base64.b64decode(m.group(1)))
        elif not href.startswith('http'):
            path = Path(href.replace('file://', ''))
            if path.exists():
                source = io.BytesIO(path.read_bytes())
        if source is None:
            return

        # 首个可见元素若为全屏图片 -> 幻灯片背景图
        if self.painted == 0 and opacity >= 0.99 and x <= 2 and y <= 2 \
                and w >= CANVAS_W - 10 and h >= CANVAS_H - 10:
            _, r_id = slide.part.get_or_add_image_part(source)
            blip = _el('a:blip')
            blip.set(f'{{{NS["r"]}}}embed', r_id)
            self._set_background(slide, _el('a:blipFill', {'dpi': '0', 'rotWithShape': '1'}, children=[
                blip, _el('a:stretch', children=[_el('a:fillRect')])]))
            self.painted += 1
            return

        try:
            from PIL import Image as PILImage
            img_w, img_h = PILImage.open(source).size
            source.seek(0)
        except Exception:
            img_w, img_h = w, h

        # preserveAspectRatio: none=拉伸，meet=完整显示，其余按 cover 居中裁剪
        fit = el.get('preserveAspectRatio', '')
        box_w, box_h = px(w), px(h)
        ratio, box_ratio = img_w / img_h, box_w / box_h
        crop_x = crop_y = 0.0
        left, top, pic_w, pic_h = px(x), px(y), box_w, box_h
        if fit != 'none' and abs(ratio - box_ratio) > 0.01:
            if 'meet' in fit:
                if ratio > box_ratio:
                    pic_h = int(box_w / ratio)
                    top += (box_h - pic_h) // 2
                else:
                    pic_w = int(box_h * ratio)
                    left += (box_w - pic_w) // 2
            elif ratio > box_ratio:
                crop_x = (1 - box_ratio / ratio) / 2
            else:
                crop_y = (1 - ratio / box_ratio) / 2

        pic = slide.shapes.add_picture(source, Emu(left), Emu(top), Emu(pic_w), Emu(pic_h))
        pic.crop_left = pic.crop_right = crop_x
        pic.crop_top = pic.crop_bottom = crop_y
        pic._element.find(f'.//{{{NS["p"]}}}cNvPr').set('id', str(self._id()))
        if opacity < 0.99:
            blip = pic._element.find(f'.//{{{NS["a"]}}}blip')
            if blip is not None:
                blip.append(_el('a:alphaModFix', {'amt': str(int(opacity * 100000))}))
        self._add(container, pic._element)            # 移入当前容器，保持文档顺序


# -------------------------------------------------------------------
# 主流程
# -------------------------------------------------------------------
def collect_svgs(svg_input):
    svg_input = Path(svg_input)
    if svg_input.is_file():
        return [svg_input]
    if svg_input.is_dir():
        return sorted(svg_input.glob('*.svg'), key=natural_key)
    return []


def convert(svg_input, output_path, transition='fade', transition_speed='med', advance_after=None,
            animate='none', animate_trigger='click', group_cards=True, fonts='safe'):
    svg_files = collect_svgs(svg_input)
    if not svg_files:
        print(f"Error: no SVG files found in {svg_input}", file=sys.stderr)
        sys.exit(1)

    prs = Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    blank = prs.slide_layouts[6]
    converter = SvgConverter(group_cards=group_cards, fonts=fonts)

    for index, svg_file in enumerate(svg_files, start=1):
        slide = prs.slides.add_slide(blank)
        converter.convert(svg_file, slide)
        apply_transition(slide, transition, speed=transition_speed, advance_after=advance_after)
        animated = 0
        if animate != 'none':
            animated = apply_entrance(slide, converter.card_ids, effect=animate, trigger=animate_trigger)
        s = converter.stats
        print(f"  [{index}/{len(svg_files)}] {svg_file.name} ({s['shapes']} shapes, "
              f"{len(converter.card_ids)} cards, {animated} animated, {s['skipped']} skipped, {s['errors']} errors)")

    prs.save(str(output_path))
    print(f"Saved: {output_path} ({len(svg_files)} slides, transition={transition}, animate={animate})")


def main():
    parser = argparse.ArgumentParser(description="SVG to PPTX (native shapes, transitions, entrance animations)")
    parser.add_argument('svg', help='SVG file or directory')
    parser.add_argument('-o', '--output', default='presentation.pptx')
    parser.add_argument('--transition', default='fade', choices=sorted(TRANSITIONS) + ['none'],
                        help='页间切换效果（默认 fade）')
    parser.add_argument('--transition-speed', default='med', choices=TRANSITION_SPEEDS)
    parser.add_argument('--advance-after', type=float, default=None, metavar='SECONDS',
                        help='每页停留若干秒后自动翻页（默认仅点击翻页）')
    parser.add_argument('--animate', default='none', choices=['none'] + sorted(ENTRANCE_EFFECTS),
                        help='卡片入场动画（默认 none）')
    parser.add_argument('--animate-trigger', default='click', choices=['click', 'auto'],
                        help='click=每次点击出现一张卡片；auto=进入页面后依次自动出现')
    parser.add_argument('--no-group', action='store_true', help='不把卡片内的形状打成组合')
    parser.add_argument('--fonts', default='safe', choices=['safe', 'design'],
                        help='safe=映射到 Office 自带字体（默认）；design=保留设计字体名（需目标机器已安装）')
    args = parser.parse_args()
    if args.animate != 'none' and args.no_group:
        parser.error('--animate 需要卡片组合，不能与 --no-group 同用')
    convert(args.svg, args.output, transition=args.transition, transition_speed=args.transition_speed,
            advance_after=args.advance_after, animate=args.animate, animate_trigger=args.animate_trigger,
            group_cards=not args.no_group, fonts=args.fonts)


if __name__ == '__main__':
    main()
