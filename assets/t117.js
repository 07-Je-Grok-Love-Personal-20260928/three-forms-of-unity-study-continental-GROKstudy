/* t117: header TOC toggle (same drawer as #tocbtn) + dock dim on #nvdock */
(function(){
  var d=document, b=d.body, w=window;
  if(!b) return;
  function wide(){return w.innerWidth>=1100}
  function isOpen(){return wide()?!b.classList.contains('tochide'):b.classList.contains('tocopen')}
  function sync(){
    var on=isOpen();
    ['tocbtn','tocx','tochd'].forEach(function(id){
      var el=d.getElementById(id);
      if(!el) return;
      el.setAttribute('aria-expanded', on?'true':'false');
      el.setAttribute('aria-label', on?'隐藏目录':'显示目录');
      el.setAttribute('title', on?'隐藏目录':'显示目录');
    });
  }
  function tog(e){
    if(e){e.preventDefault()}
    if(wide()) b.classList.toggle('tochide');
    else b.classList.toggle('tocopen');
    sync();
  }
  var hd=d.getElementById('tochd');
  if(hd) hd.addEventListener('click', tog);
  ['tocbtn','tocx'].forEach(function(id){
    var el=d.getElementById(id);
    if(!el) return;
    el.addEventListener('click', function(){ setTimeout(sync, 0); });
  });
  w.addEventListener('resize', sync);
  try{
    new MutationObserver(sync).observe(b,{attributes:true,attributeFilter:['class']});
  }catch(e){}
  sync();

  var dock=d.getElementById('nvdock');
  var launch=d.getElementById('nvlaunch');
  if(dock){
    var idle=0, ticking=false;
    w.addEventListener('scroll', function(){
      if(ticking) return;
      ticking=true;
      w.requestAnimationFrame(function(){
        ticking=false;
        if(launch && launch.hasAttribute('open')){ dock.classList.remove('dim'); return; }
        if(w.scrollY>48) dock.classList.add('dim');
        else dock.classList.remove('dim');
        w.clearTimeout(idle);
        idle=w.setTimeout(function(){ dock.classList.remove('dim'); }, 180);
      });
    }, {passive:true});
  }
})();
