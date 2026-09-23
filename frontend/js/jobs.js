requireAuth();
let editing=null;
let jobsById={};
const $=id=>document.getElementById(id);

async function load(){
 try{
  const jobs=await api("/jobs");
  jobsById=Object.fromEntries(jobs.map(j=>[j.id,j]));
  // Buttons carry only the numeric id (no JSON in an inline handler), so quotes/apostrophes
  // in a job description can no longer break the Edit button or inject markup.
  $("jobs").innerHTML=jobs.map(j=>`
  <div class="job-card"><h3>${esc(j.title)}</h3><p>${esc(j.description||"No description")}</p><p><b>Required:</b> ${esc(j.required_skills||"None")}</p><p><b>Preferred:</b> ${esc(j.preferred_skills||"None")}</p><div class="job-actions"><button class="btn small" data-action="edit" data-id="${j.id}">Edit</button><button class="btn small danger" data-action="delete" data-id="${j.id}">Delete</button></div></div>`).join("")||'<p class="muted">No roles yet.</p>';
 }catch(e){setMsg($("msg"),e.message)}
}

$("jobs").addEventListener("click",e=>{
 const b=e.target.closest("button[data-action]");if(!b)return;
 const id=Number(b.dataset.id);
 if(b.dataset.action==="edit")editJob(jobsById[id]);
 if(b.dataset.action==="delete")delJob(id);
});

$("jobForm").addEventListener("submit",async e=>{
 e.preventDefault();
 const body={title:$("title").value,description:$("description").value,required_skills:$("required").value,preferred_skills:$("preferred").value,minimum_experience:Number($("experience").value||0),education:$("education").value};
 const opts={headers:{"Content-Type":"application/json"},body:JSON.stringify(body)};
 try{
  if(editing)await api(`/jobs/${editing}`,{method:"PUT",...opts});else await api("/jobs",{method:"POST",...opts});
  reset();setMsg($("msg"),"Saved.",true);load();
 }catch(err){setMsg($("msg"),err.message)}
});

function editJob(j){if(!j)return;editing=j.id;$("jobId").value=j.id;$("title").value=j.title;$("description").value=j.description;$("required").value=j.required_skills;$("preferred").value=j.preferred_skills;$("experience").value=j.minimum_experience;$("education").value=j.education;$("cancelEdit").classList.remove("hidden");$("formTitle").textContent="Edit job role";setMsg($("msg"),"");scrollTo({top:0,behavior:"smooth"})}
$("cancelEdit").onclick=()=>{reset();setMsg($("msg"),"")};
function reset(){editing=null;$("jobForm").reset();$("experience").value=0;$("cancelEdit").classList.add("hidden");$("formTitle").textContent="Add a job role"}
async function delJob(id){if(confirm("Delete this job role?")){try{await api(`/jobs/${id}`,{method:"DELETE"});load()}catch(e){setMsg($("msg"),e.message)}}}
load();
