/* t102：接近视口或空闲时预绘真实地图图层；目录按层级展开并记住；导航簇改用线型图标 */
(function(){
  var ric=window.requestIdleCallback||function(f){return setTimeout(f,200)};
  function warm(x){
    if(!x || x.classList.contains('is-warm')) return;
    x.classList.add('is-warm');
    var im=x.querySelector('.mx-r img');
    if(im){
      im.loading='eager';
      if(im.decode) im.decode().catch(function(){});
    }
  }
  function warmAll(){
    document.querySelectorAll('.mapx').forEach(warm);
  }
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting) return;
        io.unobserve(e.target);
        warm(e.target);
      });
    }, {rootMargin:'2000px 0px'});
    document.querySelectorAll('.mapx').forEach(function(x){ io.observe(x); });
  }
  ric(warmAll, {timeout:800});
  if(document.readyState==='complete') setTimeout(warmAll, 400);
  else addEventListener('load', function(){ setTimeout(warmAll, 400); });
})();

/* 目录：一级 / 到二级 / 全部，默认到二级，记在本机 */
(function(){
  var d=document, KEY='ui.toclv';
  function $(s,r){return (r||d).querySelector(s)}
  function $$(s,r){return [].slice.call((r||d).querySelectorAll(s))}
  function hydrateT1(li){
    if(!li) return;
    var tm=li.querySelector(':scope > template.t1pack');
    if(!tm) return;
    li.appendChild(tm.content.cloneNode(true));
    tm.remove();
  }
  function setOpen(li, open){
    if(!li) return;
    if(open && li.classList.contains('t1')) hydrateT1(li);
    li.classList.toggle('closed', !open);
    var g=li.classList.contains('t1')?$('.tg',li):$('.tg2',li);
    if(g) g.setAttribute('aria-expanded', open?'true':'false');
  }
  function applyLevel(lv, persist){
    var toc=$('#toc'); if(!toc) return;
    $$('#toc .t1').forEach(function(li){
      if(lv==='1'){
        setOpen(li, false);
      }else{
        hydrateT1(li);
        setOpen(li, true);
        $$('.t2.has', li).forEach(function(t2){ setOpen(t2, lv==='all'); });
      }
    });
    $$('.toclv [data-toclv]').forEach(function(b){
      var on=b.getAttribute('data-toclv')===lv;
      b.setAttribute('aria-pressed', on?'true':'false');
      b.classList.toggle('on', on);
    });
    if(persist!==false){
      try{localStorage.setItem(KEY, lv)}catch(e){}
    }
  }
  function boot(){
    var toc=$('#toc'); if(!toc) return;
    var head=$('.tochead', toc); if(!head) return;
    if($('.toclv', toc)) return;
    var box=$('#toc .tocbtns');
    if(!box){ box=d.createElement('span'); box.className='tocbtns'; head.appendChild(box); }
    box.classList.add('toclv');
    box.setAttribute('role','group');
    box.setAttribute('aria-label','目录展开到哪一级');
    box.innerHTML=
      '<button type="button" class="btn ghost tocctl" data-toclv="1" title="只显示一级标题">一级</button>'+
      '<button type="button" class="btn ghost tocctl" data-toclv="2" title="展开到二级标题">二级</button>'+
      '<button type="button" class="btn ghost tocctl" data-toclv="all" title="展开全部层级">全部</button>';
    box.addEventListener('click', function(e){
      var b=e.target.closest('[data-toclv]');
      if(!b) return;
      applyLevel(b.getAttribute('data-toclv'), true);
    });
    var lv='2';
    try{ var s=localStorage.getItem(KEY); if(s==='1'||s==='2'||s==='all') lv=s; }catch(e){}
    applyLevel(lv, false);
  }
  if(d.readyState==='loading') d.addEventListener('DOMContentLoaded', function(){ setTimeout(boot,0); });
  else setTimeout(boot,0);
  addEventListener('load', function(){ setTimeout(boot,0); });
})();

/* 导航簇：用线型 SVG 替换符号，保持原有按钮与无障碍标签 */
(function(){
  var d=document;
  function svg(inner){
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+inner+'</svg>';
  }
  var I={
    back: svg('<path d="M15 5l-7 7 7 7"/>'),
    fwd: svg('<path d="M9 5l7 7-7 7"/>'),
    top: svg('<path d="M12 20V8"/><path d="M6 14l6-6 6 6"/><path d="M5 5h14"/>'),
    bot: svg('<path d="M12 4v12"/><path d="M6 10l6 6 6-6"/><path d="M5 19h14"/>'),
    home: svg('<path d="M4 11.5L12 4l8 7.5"/><path d="M6 10.5V20h4.5v-5h3v5H18V10.5"/>'),
    thm: svg('<circle cx="12" cy="12" r="4"/><path d="M12 3v2.2M12 18.8V21M4.6 6.2l1.6 1.6M17.8 16.2l1.6 1.6M3 12h2.2M18.8 12H21M4.6 17.8l1.6-1.6M17.8 7.8l1.6-1.6"/>'),
    nav: svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 5.5v13M5.5 12h13"/><path d="M12 8.2l2.4 6.3-6.3-2.4L15.2 9"/>'),
    toc: svg('<path d="M6 7h12M6 12h12M6 17h8"/>')
  };
  function fill(el, html){
    if(!el || el.querySelector('svg')) return;
    el.innerHTML=html;
  }
  function boot(){
    var c=d.getElementById('navc'); if(!c) return;
    if(c.getAttribute('data-t102ico')) return;
    c.setAttribute('data-t102ico','1');
    fill(c.querySelector('[data-nv=back]'), I.back);
    fill(c.querySelector('[data-nv=fwd]'), I.fwd);
    fill(c.querySelector('[data-nv=top]'), I.top);
    fill(c.querySelector('[data-nv=bot]'), I.bot);
    fill(c.querySelector('a[title="首页"],a[aria-label="回到首页"]'), I.home);
    fill(d.getElementById('thmb'), I.thm);
    fill(c.querySelector('.nv-t'), I.nav);
    var toc=d.getElementById('tocbtn');
    if(toc) fill(toc, I.toc);
  }
  if(d.readyState==='loading') d.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
