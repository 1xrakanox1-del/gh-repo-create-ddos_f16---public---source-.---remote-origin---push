/* ═══════════════════════════════════════════════════════════
   DDOS_F16 SCANWEBS v6.0 — Standalone Deployment Engine
   Uses fetch() API to communicate with Flask backend
   ═══════════════════════════════════════════════════════════ */

// ────── SVG ICONS (inline paths) ──────
const ICONS = {
  dns: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8"/><path d="M12 3a15 15 0 010 18M12 3a15 15 0 000 18"/></svg>',
  subdomains: '<svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M12 7v4l-6 6M12 11l6 6"/></svg>',
  whois: '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M12 8h.01M8 12h8M8 16h6"/><circle cx="12" cy="8" r="0.5" fill="currentColor"/></svg>',
  headers: '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h10"/><circle cx="19" cy="17" r="2"/></svg>',
  ssl: '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/><circle cx="12" cy="16" r="1" fill="currentColor"/></svg>',
  tech: '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h.01M15 9h.01M9 15h.01M15 15h.01"/><path d="M9 4v16M15 4v16M4 9h16M4 15h16"/></svg>',
  ports: '<svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  security: '<svg viewBox="0 0 24 24"><path d="M12 2l7 4v5c0 5.25-3.5 9.74-7 11-3.5-1.26-7-5.75-7-11V6l7-4z"/><path d="M9 12l2 2 4-4"/></svg>',
  reverse_dns: '<svg viewBox="0 0 24 24"><path d="M9 14l-4 4 4 4"/><path d="M5 18h14a2 2 0 002-2V8"/><path d="M15 10l4-4-4-4"/><path d="M19 6H5a2 2 0 00-2 2v8"/></svg>',
  geo: '<svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  robots: '<svg viewBox="0 0 24 24"><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"/><path d="M9 13h6M9 17h4"/></svg>'
};

// ────── MODULE DEFINITIONS ──────
const MODULES = [
  { id: 'dns',         name: 'DNS_RECON',        desc: 'Full DNS record enumeration', engine: 'dig / bind-tools' },
  { id: 'subdomains',  name: 'SUBDOMAIN_HUNTER', desc: 'Brute-force 120+ subdomain prefixes', engine: 'Python ThreadPool' },
  { id: 'whois',       name: 'WHOIS_INTEL',      desc: 'Domain registrar & registrant data', engine: 'whois CLI' },
  { id: 'headers',     name: 'HTTP_FINGERPRINT', desc: 'Server headers & redirect analysis', engine: 'cURL' },
  { id: 'ssl',         name: 'SSL_AUDIT',        desc: 'Certificate chain & cipher analysis', engine: 'OpenSSL' },
  { id: 'tech',        name: 'TECH_DETECT',      desc: 'Detect 30+ CMS/frameworks', engine: 'cURL + RegEx' },
  { id: 'ports',       name: 'PORT_RECON',       desc: 'Scan 20 critical ports', engine: 'Python socket' },
  { id: 'security',    name: 'SECURITY_HEADERS', desc: 'Audit 10 security headers (A+ to F)', engine: 'cURL + audit' },
  { id: 'reverse_dns', name: 'REVERSE_DNS',      desc: 'PTR record & IP resolution', engine: 'dig -x' },
  { id: 'geo',         name: 'GEO_LOCATE',       desc: 'Server geolocation & ISP data', engine: 'IP-API' },
  { id: 'robots',      name: 'ROBOTS_SITEMAP',   desc: 'robots.txt & sitemap extraction', engine: 'cURL' }
];

let scanResults = {};
let currentTab = null;
let isScanning = false;

// ────── MATRIX RAIN ──────
function initMatrixRain() {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*日月火水木金土';
  const fontSize = 14;
  const columns = Math.floor(canvas.width / fontSize);
  const drops = Array(columns).fill(1);

  function draw() {
    ctx.fillStyle = 'rgba(3,3,3,0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00ff41';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      ctx.globalAlpha = Math.random() * 0.5 + 0.1;
      ctx.fillText(char, i * fontSize, drops[i] * fontSize);
      ctx.globalAlpha = 1;
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
    requestAnimationFrame(draw);
  }
  draw();
}

// ────── TYPEWRITER HERO SUBTITLE ──────
function typewriterEffect() {
  const el = document.getElementById('hero-subtitle');
  if (!el) return;
  const text = 'SCANWEBS INTELLIGENCE PLATFORM v6.0';
  let i = 0;
  function type() {
    if (i <= text.length) {
      el.textContent = text.substring(0, i);
      i++;
      setTimeout(type, 50 + Math.random() * 40);
    }
  }
  setTimeout(type, 800);
}

// ────── SCROLL REVEAL ──────
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal, .reveal-fade').forEach(el => observer.observe(el));
}

// ────── GENERATE MODULE ICONS ──────
function generateModuleIcons() {
  const strip = document.getElementById('modules-strip');
  MODULES.forEach((mod, i) => {
    const item = document.createElement('div');
    item.className = 'module-icon-item';
    item.style.transitionDelay = (i * 100) + 'ms';
    item.innerHTML = `
      <div class="icon-circle">${ICONS[mod.id]}</div>
      <span class="module-icon-label">${mod.name}</span>
      <span class="module-icon-status">ONLINE</span>
    `;
    strip.appendChild(item);

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          setTimeout(() => item.classList.add('visible'), i * 100);
          obs.disconnect();
        }
      });
    }, { threshold: 0.1 });
    obs.observe(item);
  });
}

// ────── GENERATE MODULE TOGGLES (inline icons) ──────
function generateModuleToggles() {
  const container = document.getElementById('module-toggles-strip');
  MODULES.forEach(mod => {
    const toggle = document.createElement('label');
    toggle.className = 'mod-toggle selected';
    toggle.dataset.id = mod.id;
    toggle.innerHTML = `
      <input type="checkbox" value="${mod.id}" checked style="display:none;">
      ${ICONS[mod.id]}
      <span class="mod-toggle-name">${mod.name}</span>
    `;
    toggle.addEventListener('click', function(e) {
      if (e.target.tagName === 'INPUT') return;
      const cb = this.querySelector('input');
      cb.checked = !cb.checked;
      this.classList.toggle('selected', cb.checked);
    });
    const cb = toggle.querySelector('input');
    cb.addEventListener('change', function() {
      toggle.classList.toggle('selected', this.checked);
    });
    container.appendChild(toggle);
  });
}

function selectAll() {
  document.querySelectorAll('.mod-toggle input').forEach(cb => {
    cb.checked = true;
    cb.dispatchEvent(new Event('change'));
  });
}

function deselectAll() {
  document.querySelectorAll('.mod-toggle input').forEach(cb => {
    cb.checked = false;
    cb.dispatchEvent(new Event('change'));
  });
}

// ────── SCANNING ENGINE (Flask API) ──────
function getSelectedModules() {
  const selected = [];
  document.querySelectorAll('.mod-toggle input:checked').forEach(cb => {
    const mod = MODULES.find(m => m.id === cb.value);
    if (mod) selected.push(mod);
  });
  return selected;
}

function validateDomain(d) {
  return /^[a-zA-Z0-9][a-zA-Z0-9.\-]*\.[a-zA-Z]{2,}$/.test(d);
}

async function runScanModule(domain, moduleId) {
  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: domain, module: moduleId })
    });
    const data = await response.json();
    if (!response.ok) {
      return { error: data.error || 'Server error' };
    }
    return data;
  } catch (e) {
    return { error: 'Network error: ' + e.message };
  }
}

async function startScan() {
  if (isScanning) return;

  const input = document.getElementById('target-input');
  const domain = input.value.trim().replace(/^https?:\/\//, '').replace(/\/.*$/, '');

  if (!domain) {
    input.style.borderBottomColor = '#ff0040';
    input.placeholder = '⚠ DOMAIN REQUIRED';
    setTimeout(() => {
      input.style.borderBottomColor = '';
      input.placeholder = 'enter target domain — example.com';
    }, 2000);
    return;
  }

  if (!validateDomain(domain)) {
    input.style.borderBottomColor = '#ff0040';
    setTimeout(() => input.style.borderBottomColor = '', 2000);
    return;
  }

  const selectedModules = getSelectedModules();
  if (selectedModules.length === 0) return;

  isScanning = true;
  scanResults = {};
  currentTab = null;

  // UI updates
  const btn = document.getElementById('scan-btn');
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';
  btn.disabled = true;
  input.disabled = true;

  // Progress
  const prog = document.getElementById('scan-progress');
  prog.classList.add('active');
  const status = document.getElementById('progress-status');

  // Show results
  const resultsSection = document.getElementById('results');
  resultsSection.style.display = '';
  const nav = document.getElementById('results-nav');
  nav.innerHTML = '';
  document.getElementById('terminal-output').innerHTML = '<span class="line-comment">// Initializing reconnaissance modules...</span>';
  document.getElementById('stats-bar').innerHTML = '';
  document.getElementById('results-module-label').textContent = '// INITIALIZING...';

  status.innerHTML = '<span class="running">SCANNING TARGET: ' + escapeHtml(domain) + '</span>';
  document.getElementById('terminal-output').innerHTML = '<span class="line-comment">// Scanning ' + escapeHtml(domain) + '...</span>\n';

  // Build sidebar nav icons
  selectedModules.forEach(mod => {
    const navBtn = document.createElement('button');
    navBtn.className = 'nav-icon-btn';
    navBtn.id = 'nav-' + mod.id;
    navBtn.innerHTML = ICONS[mod.id] + '<span class="nav-tooltip">' + mod.name + '</span>';
    navBtn.onclick = () => switchTab(mod.id);
    nav.appendChild(navBtn);
  });

  // Scan each module via API
  let completed = 0;
  const total = selectedModules.length;

  for (const mod of selectedModules) {
    const navBtn = document.getElementById('nav-' + mod.id);
    status.innerHTML = '<span class="running">⟳ ' + mod.name + ' (' + (completed + 1) + '/' + total + ')</span>';

    try {
      const result = await runScanModule(domain, mod.id);
      scanResults[mod.id] = result;
      if (navBtn) navBtn.classList.add('complete');
    } catch (err) {
      scanResults[mod.id] = { error: err.message || 'Module failed' };
      if (navBtn) navBtn.classList.add('error');
    }

    completed++;
    document.getElementById('progress-fill').style.width = ((completed / total) * 100) + '%';

    if (completed === 1) switchTab(mod.id);
  }

  status.innerHTML = '<span class="done">✓ SCAN COMPLETE — ' + total + ' MODULES EXECUTED</span>';
  generateSummary(domain, selectedModules);

  // Reset
  btn.querySelector('.btn-text').style.display = '';
  btn.querySelector('.btn-loading').style.display = 'none';
  btn.disabled = false;
  input.disabled = false;
  isScanning = false;

  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ────── RESULTS DISPLAY ──────
function switchTab(moduleId) {
  currentTab = moduleId;
  document.querySelectorAll('.nav-icon-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('nav-' + moduleId);
  if (btn) btn.classList.add('active');
  const mod = MODULES.find(m => m.id === moduleId);
  if (mod) {
    document.getElementById('results-module-label').textContent = '◈ ' + mod.name + ' — ' + mod.desc;
  }
  renderResults(moduleId);
}

function renderResults(moduleId) {
  const output = document.getElementById('terminal-output');
  const data = scanResults[moduleId];
  const mod = MODULES.find(m => m.id === moduleId);

  if (!data) {
    output.innerHTML = '<span class="line-comment">// Scanning in progress...</span>';
    return;
  }

  if (data.error) {
    output.innerHTML = '<span class="line-error">ERROR: ' + escapeHtml(data.error) + '</span>';
    return;
  }

  let html = '<span class="line-header">◈ ' + mod.name + ' — INTELLIGENCE RESULTS</span>\n';

  switch (moduleId) {
    case 'dns':         html += renderDNS(data); break;
    case 'subdomains':  html += renderSubdomains(data); break;
    case 'whois':       html += renderWhois(data); break;
    case 'headers':     html += renderHeaders(data); break;
    case 'ssl':         html += renderSSL(data); break;
    case 'tech':        html += renderTech(data); break;
    case 'ports':       html += renderPorts(data); break;
    case 'security':    html += renderSecurity(data); break;
    case 'reverse_dns': html += renderReverseDNS(data); break;
    case 'geo':         html += renderGeo(data); break;
    case 'robots':      html += renderRobots(data); break;
    default:
      html += '<span class="line-value">' + escapeHtml(JSON.stringify(data, null, 2)) + '</span>';
  }

  output.innerHTML = html;
}

function renderDNS(data) {
  let h = '';
  ['A','AAAA','MX','NS','TXT','CNAME','SOA','SRV','CAA'].forEach(t => {
    if (data[t] && data[t].length > 0) {
      h += '\n<span class="line-key">  ┌─ [' + t + ']</span>\n';
      data[t].forEach((r, i) => {
        const pre = i === data[t].length - 1 ? '└' : '├';
        h += '  <span class="line-value">  ' + pre + '─ ' + escapeHtml(r) + '</span>\n';
      });
    }
  });
  if (data._raw) {
    h += '\n<span class="line-header">RAW OUTPUT</span>\n<span class="line-value">' + escapeHtml(data._raw) + '</span>\n';
  }
  return h || '<span class="line-comment">  No DNS records found</span>';
}

function renderSubdomains(data) {
  let h = '';
  if (Array.isArray(data) && data.length > 0) {
    h += '<span class="badge-found">  ✓ Discovered ' + data.length + ' subdomain(s)</span>\n\n';
    data.forEach((s, i) => {
      const num = String(i + 1).padStart(3, '0');
      h += '  <span class="line-key">[' + num + ']</span> <span class="line-value">' + escapeHtml((s.subdomain || '').padEnd(38)) + '</span>';
      h += '<span class="badge-found"> → ' + escapeHtml(s.ip || '') + '</span>\n';
    });
  } else {
    h += '<span class="line-comment">  No subdomains discovered</span>';
  }
  return h;
}

function renderWhois(data) {
  const text = data.data || (typeof data === 'string' ? data : JSON.stringify(data, null, 2));
  const highlighted = escapeHtml(text)
    .replace(/(Domain Name|Registrar|Creation Date|Updated Date|Registry Expiry Date|Registrant|Name Server|DNSSEC|Status)[:\s]/gi,
      '<span class="line-key">$1</span>: ');
  return '<span class="line-value">' + highlighted + '</span>';
}

function renderHeaders(data) {
  let h = '';
  if (data.scheme) {
    h += '<span class="line-key">  Protocol:</span> <span class="badge-found">' + data.scheme.toUpperCase() + '</span>\n\n';
  }
  if (data.headers) {
    data.headers.split('\n').forEach(line => {
      const parts = line.split(':');
      if (parts.length >= 2) {
        h += '<span class="line-key">  ' + escapeHtml(parts[0]) + ':</span> <span class="line-value">' + escapeHtml(parts.slice(1).join(':').trim()) + '</span>\n';
      } else if (line.trim()) {
        h += '<span class="line-value">  ' + escapeHtml(line) + '</span>\n';
      }
    });
  }
  if (data.error) h += '<span class="line-error">  ' + escapeHtml(data.error) + '</span>';
  return h;
}

function renderSSL(data) {
  let h = '';
  if (data.expiry) h += '<span class="line-key">  Expiry:</span> <span class="line-value">' + escapeHtml(data.expiry) + '</span>\n\n';
  if (data.certificate) {
    const cert = escapeHtml(data.certificate);
    h += '<span class="line-value">' + cert.replace(/(Issuer|Subject|Not Before|Not After|Serial Number|Signature Algorithm|Public Key Algorithm|DNS)[:\s]/g,
      '<span class="line-key">$1</span>: ') + '</span>';
  }
  return h || '<span class="line-comment">  No SSL certificate data</span>';
}

function renderTech(data) {
  let h = '';
  const techs = Array.isArray(data) ? data : [];
  if (techs.length > 0) {
    h += '<span class="badge-found">  ✓ Detected ' + techs.length + ' technolog' + (techs.length > 1 ? 'ies' : 'y') + '</span>\n\n';
    techs.forEach(tech => {
      h += '  <span class="line-key">  ⬡</span> <span class="line-value">' + escapeHtml(tech) + '</span>\n';
    });
  } else {
    h += '<span class="line-comment">  No technologies detected (possible obfuscation)</span>';
  }
  return h;
}

function renderPorts(data) {
  let h = '';
  if (data.ip) {
    h += '<span class="line-key">  Target IP:</span> <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
    h += '<span class="line-key">  Scanned:</span>   <span class="line-value">' + (data.total_scanned || 20) + ' ports</span>\n\n';
  }
  if (data.ports && data.ports.length > 0) {
    h += '<span class="badge-found">  ✓ ' + data.ports.length + ' open port(s)</span>\n\n';
    data.ports.forEach(p => {
      h += '  <span class="line-key">  ⚡ ' + String(p.port).padEnd(8) + '</span>';
      h += '<span class="line-value">' + (p.service || '').padEnd(14) + '</span>';
      h += '<span class="badge-open">' + p.state + '</span>\n';
    });
  } else {
    h += '<span class="line-comment">  No open ports detected (firewall active)</span>';
  }
  return h;
}

function renderSecurity(data) {
  let h = '';
  if (data.score) {
    const gc = data.grade && data.grade.startsWith('A') ? 'grade-a' :
               data.grade === 'B' ? 'grade-b' :
               data.grade === 'C' ? 'grade-c' :
               data.grade === 'D' ? 'grade-d' : 'grade-f';
    h += '<span class="line-key">  Security Score:</span> <span class="line-value">' + data.score + '</span>';
    h += ' <span class="badge-grade ' + gc + '">' + data.grade + '</span>\n\n';
  }
  if (data.found && Object.keys(data.found).length > 0) {
    h += '<span class="line-header">  ✓ PRESENT HEADERS</span>\n';
    Object.entries(data.found).forEach(([k, v]) => {
      h += '  <span class="badge-found">  ✓ ' + escapeHtml(k) + '</span>\n';
      h += '    <span class="line-sub">' + escapeHtml(v) + '</span>\n';
    });
  }
  if (data.missing && data.missing.length > 0) {
    h += '\n<span class="line-header">  ✗ MISSING HEADERS</span>\n';
    data.missing.forEach(mh => {
      h += '  <span class="badge-missing">  ✗ ' + escapeHtml(mh) + '</span>\n';
    });
  }
  return h;
}

function renderReverseDNS(data) {
  let h = '';
  h += '<span class="line-key">  Domain:</span>     <span class="line-value">' + escapeHtml(data.domain || '') + '</span>\n';
  h += '<span class="line-key">  IP Address:</span> <span class="line-value">' + escapeHtml(data.ip || '') + '</span>\n';
  h += '<span class="line-key">  PTR Record:</span> <span class="line-value">' + escapeHtml(data.ptr || data.reverse || 'None') + '</span>\n';
  return h;
}

function renderGeo(data) {
  let h = '';
  if (data.status === 'success' || data.country) {
    const fields = [
      ['Resolved IP', data.resolved_ip || data.query],
      ['Country', data.country],
      ['Region', data.regionName],
      ['City', data.city],
      ['ZIP', data.zip],
      ['Latitude', data.lat],
      ['Longitude', data.lon],
      ['Timezone', data.timezone],
      ['ISP', data.isp],
      ['Organization', data.org],
      ['AS Number', data.as],
    ];
    fields.forEach(([label, val]) => {
      if (val !== undefined && val !== '') {
        h += '<span class="line-key">  ' + label.padEnd(14) + '</span> <span class="line-value">' + escapeHtml(String(val)) + '</span>\n';
      }
    });
  } else {
    h += '<span class="line-error">  Geolocation lookup failed</span>';
  }
  return h;
}

function renderRobots(data) {
  let h = '';
  if (data['robots.txt']) {
    h += '<span class="line-header">  robots.txt</span>\n';
    h += '<span class="line-value">' + escapeHtml(data['robots.txt']) + '</span>\n';
  }
  if (data['sitemap.xml']) {
    h += '\n<span class="line-header">  sitemap.xml</span>\n';
    h += '<span class="line-value">' + escapeHtml(data['sitemap.xml'].substring(0, 3000)) + '</span>\n';
  }
  if (!data['robots.txt'] && !data['sitemap.xml']) {
    h += '<span class="line-comment">  No robots.txt or sitemap.xml found</span>';
  }
  return h;
}

// ────── SUMMARY ──────
function generateSummary(domain, modules) {
  const bar = document.getElementById('stats-bar');
  const stats = [];

  stats.push({ label: 'TARGET', value: domain });
  stats.push({ label: 'MODULES', value: modules.length });

  if (scanResults.subdomains && Array.isArray(scanResults.subdomains))
    stats.push({ label: 'SUBDOMAINS', value: scanResults.subdomains.length });

  if (scanResults.ports && scanResults.ports.ports)
    stats.push({ label: 'OPEN PORTS', value: scanResults.ports.ports.length });

  if (scanResults.security && scanResults.security.grade)
    stats.push({ label: 'SEC GRADE', value: scanResults.security.grade });

  if (scanResults.tech && Array.isArray(scanResults.tech))
    stats.push({ label: 'TECH', value: scanResults.tech.length });

  if (scanResults.geo && scanResults.geo.country)
    stats.push({ label: 'LOCATION', value: scanResults.geo.country });

  stats.push({ label: 'TIMESTAMP', value: new Date().toISOString().split('T')[0] });

  bar.innerHTML = stats.map(s => `
    <div class="stat-block">
      <span class="stat-block-val">${escapeHtml(String(s.value))}</span>
      <span class="stat-block-label">${s.label}</span>
    </div>
  `).join('');
}

// ────── ACTIONS ──────
function copyResults() {
  if (!currentTab || !scanResults[currentTab]) return;
  const text = document.getElementById('terminal-output').innerText;
  if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
  const ta = document.createElement('textarea');
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand('copy'); } catch(e) {}
  document.body.removeChild(ta);

  const btns = document.querySelectorAll('.act-btn');
  if (btns[0]) {
    const orig = btns[0].textContent;
    btns[0].textContent = '✓ COPIED';
    setTimeout(() => btns[0].textContent = orig, 2000);
  }
}

function exportJSON() {
  const json = JSON.stringify(scanResults, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const domain = document.getElementById('target-input').value.trim().replace(/[^a-z0-9.-]/gi, '_');
  a.href = url;
  a.download = `scanwebs_${domain}_${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  const btns = document.querySelectorAll('.act-btn');
  if (btns[1]) {
    const orig = btns[1].textContent;
    btns[1].textContent = '✓ EXPORTED';
    setTimeout(() => btns[1].textContent = orig, 2000);
  }
}

function newScan() {
  document.getElementById('results').style.display = 'none';
  document.getElementById('scan-progress').classList.remove('active');
  document.getElementById('progress-fill').style.width = '0%';
  document.getElementById('target-input').value = '';
  document.getElementById('target-input').focus();
  document.getElementById('scanner').scrollIntoView({ behavior: 'smooth' });
  scanResults = {};
  currentTab = null;
}

// ────── UTILITIES ──────
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ────── ENTER KEY ──────
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('target-input');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !isScanning) startScan();
    });
  }
});

// ────── INIT ──────
window.addEventListener('DOMContentLoaded', () => {
  initMatrixRain();
  typewriterEffect();
  generateModuleIcons();
  generateModuleToggles();
  initScrollReveal();
});
