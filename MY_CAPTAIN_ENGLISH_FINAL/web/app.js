let dashboard={};
let currentLessonId=null;
let currentStepIndex=0;

const content=document.getElementById("content");
const title=document.getElementById("pageTitle");

async function get(url){
  const r=await fetch(url);
  return r.json();
}

function speak(text){
  if(!text)return;
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang="en-US";
  u.rate=.82;
  speechSynthesis.speak(u);
}

function setStats(){
  const p=dashboard.progress||{};
  const xp=Number(p.XP||0), streak=Number(p.STREAK_DAYS||0);
  document.getElementById("topXP").textContent=xp;
  document.getElementById("sideXP").textContent=xp+" XP";
  document.getElementById("topStreak").textContent=streak;
  document.getElementById("sideStreak").textContent=streak;
  document.getElementById("sideLevel").textContent=(dashboard.level?.LEVEL_NAME||"A1 - Beginner");
  const done=Number(p.LESSONS_DONE||0), total=Math.max(Number(dashboard.lessons_count||1),1);
  const pct=Math.min(100,Math.round(done/total*100));
  document.getElementById("sidePercent").textContent=pct+"%";
}

function card(title,text,icon="📘"){
  return `<div class="card lesson-card"><div class="icon">${icon}</div><h3>${title}</h3><p class="muted">${text||""}</p></div>`;
}

async function home(){
  title.textContent="Головна";
  content.innerHTML=`<div class="hero"><div><div class="muted">MY CAPTAIN ENGLISH</div><h2>Твій шлях до англійської A1</h2><p class="muted">Правильна вимова → слова → фрази → граматика → слухання → говоріння → повторення.</p></div><button class="primary" onclick="openFirstLesson()">Почати урок →</button></div>
  <div class="grid">
  ${card("Правильна вимова","Починаємо з основних звуків та правильної вимови.","🔊")}
  ${card("Нові слова",`${dashboard.words_count||0} слів у базі.`,"🧠")}
  ${card("Фрази",`${dashboard.phrases_count||0} готових фраз.`,"💬")}
  ${card("Граматика",`${dashboard.grammar_count||0} граматичних блоків.`,"📖")}
  ${card("Слухання","Слухай, розумій і перевіряй себе.","🎧")}
  ${card("Говоріння","Тренуй реальні ситуації.","🗣️")}
  </div>`;
}

async function openFirstLesson(){
  const lessons=await get("/api/lessons");
  const l=lessons.find(x=>String(x.ACTIVE).toUpperCase()!=="NO")||lessons[0];
  if(l) openLesson(l.LESSON_ID);
}

async function lessons(){
  title.textContent="Уроки";
  const data=await get("/api/lessons");
  content.innerHTML=`<div class="hero"><div><h2>Уроки A1</h2><p class="muted">Уроки побудовані поступово — від правильної вимови до реального діалогу.</p></div></div><div class="grid">${data.map((l,i)=>`<div class="card lesson-card" onclick="openLesson('${l.LESSON_ID}')"><div class="icon">${i===0?"🔊":"📚"}</div><h3>Урок ${l.LESSON_NO||i+1}: ${l.TITLE||""}</h3><p class="muted">${l.TOPIC||""}</p><small>${l.EST_MINUTES||15} хв</small></div>`).join("")}</div>`;
}

async function openLesson(id, stepIndex=0){
  const d=await get("/api/lesson/"+id);
  if(!d.ok){
    content.innerHTML=`<div class="empty">${d.error}</div>`;
    return;
  }
  currentLessonId=id;
  currentStepIndex=Math.max(0, Math.min(stepIndex,(d.steps||[]).length-1));
  renderLesson(d);
}

function renderLesson(d){
  const steps=d.steps||[];
  const labels=["Вимова","Слова","Фрази","Граматика","Слухання","Говоріння","Повторення"];
  const step=steps[currentStepIndex]||{};
  const label=labels[currentStepIndex]||"Навчання";

  title.textContent=d.lesson.TITLE||"Урок";

  const question=step.QUESTION||step.CORRECT_ANSWER||"Hello";
  const answer=step.CORRECT_ANSWER||"";

  content.innerHTML=`
  <div class="steps">
    ${labels.map((x,i)=>`<div class="step ${i===currentStepIndex?"active":""}" onclick="openLesson(currentLessonId,${i})" style="cursor:pointer">
      <div class="circle">${i+1}</div><small>${x}</small>
    </div>`).join("")}
  </div>
  <div class="lesson-layout">
    <div class="card">
      <h2>${currentStepIndex+1}. ${label}</h2>
      <div class="word">
        <h2>${question}</h2>
        <div class="ipa">${answer}</div>
        <button class="speak" onclick="speak('${String(question).replaceAll("'","\\'")}')">🔊</button>
        <p class="muted">Прослухай матеріал та повтори його вголос.</p>
      </div>
      <div class="tip">💡 Порада: спочатку слухай, потім повторюй повільно.</div>
      <div class="actions">
        <button class="secondary" onclick="lessons()">← Назад</button>
        <button class="primary" onclick="nextLessonStep()">${currentStepIndex < steps.length-1 ? "Далі →" : "Завершити урок ✓"}</button>
      </div>
    </div>
    <div class="card">
      <h2>Навігація уроку</h2>
      ${labels.map((x,i)=>`<div class="row" onclick="openLesson(currentLessonId,${i})" style="cursor:pointer">
        <span>${i+1}. ${x}</span>
        <span>${i===currentStepIndex?"●":"○"}</span>
      </div>`).join("")}
    </div>
  </div>`;
}

async function nextLessonStep(){
  const d=await get("/api/lesson/"+currentLessonId);
  if(!d.ok)return;

  const steps=d.steps||[];

  if(currentStepIndex < steps.length-1){
    currentStepIndex++;
    renderLesson(d);
    window.scrollTo({top:0,behavior:"smooth"});
    return;
  }

  await fetch("/api/activity",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({USER_ID:"LOCAL_USER",LESSONS_DONE:1,XP:20})
  });

  dashboard=await get("/api/dashboard");
  setStats();

  content.innerHTML=`
    <div class="hero">
      <div>
        <div class="muted">УРОК ЗАВЕРШЕНО</div>
        <h2>Молодець! 🎉</h2>
        <p class="muted">Урок завершено. Твій прогрес збережено.</p>
      </div>
      <b>+20 XP</b>
    </div>
    <div class="actions">
      <button class="secondary" onclick="lessons()">← До уроків</button>
      <button class="primary" onclick="openLesson(currentLessonId,0)">Повторити урок</button>
    </div>`;
}

async function simplePage(name, endpoint, icon){
  title.textContent=name;
  const data=await get(endpoint);
  if(!Array.isArray(data)||!data.length){
    content.innerHTML='<div class="empty">У таблиці поки немає даних.</div>';
    return;
  }
  content.innerHTML=`<div class="hero"><div><h2>${name}</h2><p class="muted">Дані завантажуються безпосередньо з Excel.</p></div></div><div class="list">${data.map(x=>`<div class="row"><div><b>${x.ENGLISH||x.TITLE||x.PHRASE_ID||x.GRAMMAR_ID||x.LISTEN_ID||x.SCENARIO_ID||"Запис"}</b><div class="muted">${x.UKRAINIAN||x.RULE_UK||x.SITUATION||x.TRANSLATION_UK||x.DESCRIPTION||""}</div></div><button class="speak" onclick="speak('${String(x.ENGLISH||x.START_PROMPT||"").replaceAll("'","\\'")}')">${icon}</button></div>`).join("")}</div>`;
}

async function progress(){
  title.textContent="Прогрес";
  const p=dashboard.progress||{};
  content.innerHTML=`<div class="hero"><div><h2>Твій прогрес</h2><p class="muted">Результати зберігаються в таблицю PROGRESS.</p></div><b>${p.XP||0} XP</b></div><div class="grid">${card("Уроки",p.LESSONS_DONE||0,"📚")}${card("Слова",p.WORDS_LEARNED||0,"🧠")}${card("Говоріння",(p.SPEAKING_MIN||0)+" хв","🗣️")}${card("Слухання",(p.LISTENING_MIN||0)+" хв","🎧")}${card("Серія",(p.STREAK_DAYS||0)+" днів","🔥")}</div>`;
}

async function route(page){
  if(page==="home")return home();
  if(page==="lessons")return lessons();
  if(page==="words")return simplePage("Слова","/api/words","🔊");
  if(page==="phrases")return simplePage("Фрази","/api/phrases","🔊");
  if(page==="grammar")return simplePage("Граматика","/api/grammar","📖");
  if(page==="listening")return simplePage("Слухання","/api/listening","🔊");
  if(page==="speaking")return simplePage("Говоріння","/api/speaking","🗣️");
  if(page==="repeat")return simplePage("Повторення","/api/words","↻");
  if(page==="progress")return progress();
  if(page==="achievements")return simplePage("Досягнення","/api/achievements","🏆");
  if(page==="settings")return simplePage("Налаштування","/api/settings","⚙️");
}

document.querySelectorAll(".nav").forEach(b=>b.addEventListener("click",()=>{
  document.querySelectorAll(".nav").forEach(x=>x.classList.remove("active"));
  b.classList.add("active");
  route(b.dataset.page);
}));

(async()=>{
  dashboard=await get("/api/dashboard");
  setStats();
  home();
})();
