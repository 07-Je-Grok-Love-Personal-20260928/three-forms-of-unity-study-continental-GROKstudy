/* t94：目录全开/全收；当前节自动展开；惰性水合非当前一级；#tocx 在 #toc 外同步标签 */
(function(){
var d=document, b=d.body, w=window;
var toc=d.getElementById('toc');
if(!toc) return;
function $(s,r){return (r||d).querySelector(s)}
function $$(s,r){return [].slice.call((r||d).querySelectorAll(s))}
function wide(){return innerWidth>=1100}
function ariaBtn(btn, open){if(btn)btn.setAttribute('aria-expanded', open?'true':'false')}
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
  ariaBtn(g, open);
}
function currentT1(){
  var c=$('#toc .t1.cur'); if(c) return c;
  var pg=b.dataset.page;
  if(pg){var x=$('#toc .t1[data-page="'+pg+'"]'); if(x) return x}
  return null;
}
function openAncestors(a, closeSiblings){
  if(!a) return;
  var t2=a.closest('.t2.has'), t1=a.closest('.t1')||currentT1();
  if(closeSiblings && t1){
    $$('#toc .t1').forEach(function(li){ if(li!==t1) setOpen(li,false); });
    hydrateT1(t1);
    $$('.t2.has', t1).forEach(function(li){ if(li!==t2) setOpen(li,false); });
  }
  if(t1) setOpen(t1,true);
  if(t2) setOpen(t2,true);
}
function syncX(){
  var x=$('#tocx'); if(!x) return;
  var hid=wide()?b.classList.contains('tochide'):!b.classList.contains('tocopen');
  x.textContent=hid?'目录':'✕';
  x.setAttribute('aria-label', hid?'显示目录':'隐藏目录');
  x.setAttribute('title', hid?'显示目录':'隐藏目录');
}
function hookTog(el){
  if(!el) return;
  var old=el.onclick;
  el.onclick=function(e){ if(old) old.call(el,e); syncX(); };
}
hookTog($('#tocbtn')); hookTog($('#tocx')); syncX();
w.addEventListener('resize', syncX);

/* 捕获阶段：先水合再折叠；拦住 app.js 里只绑了首屏按钮的重复切换 */
toc.addEventListener('click', function(e){
  var btn=e.target.closest('.tg,.tg2');
  if(!btn||!toc.contains(btn)) return;
  e.preventDefault();
  e.stopPropagation();
  if(e.stopImmediatePropagation) e.stopImmediatePropagation();
  var is1=btn.classList.contains('tg');
  var li=btn.closest(is1?'.t1':'.t2');
  if(!li) return;
  if(is1) hydrateT1(li);
  setOpen(li, li.classList.contains('closed'));
}, true);
toc.addEventListener('click', function(e){
  var a=e.target.closest('a');
  if(a && toc.contains(a) && !wide()) b.classList.remove('tocopen');
});

/* 头栏按钮 */
(function(){
  var head=$('.tochead', toc); if(!head) return;
  if($('#toc-ex')) return;
  var box=d.createElement('span'); box.className='tocbtns';
  box.innerHTML='<button type="button" id="toc-ex" class="btn ghost tocctl" title="展开全部一、二、三级目录">全开</button>'+
                '<button type="button" id="toc-cl" class="btn ghost tocctl" title="收起全部，仅保留当前一级">全收</button>';
  head.appendChild(box);
  $('#toc-ex').addEventListener('click', function(){
    $$('#toc .t1').forEach(function(li){
      hydrateT1(li);
      setOpen(li,true);
      $$('.t2.has', li).forEach(function(t2){ setOpen(t2,true); });
    });
  });
  $('#toc-cl').addEventListener('click', function(){
    var keep=currentT1();
    $$('#toc .t1').forEach(function(li){ setOpen(li, li===keep); });
    if(keep){
      hydrateT1(keep);
      $$('.t2.has', keep).forEach(function(li){ setOpen(li, false); });
    }
    var on=$('#toc a.on')|| (keep&&$('.t1r>a',keep));
    if(on) openAncestors(on, false);
  });
})();
/* 进入页面：只打开当前一级，以及哈希对应的二/三级所在组 */
(function(){
  var t1=currentT1();
  $$('#toc .t1').forEach(function(li){ if(li!==t1) setOpen(li,false); });
  if(t1) setOpen(t1,true);
  if(!t1) return;
  $$('.t2.has', t1).forEach(function(li){ setOpen(li, false); });
  var hash=(location.hash||'').replace('#','');
  var a=null;
  if(hash){
    a=$('#toc .t1.cur a[href$="#'+hash+'"]')||$('#toc a[href$="#'+hash+'"]');
  }
  if(!a) a=$('#toc a.on')|| (t1&&$('.t1r>a',t1));
  openAncestors(a, true);
})();
/* 滚动高亮变化时：打开当前二级（不强制关掉用户已展开的其它二级，避免目录跳动） */
var lastT2=null;
function onActive(){
  var a=$('#toc a.on'); if(!a) return;
  var t2=a.closest('.t2.has');
  if(t2===lastT2){ openAncestors(a,false); return; }
  lastT2=t2;
  openAncestors(a,false);
}
var mo=new MutationObserver(function(muts){
  for(var i=0;i<muts.length;i++){
    var t=muts[i].target;
    if(t && t.classList && t.classList.contains('on') && t.tagName==='A'){ onActive(); return; }
  }
});
mo.observe(toc,{subtree:true,attributes:true,attributeFilter:['class']});
w.addEventListener('hashchange', function(){
  var hash=(location.hash||'').replace('#','');
  if(!hash) return;
  var a=$('#toc a[href$="#'+hash+'"]');
  if(a) openAncestors(a,false);
});
})();
