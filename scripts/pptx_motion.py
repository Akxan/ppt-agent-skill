#!/usr/bin/env python3
"""PPTX 动效：页间切换（p:transition）与形状入场动画（p:timing）。

python-pptx 不提供动画 API，这里直接写 PresentationML。只使用基础命名空间里的
切换与动画节点，PowerPoint 2010+ 均可识别；WPS / Keynote / Google Slides 支持不完整。

供 svg2pptx.py / png2pptx.py 调用：
    apply_transition(slide, "fade")
    apply_entrance(slide, [shape_id, ...], effect="fade", trigger="click")
"""

from lxml import etree

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _p(tag: str, attrib: dict | None = None, children: list | None = None):
    el = etree.Element(f"{{{P_NS}}}{tag}")
    for key, value in (attrib or {}).items():
        el.set(key, str(value))
    for child in children or []:
        el.append(child)
    return el


# ── 页间切换 ────────────────────────────────────────────────────────────────

TRANSITIONS = {
    "fade": lambda: _p("fade"),
    "push": lambda: _p("push", {"dir": "l"}),
    "wipe": lambda: _p("wipe", {"dir": "l"}),
    "cover": lambda: _p("cover", {"dir": "l"}),
    "split": lambda: _p("split", {"orient": "vert", "dir": "out"}),
    "zoom": lambda: _p("zoom", {"dir": "in"}),
    "dissolve": lambda: _p("dissolve"),
}
TRANSITION_SPEEDS = ("slow", "med", "fast")


def _insert_in_slide_order(slide_el, node) -> None:
    """按 CT_Slide 的子元素顺序插入：cSld, clrMapOvr, transition, timing, extLst。"""
    order = ["cSld", "clrMapOvr", "transition", "timing", "extLst"]
    rank = order.index(etree.QName(node).localname)
    for existing in slide_el.findall(f"{{{P_NS}}}{etree.QName(node).localname}"):
        slide_el.remove(existing)
    for child in slide_el:
        if order.index(etree.QName(child).localname) > rank:
            child.addprevious(node)
            return
    slide_el.append(node)


def apply_transition(slide, kind: str = "fade", speed: str = "med", advance_after: float | None = None) -> None:
    """给一页幻灯片设置进入时的切换效果。advance_after 为秒数时自动翻页。"""
    if kind == "none":
        return
    if kind not in TRANSITIONS:
        raise ValueError(f"unknown transition '{kind}', expected one of {sorted(TRANSITIONS)} or 'none'")
    attrs = {"spd": speed if speed in TRANSITION_SPEEDS else "med", "advClick": "1"}
    if advance_after is not None:
        attrs["advTm"] = str(int(advance_after * 1000))
    _insert_in_slide_order(slide._element, _p("transition", attrs, [TRANSITIONS[kind]()]))


# ── 入场动画 ────────────────────────────────────────────────────────────────

# effect -> (presetID, presetSubtype)，仅影响 PowerPoint 动画窗格里显示的名称
ENTRANCE_EFFECTS = {
    "fade": (10, 0),     # 淡入
    "wipe": (22, 8),     # 自左擦除
    "rise": (42, 0),     # 上浮
    "zoom": (53, 16),    # 缩放
}


class _Ids:
    def __init__(self, start: int = 1):
        self.value = start - 1

    def next(self) -> int:
        self.value += 1
        return self.value


def _ctn(ids: _Ids, attrib: dict | None = None, delay: str | None = None, children: list | None = None):
    """p:cTn，可带起始条件与子时间节点。"""
    node = _p("cTn", {"id": ids.next(), **(attrib or {})})
    if delay is not None:
        node.append(_p("stCondLst", children=[_p("cond", {"delay": delay})]))
    if children is not None:
        node.append(_p("childTnLst", children=children))
    return node


def _target(spid: int):
    return _p("tgtEl", children=[_p("spTgt", {"spid": spid})])


def _set_visible(ids: _Ids, spid: int):
    return _p("set", children=[
        _p("cBhvr", children=[
            _ctn(ids, {"dur": "1", "fill": "hold"}, delay="0"),
            _target(spid),
            _p("attrNameLst", children=[_text_node("attrName", "style.visibility")]),
        ]),
        _p("to", children=[_p("strVal", {"val": "visible"})]),
    ])


def _text_node(tag: str, text: str):
    node = _p(tag)
    node.text = text
    return node


def _anim_effect(ids: _Ids, spid: int, filter_name: str, duration: int):
    return _p("animEffect", {"transition": "in", "filter": filter_name}, [
        _p("cBhvr", children=[_ctn(ids, {"dur": duration}), _target(spid)]),
    ])


def _anim_property(ids: _Ids, spid: int, prop: str, start: str, end: str, duration: int):
    """属性补间：ppt_x / ppt_y / ppt_w / ppt_h，取值可用 #ppt_x 这类公式。"""
    return _p("anim", {"calcmode": "lin", "valueType": "num"}, [
        _p("cBhvr", {"additive": "base"}, [
            _ctn(ids, {"dur": duration, "fill": "hold"}),
            _target(spid),
            _p("attrNameLst", children=[_text_node("attrName", prop)]),
        ]),
        _p("tavLst", children=[
            _p("tav", {"tm": "0"}, [_p("val", children=[_p("strVal", {"val": start})])]),
            _p("tav", {"tm": "100000"}, [_p("val", children=[_p("strVal", {"val": end})])]),
        ]),
    ])


def _behaviors(ids: _Ids, spid: int, effect: str, duration: int) -> list:
    nodes = [_set_visible(ids, spid)]
    if effect == "wipe":
        nodes.append(_anim_effect(ids, spid, "wipe(left)", duration))
    elif effect == "rise":
        nodes.append(_anim_property(ids, spid, "ppt_y", "#ppt_y+.06", "#ppt_y", duration))
        nodes.append(_anim_effect(ids, spid, "fade", duration))
    elif effect == "zoom":
        nodes.append(_anim_property(ids, spid, "ppt_w", "#ppt_w*0.85", "#ppt_w", duration))
        nodes.append(_anim_property(ids, spid, "ppt_h", "#ppt_h*0.85", "#ppt_h", duration))
        nodes.append(_anim_effect(ids, spid, "fade", duration))
    else:
        nodes.append(_anim_effect(ids, spid, "fade", duration))
    return nodes


def _effect_par(ids: _Ids, spid: int, effect: str, duration: int, node_type: str, delay: int):
    """一个效果：外层 par 控制它在本步内的起始延迟，内层 cTn 带预设信息。"""
    preset_id, subtype = ENTRANCE_EFFECTS[effect]
    inner = _ctn(ids, {
        "presetID": preset_id, "presetClass": "entr", "presetSubtype": subtype,
        "fill": "hold", "nodeType": node_type,
    }, delay="0")
    inner.append(_p("childTnLst", children=_behaviors(ids, spid, effect, duration)))
    return _p("par", children=[
        _ctn(ids, {"fill": "hold"}, delay=str(delay), children=[_p("par", children=[inner])]),
    ])


def apply_entrance(slide, shape_ids: list[int], effect: str = "fade", trigger: str = "click",
                   duration: int = 500, stagger: int = 150) -> int:
    """按顺序给形状加入场动画，返回实际添加的效果数。

    trigger="click"：每次点击出现一个；trigger="auto"：进入本页后依次自动出现。
    """
    if effect not in ENTRANCE_EFFECTS:
        raise ValueError(f"unknown entrance effect '{effect}', expected one of {sorted(ENTRANCE_EFFECTS)}")
    if trigger not in ("click", "auto"):
        raise ValueError("trigger must be 'click' or 'auto'")
    if not shape_ids:
        return 0

    ids = _Ids()
    root_ctn = _p("cTn", {"id": ids.next(), "dur": "indefinite", "restart": "never", "nodeType": "tmRoot"})
    main_ctn = _p("cTn", {"id": ids.next(), "dur": "indefinite", "nodeType": "mainSeq"})
    main_seq_id = main_ctn.get("id")
    steps = []

    if trigger == "click":
        for spid in shape_ids:
            step = _ctn(ids, {"fill": "hold"}, delay="indefinite")
            step.append(_p("childTnLst", children=[
                _effect_par(ids, spid, effect, duration, "clickEffect", 0)]))
            steps.append(_p("par", children=[step]))
    else:
        step = _p("cTn", {"id": ids.next(), "fill": "hold"})
        step.append(_p("stCondLst", children=[
            _p("cond", {"delay": "indefinite"}),
            _p("cond", {"evt": "onBegin", "delay": "0"}, [_p("tn", {"val": main_seq_id})]),
        ]))
        step.append(_p("childTnLst", children=[
            _effect_par(ids, spid, effect, duration, "afterEffect", index * (duration + stagger))
            for index, spid in enumerate(shape_ids)
        ]))
        steps.append(_p("par", children=[step]))

    main_ctn.append(_p("childTnLst", children=steps))
    slide_target = lambda: _p("tgtEl", children=[_p("sldTgt")])  # noqa: E731
    sequence = _p("seq", {"concurrent": "1", "nextAc": "seek"}, [
        main_ctn,
        _p("prevCondLst", children=[_p("cond", {"evt": "onPrev", "delay": "0"}, [slide_target()])]),
        _p("nextCondLst", children=[_p("cond", {"evt": "onNext", "delay": "0"}, [slide_target()])]),
    ])
    root_ctn.append(_p("childTnLst", children=[sequence]))
    timing = _p("timing", children=[_p("tnLst", children=[_p("par", children=[root_ctn])])])
    _insert_in_slide_order(slide._element, timing)
    return len(shape_ids)
