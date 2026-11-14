/* t91：真实地图多源切换。本地 Natural Earth SVG 为默认；仅在用户点选在线源时才加载自托管 Leaflet（无 CDN）。超时则回到本地底图。 */
(function(){
var d=document, loaded=false, loading=null;
var SRC={
  osm:{name:'OpenStreetMap', attr:'© OpenStreetMap contributors', url:'https://tile.openstreetmap.org/{z}/{x}/{y}.png', sub:null, max:19},
  carto:{name:'CARTO Voyager', attr:'© OpenStreetMap contributors © CARTO', url:'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', sub:'abcd', max:20},
  'esri-img':{name:'Esri 卫星影像', attr:'Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community', url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', sub:null, max:19},
  'esri-topo':{name:'Esri 地形图', attr:'Tiles © Esri — Source: Esri, USGS, NOAA, and the GIS User Community', url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', sub:null, max:19},
  amap:{name:'高德地图', attr:'© 高德地图（公开瓦片，无站点密钥；若无法访问会自动回到本地底图）', url:'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', sub:'1234', max:18}
};
function ver(){
  var l=d.querySelector('link[href*="assets/t91.css"]');
  if(!l) return '';
  var m=l.getAttribute('href').match(/[?&]v=([^&]+)/);
  return m?'?v='+m[1]:'';
}
function loadL(cb, err){
  if(window.L){cb();return}
  if(loading){loading.push([cb,err]);return}
  loading=[[cb,err]];
  var q=ver();
  var css=d.createElement('link'); css.rel='stylesheet'; css.href='assets/leaflet/leaflet.css'+q;
  d.head.appendChild(css);
  var s=d.createElement('script'); s.src='assets/leaflet/leaflet.js'+q; s.async=true;
  s.onload=function(){loaded=true; var q2=loading; loading=null; q2.forEach(function(x){x[0]()});};
  s.onerror=function(){var q2=loading; loading=null; q2.forEach(function(x){x[1]&&x[1]('地图脚本载入失败，已回到本地底图')});};
  d.head.appendChild(s);
}
function st(root, msg, kind){
  var n=root.querySelector('.rm-st'); if(!n) return;
  n.textContent=msg; n.className='rm-st'+(kind?' '+kind:'');
}
function meta(root){
  var raw=root.getAttribute('data-rm'); if(!raw) return null;
  try{return JSON.parse(raw)}catch(e){return null}
}
function setSel(bar, id){
  bar.querySelectorAll('button[data-src]').forEach(function(b){
    var on=b.getAttribute('data-src')===id;
    b.setAttribute('aria-selected', on?'true':'false');
    b.classList.toggle('on', on);
  });
}
function localOn(root, show){
  var pic=root.querySelector('.rmw');
  var ol=root.querySelector('.rm-ol');
  if(pic) pic.hidden=!show;
  if(ol) ol.hidden=show;
  root.querySelectorAll('.rm-go, .rm-ctl').forEach(function(el){ el.hidden=!show; });
}
function destroy(root){
  if(root._t91map){try{root._t91map.remove()}catch(e){} root._t91map=null; root._t91layer=null; root._t91armed=false;}
  if(root._t91timer){clearTimeout(root._t91timer); root._t91timer=0;}
}
function armLeaflet(map, root, on){
  root._t91armed=on;
  if(on){ map.dragging.enable(); map.scrollWheelZoom.enable(); map.doubleClickZoom.enable(); if(map.tap) map.tap.enable(); }
  else { map.dragging.disable(); map.scrollWheelZoom.disable(); map.doubleClickZoom.disable(); if(map.tap) map.tap.disable(); }
}
function ensureMap(root, data, cb, err){
  loadL(function(){
    var box=root.querySelector('.rm-ol');
    if(!box){err&&err('找不到地图容器');return}
    box.hidden=false;
    if(root._t91map){cb(root._t91map);return}
    var b=data.bbox, bounds=[[b[2],b[0]],[b[3],b[1]]];
    var map=window.L.map(box,{
      attributionControl:true, zoomControl:true, scrollWheelZoom:false, dragging:false,
      doubleClickZoom:false, boxZoom:false, keyboard:false, zoomSnap:.25
    });
    map.fitBounds(bounds,{padding:[12,12], maxZoom:8, animate:false});
    data.markers.forEach(function(m){
      var ic=window.L.divIcon({className:'t91pin', html:'<b style="--c:'+m.c+'">'+m.i+'</b>', iconSize:[26,26], iconAnchor:[13,13]});
      var t=(m.n||'')+(m.en?(' / '+m.en):'')+(m.y?(' · '+m.y):'');
      window.L.marker([m.ll[1], m.ll[0]],{icon:ic, keyboard:true, title:t}).addTo(map).bindPopup(t);
    });
    root._t91map=map; root._t91armed=false;
    var arm=root.querySelector('.rm-ol-go');
    if(!arm){
      arm=d.createElement('button'); arm.type='button'; arm.className='rm-ol-go';
      arm.textContent='🔍 点按开启缩放 / 拖动';
      box.appendChild(arm);
    }
    arm.hidden=false;
    arm.onclick=function(ev){ev.preventDefault();ev.stopPropagation(); armLeaflet(map,root,true); arm.hidden=true; st(root,'已开启缩放与拖动。点按 ✕ 可恢复页面滚动。','ok');};
    cb(map);
    setTimeout(function(){map.invalidateSize()}, 60);
  }, err);
}
function useLocal(root, why){
  destroy(root);
  localOn(root, true);
  setSel(root.querySelector('.rm-src'), 'local');
  root.setAttribute('data-src','local');
  st(root, why||'当前：本地静态底图（Natural Earth 公有领域），无需网络，始终可用。', why?'err':'ok');
}
function useOnline(root, id){
  var data=meta(root), src=SRC[id];
  if(!data||!src){useLocal(root,'未知的地图源，已回到本地底图。');return}
  localOn(root,false);
  setSel(root.querySelector('.rm-src'), id);
  root.setAttribute('data-src',id);
  st(root,'正在载入 '+src.name+'… 若超过 8 秒无响应，将自动回到本地底图。','wait');
  if(root._t91timer) clearTimeout(root._t91timer);
  ensureMap(root, data, function(map){
    if(root._t91layer){try{map.removeLayer(root._t91layer)}catch(e){}}
    var opts={attribution:src.attr, maxZoom:src.max, crossOrigin:true};
    if(src.sub) opts.subdomains=src.sub;
    var layer=window.L.tileLayer(src.url, opts);
    var ok=0;
    layer.on('tileload', function(){ ok++; if(ok===1){ if(root._t91timer){clearTimeout(root._t91timer);root._t91timer=0;} st(root,'当前：'+src.name+'（点击才载入；'+src.attr+'）。网络不稳时可改回本地底图。','ok'); }});
    layer.on('tileerror', function(){ /* wait for timeout or a later success */ });
    layer.addTo(map);
    root._t91layer=layer;
    map.invalidateSize();
    root._t91timer=setTimeout(function(){
      root._t91timer=0;
      if(ok===0) useLocal(root, src.name+' 超时未载入瓦片，已回到本地底图。可再试其他源，或检查网络。');
    }, 8000);
  }, function(msg){ useLocal(root, msg); });
}
d.addEventListener('click', function(e){
  var b=e.target.closest && e.target.closest('.rm-src button[data-src]');
  if(!b) return;
  e.preventDefault();
  var root=b.closest('.rmap'); if(!root) return;
  var id=b.getAttribute('data-src');
  if(id==='local' || id===root.getAttribute('data-src')){
    if(id==='local') useLocal(root);
    return;
  }
  useOnline(root, id);
});
})();
