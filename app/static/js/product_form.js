// ─── Preview de archivo ───────────────────────────
const fileInput   = document.getElementById("image-file");
const preview     = document.getElementById("file-preview");
const previewImg  = document.getElementById("preview-img");
const fileName    = document.getElementById("file-name");
const uploadArea  = document.getElementById("upload-area");
const urlInput    = document.getElementById("image-url-input");
const urlPreview  = document.getElementById("url-preview");
const urlPreviewImg = document.getElementById("url-preview-img");

if (fileInput) {
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      fileName.textContent = file.name;
      preview.style.display = "block";
      // Limpiar URL si se sube archivo
      if (urlInput) urlInput.value = "";
      if (urlPreview) urlPreview.style.display = "none";
    };
    reader.readAsDataURL(file);
  });
}

// ─── Drag & Drop ──────────────────────────────────
if (uploadArea) {
  uploadArea.addEventListener("dragover", e => {
    e.preventDefault();
    uploadArea.classList.add("dragover");
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
  });

  uploadArea.addEventListener("drop", e => {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && fileInput) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      fileInput.dispatchEvent(new Event("change"));
    }
  });
}

// ─── Preview de URL ───────────────────────────────
if (urlInput) {
  let timeout;
  urlInput.addEventListener("input", () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      const url = urlInput.value.trim();
      if (url) {
        urlPreviewImg.src = url;
        urlPreviewImg.onload  = () => urlPreview.style.display = "block";
        urlPreviewImg.onerror = () => urlPreview.style.display = "none";
        // Limpiar archivo si se escribe URL
        if (fileInput) fileInput.value = "";
        if (preview) preview.style.display = "none";
      } else {
        urlPreview.style.display = "none";
      }
    }, 600);
  });
}