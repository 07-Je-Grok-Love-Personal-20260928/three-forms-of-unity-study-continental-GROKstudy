/* t102：接近视口的地图解除 content-visibility 跳过，并预绘真实图层，避免切到「真实地图」时出现长任务 */
(function(){
  var ric=window.requestIdleCallback||function(f){return setTimeout(f,200)};
  function warm(x){
    if(!x || x.classList.contains('is-warm')) return;
    var im=x.querySelector('.mx-r img');
    function go(){ x.classList.add('is-warm'); }
    if(im){
      im.loading='eager';
      if(im.decode){ im.decode().then(go).catch(go); }
      else if(im.complete) go();
      else im.addEventListener('load', go, {once:true});
    } else go();
  }
  if(!('IntersectionObserver' in window)) return;
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      io.unobserve(e.target);
      ric(function(){ warm(e.target); }, {timeout:1500});
    });
  }, {rootMargin:'1400px 0px'});
  document.querySelectorAll('.mapx').forEach(function(x){ io.observe(x); });
})();
