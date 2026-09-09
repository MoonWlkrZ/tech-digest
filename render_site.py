#!/usr/bin/env python3
"""Render the structured digest source into a static GitHub Pages site.

Input:  source/daily_digest.json
Output: digest.json (browser-readable data) and index.html
Markdown in recommendation.full_analysis_md is rendered server-side with Python-Markdown.
"""
import html, json, shutil
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "daily_digest.json"
OUT_DATA = ROOT / "digest.json"
OUT_HTML = ROOT / "index.html"

CSS = r'''
:root{--bg:#101211;--panel:#171a18;--ink:#edf1e9;--muted:#9da89e;--line:#303832;--accent:#b7e36b;--warm:#f2b56b;--serif:Georgia,'Times New Roman',serif;--sans:Inter,ui-sans-serif,system-ui,sans-serif;--mono:'SFMono-Regular',Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans)}a{color:inherit}.shell{max-width:1180px;margin:auto;padding:34px 24px 72px}.topline{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:14px}.brand,.date,.source,.score,.meta{font:11px var(--mono);letter-spacing:.1em;text-transform:uppercase}.brand{color:var(--accent)}.date,.meta{color:var(--muted)}header{display:grid;grid-template-columns:1.2fr .8fr;gap:48px;padding:62px 0 44px}h1{font:400 clamp(42px,6vw,76px)/.98 var(--serif);letter-spacing:-.055em;margin:0 0 20px}.dek{color:var(--muted);font-size:17px;line-height:1.6;margin:0}.note{border-left:1px solid var(--line);padding-left:25px;align-self:end;color:var(--muted);line-height:1.65}.toolbar{display:flex;gap:10px;border-block:1px solid var(--line);padding:13px 0;margin-bottom:30px}input,select{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:5px;padding:10px 12px;font:inherit}input{flex:1}.count{margin-left:auto;color:var(--muted);font:12px var(--mono)}.section{margin-top:38px}.section-head{display:flex;gap:14px;align-items:baseline;margin-bottom:14px}h2{font:400 27px var(--serif);margin:0}.section-count{color:var(--muted);font:11px var(--mono)}.recommendations{display:grid;gap:14px}.recommendation{background:var(--panel);border:1px solid #596b4d;padding:24px;display:grid;grid-template-columns:56px 1fr;gap:18px}.rank{color:var(--accent);font:32px/1 var(--serif)}.score{color:var(--warm)}.recommendation h3{font:400 28px/1.1 var(--serif);margin:0 0 12px}.recommendation h3 a{text-decoration:none}.recommendation h3 a:hover{color:var(--accent)}.reason{font-size:15px;line-height:1.6;margin:0 0 13px}.read-more{margin-top:14px;border-top:1px solid var(--line);padding-top:12px}.read-more summary{color:var(--accent);cursor:pointer;font:12px var(--mono)}.full{color:var(--muted);font-size:15px;line-height:1.72;margin-top:18px}.full h1,.full h2,.full h3{font-family:var(--serif);color:var(--ink);letter-spacing:normal}.full h2{font-size:24px;margin:28px 0 10px}.full h3{font-size:19px;margin:20px 0 8px}.full p{margin:10px 0}.full ul,.full ol{padding-left:24px}.full blockquote{border-left:2px solid var(--accent);padding-left:16px;color:var(--ink)}.card-foot{display:flex;justify-content:space-between;gap:10px;margin-top:18px;color:#6f7a71;font:10px var(--mono)}.recommendation .card-foot{grid-column:2}.judgment{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:22px 0;color:var(--muted);font:18px/1.55 var(--serif)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.item{background:var(--panel);border:1px solid var(--line);padding:18px;min-height:190px;display:flex;flex-direction:column;transition:border-color .15s ease}.item:hover{border-color:var(--accent)}.item h3{font:400 21px/1.15 var(--serif);margin:14px 0 12px}.item h3 a{text-decoration:none}.item h3 a:hover{color:var(--accent)}.summary{color:var(--muted);font-size:13px;line-height:1.6;margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.item:hover .summary{-webkit-line-clamp:999;color:var(--ink)}.empty{color:var(--muted);padding:30px 0}footer{border-top:1px solid var(--line);margin-top:58px;padding-top:18px;color:#69746b;font:11px var(--mono);display:flex;justify-content:space-between}@media(max-width:850px){header{grid-template-columns:1fr;gap:28px}.note{border-left:0;border-top:1px solid var(--line);padding:18px 0 0}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.count{margin-left:0}}@media(max-width:560px){.shell{padding:22px 16px 52px}.grid{grid-template-columns:1fr}.toolbar{flex-wrap:wrap}.count{width:100%}footer{flex-direction:column}}
'''


def stars(score):
    return f"{'★'*score}{'☆'*(5-score)}" if isinstance(score,int) and 1 <= score <= 5 else '待评估'

def render_markdown(text):
    return markdown.markdown(text or '', extensions=['extra','sane_lists','nl2br'])

def main():
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    recs=data.get('recommendations',[])
    items=data.get('items',[])
    payload=json.dumps(data,ensure_ascii=False,indent=2)
    OUT_DATA.write_text(payload,encoding='utf-8')
    rec_html=[]
    for n,r in enumerate(recs,1):
        rec_html.append(f'''<article class="recommendation"><div class="rank">{n:02d}</div><div><div class="source">{html.escape(r.get('verdict','推荐'))} · <span class="score">{stars(r.get('score'))}</span> · {html.escape(r.get('source',''))}</div><h3><a href="{html.escape(r['url'])}" target="_blank" rel="noopener noreferrer">{html.escape(r['title'])}</a></h3><p class="reason"><strong>为什么值得看：</strong>{html.escape(r.get('reason',''))}</p><details class="read-more"><summary>展开完整精读</summary><div class="full">{render_markdown(r.get('full_analysis_md') or r.get('full_analysis',''))}</div></details><div class="card-foot"><span>{html.escape(r.get('reading_cost',''))}</span><span>↗ 原文</span></div></div></article>''')
    item_html=[]
    for i in sorted(items,key=lambda x:(-(x.get('rough_score') or x.get('score') or 0),str(x.get('published',''))),reverse=False):
        score=i.get('rough_score',i.get('score'))
        body = i.get('highlight') or i.get('summary') or ''
        body_html = f'<p class="summary">{html.escape(body)}</p>' if body else ''
        item_html.append(f'''<article class="item"><div class="source">{html.escape(i.get('source',''))} <span class="score">{stars(score)}</span></div><h3><a href="{html.escape(i.get('url',''))}" target="_blank" rel="noopener noreferrer">{html.escape(i.get('title',''))}</a></h3>{body_html}<div class="card-foot"><span>{html.escape(str(i.get('published',''))[:16])}</span><span>↗ 原文</span></div></article>''')
    html_doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="AI-curated technology reading digest"><title>Tech Brief — 技术阅读日报</title><style>{CSS}</style></head><body><main class="shell"><div class="topline"><div class="brand">Tech Brief / Reading Desk</div><div class="date">edition / {html.escape(str(data.get('edition','')))}</div></div><header><div><div class="source">AI-assisted daily reading</div><h1>值得读的技术，<br>不只是收到的技术。</h1><p class="dek">先聚合，再筛选；AI 读完少数真正重要的文章，给出推荐顺序和完整判断。</p></div><aside class="note">{len(recs)} 篇完整精读<br>{len(items)} 篇标题级初筛<br>来源只作为辅助标签</aside></header><section class="section"><div class="section-head"><h2>今日推荐顺序</h2><span class="section-count">{len(recs)} selected</span></div><div class="recommendations">{''.join(rec_html)}</div></section><section class="section"><div class="section-head"><h2>今日判断</h2></div><p class="judgment">{html.escape(data.get('judgment',''))}</p></section><section class="section"><div class="section-head"><h2>阅读队列</h2><span class="section-count">标题/摘要初筛分</span></div><div class="grid">{''.join(item_html)}</div></section><footer><span>原文链接指向文章作者/发布站点</span><span>Generated from structured digest data</span></footer></main></body></html>'''
    OUT_HTML.write_text(html_doc,encoding='utf-8')
    print(json.dumps({'generated':str(OUT_HTML),'recommendations':len(recs),'items':len(items),'markdown':'python-markdown'}))

if __name__=='__main__': main()
