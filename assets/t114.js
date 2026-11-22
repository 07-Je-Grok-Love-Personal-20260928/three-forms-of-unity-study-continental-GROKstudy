/* t114: migrate stored themes; hideable top section tabs */
(function(){
  var AL={dawn:'paper',jade:'dim',grape:'mono',sakura:'mono',ocean:'dim',amber:'lights',eye:'warm',navy:'dim',celadon:'warm',wisteria:'mono',charcoal:'lights'};
  var OK={night:1,lights:1,dim:1,paper:1,warm:1,mono:1};
  var META={night:'#0f1011',lights:'#000000',dim:'#15202b',paper:'#f0f2f5',warm:'#fbfbfa',mono:'#ffffff'};
  try{
    var t=localStorage.getItem('ui.theme');
    var n=AL[t]||(OK[t]?t:'night');
    if(n!==t){localStorage.setItem('ui.theme',n);t=n;
      var de=document.documentElement;
      if(t==='night')de.removeAttribute('data-theme');else de.setAttribute('data-theme',t);
      var m=document.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',META[t]);
    }
  }catch(e){}
})();
(function(){
  var d=document, wrap=d.getElementById('ptabwrap'), line=d.getElementById('ptabline');
  if(!wrap||!line)return;
  var tog=wrap.querySelector('.ptab-tog');
  var hair=line.querySelector('.ptab-hair');
  var handle=line.querySelector('.ptab-handle');
  var K='ui.ptabs';
  var peek=false, lastY=0;
  function pref(){try{return localStorage.getItem(K)||'on'}catch(e){return 'on'}}
  function save(v){try{localStorage.setItem(K,v)}catch(e){}}
  function hidden(){return wrap.classList.contains('is-hide')}
  function show(){
    wrap.classList.remove('is-hide');
    wrap.setAttribute('aria-hidden','false');
    line.setAttribute('aria-hidden','true');
    if(tog){tog.setAttribute('aria-expanded','true');tog.setAttribute('title','隐藏顶栏目录');tog.setAttribute('aria-label','隐藏顶栏目录')}
  }
  function hide(){
    wrap.classList.add('is-hide');
    wrap.setAttribute('aria-hidden','true');
    line.setAttribute('aria-hidden','false');
    if(tog){tog.setAttribute('aria-expanded','false');tog.setAttribute('title','显示顶栏目录');tog.setAttribute('aria-label','显示顶栏目录')}
  }
  function atTop(){return (window.scrollY||document.documentElement.scrollTop||0)<24}
  function sync(){
    var y=window.scrollY||document.documentElement.scrollTop||0;
    var p=pref();
    if(p==='on' && !peek) show();
    else if(atTop()) show();
    else if(peek) show();
    else hide();
    lastY=y;
  }
  function onScroll(){
    var y=window.scrollY||document.documentElement.scrollTop||0;
    if(y<24){peek=false;show()}
    else if(pref()==='on'){peek=false;show()}
    else if(y>lastY+6 && y>48){peek=false;hide()}
    lastY=y;
  }
  function reveal(){peek=true;show()}
  function toggle(){
    if(pref()==='on'){save('off');peek=false;if(!atTop())hide();else show()}
    else{save('on');peek=false;show()}
  }
  if(tog)tog.addEventListener('click',function(e){e.preventDefault();toggle()});
  if(hair)hair.addEventListener('click',function(e){e.preventDefault();if(pref()==='off'){save('on')}peek=false;show()});
  if(handle)handle.addEventListener('click',function(e){e.preventDefault();if(pref()==='off'){save('on')}peek=false;show()});
  window.addEventListener('scroll',onScroll,{passive:true});
  sync();
})();
