/* t107: keep the fixed #tocbtn / #navc cluster off text.
   Hide both while scrolling; on idle, shrink only the colliding boxes
   so body text stays edge-to-edge except in the cluster's corner. */
(function(){
  var d=document, w=window;
  var toc=d.getElementById('tocbtn');
  var nav=d.getElementById('navc');
  if(!toc && !nav) return;
  var SEL='main p, main li, main h1, main h2, main h3, main h4, main td, main th, main svg, main .mapx, main .t90viz, main .hx, main figure, main table, main .ptabs a, main .hero h1';
  var cleared=[], lastY=w.scrollY, acc=0, ticking=false, idle=0;

  function visBox(el){
    if(!el) return null;
    var r=el.getBoundingClientRect(), cs=getComputedStyle(el);
    if(r.width<=2 || r.height<=2) return null;
    if(cs.display==='none' || cs.visibility==='hidden' || +cs.opacity<0.2) return null;
    return r;
  }
  function clusterRect(){
    var boxes=[], t=visBox(toc), n=visBox(nav);
    if(t) boxes.push(t);
    if(n) boxes.push(n);
    if(!boxes.length) return null;
    var L=Infinity, T=Infinity, R=-Infinity, B=-Infinity, i;
    for(i=0;i<boxes.length;i++){
      L=Math.min(L,boxes[i].left); T=Math.min(T,boxes[i].top);
      R=Math.max(R,boxes[i].right); B=Math.max(B,boxes[i].bottom);
    }
    return {left:L-4, top:T-4, right:R+4, bottom:B+4};
  }
  function hit(a,r){
    return !(a.right<=r.left+1 || a.left>=r.right-1 || a.bottom<=r.top+1 || a.top>=r.bottom-1);
  }
  function reset(){
    for(var i=0;i<cleared.length;i++){
      cleared[i].classList.remove('nav-clear');
    }
    cleared=[];
  }
  function mark(el){
    if(!el || el.classList.contains('nav-clear')) return;
    el.classList.add('nav-clear');
    cleared.push(el);
  }
  function clear(){
    reset();
    var a=clusterRect();
    if(!a) return;
    var vw=d.documentElement.clientWidth || w.innerWidth;
    var gap=Math.ceil(vw-a.left);
    if(gap<=8) return;
    d.documentElement.style.setProperty('--nav-clear', gap+'px');
    var nodes=d.querySelectorAll(SEL), i, el, r, host;
    for(i=0;i<nodes.length;i++){
      el=nodes[i];
      if(el.closest('#navc') || el.closest('#thm') || el.closest('#tocbtn')) continue;
      r=el.getBoundingClientRect();
      if(r.width<4 || r.height<4) continue;
      if(r.bottom<0 || r.top>w.innerHeight || r.right<0 || r.left>w.innerWidth) continue;
      if(!hit(a,r)) continue;
      host=el.closest('table, figure, .t90viz, .mapx, .hx') || el;
      if(host.tagName==='TD' || host.tagName==='TH') host=host.closest('table')||host;
      mark(host);
    }
  }
  function show(){
    if(nav) nav.classList.remove('away');
    if(toc) toc.classList.remove('away');
    clear();
  }
  function hide(){
    if(nav && nav.classList.contains('open')) return;
    if(nav && d.activeElement && nav.contains(d.activeElement)) return;
    if(toc && d.activeElement===toc) return;
    if(nav) nav.classList.add('away');
    if(toc) toc.classList.add('away');
    reset();
  }
  function onScroll(){
    var y=w.scrollY, dy=y-lastY;
    if(y<48){ show(); lastY=y; acc=0; return; }
    if(dy>6){ acc=Math.max(0,acc+dy); if(acc>24) hide(); }
    else if(dy<-6){ acc=Math.min(0,acc+dy); if(acc<-12) show(); }
    lastY=y;
    w.clearTimeout(idle);
    idle=w.setTimeout(function(){ show(); }, 160);
  }
  w.addEventListener('scroll', function(){
    if(ticking) return;
    ticking=true;
    w.requestAnimationFrame(function(){ onScroll(); ticking=false; });
  }, {passive:true});
  w.addEventListener('resize', function(){ show(); }, {passive:true});
  if(nav) nav.addEventListener('click', show);
  if(toc) toc.addEventListener('click', show);
  d.addEventListener('keydown', function(e){ if(e.key==='Escape') show(); });
  if(d.readyState==='loading') d.addEventListener('DOMContentLoaded', show);
  else show();
  w.addEventListener('load', show);
})();
