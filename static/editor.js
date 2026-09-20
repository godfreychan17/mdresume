/* editor.js — text-only inline editing, save + PDF export */
'use strict';

const status   = document.getElementById('status');
const btnSave  = document.getElementById('btn-save');
const btnExport = document.getElementById('btn-export');
const anchor   = document.getElementById('download-anchor');

let dirty = false;

function setStatus(msg, cls = '') {
  status.textContent = msg;
  status.className = cls;
}

/* ── Collect editable fields ── */
function collectFields() {
  const fields = {};
  document.querySelectorAll('[data-field][contenteditable]').forEach(el => {
    fields[el.dataset.field] = el.innerText.trim();
  });
  return fields;
}

/* ── Mark page dirty on any edit ── */
document.addEventListener('input', e => {
  if (e.target.hasAttribute('contenteditable')) {
    dirty = true;
    setStatus('Unsaved changes', 'busy');
  }
});

/* Prevent newlines — text-only editing */
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.target.hasAttribute('contenteditable')) {
    e.preventDefault();
  }
});

/* Paste as plain text only */
document.addEventListener('paste', e => {
  if (e.target.hasAttribute('contenteditable')) {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData('text/plain');
    document.execCommand('insertText', false, text);
  }
});

/* ── Save ── */
async function saveChanges() {
  if (!dirty) { setStatus('All saved', 'ok'); return; }
  setStatus('Saving…', 'busy');
  try {
    const res = await fetch('/api/content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields: collectFields() }),
    });
    if (!res.ok) throw new Error(await res.text());
    dirty = false;
    setStatus('Saved', 'ok');
    setTimeout(() => setStatus('All saved', ''), 2000);
  } catch (err) {
    setStatus('Save failed', 'err');
    console.error(err);
  }
}

btnSave.addEventListener('click', saveChanges);

/* Auto-save on blur of any editable field */
document.addEventListener('focusout', e => {
  if (e.target.hasAttribute('contenteditable') && dirty) {
    saveChanges();
  }
});

/* ── Export PDF ── */
async function exportPDF() {
  /* Save first so PDF reflects latest edits */
  if (dirty) await saveChanges();

  setStatus('Generating PDF…', 'busy');
  btnExport.disabled = true;
  try {
    const res = await fetch('/api/export', { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const filename = res.headers.get('X-Filename') || 'resume.pdf';

    anchor.href     = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);

    setStatus('PDF downloaded', 'ok');
    setTimeout(() => setStatus('All saved', ''), 3000);
  } catch (err) {
    setStatus('Export failed', 'err');
    console.error(err);
  } finally {
    btnExport.disabled = false;
  }
}

btnExport.addEventListener('click', exportPDF);

/* ── Warn before closing with unsaved changes ── */
window.addEventListener('beforeunload', e => {
  if (dirty) {
    e.preventDefault();
    e.returnValue = '';
  }
});
