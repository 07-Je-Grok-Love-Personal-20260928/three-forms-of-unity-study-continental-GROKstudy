/* t100：统一右下导航簇——历史回退/前进、平滑到顶到底、不可用态；不在载入时测布局 */
(function(){
var d=document,w=window,n=d.getElementById('navc');
if(!n) return;
var back=n.querySelector('[data-nv=back]');
var fwd=n.querySelector('[data-nv=fwd]');
var DK='t100.depth', FK='t100.canFwd';
function sameRef(){
  try{
    if(!d.referrer) return false;
    return new URL(d.referrer).origin===location.origin;
  }catch(e){return false}
}
function typ(){
  try{var e=performance.getEntriesByType('navigation')[0];return e&&e.type||''}catch(e){return ''}
}
function depth(){try{return +(sessionStorage.getItem(DK)||0)}catch(e){return 0}}
function setD(v){try{sessionStorage.setItem(DK,String(Math.max(0,v)))}catch(e){}}
function canFwd(){try{return sessionStorage.getItem(FK)==='1'}catch(e){return false}}
function setF(on){try{on?sessionStorage.setItem(FK,'1'):sessionStorage.removeItem(FK)}catch(e){}}
function atHome(){return /(^|\/)(index\.html)?$/.test(location.pathname)}
function canBack(){return depth()>0||sameRef()}
var t=typ();
if(t==='navigate'){
  if(sameRef()) setD(depth()+1); else setD(0);
  setF(false);
}else if(t==='back_forward'){
  setF(true);
}
function paint(){
  var cb=canBack();
  if(back){
    var useHome=!cb&&!atHome();
    var on=cb||useHome;
    back.disabled=!on;
    back.setAttribute('aria-disabled',on?'false':'true');
    back.title=cb?'后退':(useHome?'返回首页':'后退（没有上一步）');
    back.setAttribute('aria-label',back.title);
  }
  if(fwd){
    var cf=canFwd();
    fwd.disabled=!cf;
    fwd.setAttribute('aria-disabled',cf?'false':'true');
    fwd.title=cf?'前进':'前进（没有下一步）';
    fwd.setAttribute('aria-label',fwd.title);
  }
}
paint();
function smooth(){return (w.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)?'auto':'smooth'}
n.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('[data-nv]');
  if(!b||!n.contains(b)) return;
  var v=b.getAttribute('data-nv');
  if(v==='back'){
    e.preventDefault();e.stopPropagation();
    if(b.disabled) return;
    if(canBack()){setD(depth()-1);setF(true);history.back()}
    else location.href='index.html';
  }else if(v==='fwd'){
    e.preventDefault();e.stopPropagation();
    if(b.disabled) return;
    setD(depth()+1);setF(false);history.forward();
  }else if(v==='top'){
    e.preventDefault();e.stopPropagation();
    w.scrollTo({top:0,behavior:smooth()});
  }else if(v==='bot'){
    e.preventDefault();e.stopPropagation();
    w.scrollTo({top:d.documentElement.scrollHeight,behavior:smooth()});
  }
},true);
w.addEventListener('popstate',paint);
})();
