/* t118: hairline class on #ptabrow; keep #tocx label in sync when #tochd toggles the drawer */
(function(){
  var d=document, row=d.getElementById('ptabrow'), wrap=d.getElementById('ptabwrap'), b=d.body, w=window;
  if(!b) return;
  function wide(){return w.innerWidth>=1100}
  function syncHair(){
    if(!row||!wrap) return;
    row.classList.toggle('is-hair', wrap.classList.contains('is-hide'));
  }
  function syncX(){
    var x=d.getElementById('tocx'); if(!x) return;
    var hid=wide()?b.classList.contains('tochide'):!b.classList.contains('tocopen');
    x.textContent=hid?'目录':'✕';
    x.setAttribute('aria-label', hid?'显示目录':'隐藏目录');
    x.setAttribute('title', hid?'显示目录':'隐藏目录');
  }
  function sync(){ syncHair(); syncX(); }
  sync();
  try{ if(wrap) new MutationObserver(syncHair).observe(wrap,{attributes:true,attributeFilter:['class']}); }catch(e){}
  try{ new MutationObserver(syncX).observe(b,{attributes:true,attributeFilter:['class']}); }catch(e){}
  w.addEventListener('resize', syncX);
})();
