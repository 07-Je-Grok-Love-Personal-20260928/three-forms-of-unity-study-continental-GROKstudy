/* t112: ⋯ launcher — open/close, keep the popover on screen, dim while scrolling. */
(function(){
  var d=document, w=window;
  var root=d.getElementById('nvlaunch');
  if(!root) return;
  var sum=d.getElementById('nvsum') || root.querySelector('summary');
  var pop=d.getElementById('nvpop') || root.querySelector('.nvlaunch-pop');
  var idle=0, ticking=false;

  function open(){ return root.hasAttribute('open'); }
  function setExp(){
    if(sum) sum.setAttribute('aria-expanded', open()?'true':'false');
  }
  function close(){
    if(open()) root.removeAttribute('open');
    var thm=d.getElementById('thm'), btn=d.getElementById('thmb');
    if(thm) thm.classList.remove('open');
    if(btn) btn.setAttribute('aria-expanded','false');
    setExp();
  }
  function pin(){
    if(!pop || !open()) return;
    pop.style.top='';
    pop.style.bottom='';
    pop.style.right='';
    pop.style.left='';
    pop.style.maxHeight='';
    var r=pop.getBoundingClientRect();
    var vw=d.documentElement.clientWidth || w.innerWidth;
    var vh=d.documentElement.clientHeight || w.innerHeight;
    if(r.right>vw-4) pop.style.right='0px';
    if(r.left<4) pop.style.left='0px';
    if(r.top<4){
      pop.style.bottom='auto';
      pop.style.top='4px';
      pop.style.maxHeight=(vh-12)+'px';
    }else if(r.bottom>vh-4){
      pop.style.maxHeight=Math.max(120, vh-r.top-8)+'px';
    }
  }

  root.addEventListener('toggle', function(){ setExp(); if(open()){ pin(); }});
  setExp();

  d.addEventListener('click', function(e){
    if(!open()) return;
    if(root.contains(e.target)) return;
    close();
  });
  d.addEventListener('keydown', function(e){
    if(e.key==='Escape' && open()){
      close();
      if(sum) sum.focus();
    }
  });

  // Close after a chosen action (theme pick, nav, TOC). Let the action run first.
  root.addEventListener('click', function(e){
    var t=e.target.closest && e.target.closest('a, button');
    if(!t || t===sum) return;
    if(t.id==='thmb') return;           // opens the theme list
    if(t.closest && t.closest('#thmm') && t.getAttribute('data-theme-set')){
      setTimeout(close, 0);
      return;
    }
    if(t.id==='tocbtn' || t.getAttribute('data-nv') || (t.tagName==='A' && t.getAttribute('href'))){
      setTimeout(close, 0);
    }
  });

  w.addEventListener('resize', function(){ if(open()) pin(); }, {passive:true});

  w.addEventListener('scroll', function(){
    if(ticking) return;
    ticking=true;
    w.requestAnimationFrame(function(){
      ticking=false;
      if(open()){ pin(); root.classList.remove('dim'); return; }
      if(w.scrollY>48) root.classList.add('dim');
      else root.classList.remove('dim');
      w.clearTimeout(idle);
      idle=w.setTimeout(function(){ root.classList.remove('dim'); }, 180);
    });
  }, {passive:true});
})();
