
window.initHandModel = function () {
  const videoElement = document.getElementById("video");
  const outputElement = document.getElementById("output");
  const drawCheckbox = document.getElementById("drawLandmarks");

  const MAX_FRAMES = 50;
  const CONF_THRESHOLD = 0.5;

  let sequence = [];
  let predictions = [];
  let sentence = [];

  const canvasElement = document.createElement("canvas");
  canvasElement.width = 640;
  canvasElement.height = 480;
  canvasElement.style.position = "absolute";
  canvasElement.style.left = "0";
  canvasElement.style.top = "0";
  canvasElement.style.zIndex = "10";
  canvasElement.style.pointerEvents = "none";
  
  videoElement.parentElement.appendChild(canvasElement);
  const canvasCtx = canvasElement.getContext("2d");
  
  function updateCanvasSize() {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
  }
  videoElement.onloadedmetadata = updateCanvasSize;
  window.addEventListener("resize", updateCanvasSize);


  async function predictLandmarks(sequence) {

    if (sequence.length !== 50) return null;

    const left_hand_sequence = sequence.map(frame => frame.slice(0, 63));
    const right_hand_sequence = sequence.map(frame => frame.slice(63, 126));

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left_hand_sequence, right_hand_sequence }),
      });

      if (!response.ok) {
        const err = await response.text();
        console.error("\u274C Server error:", err);
        return null;
      }
      console.log("\u2705 Dữ liệu đã được gửi thành công đến server");

      const data = await response.json();
      return {
        label: data.prediction,
        confidence: data.confidence
      };
    } catch (err) {
      console.error("Lỗi khi gửi dữ liệu đến server:", err);
      return null;
    }
  }


  function updateSentence(predictedLabel, confidence) {
    if (confidence > CONF_THRESHOLD) {
      predictions.push(predictedLabel);
      const recent10 = predictions.slice(-10);
      const isStable = recent10.every(label => label === predictedLabel);

      if (isStable) {
        const lastWord = sentence[sentence.length - 1];
        if (predictedLabel !== lastWord) {
          sentence.push(predictedLabel);
          outputElement.value = sentence.join(" ");
        }
      }
    }
  }

  function clearResult() {
      if (sentence.length > 0) {
        sentence.pop();
        outputElement.value = sentence.join(" ");
      }
      predictions = [];
      sequence = [];
    }
    

  const hands = new Hands({
    locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
  });
  hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
  });

  hands.onResults(async (results) => {
    if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
      return;
    }



    if (drawCheckbox && drawCheckbox.checked) {
      canvasCtx.save();
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
      canvasCtx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
      results.multiHandLandmarks.forEach(lms => {
        drawConnectors(canvasCtx, lms, HAND_CONNECTIONS, { color: "#00FF00", lineWidth: 2 });
        drawLandmarks(canvasCtx, lms, { color: "#FF0000", radius: 3 });
      });
      canvasCtx.restore();
    } else {
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    }

    let allLandmarks = [];
    for (let i = 0; i < 2; i++) {
      if (results.multiHandLandmarks[i]) {
        const lm = results.multiHandLandmarks[i];
        const flat = lm.flatMap(pt => [pt.x, pt.y, pt.z]);
        allLandmarks.push(...flat);
      } else {
        allLandmarks.push(...Array(63).fill(0));
      }
    }

    if (allLandmarks.length === 126) {
      sequence.push(allLandmarks);
      sequence = sequence.slice(-MAX_FRAMES);

      if (sequence.length === MAX_FRAMES) {
        const result = await predictLandmarks(sequence);
        if (result) {
          updateSentence(result.label, result.confidence);
        }
      }
    }
  });

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoElement.srcObject = stream;
    } catch (err) {
      console.error("\u274C Không thể mở camera:", err);
      alert("Không thể truy cập camera. Vui lòng cho phép quyền camera.");
    }
  }
  canvasElement.classList.add('video-canvas');
  const camera = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 640,
    height: 480,
    
  });
  if (videoElement) {
      startCamera();
      camera.start();
  }
}
