// NOTE: use getElementById, not bare globals. `name` is window.name (a string), so a bare
// `name.value` is undefined and the registration request was sent without a name.
const $ = id => document.getElementById(id);
const form = document.querySelector("form");

async function postJSON(url, body){
  let res;
  try{
    res = await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  }catch(e){ throw new Error("Cannot reach the server. Is the backend running?"); }
  let data={}; try{ data = await res.json(); }catch(e){}
  if(!res.ok) throw new Error(errMsg(data));
  return data;
}

if(form?.id==="loginForm"){
  // Arriving here right after registering: show a confirmation.
  if(new URLSearchParams(location.search).get("registered")==="1"){
    setMsg($("msg"),"Account created successfully. Please log in.",true);
    $("email").focus();
  }
  form.addEventListener("submit",async e=>{
    e.preventDefault(); setMsg($("msg"),"");
    const btn=form.querySelector("button"); btn.disabled=true;
    try{
      const x=await postJSON("/api/auth/login",{email:$("email").value.trim(),password:$("password").value});
      localStorage.setItem("token",x.access_token);
      location.href="/static/dashboard.html";
    }catch(err){ setMsg($("msg"),err.message); btn.disabled=false; }
  });
}

if(form?.id==="registerForm"){
  form.addEventListener("submit",async e=>{
    e.preventDefault(); setMsg($("msg"),"");
    const btn=form.querySelector("button"); btn.disabled=true;
    try{
      await postJSON("/api/auth/register",{
        name:$("name").value.trim(),
        email:$("email").value.trim(),
        password:$("password").value
      });
      // Success -> go to the login page.
      location.href="/static/login.html?registered=1";
    }catch(err){ setMsg($("msg"),err.message); btn.disabled=false; }
  });
}
