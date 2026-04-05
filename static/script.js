/* ═══════════════════════════════════════════════════════════
   DDOS_F16 SCANWEBS v7.0 — 25 Module Engine
   Old design restored + quantum upgrade
   ═══════════════════════════════════════════════════════════ */

// ────── SVG ICONS ──────
const ICONS = {
  dns: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3.6 9h16.8M3.6 15h16.8"/><path d="M12 3a15 15 0 010 18M12 3a15 15 0 000 18"/></svg>',
  subdomains: '<svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M12 7v4l-6 6M12 11l6 6"/></svg>',
  whois: '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M12 8h.01M8 12h8M8 16h6"/></svg>',
  headers: '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h10"/><circle cx="19" cy="17" r="2"/></svg>',
  ssl: '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/><circle cx="12" cy="16" r="1" fill="currentColor"/></svg>',
  tech: '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9h.01M15 9h.01M9 15h.01M15 15h.01"/><path d="M9 4v16M15 4v16M4 9h16M4 15h16"/></svg>',
  ports: '<svg viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
  security: '<svg viewBox="0 0 24 24"><path d="M12 2l7 4v5c0 5.25-3.5 9.74-7 11-3.5-1.26-7-5.75-7-11V6l7-4z"/><path d="M9 12l2 2 4-4"/></svg>',
  reverse_dns: '<svg viewBox="0 0 24 24"><path d="M9 14l-4 4 4 4"/><path d="M5 18h14a2 2 0 002-2V8"/><path d="M15 10l4-4-4-4"/><path d="M19 6H5a2 2 0 00-2 2v8"/></svg>',
  geo: '<svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  robots: '<svg viewBox="0 0 24 24"><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"/><path d="M9 13h6M9 17h4"/></svg>',
  email_sec: '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4l-10 8L2 4"/><path d="M17 15l2 2 4-4" stroke="#00ff41" stroke-width="2"/></svg>',
  trace: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="5" fill="none"/><circle cx="12" cy="12" r="9" fill="none"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>',
  cloud: '<svg viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 109 20h9a5 5 0 000-10z"/></svg>',
  waf: '<svg viewBox="0 0 24 24"><path d="M12 2l7 4v5c0 5.25-3.5 9.74-7 11-3.5-1.26-7-5.75-7-11V6l7-4z"/><path d="M8 12h8M8 8h8M8 16h8"/></svg>',
  js_analysis: '<svg viewBox="0 0 24 24"><path d="M4 4h16v16H4z" rx="2"/><path d="M8 12v4c0 1 1 2 2 2s2-1 2-2"/><path d="M14 10c1 0 2 .5 2 2s-1 2-2 2 2 .5 2 2-1 2-2 2"/></svg>',
  links: '<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>',
  cms: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>',
  cors: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>',
  redirect: '<svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>',
  cookies: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="8" cy="9" r="1" fill="currentColor"/><circle cx="15" cy="8" r="1" fill="currentColor"/><circle cx="10" cy="14" r="1" fill="currentColor"/><circle cx="15" cy="14" r="1" fill="currentColor"/></svg>',
  takeover: '<svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
  reputation: '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M9 15l2 2 4-4"/></svg>',
  full_scan: '<svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
  export_report: '<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
};

// ────── MODULE DEFINITIONS (25 modules, 6 categories) ──────
const MODULES = [
  // DNS Intelligence
  { id: 'dns',         name: 'DNS_RECON',        cat: 'dns_intel',      desc: 'Full DNS record enumeration (A/AAAA/MX/NS/TXT/SOA/CAA)' },
  { id: 'subdomains',  name: 'SUBDOMAIN_HUNTER', cat: 'dns_intel',      desc: 'Multi-source: crt.sh + brute-force + Web Archive' },
  { id: 'reverse_dns', name: 'REVERSE_DNS',      cat: 'dns_intel',      desc: 'PTR record & reverse IP resolution' },
  { id: 'email_sec',   name: 'EMAIL_SECURITY',   cat: 'dns_intel',      desc: 'SPF/DKIM/DMARC audit' },
  // Infrastructure
  { id: 'ports',       name: 'PORT_SCANNER_PRO', cat: 'infrastructure', desc: 'Scan 30 critical ports with service detection' },
  { id: 'trace',       name: 'NETWORK_TRACE',    cat: 'infrastructure', desc: 'Traceroute & hop analysis' },
  { id: 'cloud',       name: 'CLOUD_INFRA',      cat: 'infrastructure', desc: 'AWS/Azure/GCP/Cloudflare detection' },
  { id: 'geo',         name: 'GEOIP_ADVANCED',   cat: 'infrastructure', desc: 'Geolocation, ISP, ASN data' },
  // Web Analysis
  { id: 'waf',         name: 'WAF_DETECTION',    cat: 'web_analysis',   desc: 'Detect WAF/CDN (Cloudflare, AWS, etc.)' },
  { id: 'tech',        name: 'TECH_STACK_XRAY',  cat: 'web_analysis',   desc: 'Detect 50+ CMS/frameworks/libraries' },
  { id: 'headers',     name: 'HTTP_FINGERPRINT', cat: 'web_analysis',   desc: 'Server headers & redirect chain' },
  { id: 'js_analysis', name: 'JS_ANALYZER',      cat: 'web_analysis',   desc: 'JavaScript files, APIs, secrets detection' },
  { id: 'links',       name: 'LINK_EXTRACTOR',   cat: 'web_analysis',   desc: 'All links, forms, and resources' },
  { id: 'cms',         name: 'CMS_SCANNER',      cat: 'web_analysis',   desc: 'WordPress/Joomla/Drupal version detection' },
  // Security Audit
  { id: 'ssl',         name: 'SSL_TLS_AUDIT',    cat: 'security',       desc: 'Certificate chain, ciphers, vulnerabilities' },
  { id: 'security',    name: 'SEC_HEADERS',      cat: 'security',       desc: 'Audit 12 security headers (A+ to F grade)' },
  { id: 'cors',        name: 'CORS_CHECK',       cat: 'security',       desc: 'CORS misconfiguration detection' },
  { id: 'redirect',    name: 'OPEN_REDIRECT',    cat: 'security',       desc: 'Open redirect vulnerability scan' },
  { id: 'cookies',     name: 'COOKIE_ANALYZER',  cat: 'security',       desc: 'Cookie flags, security attributes' },
  { id: 'takeover',    name: 'SUB_TAKEOVER',     cat: 'security',       desc: 'Subdomain takeover detection' },
  // Intelligence
  { id: 'whois',       name: 'WHOIS_INTEL',      cat: 'intelligence',   desc: 'Registrar, registrant, dates, DNSSEC' },
  { id: 'reputation',  name: 'DOMAIN_REPUTATION',cat: 'intelligence',   desc: 'Check 10+ blacklists & threat feeds' },
  { id: 'robots',      name: 'ROBOTS_SITEMAP',   cat: 'intelligence',   desc: 'robots.txt & sitemap extraction' },
  // Full Scan
  { id: 'full_scan',   name: 'FULL_RECON',       cat: 'full_scan',      desc: 'Execute ALL modules at once' },
  { id: 'export_report', name: 'EXPORT_REPORT',  cat: 'full_scan',      desc: 'Download full JSON/TXT report' }
];

const CAT_LABELS = {
  dns_intel: '🔍 DNS INTELLIGENCE',
  infrastructure: '🏗 INFRASTRUCTURE',
  web_analysis: '🌐 WEB ANALYSIS',
  security: '🔐 SECURITY AUDIT',
  intelligence: '📋 INTELLIGENCE',
  full_scan: '⚡ FULL SCAN'
};

let scanResults = {};
let currentTab = null;
let isScanning = false;

// ────── MATRIX RAIN ──────
function initMatrixRain() {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
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

// ────── TYPEWRITER ──────
function typewriterEffect() {
  const el = document.getElementById('hero-subtitle');
  if (!el) return;
  const text = 'SCANWEBS QUANTUM INTELLIGENCE v7.0 — 25 MODULES ONLINE';
  let i = 0;
  function type() {
    if (i <= text.length) { el.textContent = text.substring(0, i); i++; setTimeout(type, 40 + Math.random() * 30); }
  }
  setTimeout(type, 800);
}

// ────── SCROLL REVEAL ──────
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
  document.querySelectorAll('.reveal, .reveal-fade').forEach(el => observer.observe(el));
}

// ────── GENERATE MODULE ICONS ──────
function generateModuleIcons() {
  const strip = document.getElementById('modules-strip');
  const scanModules = MODULES.filter(m => m.id !== 'full_scan' && m.id !== 'export_report');
  scanModules.forEach((mod, i) => {
    const item = document.createElement('div');
    item.className = 'module-icon-item';
    item.style.transitionDelay = (i * 80) + 'ms';
    item.innerHTML = `
      <div class="icon-circle">${ICONS[mod.id]}</div>
      <span class="module-icon-label">${mod.name}</span>
      <span class="module-icon-status">ONLINE</span>
    `;
    strip.appendChild(item);
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { setTimeout(() => item.classList.add('visible'), i * 80); obs.disconnect(); } });
    }, { threshold: 0.1 });
    obs.observe(item);
  });
}

// ────── GENERATE MODULE TOGGLES ──────
function generateModuleToggles() {
  const container = document.getElementById('module-toggles-strip');
  let lastCat = '';
  const scanModules = MODULES.filter(m => m.id !== 'full_scan' && m.id !== 'export_report');
  scanModules.forEach(mod => {
    if (mod.cat !== lastCat) {
      lastCat = mod.cat;
      const label = document.createElement('div');
      label.className = 'mod-toggle-cat-label';
      label.textContent = CAT_LABELS[mod.cat] || mod.cat;
      container.appendChild(label);
    }
    const toggle = document.createElement('label');
    toggle.className = 'mod-toggle selected';
    toggle.dataset.id = mod.id;
    toggle.dataset.cat = mod.cat;
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
    cb.addEventListener('change', function() { toggle.classList.toggle('selected', this.checked); });
    container.appendChild(toggle);
  });
}

function selectAll() {
  document.querySelectorAll('.mod-toggle input').forEach(cb => { cb.checked = true; cb.dispatchEvent(new Event('change')); });
}

function deselectAll() {
  document.querySelectorAll('.mod-toggle input').forEach(cb => { cb.checked = false; cb.dispatchEvent(new Event('change')); });
}

function selectCategory(cat) {
  deselectAll();
  document.querySelectorAll('.mod-toggle').forEach(t => {
    if (t.dataset.cat === cat) {
      const cb = t.querySelector('input');
      cb.checked = true;
      cb.dispatchEvent(new Event('change'));
    }
  });
}

// ────── SCANNING ENGINE ──────
function getSelectedModules() {
  const selected = [];
  document.querySelectorAll('.mod-toggle input:checked').forEach(cb => {
    const mod = MODULES.find(m => m.id === cb.value);
    if (mod) selected.push(mod);
  });
  return selected;
}

function validateDomain(d) { return /^[a-zA-Z0-9][a-zA-Z0-9.\-]*\.[a-zA-Z]{2,}$/.test(d); }

async function runScanModule(domain, moduleId) {
  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain: domain, module: moduleId })
    });
    const data = await response.json();
    if (!response.ok) return { error: data.error || 'Server error' };
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
    setTimeout(() => { input.style.borderBottomColor = ''; input.placeholder = 'enter target domain — example.com'; }, 2000);
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

  const btn = document.getElementById('scan-btn');
  btn.querySelector('.btn-text').style.display = 'none';
  btn.querySelector('.btn-loading').style.display = 'inline';
  btn.disabled = true;
  input.disabled = true;

  const prog = document.getElementById('scan-progress');
  prog.classList.add('active');
  const status = document.getElementById('progress-status');

  const resultsSection = document.getElementById('results');
  resultsSection.style.display = '';
  const nav = document.getElementById('results-nav');
  nav.innerHTML = '';
  document.getElementById('terminal-output').innerHTML = '<span class="line-comment">// Initializing quantum reconnaissance...</span>';
  document.getElementById('stats-bar').innerHTML = '';
  document.getElementById('results-module-label').textContent = '// INITIALIZING...';

  status.innerHTML = '<span class="running">SCANNING TARGET: ' + escapeHtml(domain) + '</span>';

  // Build sidebar nav
  selectedModules.forEach(mod => {
    const navBtn = document.createElement('button');
    navBtn.className = 'nav-icon-btn';
    navBtn.id = 'nav-' + mod.id;
    navBtn.innerHTML = ICONS[mod.id] + '<span class="nav-tooltip">' + mod.name + '</span>';
    navBtn.onclick = () => switchTab(mod.id);
    nav.appendChild(navBtn);
  });

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
  if (mod) document.getElementById('results-module-label').textContent = '◈ ' + mod.name + ' — ' + mod.desc;
  renderResults(moduleId);
}

function renderResults(moduleId) {
  const output = document.getElementById('terminal-output');
  const data = scanResults[moduleId];
  const mod = MODULES.find(m => m.id === moduleId);

  if (!data) { output.innerHTML = '<span class="line-comment">// Scanning in progress...</span>'; return; }
  if (data.error) { output.innerHTML = '<span class="line-error">ERROR: ' + escapeHtml(data.error) + '</span>'; return; }

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
    case 'email_sec':   html += renderEmailSec(data); break;
    case 'trace':       html += renderTrace(data); break;
    case 'cloud':       html += renderCloud(data); break;
    case 'waf':         html += renderWAF(data); break;
    case 'js_analysis': html += renderJSAnalysis(data); break;
    case 'links':       html += renderLinks(data); break;
    case 'cms':         html += renderCMS(data); break;
    case 'cors':        html += renderCORS(data); break;
    case 'redirect':    html += renderRedirect(data); break;
    case 'cookies':     html += renderCookies(data); break;
    case 'takeover':    html += renderTakeover(data); break;
    case 'reputation':  html += renderReputation(data); break;
    default:
      html += '<span class="line-value">' + escapeHtml(JSON.stringify(data, null, 2)) + '</span>';
  }
  output.innerHTML = html;
}

// ────── RENDERERS (original 11) ──────
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
  if (data._raw) h += '\n<span class="line-header">RAW OUTPUT</span>\n<span class="line-value">' + escapeHtml(data._raw) + '</span>\n';
  return h || '<span class="line-comment">  No DNS records found</span>';
}

function renderSubdomains(data) {
  let h = '';
  const subs = data.subdomains || (Array.isArray(data) ? data : []);
  if (subs.length > 0) {
    h += '<span class="badge-found">  ✓ Discovered ' + subs.length + ' subdomain(s)</span>\n';
    if (data.sources) h += '<span class="line-comment">  Sources: ' + escapeHtml(JSON.stringify(data.sources)) + '</span>\n';
    h += '\n';
    subs.forEach((s, i) => {
      const num = String(i + 1).padStart(3, '0');
      const sub = typeof s === 'string' ? s : (s.subdomain || s);
      const ip = typeof s === 'object' ? (s.ip || '') : '';
      h += '  <span class="line-key">[' + num + ']</span> <span class="line-value">' + escapeHtml(String(sub).padEnd(38)) + '</span>';
      if (ip) h += '<span class="badge-found"> → ' + escapeHtml(ip) + '</span>';
      h += '\n';
    });
  } else {
    h += '<span class="line-comment">  No subdomains discovered</span>';
  }
  return h;
}

function renderWhois(data) {
  const text = data.data || (typeof data === 'string' ? data : JSON.stringify(data, null, 2));
  return '<span class="line-value">' + escapeHtml(text).replace(/(Domain Name|Registrar|Creation Date|Updated Date|Registry Expiry Date|Registrant|Name Server|DNSSEC|Status)[:\s]/gi, '<span class="line-key">$1</span>: ') + '</span>';
}

function renderHeaders(data) {
  let h = '';
  if (data.scheme) h += '<span class="line-key">  Protocol:</span> <span class="badge-found">' + data.scheme.toUpperCase() + '</span>\n\n';
  if (data.headers) {
    data.headers.split('\n').forEach(line => {
      const parts = line.split(':');
      if (parts.length >= 2) h += '<span class="line-key">  ' + escapeHtml(parts[0]) + ':</span> <span class="line-value">' + escapeHtml(parts.slice(1).join(':').trim()) + '</span>\n';
      else if (line.trim()) h += '<span class="line-value">  ' + escapeHtml(line) + '</span>\n';
    });
  }
  if (data.redirect_chain) {
    h += '\n<span class="line-header">  REDIRECT CHAIN</span>\n';
    data.redirect_chain.forEach((r, i) => h += '  <span class="line-key">  [' + i + ']</span> <span class="line-value">' + escapeHtml(r) + '</span>\n');
  }
  return h;
}

function renderSSL(data) {
  let h = '';
  if (data.expiry) h += '<span class="line-key">  Expiry:</span> <span class="line-value">' + escapeHtml(data.expiry) + '</span>\n\n';
  if (data.certificate) {
    h += '<span class="line-value">' + escapeHtml(data.certificate).replace(/(Issuer|Subject|Not Before|Not After|Serial Number|Signature Algorithm|Public Key Algorithm|DNS)[:\s]/g, '<span class="line-key">$1</span>: ') + '</span>';
  }
  if (data.grade) h += '\n<span class="line-key">  Grade:</span> <span class="badge-grade grade-' + data.grade[0].toLowerCase() + '">' + escapeHtml(data.grade) + '</span>';
  return h || '<span class="line-comment">  No SSL certificate data</span>';
}

function renderTech(data) {
  let h = '';
  const techs = data.technologies || (Array.isArray(data) ? data : []);
  if (techs.length > 0) {
    h += '<span class="badge-found">  ✓ Detected ' + techs.length + ' technolog' + (techs.length > 1 ? 'ies' : 'y') + '</span>\n\n';
    techs.forEach(tech => {
      const name = typeof tech === 'string' ? tech : (tech.name || tech);
      const cat = typeof tech === 'object' ? (tech.category || '') : '';
      h += '  <span class="line-key">  ⬡</span> <span class="line-value">' + escapeHtml(name) + '</span>';
      if (cat) h += ' <span class="line-comment">(' + escapeHtml(cat) + ')</span>';
      h += '\n';
    });
  } else { h += '<span class="line-comment">  No technologies detected</span>'; }
  return h;
}

function renderPorts(data) {
  let h = '';
  if (data.ip) {
    h += '<span class="line-key">  Target IP:</span> <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
    h += '<span class="line-key">  Scanned:</span>   <span class="line-value">' + (data.total_scanned || 30) + ' ports</span>\n\n';
  }
  if (data.ports && data.ports.length > 0) {
    h += '<span class="badge-found">  ✓ ' + data.ports.length + ' open port(s)</span>\n\n';
    data.ports.forEach(p => {
      h += '  <span class="line-key">  ⚡ ' + String(p.port).padEnd(8) + '</span>';
      h += '<span class="line-value">' + (p.service || '').padEnd(14) + '</span>';
      h += '<span class="badge-open">' + (p.state || 'OPEN') + '</span>';
      if (p.banner) h += ' <span class="line-comment">' + escapeHtml(p.banner) + '</span>';
      h += '\n';
    });
  } else { h += '<span class="line-comment">  No open ports detected (firewall active)</span>'; }
  return h;
}

function renderSecurity(data) {
  let h = '';
  if (data.score !== undefined) {
    const gc = data.grade && data.grade.startsWith('A') ? 'grade-a' : data.grade === 'B' ? 'grade-b' : data.grade === 'C' ? 'grade-c' : data.grade === 'D' ? 'grade-d' : 'grade-f';
    h += '<span class="line-key">  Security Score:</span> <span class="line-value">' + data.score + '/100</span>';
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
    data.missing.forEach(mh => { h += '  <span class="badge-missing">  ✗ ' + escapeHtml(mh) + '</span>\n'; });
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
    [['Resolved IP', data.resolved_ip || data.query], ['Country', data.country], ['Region', data.regionName],
     ['City', data.city], ['ZIP', data.zip], ['Latitude', data.lat], ['Longitude', data.lon],
     ['Timezone', data.timezone], ['ISP', data.isp], ['Organization', data.org], ['AS Number', data.as]
    ].forEach(([label, val]) => {
      if (val !== undefined && val !== '') h += '<span class="line-key">  ' + label.padEnd(14) + '</span> <span class="line-value">' + escapeHtml(String(val)) + '</span>\n';
    });
  } else { h += '<span class="line-error">  Geolocation lookup failed</span>'; }
  return h;
}

function renderRobots(data) {
  let h = '';
  if (data['robots.txt']) { h += '<span class="line-header">  robots.txt</span>\n<span class="line-value">' + escapeHtml(data['robots.txt']) + '</span>\n'; }
  if (data['sitemap.xml']) { h += '\n<span class="line-header">  sitemap.xml</span>\n<span class="line-value">' + escapeHtml(data['sitemap.xml'].substring(0, 3000)) + '</span>\n'; }
  if (!data['robots.txt'] && !data['sitemap.xml']) h += '<span class="line-comment">  No robots.txt or sitemap.xml found</span>';
  return h;
}

// ────── RENDERERS (new 14 modules) ──────
function renderEmailSec(data) {
  let h = '';
  ['spf', 'dmarc', 'dkim'].forEach(type => {
    const rec = data[type];
    if (rec) {
      const status = rec.found || rec.record ? 'badge-found' : 'badge-missing';
      const icon = rec.found || rec.record ? '✓' : '✗';
      h += '<span class="' + status + '">  ' + icon + ' ' + type.toUpperCase() + '</span>\n';
      if (rec.record) h += '    <span class="line-sub">' + escapeHtml(rec.record) + '</span>\n';
      if (rec.details) h += '    <span class="line-comment">' + escapeHtml(rec.details) + '</span>\n';
      h += '\n';
    }
  });
  if (data.score !== undefined) {
    h += '<span class="line-key">  Email Security Score:</span> <span class="line-value">' + data.score + '/100</span>\n';
  }
  return h || renderGeneric(data);
}

function renderTrace(data) {
  let h = '';
  if (data.hops && Array.isArray(data.hops)) {
    h += '<span class="badge-found">  ✓ ' + data.hops.length + ' hop(s) traced</span>\n\n';
    data.hops.forEach((hop, i) => {
      const num = String(i + 1).padStart(2, '0');
      h += '  <span class="line-key">  [' + num + ']</span> ';
      h += '<span class="line-value">' + escapeHtml(hop.ip || hop.host || '*').padEnd(20) + '</span>';
      if (hop.rtt) h += ' <span class="line-comment">' + escapeHtml(hop.rtt) + '</span>';
      if (hop.hostname) h += ' <span class="badge-found">(' + escapeHtml(hop.hostname) + ')</span>';
      h += '\n';
    });
  }
  return h || renderGeneric(data);
}

function renderCloud(data) {
  let h = '';
  if (data.provider) {
    h += '<span class="line-key">  Provider:</span> <span class="badge-found">' + escapeHtml(data.provider) + '</span>\n';
    if (data.cdn) h += '<span class="line-key">  CDN:</span>      <span class="line-value">' + escapeHtml(data.cdn) + '</span>\n';
    if (data.details) {
      h += '\n<span class="line-header">  DETECTION DETAILS</span>\n';
      Object.entries(data.details).forEach(([k, v]) => {
        h += '  <span class="line-key">  ' + escapeHtml(k) + ':</span> <span class="line-value">' + escapeHtml(String(v)) + '</span>\n';
      });
    }
  }
  if (data.ip_ranges) {
    h += '\n<span class="line-header">  IP RANGE MATCHES</span>\n';
    data.ip_ranges.forEach(r => { h += '  <span class="line-value">  ├─ ' + escapeHtml(r) + '</span>\n'; });
  }
  return h || renderGeneric(data);
}

function renderWAF(data) {
  let h = '';
  if (data.detected !== undefined) {
    h += '<span class="line-key">  WAF Detected:</span> <span class="' + (data.detected ? 'badge-found' : 'badge-missing') + '">' + (data.detected ? 'YES' : 'NO') + '</span>\n';
    if (data.waf_name) h += '<span class="line-key">  WAF Name:</span>     <span class="badge-found">' + escapeHtml(data.waf_name) + '</span>\n';
    if (data.evidence) {
      h += '\n<span class="line-header">  EVIDENCE</span>\n';
      data.evidence.forEach(e => { h += '  <span class="line-value">  ├─ ' + escapeHtml(e) + '</span>\n'; });
    }
  }
  return h || renderGeneric(data);
}

function renderJSAnalysis(data) {
  let h = '';
  if (data.scripts && data.scripts.length > 0) {
    h += '<span class="badge-found">  ✓ ' + data.scripts.length + ' script(s) found</span>\n\n';
    data.scripts.forEach(s => { h += '  <span class="line-key">  ⬡</span> <span class="line-value">' + escapeHtml(s) + '</span>\n'; });
  }
  if (data.apis && data.apis.length > 0) {
    h += '\n<span class="line-header">  API ENDPOINTS</span>\n';
    data.apis.forEach(a => { h += '  <span class="line-warn">  → ' + escapeHtml(a) + '</span>\n'; });
  }
  if (data.secrets && data.secrets.length > 0) {
    h += '\n<span class="line-header">  ⚠ POTENTIAL SECRETS</span>\n';
    data.secrets.forEach(s => { h += '  <span class="line-error">  ⚠ ' + escapeHtml(s) + '</span>\n'; });
  }
  return h || renderGeneric(data);
}

function renderLinks(data) {
  let h = '';
  ['internal', 'external', 'resources', 'forms'].forEach(type => {
    const items = data[type];
    if (items && items.length > 0) {
      h += '<span class="line-header">  ' + type.toUpperCase() + ' (' + items.length + ')</span>\n';
      items.slice(0, 30).forEach(l => { h += '  <span class="line-value">  ├─ ' + escapeHtml(l) + '</span>\n'; });
      if (items.length > 30) h += '  <span class="line-comment">  └─ ... and ' + (items.length - 30) + ' more</span>\n';
      h += '\n';
    }
  });
  return h || renderGeneric(data);
}

function renderCMS(data) {
  let h = '';
  if (data.cms) {
    h += '<span class="line-key">  CMS Detected:</span> <span class="badge-found">' + escapeHtml(data.cms) + '</span>\n';
    if (data.version) h += '<span class="line-key">  Version:</span>      <span class="line-value">' + escapeHtml(data.version) + '</span>\n';
    if (data.themes) {
      h += '\n<span class="line-header">  THEMES</span>\n';
      data.themes.forEach(t => { h += '  <span class="line-value">  ├─ ' + escapeHtml(t) + '</span>\n'; });
    }
    if (data.plugins) {
      h += '\n<span class="line-header">  PLUGINS</span>\n';
      data.plugins.forEach(p => { h += '  <span class="line-value">  ├─ ' + escapeHtml(p) + '</span>\n'; });
    }
  } else { h += '<span class="line-comment">  No CMS detected</span>'; }
  return h;
}

function renderCORS(data) {
  let h = '';
  if (data.vulnerable !== undefined) {
    h += '<span class="line-key">  CORS Status:</span> <span class="' + (data.vulnerable ? 'line-error' : 'badge-found') + '">' + (data.vulnerable ? '⚠ VULNERABLE' : '✓ SECURE') + '</span>\n\n';
    if (data.headers) {
      Object.entries(data.headers).forEach(([k, v]) => {
        h += '<span class="line-key">  ' + escapeHtml(k) + ':</span> <span class="line-value">' + escapeHtml(v) + '</span>\n';
      });
    }
    if (data.tests) {
      h += '\n<span class="line-header">  TESTS</span>\n';
      data.tests.forEach(t => {
        const icon = t.vulnerable ? '⚠' : '✓';
        const cls = t.vulnerable ? 'line-error' : 'badge-found';
        h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(t.test || t.name || '') + '</span>\n';
        if (t.details) h += '    <span class="line-sub">' + escapeHtml(t.details) + '</span>\n';
      });
    }
  }
  return h || renderGeneric(data);
}

function renderRedirect(data) {
  let h = '';
  if (data.vulnerable !== undefined) {
    h += '<span class="line-key">  Status:</span> <span class="' + (data.vulnerable ? 'line-error' : 'badge-found') + '">' + (data.vulnerable ? '⚠ VULNERABLE' : '✓ SECURE') + '</span>\n\n';
  }
  if (data.tests && data.tests.length > 0) {
    h += '<span class="line-header">  REDIRECT TESTS</span>\n';
    data.tests.forEach(t => {
      const icon = t.vulnerable ? '⚠' : '✓';
      const cls = t.vulnerable ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(t.payload || t.test || '') + '</span>\n';
      if (t.location) h += '    <span class="line-sub">→ ' + escapeHtml(t.location) + '</span>\n';
    });
  }
  return h || renderGeneric(data);
}

function renderCookies(data) {
  let h = '';
  if (data.cookies && data.cookies.length > 0) {
    h += '<span class="badge-found">  ✓ ' + data.cookies.length + ' cookie(s) found</span>\n\n';
    data.cookies.forEach(c => {
      h += '<span class="line-key">  ┌─ ' + escapeHtml(c.name) + '</span>\n';
      if (c.value) h += '  <span class="line-value">  │  Value: ' + escapeHtml(c.value.substring(0, 60)) + (c.value.length > 60 ? '...' : '') + '</span>\n';
      h += '  <span class="' + (c.secure ? 'badge-found' : 'badge-missing') + '">  │  Secure: ' + (c.secure ? 'YES' : 'NO') + '</span>\n';
      h += '  <span class="' + (c.httponly ? 'badge-found' : 'badge-missing') + '">  │  HttpOnly: ' + (c.httponly ? 'YES' : 'NO') + '</span>\n';
      if (c.samesite) h += '  <span class="line-value">  │  SameSite: ' + escapeHtml(c.samesite) + '</span>\n';
      h += '  <span class="line-value">  └─────────</span>\n\n';
    });
  } else { h += '<span class="line-comment">  No cookies found</span>'; }
  if (data.score !== undefined) h += '\n<span class="line-key">  Cookie Security Score:</span> <span class="line-value">' + data.score + '/100</span>';
  return h;
}

function renderTakeover(data) {
  let h = '';
  if (data.results && data.results.length > 0) {
    h += '<span class="badge-found">  Checked ' + data.results.length + ' subdomain(s)</span>\n\n';
    data.results.forEach(r => {
      const icon = r.vulnerable ? '⚠' : '✓';
      const cls = r.vulnerable ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(r.subdomain || r.domain || '') + '</span>';
      if (r.cname) h += ' <span class="line-comment">→ ' + escapeHtml(r.cname) + '</span>';
      if (r.service) h += ' <span class="line-warn">[' + escapeHtml(r.service) + ']</span>';
      h += '\n';
    });
  }
  if (data.vulnerable_count !== undefined) {
    h += '\n<span class="line-key">  Vulnerable:</span> <span class="' + (data.vulnerable_count > 0 ? 'line-error' : 'badge-found') + '">' + data.vulnerable_count + '</span>\n';
  }
  return h || renderGeneric(data);
}

function renderReputation(data) {
  let h = '';
  if (data.score !== undefined) {
    const gc = data.score >= 80 ? 'grade-a' : data.score >= 60 ? 'grade-b' : data.score >= 40 ? 'grade-c' : 'grade-f';
    h += '<span class="line-key">  Reputation Score:</span> <span class="line-value">' + data.score + '/100</span> <span class="badge-grade ' + gc + '">' + (data.grade || '') + '</span>\n\n';
  }
  if (data.blacklists) {
    h += '<span class="line-header">  BLACKLIST CHECK</span>\n';
    data.blacklists.forEach(bl => {
      const icon = bl.listed ? '⚠' : '✓';
      const cls = bl.listed ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(bl.name || bl.source || '') + '</span>\n';
    });
  }
  return h || renderGeneric(data);
}

function renderGeneric(data) {
  return '<span class="line-value">' + escapeHtml(JSON.stringify(data, null, 2)) + '</span>';
}

// ────── SUMMARY ──────
function generateSummary(domain, modules) {
  const bar = document.getElementById('stats-bar');
  const stats = [{ label: 'TARGET', value: domain }, { label: 'MODULES', value: modules.length }];
  if (scanResults.subdomains) {
    const subs = scanResults.subdomains.subdomains || (Array.isArray(scanResults.subdomains) ? scanResults.subdomains : []);
    if (subs.length) stats.push({ label: 'SUBDOMAINS', value: subs.length });
  }
  if (scanResults.ports && scanResults.ports.ports) stats.push({ label: 'OPEN PORTS', value: scanResults.ports.ports.length });
  if (scanResults.security && scanResults.security.grade) stats.push({ label: 'SEC GRADE', value: scanResults.security.grade });
  if (scanResults.tech) {
    const techs = scanResults.tech.technologies || (Array.isArray(scanResults.tech) ? scanResults.tech : []);
    if (techs.length) stats.push({ label: 'TECH', value: techs.length });
  }
  if (scanResults.geo && scanResults.geo.country) stats.push({ label: 'LOCATION', value: scanResults.geo.country });
  if (scanResults.reputation && scanResults.reputation.score !== undefined) stats.push({ label: 'REPUTATION', value: scanResults.reputation.score + '/100' });
  stats.push({ label: 'TIMESTAMP', value: new Date().toISOString().split('T')[0] });
  bar.innerHTML = stats.map(s => `<div class="stat-block"><span class="stat-block-val">${escapeHtml(String(s.value))}</span><span class="stat-block-label">${s.label}</span></div>`).join('');
}

// ────── ACTIONS ──────
function copyResults() {
  if (!currentTab || !scanResults[currentTab]) return;
  const text = document.getElementById('terminal-output').innerText;
  if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
  const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); } catch(e) {}
  document.body.removeChild(ta);
  const btns = document.querySelectorAll('.act-btn');
  if (btns[0]) { const orig = btns[0].textContent; btns[0].textContent = '✓ COPIED'; setTimeout(() => btns[0].textContent = orig, 2000); }
}

function exportJSON() {
  const json = JSON.stringify(scanResults, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const domain = document.getElementById('target-input').value.trim().replace(/[^a-z0-9.-]/gi, '_');
  a.href = url; a.download = `scanwebs_${domain}_${Date.now()}.json`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
  const btns = document.querySelectorAll('.act-btn');
  if (btns[1]) { const orig = btns[1].textContent; btns[1].textContent = '✓ EXPORTED'; setTimeout(() => btns[1].textContent = orig, 2000); }
}

function newScan() {
  document.getElementById('results').style.display = 'none';
  document.getElementById('scan-progress').classList.remove('active');
  document.getElementById('progress-fill').style.width = '0%';
  document.getElementById('target-input').value = '';
  document.getElementById('target-input').focus();
  document.getElementById('scanner').scrollIntoView({ behavior: 'smooth' });
  scanResults = {}; currentTab = null;
}

// ────── UTILITIES ──────
function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ────── ENTER KEY ──────
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('target-input');
  if (input) input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !isScanning) startScan(); });
});

// ────── INIT ──────
window.addEventListener('DOMContentLoaded', () => {
  initMatrixRain();
  typewriterEffect();
  generateModuleIcons();
  generateModuleToggles();
  initScrollReveal();
});
