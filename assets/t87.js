/* t87：主题切换 + 背诵版全部展开/收起 */
(function(){var d=document,de=d.documentElement,K='ui.theme',C={night:'#0b1110',navy:'#0a1020',paper:'#f3ead8',celadon:'#e8f0ea',wisteria:'#efeaf4',charcoal:'#161314'},AL={dawn:'paper',jade:'navy',grape:'wisteria',sakura:'wisteria',ocean:'navy',amber:'charcoal',eye:'celadon'};
var box=d.getElementById('thm'),btn=d.getElementById('thmb');
function cur(){return de.getAttribute('data-theme')||'night'}
function mark(){[].forEach.call(d.querySelectorAll('[data-theme-set]'),function(b){b.setAttribute('aria-checked',b.getAttribute('data-theme-set')===cur())})}
function ap(t){if(t==='night')de.removeAttribute('data-theme');else de.setAttribute('data-theme',t);var m=d.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',C[t]);mark()}function set(t){t=AL[t]||t;if(!C[t])t='night';try{localStorage.setItem(K,t)}catch(e){}var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;if(d.startViewTransition&&!rm){d.startViewTransition(function(){ap(t)})}else ap(t)}
if(box&&btn){btn.addEventListener('click',function(e){e.stopPropagation();var o=box.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
 [].forEach.call(d.querySelectorAll('[data-theme-set]'),function(b){b.addEventListener('click',function(){set(b.getAttribute('data-theme-set'));box.classList.remove('open');btn.setAttribute('aria-expanded','false')})});
 d.addEventListener('click',function(e){if(!box.contains(e.target)){box.classList.remove('open');btn.setAttribute('aria-expanded','false')}});
 d.addEventListener('keydown',function(e){if(e.key==='Escape'){box.classList.remove('open');btn.setAttribute('aria-expanded','false')}});mark()}
[].forEach.call(d.querySelectorAll('[data-rx]'),function(b){b.addEventListener('click',function(){var o=b.getAttribute('data-rx')==='open';[].forEach.call(d.querySelectorAll('details.rfx'),function(x){x.open=o})})});
})();
;(function(){var de=document.documentElement,K='ui.core';try{if(localStorage.getItem(K)==='1')de.classList.add('coreonly')}catch(x){}
function paint(){var on=de.classList.contains('coreonly');document.querySelectorAll('[data-coreonly]').forEach(function(b){b.setAttribute('aria-pressed',String(on));b.textContent=on?'只看核心：开':'只看核心：关'})}
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-coreonly]');if(!b)return;de.classList.toggle('coreonly');try{localStorage.setItem(K,de.classList.contains('coreonly')?'1':'0')}catch(x){}paint();b.scrollIntoView({block:'center'})});paint()})();
