/* t97：把 t87–t94 错开到独立短任务再执行，避免和 app.js 挤成一次 >50ms 的长任务 */
(function(){
  var me=document.currentScript;
  var chain=(me && me.getAttribute('data-chain')) || 't87,t89,t90,t91,t93,t94';
  var ver='';
  var src=me && me.src || '';
  var q=src.indexOf('?v=');
  if(q>=0) ver=src.slice(q);
  var files=chain.split(',').map(function(s){return s.trim()}).filter(Boolean);
  function loadNext(){
    if(!files.length) return;
    var n=files.shift();
    var s=document.createElement('script');
    s.src='assets/'+n+'.js'+ver;
    s.onload=function(){ setTimeout(loadNext,0); };
    s.onerror=function(){ setTimeout(loadNext,0); };
    (document.body||document.documentElement).appendChild(s);
  }
  function start(){
    if(window.__t97chain) return;
    window.__t97chain=1;
    setTimeout(loadNext,0);
  }
  if(document.readyState==='complete') start();
  else addEventListener('load', start);
})();
