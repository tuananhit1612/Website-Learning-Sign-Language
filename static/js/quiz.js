let index = 0;
let correct = 0;
const startTime = Date.now();

const currentEl = document.getElementById("current");
const totalEl = document.getElementById("total");
const progressBar = document.getElementById("progress-bar");
const questionArea = document.getElementById("questionArea");


function renderQuestion() {
  const q = questions[index];
  if (!q) return showResult();

  currentEl.textContent = index + 1;
  totalEl.textContent = questions.length;
  progressBar.style.width = `${((index + 1) / questions.length) * 100}%`;

  let html = `
    <div class="card shadow-sm p-4 mb-3">
      <h5 class="mb-4 text-primary fw-bold">❓ Câu hỏi ${index + 1}</h5>
  `;

  if (q.type === "text") {
    html += `
      <p class="fs-5">👉 Thực hiện ký hiệu cho: <strong>${q.video.title}</strong></p>
      <div class="row justify-content-center g-4">
        <div class="col-lg-6 col-md-8">
          <label class="form-label">🎯 Kết quả dự đoán:</label>
          <input type="text" id="output" class="form-control fs-4 text-center mb-3">
          <div class="d-flex justify-content-center gap-3 mb-3">
            <button onclick="checkTextAnswer()" class="btn btn-success px-4" id="submit-btn">✅ Kiểm tra</button>
            <button onclick="clearLastResult()" class="btn btn-outline-secondary px-4">🗑 Xoá từ</button>
          </div>
          <div class="text-center">
            <button id="next-btn" onclick="nextQuestion()" class="btn btn-primary px-4 d-none">➡️ Tiếp theo</button>
          </div>
        </div>
        <div class="col-md-6">
          <div class="position-relative text-center">
            <video id="video" autoplay playsinline class="rounded border shadow w-100"></video>
            <canvas id="canvas" class="position-absolute top-0 start-0 w-100 h-100" style="z-index: 10;"></canvas>
          </div>
        </div>
      </div>
    `;
  } else if (q.type === "video") {
    html += `
      <p class="fs-5">📺 Xem video và nhập ký hiệu bạn thấy:</p>
      <div class="mx-auto" style="width: 800px; max-width: 100%; weight: 100%;">
        <video controls src="${q.video.url}" class="rounded shadow mb-3 w-100" style="max-height: 400px; object-fit: contain;"></video>
        <input type="text" id="text-answer" class="form-control fs-5 text-center mb-3" placeholder="Nhập đáp án...">
        <div class="d-flex justify-content-center gap-3 mb-3">
          <button onclick="checkVideoAnswer('${q.video.title}')" class="btn btn-success px-4" id="submit-btn">✅ Kiểm tra</button>
          <button id="next-btn" onclick="nextQuestion()" class="btn btn-primary px-4 d-none">➡️ Tiếp theo</button>
        </div>
      </div>
    `;
  }
  

  html += `</div>`;
  questionArea.innerHTML = html;

  if (q.type === "text") {
    initHandModel();
  }
}
function getChapterUrl() {
  const parts = window.location.pathname.split("/");
  if (parts.length >= 3) {
    const chapterId = parts[2];
    return `/lessons/${chapterId}`;
  }
  return "/lessons";
}

function checkTextAnswer() {
  const outputEl = document.getElementById("output");
  const submitBtn = document.getElementById("submit-btn");
  const nextBtn = document.getElementById("next-btn");
  const answer = outputEl.value.trim().toLowerCase();
  const correctAnswer = questions[index].video.title.toLowerCase();

  outputEl.classList.remove("input-correct", "input-wrong");

  if (answer === correctAnswer) {
    outputEl.classList.add("input-correct");
    correct++;
    submitBtn.disabled = true;
    nextBtn.classList.remove("d-none");
  } else {
    outputEl.classList.add("input-wrong");
  }

}


function checkVideoAnswer(expected) {
  const inputEl = document.getElementById("text-answer");
  const submitBtn = document.getElementById("submit-btn");
  const nextBtn = document.getElementById("next-btn");
  const answer = inputEl.value.trim().toLowerCase();

  inputEl.classList.remove("input-correct", "input-wrong");

  if (answer === expected.toLowerCase()) {
    inputEl.classList.add("input-correct");
    correct++;
    submitBtn.disabled = true;
    nextBtn.classList.remove("d-none");
  } else {
    inputEl.classList.add("input-wrong");
  }

  setTimeout(() => {
    inputEl.classList.remove("input-correct", "input-wrong");
  }, 5000);
}


function clearLastResult() {
  const outputEl = document.getElementById("output");
  let words = outputEl.value.trim().split(" ");
  words.pop();
  outputEl.value = words.join(" ");
}

function showResult() {
  const endTime = Date.now();
  const durationMs = endTime - startTime;
  const minutes = Math.floor(durationMs / 60000);
  const seconds = Math.floor((durationMs % 60000) / 1000);
  const formattedTime = `${minutes} phút ${seconds} giây`;
  const chapterUrl = getChapterUrl();
  questionArea.innerHTML = `
  <div class="text-center p-5 card shadow-lg position-relative" style="overflow: hidden;">
    
    <div style="
      position: absolute;
      inset: 0;
      background: url('/static/assets/gif/happy.gif') center center / cover no-repeat;
      opacity: 1;
      z-index: 1;
      pointer-events: none;
    "></div>

    <div style="position: relative; z-index: 2;">
      <h2 class="text-success fw-bold mb-3">🎉 Bạn đã hoàn thành bài học!</h2>
      <p class="fs-5 mb-4">Chúc mừng bạn đã vượt qua tất cả câu hỏi trong bài học này.</p>
      <p class="fs-6 text-muted">⏱️ Thời gian hoàn thành: <strong>${formattedTime}</strong></p>
      <div class="mt-4 d-flex justify-content-center gap-3">
        <a href="#" onclick="location.reload()" class="btn btn-outline-primary px-4">🔁 Làm lại bài học</a>
        <a href="${chapterUrl}" class="btn btn-success px-4">➡️ Học bài tiếp theo</a>
      </div>
    </div>
    
  </div>
`;


  progressBar.style.width = "100%";
  currentEl.textContent = questions.length;

  fetch("/api/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chapter_id: chapterId,
      lesson_id: lessonId
    })
  }).then(res => {
    if (!res.ok) {
      console.error("Không cập nhật được tiến độ học.");
    }
  });
}
function nextQuestion() {
  index++;
  if (index >= questions.length) {
    showResult();
  } else {
    renderQuestion();
  }
}

renderQuestion();
