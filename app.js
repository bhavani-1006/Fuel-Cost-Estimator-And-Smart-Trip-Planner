let lastEstimate=null,voices=[];
const form=document.getElementById('tripForm');
const money=n=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:2}).format(n);
const vehicleNames={car:'Car',bus:'Bus',bike:'Bike'};
const defaults={car:{mileage:15,price:105,unit:'km/L'},bus:{mileage:4,price:90,unit:'km/L'},bike:{mileage:40,price:105,unit:'km/L'}};
function loadVoices(){voices=window.speechSynthesis?window.speechSynthesis.getVoices():[]}
if('speechSynthesis'in window){loadVoices();speechSynthesis.onvoiceschanged=loadVoices}
function fmtDuration(m){const h=Math.floor(m/60),mins=m%60;return h?`${h} hr ${mins} min`:`${mins} min`}
function selectedVehicle(){return form.elements.vehicle_type.value}
function updateVehicleDefaults(){const p=defaults[selectedVehicle()];document.getElementById('mileageInput').value=p.mileage;document.getElementById('mileageUnit').textContent=p.unit}
document.querySelectorAll('input[name="vehicle_type"]').forEach(el=>el.addEventListener('change',updateVehicleDefaults));
if(form){
 updateVehicleDefaults();
 form.addEventListener('submit',async e=>{
  e.preventDefault();const status=document.getElementById('status'),origin=form.elements.origin.value.trim(),destination=form.elements.destination.value.trim(),vehicle=selectedVehicle(),travelers=Number(form.elements.travelers.value),mileage=Number(form.elements.mileage.value);
  if(!origin||!destination){status.textContent='Please enter a starting point and destination.';return}
  if(!(mileage>0)){status.textContent='Enter mileage greater than zero.';return}if(!(travelers>=1&&travelers<=100)){status.textContent='Enter passengers between 1 and 100.';return}
  status.textContent='Finding your route and estimating your trip…';const button=form.querySelector('button[type="submit"]');button.disabled=true;
  try{
   const res=await fetch('/api/route-estimate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({origin,destination,vehicle_type:vehicle,trip_direction:'one-way',travelers,mileage,save_trip:form.elements.save_trip.checked})});
   const r=await res.json();if(!res.ok)throw Error(r.error||'Could not find this route.');
   lastEstimate={...r,origin,destination,vehicle_type:vehicle,travelers};
   document.getElementById('routeTitle').textContent=`${origin} → ${destination}`;document.getElementById('totalCost').textContent=money(r.fuel_cost);
   document.getElementById('costLabel').textContent=vehicle==='bus'?'Estimated bus fuel cost (not ticket fare)':'Estimated fuel cost';
   document.getElementById('distance').textContent=Number(r.distance_km).toLocaleString('en-IN')+' km';document.getElementById('fuelLiters').textContent=Number(r.fuel_liters).toFixed(2)+' L';
   document.getElementById('duration').textContent=fmtDuration(r.duration_minutes);document.getElementById('fuelPriceUsed').textContent=money(r.fuel_price)+' / L';document.getElementById('selectedRide').textContent=vehicleNames[vehicle];
   const q1=encodeURIComponent(origin),q2=encodeURIComponent(destination),map=document.getElementById('routeMap'),mode=vehicle==='bike'?'bicycling':'driving';
   map.src=`https://maps.google.com/maps?output=embed&saddr=${q1}&daddr=${q2}&dirflg=${mode==='transit'?'r':mode==='bicycling'?'b':'d'}`;
   document.getElementById('openMaps').href=`https://www.google.com/maps/dir/?api=1&origin=${q1}&destination=${q2}&travelmode=${mode}`;
   status.textContent=`Route ready for your ${vehicleNames[vehicle].toLowerCase()}.${r.saved_trip_id?' Trip saved to history.':''}`;document.getElementById('mapSection').scrollIntoView({behavior:'smooth',block:'start'});
  }catch(err){status.textContent=err.message}finally{button.disabled=false}
 });
 form.addEventListener('reset',()=>setTimeout(()=>{document.getElementById('status').textContent='';document.getElementById('routeMap').src='https://maps.google.com/maps?q=India&output=embed';document.getElementById('openMaps').href='https://www.google.com/maps';document.getElementById('totalCost').textContent='₹—';document.getElementById('distance').textContent='— km';document.getElementById('fuelLiters').textContent='—';document.getElementById('duration').textContent='—';document.getElementById('fuelPriceUsed').textContent='₹— / L';document.getElementById('routeTitle').textContent='Your route will appear here';document.getElementById('selectedRide').textContent='Car';document.getElementById('costLabel').textContent='Estimated fuel cost';lastEstimate=null;updateVehicleDefaults()},0));
}
const voice=document.getElementById('voiceBtn');
if(voice)voice.addEventListener('click',()=>{const R=window.SpeechRecognition||window.webkitSpeechRecognition;if(!R){document.getElementById('status').textContent='Voice input is not supported in this browser. Type the two places instead.';return}const rec=new R();rec.lang='en-IN';rec.continuous=false;rec.interimResults=false;rec.onresult=e=>{const spoken=e.results[0][0].transcript,match=spoken.match(/(.+?)\s+(?:to|towards|until|up to)\s+(.+)/i);if(match){form.elements.origin.value=match[1].trim();form.elements.destination.value=match[2].trim();document.getElementById('status').textContent=`Heard: ${match[1]} to ${match[2]}. Press Show route & estimate.`}else document.getElementById('status').textContent=`Heard “${spoken}”. Say “Hyderabad to Vijayawada” or type the places.`};rec.onerror=()=>document.getElementById('status').textContent='Voice input failed. Allow microphone access, or type the places.';rec.start()});
const speak=document.getElementById('speakBtn');
if(speak)speak.addEventListener('click',()=>{if(!lastEstimate){document.getElementById('status').textContent='Find a route first, then I can read your estimate.';return}if(!('speechSynthesis'in window)){document.getElementById('status').textContent='Speech output is not supported in this browser.';return}speechSynthesis.cancel();const r=lastEstimate,style=document.getElementById('voiceStyle').value,vehicle=vehicleNames[r.vehicle_type];let message;if(style==='rap')message=`TripWise on the track. ${vehicle} ride from ${r.origin} to ${r.destination}. ${r.distance_km} kilometres, keep it in sight. Estimated fuel cost ${Math.round(r.fuel_cost)} rupees. Plan that ride, keep your budget right. Drive safe, arrive right.`;else if(style==='boss')message=`Route confirmed. ${vehicle} from ${r.origin} to ${r.destination}. Distance ${r.distance_km} kilometres. Estimated time ${fmtDuration(r.duration_minutes)}. Estimated fuel cost ${Math.round(r.fuel_cost)} rupees. Travel smart.`;else message=`Your ${vehicle.toLowerCase()} trip is from ${r.origin} to ${r.destination}. Distance ${r.distance_km} kilometres. Estimated travel time ${fmtDuration(r.duration_minutes)}. Estimated fuel cost ${Math.round(r.fuel_cost)} rupees. This is an estimate, not a guaranteed fare. Travel safely.`;const u=new SpeechSynthesisUtterance(message);u.lang='en-IN';u.rate=style==='rap'?1.08:style==='boss'?.92:1;u.pitch=style==='boss'?.82:style==='rap'?1.12:1;const preferred=voices.find(v=>/en-IN/i.test(v.lang))||voices.find(v=>/^en/i.test(v.lang));if(preferred)u.voice=preferred;speechSynthesis.speak(u)});

// Installable web app: Android/desktop browsers may show a native install prompt.
let deferredInstallPrompt=null;
const installAppBtn=document.getElementById('installAppBtn');
window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();deferredInstallPrompt=event;if(installAppBtn)installAppBtn.textContent='⬇ Download App';});
if(installAppBtn){installAppBtn.addEventListener('click',async()=>{if(deferredInstallPrompt){deferredInstallPrompt.prompt();await deferredInstallPrompt.userChoice;deferredInstallPrompt=null;return;}const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent);const status=document.getElementById('status');if(isIOS){alert('To install TripWise on iPhone: tap the Share button in Safari, then choose “Add to Home Screen”.');}else{alert('To install TripWise, open this website using Chrome or Edge over HTTPS, then choose “Install app” from the browser menu. The app must be hosted online for installation on your phone.');}});}
if('serviceWorker' in navigator && location.protocol!=='file:'){window.addEventListener('load',()=>navigator.serviceWorker.register('/service-worker.js').catch(()=>{}));}
