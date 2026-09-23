const API = "/api";
function token(){ return localStorage.getItem("token"); }
function authHeaders(extra={}){ return {...extra, ...(token()?{"Authorization":"Bearer "+token()}: {})}; }

// FastAPI returns `detail` as a string for normal errors but as an ARRAY of objects for
// validation errors (422). Turn either into a readable sentence.
function errMsg(data, fallback="Request failed"){
  const d = data && data.detail;
  if(!d) return fallback;
  if(typeof d === "string") return d;
  if(Array.isArray(d)) return d.map(e=>{
    const field = Array.isArray(e.loc) ? e.loc.filter(x=>x!=="body").join(".") : "";
    const text = String(e.msg||"Invalid value").replace(/^Value error,\s*/i,"");
    return field ? `${field}: ${text}` : text;
  }).join("; ");
  return fallback;
}

function setMsg(el, text, ok=false){ el.textContent = text; el.classList.toggle("success", !!ok); }

function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]))}

async function api(path, options={}){
  const opts={...options,headers:authHeaders(options.headers||{})};
  let res;
  try{ res=await fetch(API+path,opts); }
  catch(e){ throw new Error("Cannot reach the server. Is the backend running?"); }
  let data={}; try{data=await res.json()}catch(e){}
  if(res.status===401){localStorage.removeItem("token"); location.href="/static/login.html"; throw new Error("Please login again");}
  if(!res.ok) throw new Error(errMsg(data));
  return data;
}
function requireAuth(){ if(!token()) location.href="/static/login.html"; }
function logout(){localStorage.removeItem("token");location.href="/static/login.html";}
document.addEventListener("click",e=>{if(e.target.id==="logout")logout()});
