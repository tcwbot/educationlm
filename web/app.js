const chatEl = document.getElementById("chat");
const composerEl = document.getElementById("composer");
const promptEl = document.getElementById("prompt");
const modelEl = document.getElementById("model");
const systemPromptEl = document.getElementById("systemPrompt");
const includeProfileEl = document.getElementById("includeProfile");
const enableToolsEl = document.getElementById("enableTools");
const loadProfileEl = document.getElementById("loadProfile");
const clearChatEl = document.getElementById("clearChat");
const profileDialogEl = document.getElementById("profileDialog");
const profilePreviewEl = document.getElementById("profilePreview");
const compactionBadgeEl = document.getElementById("compactionBadge");
const refreshProgressEl = document.getElementById("refreshProgress");
const masteryChartEl = document.getElementById("masteryChart");
const trendChartEl = document.getElementById("trendChart");
const chatViewEl = document.getElementById("chatView");
const trajectoryViewEl = document.getElementById("trajectoryView");
const promptViewEl = document.getElementById("promptView");
const showChatViewEl = document.getElementById("showChatView");
const showTrajectoryViewEl = document.getElementById("showTrajectoryView");
const showPromptViewEl = document.getElementById("showPromptView");
const micBtnEl = document.getElementById("micBtn");
const micStatusEl = document.getElementById("micStatus");
const autoSpeakEl = document.getElementById("autoSpeak");
const toggleAutoSpeakEl = document.getElementById("toggleAutoSpeak");
const stopSpeakEl = document.getElementById("stopSpeak");
const newSessionEl = document.getElementById("newSession");
const ttsStatusEl = document.getElementById("ttsStatus");
const ttsVoiceEl = document.getElementById("ttsVoice");
const ttsRateEl = document.getElementById("ttsRate");
const ttsPitchEl = document.getElementById("ttsPitch");
const ttsRateValueEl = document.getElementById("ttsRateValue");
const ttsPitchValueEl = document.getElementById("ttsPitchValue");

const messages = [];
const defaultSystemPrompt = `You are an adaptive tutor.
Follow this workflow every session:
1. Review current learning progress and goals.
2. Assess knowledge with short quizzes or practice problems.
3. Track topic mastery (0-100) and identify strengths/gaps.
4. Adapt explanations, examples, and pacing based on performance.
5. Provide a clear feedback loop (what was good, what to improve).
6. End each session with a concise summary:
   - topics covered
   - strengths
   - improvement areas
   - next steps
7. Contribute inputs for weekly/monthly progress reports.
8. Revisit and adjust short-term/long-term goals as needed.

When profile context is provided, use it for personalization.
When the student asks for further understanding resources, call the recommend_youtube_videos tool.`;

if (systemPromptEl) {
  systemPromptEl.value = defaultSystemPrompt;
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const synth = window.speechSynthesis;
let recognition = null;
let micActive = false;
const ttsSupported = typeof window.SpeechSynthesisUtterance !== "undefined" && !!synth;
const TTS_SETTINGS_KEY = "educationlm_tts_settings";
let availableVoices = [];

function setMicStatus(text, active = false) {
  if (!micStatusEl || !micBtnEl) return;
  micStatusEl.textContent = text;
  micBtnEl.textContent = active ? "Stop Mic" : "Start Mic";
  micBtnEl.classList.toggle("mic-active", active);
}

function ensureRecognition() {
  if (!SpeechRecognition) {
    setMicStatus("Mic: unsupported in this browser");
    if (micBtnEl) micBtnEl.disabled = true;
    return null;
  }
  if (recognition) return recognition;

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = true;
  recognition.continuous = true;

  recognition.onstart = () => {
    micActive = true;
    setMicStatus("Mic: listening...", true);
  };

  recognition.onresult = (event) => {
    let finalText = "";
    let interimText = "";
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalText += transcript;
      } else {
        interimText += transcript;
      }
    }

    if (finalText) {
      const prefix = promptEl.value.trim() ? `${promptEl.value.trim()} ` : "";
      promptEl.value = `${prefix}${finalText}`.trim();
    }
    setMicStatus(interimText ? `Mic: hearing "${interimText.slice(0, 40)}..."` : "Mic: listening...", true);
  };

  recognition.onerror = (event) => {
    setMicStatus(`Mic error: ${event.error}`);
  };

  recognition.onend = () => {
    micActive = false;
    setMicStatus("Mic: idle");
  };

  return recognition;
}

function setTtsStatus(text) {
  if (!ttsStatusEl) return;
  ttsStatusEl.textContent = text;
}

function loadTtsSettings() {
  try {
    const raw = localStorage.getItem(TTS_SETTINGS_KEY);
    if (!raw) return { voiceURI: "", rate: 1, pitch: 1, autoSpeak: true };
    const parsed = JSON.parse(raw);
    return {
      voiceURI: parsed.voiceURI || "",
      rate: Number(parsed.rate) || 1,
      pitch: Number(parsed.pitch) || 1,
      autoSpeak: Boolean(parsed.autoSpeak),
    };
  } catch {
    return { voiceURI: "", rate: 1, pitch: 1, autoSpeak: true };
  }
}

function saveTtsSettings() {
  if (!ttsSupported) return;
  const payload = {
    voiceURI: ttsVoiceEl?.value || "",
    rate: Number(ttsRateEl?.value || 1),
    pitch: Number(ttsPitchEl?.value || 1),
    autoSpeak: Boolean(autoSpeakEl?.checked),
  };
  localStorage.setItem(TTS_SETTINGS_KEY, JSON.stringify(payload));
}

function updateTtsValueLabels() {
  if (ttsRateValueEl && ttsRateEl) ttsRateValueEl.textContent = Number(ttsRateEl.value).toFixed(1);
  if (ttsPitchValueEl && ttsPitchEl) ttsPitchValueEl.textContent = Number(ttsPitchEl.value).toFixed(1);
}

function syncAutoSpeakUi() {
  const enabled = Boolean(autoSpeakEl?.checked);
  if (toggleAutoSpeakEl) {
    toggleAutoSpeakEl.textContent = enabled ? "Turn Auto-read Off" : "Turn Auto-read On";
  }
  if (enabled) {
    setTtsStatus("TTS: auto-read on");
  } else {
    setTtsStatus("TTS: auto-read off");
  }
}

function populateVoiceOptions(selectedVoiceURI = "") {
  if (!ttsVoiceEl || !ttsSupported) return;
  const allVoices = synth.getVoices();
  availableVoices = allVoices.filter((voice) => /^en-US$/i.test(voice.lang));
  ttsVoiceEl.innerHTML = "";
  for (const voice of availableVoices) {
    const option = document.createElement("option");
    option.value = voice.voiceURI;
    option.textContent = `${voice.name} (${voice.lang})${voice.default ? " • default" : ""}`;
    ttsVoiceEl.appendChild(option);
  }
  if (!availableVoices.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No en-US voices available";
    ttsVoiceEl.appendChild(option);
  }

  const hasSaved = availableVoices.some((v) => v.voiceURI === selectedVoiceURI);
  if (hasSaved) {
    ttsVoiceEl.value = selectedVoiceURI;
  } else if (availableVoices.length) {
    const preferred =
      availableVoices.find((v) => /(siri|neural|natural|enhanced|premium)/i.test(v.name)) ||
      availableVoices.find((v) => /(aria|jenny|guy)/i.test(v.name)) ||
      availableVoices.find((v) => /(google|microsoft|apple|samantha|daniel)/i.test(v.name)) ||
      availableVoices[0];
    ttsVoiceEl.value = preferred.voiceURI;
    saveTtsSettings();
  }
}

function markdownToSpeechText(content) {
  return (content || "")
    .replace(/```[\s\S]*?```/g, " code block omitted ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1")
    .replace(/[*_#>-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function speakAssistantText(content) {
  if (!ttsSupported) {
    setTtsStatus("TTS: unsupported in this browser");
    return;
  }
  const text = markdownToSpeechText(content);
  if (!text) return;
  synth.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = Number(ttsRateEl?.value || 1.0);
  utterance.pitch = Number(ttsPitchEl?.value || 1.0);
  const selectedVoice = availableVoices.find((v) => v.voiceURI === (ttsVoiceEl?.value || ""));
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }
  utterance.onstart = () => setTtsStatus("TTS: speaking...");
  utterance.onend = () => setTtsStatus("TTS: idle");
  utterance.onerror = () => setTtsStatus("TTS: error");
  synth.speak(utterance);
}

function escapeHtml(input) {
  return input
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderMarkdown(mdText) {
  const text = escapeHtml(mdText || "");
  const blocks = text.split(/\n{2,}/);
  const htmlBlocks = blocks.map((block) => {
    if (block.startsWith("```") && block.endsWith("```")) {
      const lines = block.split("\n");
      const lang = lines[0].replace("```", "").trim();
      const content = lines.slice(1, -1).join("\n");
      return `<pre><code class="lang-${lang}">${content}</code></pre>`;
    }

    if (/^#{1,6}\s/.test(block)) {
      const level = block.match(/^#{1,6}/)[0].length;
      const content = block.replace(/^#{1,6}\s/, "");
      return `<h${level}>${content}</h${level}>`;
    }

    const lines = block.split("\n");
    const allBullets = lines.every((line) => /^[-*]\s+/.test(line));
    if (allBullets) {
      const items = lines
        .map((line) => line.replace(/^[-*]\s+/, ""))
        .map((line) => `<li>${line}</li>`)
        .join("");
      return `<ul>${items}</ul>`;
    }

    const allNumbered = lines.every((line) => /^\d+\.\s+/.test(line));
    if (allNumbered) {
      const items = lines
        .map((line) => line.replace(/^\d+\.\s+/, ""))
        .map((line) => `<li>${line}</li>`)
        .join("");
      return `<ol>${items}</ol>`;
    }

    const withInline = block
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
      .replace(/(^|[\s(])(https?:\/\/[^\s<>"')\]]+)([.,!?])?/g, '$1<a href="$2" target="_blank" rel="noreferrer">$2</a>$3')
      .replace(/\n/g, "<br>");
    return `<p>${withInline}</p>`;
  });

  return htmlBlocks.join("\n");
}

function renderMessage(role, content) {
  const wrap = document.createElement("article");
  wrap.className = `msg ${role}`;

  const roleEl = document.createElement("div");
  roleEl.className = "role";
  if (role === "assistant") {
    const roleLabel = document.createElement("span");
    roleLabel.textContent = role;
    const speakBtn = document.createElement("button");
    speakBtn.type = "button";
    speakBtn.className = "tiny-btn";
    speakBtn.textContent = "Speak";
    speakBtn.addEventListener("click", () => speakAssistantText(content));
    roleEl.appendChild(roleLabel);
    roleEl.appendChild(speakBtn);
  } else {
    roleEl.textContent = role;
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") {
    bubble.innerHTML = renderMarkdown(content);
  } else {
    bubble.textContent = content;
  }

  wrap.appendChild(roleEl);
  wrap.appendChild(bubble);
  chatEl.appendChild(wrap);
  chatEl.scrollTop = chatEl.scrollHeight;
  if (role === "assistant" && window.MathJax?.typesetPromise) {
    window.MathJax.typesetPromise([bubble]).catch(() => {});
  }
  if (role === "assistant" && autoSpeakEl?.checked) {
    speakAssistantText(content);
  }
}

function updateCompactionBadge(meta) {
  if (!compactionBadgeEl || !meta) return;
  const profile = Boolean(meta.profile_compacted);
  const convo = Boolean(meta.conversation_compacted);
  const used = Number(meta.context_chars || 0);
  const max = Number(meta.max_context_chars || 0);

  if (!profile && !convo) {
    compactionBadgeEl.textContent = `Compaction: off (${used}/${max})`;
    compactionBadgeEl.className = "badge badge-ok";
    return;
  }

  const parts = [];
  if (convo) parts.push("chat");
  if (profile) parts.push("profile");
  compactionBadgeEl.textContent = `Compaction: ${parts.join(" + ")} (${used}/${max})`;
  compactionBadgeEl.className = "badge badge-active";
}

function drawMasteryChart(data, targetMastery = 80) {
  if (!window.d3 || !masteryChartEl) return;
  const d3 = window.d3;
  const width = 640;
  const height = 260;
  const margin = { top: 20, right: 20, bottom: 60, left: 45 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = d3.select(masteryChartEl);
  svg.selectAll("*").remove();
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  if (!data.length) {
    g.append("text").attr("x", 8).attr("y", 20).text("No mastery data yet. Complete quizzes to populate.");
    return;
  }

  const x = d3.scaleBand().domain(data.map((d) => d.topic)).range([0, innerW]).padding(0.2);
  const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  g.append("g").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-20)")
    .style("text-anchor", "end");
  g.append("g").call(d3.axisLeft(y));

  g.selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d) => x(d.topic))
    .attr("y", (d) => y(d.mastery))
    .attr("width", x.bandwidth())
    .attr("height", (d) => innerH - y(d.mastery))
    .attr("fill", "#2d7dd2");

  g.append("line")
    .attr("x1", 0)
    .attr("x2", innerW)
    .attr("y1", y(targetMastery))
    .attr("y2", y(targetMastery))
    .attr("stroke", "#d17b0f")
    .attr("stroke-dasharray", "4,4");
}

function projectedScore(points) {
  if (points.length < 2) return null;
  const last = points[points.length - 1];
  const prev = points[points.length - 2];
  const trend = last.score - prev.score;
  return Math.max(0, Math.min(100, last.score + trend));
}

function drawTrendChart(scores) {
  if (!window.d3 || !trendChartEl) return;
  const d3 = window.d3;
  const width = 640;
  const height = 260;
  const margin = { top: 20, right: 20, bottom: 45, left: 45 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;

  const svg = d3.select(trendChartEl);
  svg.selectAll("*").remove();
  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  if (!scores.length) {
    g.append("text").attr("x", 8).attr("y", 20).text("No scored quizzes yet.");
    return;
  }

  const points = scores.map((d, i) => ({ ...d, i: i + 1 }));
  const x = d3.scaleLinear().domain([1, points.length + 1]).range([0, innerW]);
  const y = d3.scaleLinear().domain([0, 100]).range([innerH, 0]);

  g.append("g").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x).ticks(Math.min(8, points.length + 1)));
  g.append("g").call(d3.axisLeft(y));

  const line = d3.line().x((d) => x(d.i)).y((d) => y(d.score));
  g.append("path")
    .datum(points)
    .attr("fill", "none")
    .attr("stroke", "#145ea8")
    .attr("stroke-width", 2)
    .attr("d", line);

  g.selectAll(".dot")
    .data(points)
    .enter()
    .append("circle")
    .attr("cx", (d) => x(d.i))
    .attr("cy", (d) => y(d.score))
    .attr("r", 3.5)
    .attr("fill", "#145ea8");

  const nextScore = projectedScore(points);
  if (nextScore !== null) {
    const projected = [{ i: points.length, score: points[points.length - 1].score }, { i: points.length + 1, score: nextScore }];
    g.append("path")
      .datum(projected)
      .attr("fill", "none")
      .attr("stroke", "#d17b0f")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,4")
      .attr("d", d3.line().x((d) => x(d.i)).y((d) => y(d.score)));
  }
}

async function loadProgress() {
  try {
    const response = await fetch("/api/progress");
    const data = await response.json();
    drawMasteryChart(data.mastery || [], data.target_mastery || 80);
    drawTrendChart(data.quiz_scores || []);
  } catch (err) {
    if (window.d3 && masteryChartEl) {
      window.d3.select(masteryChartEl).selectAll("*").remove();
      window.d3.select(masteryChartEl).append("text").attr("x", 8).attr("y", 20).text(`Progress load error: ${err.message}`);
    }
  }
}

function setView(viewName) {
  const showChat = viewName === "chat";
  const showTrajectory = viewName === "trajectory";
  const showPrompt = viewName === "prompt";

  chatViewEl?.classList.toggle("view-active", showChat);
  trajectoryViewEl?.classList.toggle("view-active", showTrajectory);
  promptViewEl?.classList.toggle("view-active", showPrompt);

  if (showChatViewEl) {
    showChatViewEl.classList.toggle("view-btn-active", showChat);
    showChatViewEl.setAttribute("aria-selected", String(showChat));
  }
  if (showTrajectoryViewEl) {
    showTrajectoryViewEl.classList.toggle("view-btn-active", showTrajectory);
    showTrajectoryViewEl.setAttribute("aria-selected", String(showTrajectory));
  }
  if (showPromptViewEl) {
    showPromptViewEl.classList.toggle("view-btn-active", showPrompt);
    showPromptViewEl.setAttribute("aria-selected", String(showPrompt));
  }
  if (showTrajectory) {
    loadProgress();
  }
}

function resetChatSession() {
  messages.length = 0;
  if (chatEl) chatEl.innerHTML = "";
  if (compactionBadgeEl) {
    compactionBadgeEl.textContent = "Compaction: n/a";
    compactionBadgeEl.className = "badge badge-idle";
  }
}

async function sendMessage() {
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  messages.push({ role: "user", content: prompt });
  renderMessage("user", prompt);
  promptEl.value = "";

  const pending = document.createElement("article");
  pending.className = "msg assistant";
  pending.innerHTML = `<div class="role">assistant</div><div class="bubble">Thinking...</div>`;
  chatEl.appendChild(pending);
  chatEl.scrollTop = chatEl.scrollHeight;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: modelEl.value.trim() || "granite4:7b-a1b-h",
        messages,
        systemPrompt: systemPromptEl.value,
        includeProfile: includeProfileEl.checked,
        enableTools: enableToolsEl.checked,
      }),
    });

    const data = await response.json();
    pending.remove();

    if (!response.ok) {
      const errText = data.detail || data.error || "Unknown error";
      renderMessage("assistant", `Error: ${errText}`);
      return;
    }

    const content = (data.content || "").trim();
    messages.push({ role: "assistant", content });
    renderMessage("assistant", content || "(No response content)");
    updateCompactionBadge(data.meta);
  } catch (err) {
    pending.remove();
    renderMessage("assistant", `Error: ${err.message}`);
  }
}

if (composerEl) {
  composerEl.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage();
  });
}
if (promptEl) {
  promptEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
}

if (clearChatEl) {
  clearChatEl.addEventListener("click", () => {
    resetChatSession();
  });
}
if (newSessionEl) {
  newSessionEl.addEventListener("click", () => {
    resetChatSession();
    renderMessage("assistant", "Started a new session. Ask a question to continue.");
  });
}

if (loadProfileEl && profilePreviewEl && profileDialogEl) {
  loadProfileEl.addEventListener("click", async () => {
    const response = await fetch("/api/profile");
    const data = await response.json();
    profilePreviewEl.textContent = data.profile || "profile.md not found";
    profileDialogEl.showModal();
  });
}

if (refreshProgressEl) {
  refreshProgressEl.addEventListener("click", () => {
    loadProgress();
  });
}
if (showChatViewEl) {
  showChatViewEl.addEventListener("click", () => setView("chat"));
}
if (showTrajectoryViewEl) {
  showTrajectoryViewEl.addEventListener("click", () => setView("trajectory"));
}
if (showPromptViewEl) {
  showPromptViewEl.addEventListener("click", () => setView("prompt"));
}
if (micBtnEl) {
  micBtnEl.addEventListener("click", () => {
    const rec = ensureRecognition();
    if (!rec) return;
    if (micActive) {
      rec.stop();
    } else {
      rec.start();
    }
  });
}
if (!ttsSupported) {
  if (autoSpeakEl) autoSpeakEl.disabled = true;
  if (toggleAutoSpeakEl) toggleAutoSpeakEl.disabled = true;
  if (stopSpeakEl) stopSpeakEl.disabled = true;
  if (ttsVoiceEl) ttsVoiceEl.disabled = true;
  if (ttsRateEl) ttsRateEl.disabled = true;
  if (ttsPitchEl) ttsPitchEl.disabled = true;
  setTtsStatus("TTS: unsupported in this browser");
}
if (ttsSupported) {
  const settings = loadTtsSettings();
  if (ttsRateEl) ttsRateEl.value = String(settings.rate);
  if (ttsPitchEl) ttsPitchEl.value = String(settings.pitch);
  if (autoSpeakEl) autoSpeakEl.checked = settings.autoSpeak;
  updateTtsValueLabels();
  populateVoiceOptions(settings.voiceURI);
  syncAutoSpeakUi();
  if (typeof synth.onvoiceschanged !== "undefined") {
    synth.onvoiceschanged = () => populateVoiceOptions(ttsVoiceEl?.value || settings.voiceURI);
  }
  autoSpeakEl?.addEventListener("change", () => {
    saveTtsSettings();
    syncAutoSpeakUi();
  });
  toggleAutoSpeakEl?.addEventListener("click", () => {
    if (!autoSpeakEl) return;
    autoSpeakEl.checked = !autoSpeakEl.checked;
    saveTtsSettings();
    syncAutoSpeakUi();
    if (!autoSpeakEl.checked) {
      synth.cancel();
      setTtsStatus("TTS: auto-read off");
    }
  });
  ttsVoiceEl?.addEventListener("change", saveTtsSettings);
  ttsRateEl?.addEventListener("input", () => {
    updateTtsValueLabels();
    saveTtsSettings();
  });
  ttsPitchEl?.addEventListener("input", () => {
    updateTtsValueLabels();
    saveTtsSettings();
  });
}
if (stopSpeakEl) {
  stopSpeakEl.addEventListener("click", () => {
    if (!ttsSupported) return;
    synth.cancel();
    if (autoSpeakEl) {
      autoSpeakEl.checked = false;
      saveTtsSettings();
      syncAutoSpeakUi();
    } else {
      setTtsStatus("TTS: stopped");
    }
  });
}

renderMessage("assistant", "Ready. Ask a question to start.");
loadProgress();
