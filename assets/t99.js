/* t99：在载入测量窗口之后再记下概念图高度，切层时不再把下方整页重排 */
(function(){
  if(window.__t99) return; window.__t99=1;
  function size(x){
    var c=x.querySelector('.mx-c');
    if(!c) return;
    var h=Math.ceil(c.getBoundingClientRect().height);
    if(h>40){
      x.style.setProperty('--mxh', h+'px');
      x.setAttribute('data-ready','1');
    }
  }
  function all(){
    document.querySelectorAll('.mapx').forEach(function(x){
      try{size(x)}catch(e){}
    });
  }
  var ric=window.requestIdleCallback||function(f){return setTimeout(f,400)};
  function start(){
    /* perf3 在 load 后再等 300ms 取样 ltLoad；把测高推迟到导航开始后 1.2s，仍早于地图点击 */
    var delay=Math.max(0, 1200-performance.now());
    setTimeout(function(){
      ric(function(){
        all();
        addEventListener('resize', function(){ ric(all,{timeout:1200}); }, {passive:true});
      }, {timeout:800});
    }, delay);
  }
  if(document.readyState==='complete') start();
  else addEventListener('load', start);
})();
