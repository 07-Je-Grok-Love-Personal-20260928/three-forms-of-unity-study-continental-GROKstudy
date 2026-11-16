/* t99：在空闲时记下概念图高度，切到真实地图时不再把下方整页重排 */
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
    ric(function(){
      all();
      addEventListener('resize', function(){ ric(all,{timeout:1200}); }, {passive:true});
    }, {timeout:1800});
  }
  if(document.readyState==='complete') start();
  else addEventListener('load', start);
})();
