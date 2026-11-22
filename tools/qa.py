"""Playwright QA：每页 × 6 个宽度。检查水平溢出、被裁切的文字、JS 错误、no-JS 与 reduced-motion 下内容可见。
用法：python3 tools/qa.py [--shots] [--nojs] [--rm] [页面...]  （file:// 打开）"""
import sys,os,glob,json
from playwright.sync_api import sync_playwright
args=sys.argv[1:]; shots='--shots' in args; nojs='--nojs' in args; rm='--rm' in args; opn='--open' in args
pages=[a for a in args if a.endswith('.html')] or sorted(glob.glob('*.html'))
W=[360,390,430,768,1280,1440]
JS_OVER='''()=>{
 const vw=document.documentElement.clientWidth, out=[];
 const sc=(el)=>{for(let p=el;p&&p!==document.body;p=p.parentElement){const o=getComputedStyle(p).overflowX; if((o==='auto'||o==='scroll')&&p.scrollWidth>p.clientWidth) return true;} return false};
 document.querySelectorAll('main *, #toc *').forEach(el=>{
   if(el.closest('svg')&&el.tagName!=='svg') return;
   const r=el.getBoundingClientRect(); if(r.width===0||r.height===0) return;
   if(getComputedStyle(el).position==='fixed') return;
   if(r.right>vw+1||r.left<-1){ if(!sc(el)&&!el.closest('#toc')) out.push([el.tagName+'.'+(el.className&&el.className.baseVal===undefined?el.className:''),Math.round(r.left),Math.round(r.right)]); }
 });
 return {sw:document.documentElement.scrollWidth,vw:vw,over:out.slice(0,6),n:out.length};
}'''
JS_CLIP='''()=>{const out=[];document.querySelectorAll('main p,main li,main td,main th,main b,main a,main span,main h3,main h4,main small,main summary,main button').forEach(el=>{
 const cs=getComputedStyle(el); if(el.closest('svg')||el.closest('#toc')) return;
 if(el.scrollWidth>el.clientWidth+2&&(cs.overflowX==='hidden'||cs.overflowX==='clip')&&el.clientWidth>0&&getComputedStyle(el).display!=='inline') out.push(el.tagName+'.'+el.className+':'+(el.textContent||'').slice(0,20));
 });return out.slice(0,5)}'''
JS_VIS='''()=>{let n=0,bad=[];document.querySelectorAll('.reveal').forEach(e=>{const o=parseFloat(getComputedStyle(e).opacity);if(o<0.99){n++;if(bad.length<3)bad.push(e.className.slice(0,30))}});return {hidden:n,bad:bad,js:document.documentElement.classList.contains('js')}}'''
JS_T100=r'''()=>{
  const bad=[];
  const th=document.querySelector('.thbar');
  if(th){
    const cs=getComputedStyle(th);
    if(cs.display!=='none' && cs.visibility!=='hidden' && +cs.opacity>0) bad.push('header thbar visible');
  }
  const main=document.getElementById('main');
  if(main){
    const first=main.firstElementChild;
    if(first && first.classList && first.classList.contains('thbar')){
      const cs=getComputedStyle(first);
      if(cs.display!=='none') bad.push('thbar still first in main');
    }
  }
  const nav=document.getElementById('navc');
  if(!nav) bad.push('missing #navc');
  const toc=document.getElementById('tocbtn');
  function vis(el){
    if(!el) return false;
    const r=el.getBoundingClientRect(), cs=getComputedStyle(el);
    return r.width>2 && r.height>2 && cs.display!=='none' && cs.visibility!=='hidden' && +cs.opacity>=0.2 && cs.pointerEvents!=='none';
  }
  const crs=[];
  if(vis(nav)){
    const open=nav.classList.contains('open');
    nav.querySelectorAll('.nv-t, #thmb, .nv-l > :not([hidden])').forEach(p=>{
      if(p.closest('.nv-l') && !open){
        const cs=getComputedStyle(p);
        if(cs.visibility==='hidden'||+cs.opacity<0.2||cs.pointerEvents==='none') return;
      }
      const r=p.getBoundingClientRect();
      const cs=getComputedStyle(p);
      if(r.width>2&&r.height>2&&cs.visibility!=='hidden'&&+cs.opacity>=0.2) crs.push({sel:p.getAttribute('data-nv')||p.id||p.className||'nav',r});
    });
  }
  /* t112: ⋯ may overlap content edges; only fail if the open popover is off-screen. */
  var launch=document.getElementById('nvlaunch');
  var pop=document.getElementById('nvpop');
  if(launch && pop && launch.hasAttribute('open')){
    var pr=pop.getBoundingClientRect();
    var vw=document.documentElement.clientWidth||window.innerWidth;
    var vh=document.documentElement.clientHeight||window.innerHeight;
    if(pr.width>2 && pr.height>2){
      if(pr.left<-1 || pr.right>vw+1 || pr.top<-1 || pr.bottom>vh+1)
        bad.push('launcher popover off-screen '+[Math.round(pr.left),Math.round(pr.top),Math.round(pr.right),Math.round(pr.bottom),vw,vh].join(','));
    }
  }
  return bad;
}'''
JS_T118=r"""()=>{
  const bad=[];
  const vw=document.documentElement.clientWidth||window.innerWidth;
  const vh=document.documentElement.clientHeight||window.innerHeight;
  function vis(el){
    if(!el) return false;
    const r=el.getBoundingClientRect(), cs=getComputedStyle(el);
    if(!(r.width>2 && r.height>2 && cs.display!=='none' && cs.visibility!=='hidden' && +cs.opacity>=0.2 && cs.pointerEvents!=='none')) return false;
    if(r.right<=2 || r.bottom<=2 || r.left>=vw-2 || r.top>=vh-2) return false;
    return true;
  }
  function box(el){return el.getBoundingClientRect()}
  function visibleRect(el, r){
    r = r || (el.getBoundingClientRect ? el.getBoundingClientRect() : r);
    if(!r) return null;
    let x1=r.left, y1=r.top, x2=r.right, y2=r.bottom;
    let p=el && (el.nodeType===1?el.parentElement:el.parentElement);
    while(p && p!==document.documentElement){
      const cs=getComputedStyle(p);
      const clipX=cs.overflowX==='hidden'||cs.overflowX==='auto'||cs.overflowX==='scroll'||cs.overflowX==='clip';
      const clipY=cs.overflowY==='hidden'||cs.overflowY==='auto'||cs.overflowY==='scroll'||cs.overflowY==='clip';
      if(clipX||clipY){
        const pr=p.getBoundingClientRect();
        if(clipX){ x1=Math.max(x1, pr.left); x2=Math.min(x2, pr.right); }
        if(clipY){ y1=Math.max(y1, pr.top); y2=Math.min(y2, pr.bottom); }
      }
      p=p.parentElement;
    }
    x1=Math.max(x1,0); y1=Math.max(y1,0); x2=Math.min(x2,vw); y2=Math.min(y2,vh);
    if(x2-x1<=2 || y2-y1<=2) return null;
    return {left:x1,top:y1,right:x2,bottom:y2};
  }
  function hit(a,b){
    const x=Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left));
    const y=Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top));
    return (x>2 && y>2) ? {x:Math.round(x),y:Math.round(y)} : null;
  }
  function lab(el){
    if(!el) return '?';
    return (el.id && ('#'+el.id)) || (el.getAttribute && el.getAttribute('class') && ('.'+String(el.getAttribute('class')).split(/\s+/).slice(0,2).join('.'))) || el.tagName;
  }
  function wide(){return window.innerWidth>=1100}
  function drawerOpen(){return wide()?!document.body.classList.contains('tochide'):document.body.classList.contains('tocopen')}
  function setDrawer(open){
    if(wide()) document.body.classList.toggle('tochide', !open);
    else document.body.classList.toggle('tocopen', !!open);
  }
  function isOwn(chrome, node){
    const el=node.nodeType===1?node:node.parentElement;
    return !!(el && chrome.contains(el));
  }
  function inMainFlow(node){
    const el=node.nodeType===1?node:node.parentElement;
    if(!el) return false;
    if(el.closest('#ptabrow,#ptabwrap,#ptabline,#toc,#tocx,#tochd,#nvdock,#nvpop,#navc,#tocgrip')) return false;
    return !!el.closest('#main');
  }
  function inChromeLayer(node){
    const el=node.nodeType===1?node:node.parentElement;
    return !!(el && el.closest('#ptabrow,#ptabwrap,#ptabline,#toc,#tocx,#tochd,#nvdock,#nvpop,#navc,#tocgrip'));
  }
  function interactive(el){
    if(!el || el.nodeType!==1) return false;
    const t=el.tagName;
    if(t==='A'||t==='BUTTON'||t==='SUMMARY'||t==='INPUT'||t==='SELECT'||t==='TEXTAREA') return true;
    const role=el.getAttribute('role');
    if(role==='button'||role==='menuitem'||role==='menuitemradio'||role==='link'||role==='tab') return true;
    if(el.hasAttribute('tabindex') && el.getAttribute('tabindex')!=='-1') return true;
    return false;
  }
  function textHits(chrome, r, dockMode){
    const out=[];
    const tw=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode:function(n){
        if(!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const p=n.parentElement;
        if(!p || p.closest('script,style,noscript,title')) return NodeFilter.FILTER_REJECT;
        if(isOwn(chrome,n)) return NodeFilter.FILTER_REJECT;
        if(dockMode && inMainFlow(n) && !inChromeLayer(n)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    let n;
    while((n=tw.nextNode())){
      const p=n.parentElement; if(!p) continue;
      const pr=p.getBoundingClientRect();
      if(pr.width<2||pr.height<2) continue;
      if(!hit(r,pr)) continue;
      const range=document.createRange();
      range.selectNodeContents(n);
      const rects=range.getClientRects();
      for(const tr of rects){
        const vr=visibleRect(p, tr);
        if(!vr) continue;
        const o=hit(r,vr);
        if(o){ out.push((n.nodeValue||'').trim().slice(0,16)); break; }
      }
      if(out.length>=3) break;
    }
    return out;
  }
  function controlHits(chrome, r, dockMode){
    const out=[];
    document.querySelectorAll('a,button,summary,input,select,textarea,[role="button"],[role="menuitem"],[role="menuitemradio"],#tocx,.tocctl,.ptab-tog,.ptab-hair,#nvsum,#tocbtn,#tochd').forEach(el=>{
      if(isOwn(chrome,el)) return;
      if(!vis(el)) return;
      if(dockMode && inMainFlow(el) && !inChromeLayer(el)) return;
      const br=visibleRect(el);
      if(!br) return;
      const o=hit(r, br);
      if(o) out.push(lab(el)+'@'+o.x+'x'+o.y);
    });
    return out.slice(0,4);
  }
  function checkOne(el, name, dockMode){
    if(!vis(el)) return;
    const r=visibleRect(el); if(!r) return;
    const ih=controlHits(el,r,dockMode);
    const th=textHits(el,r,dockMode);
    if(ih.length) bad.push(name+' overlaps controls '+ih.join(','));
    if(th.length) bad.push(name+' overlaps text '+JSON.stringify(th));
  }
  function checkLevelRow(){
    const toc=document.getElementById('toc');
    if(!vis(toc)) return;
    const cr=toc.getBoundingClientRect();
    const cs=getComputedStyle(toc);
    const padR=parseFloat(cs.paddingRight)||0;
    const innerRight=cr.right-padR;
    const innerLeft=cr.left+(parseFloat(cs.paddingLeft)||0);
    toc.querySelectorAll('.tochead b, .tochead .tocctl, #toc-ex, #toc-cl').forEach(el=>{
      if(!vis(el)) return;
      const r=box(el);
      if(r.right>innerRight+1 || r.left<innerLeft-1 || r.right>cr.right+1){
        bad.push('toc control clipped '+lab(el)+' r='+Math.round(r.right)+' tocR='+Math.round(cr.right)+' inner='+Math.round(innerRight));
      }
    });
    const x=document.getElementById('tocx');
    if(vis(x)){
      const xr=box(x);
      toc.querySelectorAll('.tochead b, .tochead .tocctl, #toc-ex, #toc-cl').forEach(el=>{
        if(!vis(el)) return;
        const o=hit(xr, box(el));
        if(o) bad.push('#tocx overlaps '+lab(el)+'@'+o.x+'x'+o.y);
      });
    }
  }
  function run(tag){
    const hd=document.getElementById('tochd');
    checkOne(hd, tag+' #tochd', false);
    const hair=document.querySelector('#ptabline .ptab-hair, .ptab-hair');
    const wrap=document.getElementById('ptabwrap');
    if(wrap && wrap.classList.contains('is-hide')) checkOne(hair, tag+' hairline', true);
    ['#nvdock #tocbtn','#nvdock #nvsum','#nvdock .nv-toc-fallback'].forEach(sel=>{
      const el=document.querySelector(sel);
      checkOne(el, tag+' '+sel, true);
    });
    const launch=document.getElementById('nvlaunch');
    const pop=document.getElementById('nvpop');
    if(launch && pop && launch.hasAttribute('open')) checkOne(pop, tag+' #nvpop', true);
    checkLevelRow();
  }
  const wasOpen=drawerOpen();
  const root=document.documentElement;
  const prop=wide()?'--tw':'--twm';
  const prev=root.style.getPropertyValue(prop);
  setDrawer(false);
  run('closed');
  setDrawer(true);
  run('open');
  const min=wide()?240:200;
  root.style.setProperty(prop, min+'px');
  run('open-min'+min);
  if(prev) root.style.setProperty(prop, prev);
  else root.style.removeProperty(prop);
  setDrawer(wasOpen);
  return bad;
}"""

res=[];fail=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for f in pages:
        for w in W:
            ctx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=not nojs,reduced_motion='reduce' if rm else 'no-preference')
            if os.environ.get('THEME'): ctx.add_init_script("try{localStorage.setItem('ui.theme','%s')}catch(e){}"%os.environ['THEME'])
            pg=ctx.new_page(); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
            pg.goto('file://'+os.path.abspath(f)); pg.wait_for_timeout(300); pg.evaluate("s=>{const e=document.createElement('style');e.textContent=s;document.head.appendChild(e)}",'main section.l2,main section.l3,main figure,main .icm{content-visibility:visible!important}')  # v8：测量时强制渲染 content-visibility:auto 的区块
            if opn: pg.evaluate("document.querySelectorAll('details').forEach(e=>e.open=true)")
            if not nojs:
                # 滚动一遍以触发 reveal / 进度
                h=pg.evaluate('document.documentElement.scrollHeight')
                pg.evaluate('''async(h)=>{const f=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));for(let y=0;y<h;y+=700){window.scrollTo(0,y);await f();}}''',h)  # 单次 evaluate 内滚动，免去每步往返
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(200)
            ov=pg.evaluate(JS_OVER); cl=pg.evaluate(JS_CLIP); vis=pg.evaluate(JS_VIS)
            pg.evaluate("()=>{var el=document.getElementById('nvlaunch'); if(el) el.setAttribute('open','');}")
            t100=pg.evaluate(JS_T100)
            t118d=pg.evaluate(JS_T118) if not nojs else []
            pg.evaluate("()=>{var el=document.getElementById('nvlaunch'); if(el) el.removeAttribute('open');}")
            t118=pg.evaluate(JS_T118) if not nojs else []
            if t118d: t118=list(t118)+['dockopen '+x for x in t118d]
            bad=[]
            if ov['sw']>ov['vw']+1: bad.append(f"页面横向溢出 sw={ov['sw']} vw={ov['vw']}")
            if ov['n']: bad.append(f"元素越界 {ov['n']}: {ov['over']}")
            if cl: bad.append(f"文字被裁切: {cl}")
            if errs: bad.append(f"JS错误: {errs[:2]}")
            if (nojs or rm) and vis['hidden']: bad.append(f"不可见元素 {vis}")
            if (nojs and vis['js']) : bad.append("no-JS 却带 js 类")
            if rm and vis['js']: bad.append("reduced-motion 却启用 reveal")
            if t100: bad.append("t100: "+str(t100))
            if t118: bad.append("t118: "+str(t118))
            if shots and w in (360,1280) and not nojs and not rm:
                os.makedirs('_shots',exist_ok=True); pg.screenshot(path=f'_shots/{f[:-5]}_{w}.png',full_page=True)
            tag='FAIL' if bad else 'ok'
            if bad: fail+=1; print(tag,f,w,bad)
            ctx.close()
    b.close()
print('QA',('nojs' if nojs else 'rm' if rm else 'normal'),'theme='+os.environ.get('THEME','night'),'open' if opn else 'collapsed','pages',len(pages),'widths',W,'fails',fail)
