/* t102：接近视口或空闲时预绘真实地图图层，切层只改透明度，避免点到「真实地图」时出现长任务 */
(function(){
  var ric=window.requestIdleCallback||function(f){return setTimeout(f,200)};
  function warm(x){
    if(!x || x.classList.contains('is-warm')) return;
    // 先加 class，让隐藏的真实图层改为 visibility:visible;opacity:0，才能真正预绘
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
  // 页面只有 1–2 张地图：空闲时全部预热，避免第一次滚动时脚本尚未就绪而错过相交
  ric(warmAll, {timeout:800});
  if(document.readyState==='complete') setTimeout(warmAll, 400);
  else addEventListener('load', function(){ setTimeout(warmAll, 400); });
})();
