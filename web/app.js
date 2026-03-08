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

systemPromptEl.value = defaultSystemPrompt;

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
  roleEl.textContent = role;

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

composerEl.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage();
});

clearChatEl.addEventListener("click", () => {
  messages.length = 0;
  chatEl.innerHTML = "";
  if (compactionBadgeEl) {
    compactionBadgeEl.textContent = "Compaction: n/a";
    compactionBadgeEl.className = "badge badge-idle";
  }
});

loadProfileEl.addEventListener("click", async () => {
  const response = await fetch("/api/profile");
  const data = await response.json();
  profilePreviewEl.textContent = data.profile || "profile.md not found";
  profileDialogEl.showModal();
});

renderMessage("assistant", "Ready. Ask a question to start.");
