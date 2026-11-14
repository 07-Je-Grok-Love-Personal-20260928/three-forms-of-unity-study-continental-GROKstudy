/* t93：手机导航滚动下藏、上滚或点按再显示；不挡正文 */
(function(){
var d=document, w=window, n=d.getElementById('navc');
if(!n) return;
var last=w.scrollY, acc=0, ticking=false;
function phone(){return w.innerWidth<=700}
function show(){n.classList.remove('away')}
function hide(){if(n.classList.contains('open'))return; if(d.activeElement&&n.contains(d.activeElement))return; n.classList.add('away')}
function onScroll(){
  if(!phone()){show();return}
  var y=w.scrollY, dy=y-last;
  if(y<48){show(); last=y; return}
  if(dy>6){acc=Math.max(0,acc+dy); if(acc>24) hide()}
  else if(dy<-6){acc=Math.min(0,acc+dy); if(acc<-12) show()}
  last=y;
}
w.addEventListener('scroll',function(){
  if(ticking) return;
  ticking=true;
  w.requestAnimationFrame(function(){onScroll(); ticking=false});
},{passive:true});
w.addEventListener('resize',function(){if(!phone())show()},{passive:true});
n.addEventListener('click',function(){show()});
d.addEventListener('keydown',function(e){if(e.key==='Escape') show()});
if(phone() && w.scrollY>80) hide();
})();
