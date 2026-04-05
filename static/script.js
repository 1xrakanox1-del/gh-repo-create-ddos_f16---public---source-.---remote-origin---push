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
  shodan: '<svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  info_leak: '<svg viewBox="0 0 24 24"><path d="M14 3v4a1 1 0 001 1h4"/><path d="M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h7l5 5v11a2 2 0 01-2 2z"/><path d="M9 13h6M9 17h4"/></svg>',
  email_sec: '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4l-10 8L2 4"/><path d="M17 15l2 2 4-4" stroke="#00ff41" stroke-width="2"/></svg>',
  wayback: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="5" fill="none"/><circle cx="12" cy="12" r="9" fill="none"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2"/></svg>',
  cloud: '<svg viewBox="0 0 24 24"><path d="M18 10h-1.26A8 8 0 109 20h9a5 5 0 000-10z"/></svg>',
  waf: '<svg viewBox="0 0 24 24"><path d="M12 2l7 4v5c0 5.25-3.5 9.74-7 11-3.5-1.26-7-5.75-7-11V6l7-4z"/><path d="M8 12h8M8 8h8M8 16h8"/></svg>',
  threat_intel: '<svg viewBox="0 0 24 24"><path d="M4 4h16v16H4z" rx="2"/><path d="M8 12v4c0 1 1 2 2 2s2-1 2-2"/><path d="M14 10c1 0 2 .5 2 2s-1 2-2 2 2 .5 2 2-1 2-2 2"/></svg>',
  sensitive_paths: '<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>',
  cve_hunter: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>',
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
  { id: 'wayback',     name: 'WAYBACK_RECON',    cat: 'infrastructure', desc: 'Historical URLs + Hidden endpoints + Config files' },
  { id: 'cloud',       name: 'CLOUD_INFRA',      cat: 'infrastructure', desc: 'AWS/Azure/GCP/Cloudflare detection' },
  { id: 'shodan',      name: 'SHODAN_INTEL',     cat: 'infrastructure', desc: 'Real CVEs + Open ports + CPEs from Shodan' },
  // Web Analysis
  { id: 'waf',         name: 'WAF_DETECTION',    cat: 'web_analysis',   desc: 'Detect WAF/CDN (Cloudflare, AWS, etc.)' },
  { id: 'tech',            name: 'DEEP_TECH_FP',     cat: 'web_analysis',   desc: '200+ signatures - CMS + Frameworks + Analytics' },
  { id: 'headers',         name: 'HTTP_FINGERPRINT', cat: 'web_analysis',   desc: 'Server headers & redirect chain' },
  { id: 'threat_intel',    name: 'THREAT_INTEL',     cat: 'intelligence',   desc: 'AlienVault OTX: Threat pulses + Malware + MITRE ATT&CK' },
  { id: 'sensitive_paths', name: 'PATH_SCANNER',     cat: 'security',       desc: '120+ paths: .git, .env, backups, admin panels' },
  { id: 'cve_hunter',     name: 'CVE_HUNTER',       cat: 'security',       desc: 'Real CVE lookup + CVSS scores + Exploits' },
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
  { id: 'info_leak',    name: 'INFO_LEAK_DETECT', cat: 'intelligence',   desc: 'HTML comments + Secrets + Source maps + Error pages' },
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
    case 'tech':        html += renderDeepTech(data); break;
    case 'ports':       html += renderPorts(data); break;
    case 'security':    html += renderSecurity(data); break;
    case 'reverse_dns': html += renderReverseDNS(data); break;
    case 'shodan':      html += renderShodan(data); break;
    case 'info_leak':   html += renderInfoLeak(data); break;
    case 'email_sec':   html += renderEmailSec(data); break;
    case 'wayback':     html += renderWayback(data); break;
    case 'cloud':       html += renderCloud(data); break;
    case 'waf':         html += renderWAF(data); break;
    case 'threat_intel': html += renderThreatIntel(data); break;
    case 'sensitive_paths': html += renderSensitivePaths(data); break;
    case 'cve_hunter':  html += renderCveHunter(data); break;
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

// ────── RENDERERS — MATCHED TO BACKEND OUTPUT ──────
function renderDNS(data) {
  let h = '';
  // Backend returns data.records = { A: [...], AAAA: [...], ... }
  const records = data.records || data;
  ['A','AAAA','MX','NS','TXT','CNAME','SOA','SRV','CAA','PTR'].forEach(t => {
    const recs = records[t] || data[t];
    if (recs && recs.length > 0) {
      h += '\n<span class="line-key">  ┌─ [' + t + ']</span>\n';
      recs.forEach((r, i) => {
        const pre = i === recs.length - 1 ? '└' : '├';
        h += '  <span class="line-value">  ' + pre + '─ ' + escapeHtml(r) + '</span>\n';
      });
    }
  });
  // DNSSEC
  if (data.dnssec) h += '\n<span class="line-key">  DNSSEC:</span> <span class="line-value">' + escapeHtml(data.dnssec) + '</span>\n';
  // Zone Transfer
  if (data.zone_transfer && Array.isArray(data.zone_transfer) && data.zone_transfer.length > 0) {
    h += '\n<span class="line-header">  ZONE TRANSFER</span>\n';
    data.zone_transfer.forEach(zt => {
      const icon = zt.status === 'VULNERABLE' ? '⚠' : '✓';
      const cls = zt.status === 'VULNERABLE' ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(zt.nameserver || '') + ' — ' + escapeHtml(zt.status || '') + '</span>\n';
      if (zt.records_leaked) h += '    <span class="line-warn">  Records leaked: ' + zt.records_leaked + '</span>\n';
    });
  }
  // Stats
  if (data.stats) {
    h += '\n<span class="line-key">  Total Records:</span> <span class="line-value">' + (data.stats.total_records || 0) + '</span>\n';
    h += '<span class="line-key">  Types Found:</span>   <span class="line-value">' + (data.stats.types_found || 0) + '</span>\n';
  }
  return h || '<span class="line-comment">  No DNS records found</span>';
}

function renderSubdomains(data) {
  let h = '';
  // Backend returns data.all_subdomains (array of strings) + data.sources
  const subs = data.all_subdomains || data.subdomains || (Array.isArray(data) ? data : []);
  if (subs.length > 0) {
    h += '<span class="badge-found">  ✓ Discovered ' + subs.length + ' subdomain(s)</span>\n';
    // Source stats
    if (data.stats) {
      h += '<span class="line-comment">  Sources: crt.sh(' + (data.stats.from_crt||0) + ') + bruteforce(' + (data.stats.from_bruteforce||0) + ') + archive(' + (data.stats.from_archive||0) + ')</span>\n';
    }
    h += '\n';
    // Show brute-force results with IPs first
    const bruteResults = (data.sources && data.sources.dns_bruteforce) ? data.sources.dns_bruteforce.subdomains || [] : [];
    const bruteMap = {};
    bruteResults.forEach(b => { if (b.subdomain) bruteMap[b.subdomain] = b.ip; });
    subs.forEach((s, i) => {
      const num = String(i + 1).padStart(3, '0');
      const sub = typeof s === 'string' ? s : (s.subdomain || s);
      const ip = bruteMap[sub] || (typeof s === 'object' ? (s.ip || '') : '');
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
  let h = '';
  // Backend returns data.whois = { registrar, creation_date, ... }
  const w = data.whois || data;
  if (w.error && !w.raw) {
    return '<span class="line-error">  ' + escapeHtml(w.error) + '</span>';
  }
  if (w.raw) {
    return '<span class="line-value">' + escapeHtml(w.raw).replace(/(Domain Name|Registrar|Creation Date|Updated Date|Registry Expiry Date|Registrant|Name Server|DNSSEC|Status)[:\s]/gi, '<span class="line-key">$1</span>: ') + '</span>';
  }
  const fields = [
    ['Domain', w.domain_name], ['Registrar', w.registrar], ['Registrar URL', w.registrar_url],
    ['Created', w.creation_date], ['Expires', w.expiration_date], ['Updated', w.updated_date],
    ['Age (years)', w.domain_age_years], ['Expires in (days)', w.expires_in_days],
    ['Registrant', w.registrant], ['Organization', w.org],
    ['Country', w.country], ['State', w.state], ['City', w.city],
    ['DNSSEC', w.dnssec]
  ];
  fields.forEach(([label, val]) => {
    if (val !== undefined && val !== null && val !== 'Unknown' && val !== 'N/A' && val !== 'REDACTED') {
      h += '<span class="line-key">  ' + label.padEnd(20) + '</span> <span class="line-value">' + escapeHtml(String(val)) + '</span>\n';
    }
  });
  if (w.name_servers && w.name_servers.length) {
    h += '\n<span class="line-header">  NAME SERVERS</span>\n';
    w.name_servers.forEach(ns => { h += '  <span class="line-value">  ├─ ' + escapeHtml(ns) + '</span>\n'; });
  }
  if (w.emails && w.emails.length) {
    h += '\n<span class="line-header">  CONTACT EMAILS</span>\n';
    w.emails.forEach(e => { h += '  <span class="line-value">  ├─ ' + escapeHtml(e) + '</span>\n'; });
  }
  if (w.status && w.status.length) {
    h += '\n<span class="line-header">  STATUS</span>\n';
    (Array.isArray(w.status) ? w.status : [w.status]).forEach(s => { h += '  <span class="line-value">  ├─ ' + escapeHtml(s) + '</span>\n'; });
  }
  return h || renderGeneric(data);
}

function renderHeaders(data) {
  let h = '';
  // Backend returns data.https = { status_code, server, all_headers, ... }, data.http = { ... }, data.redirects, data.cookies
  ['https', 'http'].forEach(scheme => {
    const info = data[scheme];
    if (info && !info.error) {
      h += '<span class="line-header">  ' + scheme.toUpperCase() + ' RESPONSE</span>\n';
      h += '<span class="line-key">  Status:</span>          <span class="line-value">' + (info.status_code || 'N/A') + '</span>\n';
      h += '<span class="line-key">  Response Time:</span>   <span class="line-value">' + (info.response_time_ms || '?') + ' ms</span>\n';
      h += '<span class="line-key">  Server:</span>          <span class="badge-found">' + escapeHtml(info.server || 'Hidden') + '</span>\n';
      h += '<span class="line-key">  Powered By:</span>      <span class="line-value">' + escapeHtml(info.powered_by || 'Hidden') + '</span>\n';
      h += '<span class="line-key">  Content-Type:</span>    <span class="line-value">' + escapeHtml(info.content_type || '') + '</span>\n';
      h += '<span class="line-key">  Content-Encoding:</span><span class="line-value"> ' + escapeHtml(info.content_encoding || 'None') + '</span>\n';
      h += '<span class="line-key">  Cache-Control:</span>   <span class="line-value">' + escapeHtml(info.cache_control || 'None') + '</span>\n';
      if (info.all_headers) {
        h += '\n<span class="line-header">  ALL HEADERS</span>\n';
        Object.entries(info.all_headers).forEach(([k, v]) => {
          h += '  <span class="line-key">  ' + escapeHtml(k) + ':</span> <span class="line-value">' + escapeHtml(v) + '</span>\n';
        });
      }
      h += '\n';
    } else if (info && info.error) {
      h += '<span class="line-key">  ' + scheme.toUpperCase() + ':</span> <span class="line-error">' + escapeHtml(info.error) + '</span>\n';
    }
  });
  // Redirects
  if (data.redirects && data.redirects.length > 0) {
    h += '<span class="line-header">  REDIRECT CHAIN</span>\n';
    data.redirects.forEach((r, i) => {
      if (r.final_url) {
        h += '  <span class="badge-found">  ✓ Final: ' + escapeHtml(r.final_url) + ' (' + r.final_code + ')</span>\n';
      } else {
        h += '  <span class="line-key">  [' + i + ']</span> <span class="line-value">' + escapeHtml(r.from || '') + ' → ' + escapeHtml(r.to || '') + ' (HTTP ' + (r.code || '') + ')</span>\n';
      }
    });
  }
  // Cookies
  if (data.cookies && data.cookies.length > 0) {
    h += '\n<span class="line-header">  COOKIES</span>\n';
    data.cookies.forEach(c => {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(c.name || '') + ' (Secure: ' + (c.secure ? 'Yes' : 'No') + ', HttpOnly: ' + (c.httponly ? 'Yes' : 'No') + ')</span>\n';
    });
  }
  return h || renderGeneric(data);
}

function renderSSL(data) {
  let h = '';
  // Backend: data.certificate = { subject, issuer, not_before, not_after, san, days_until_expiry, expired, ... }
  // data.grade, data.score, data.protocols, data.current_cipher, data.tls_version, data.vulnerabilities
  const cert = data.certificate || {};
  if (cert.error) {
    h += '<span class="line-error">  SSL Error: ' + escapeHtml(cert.error) + '</span>\n';
  } else {
    if (cert.subject) {
      const cn = cert.subject.commonName || cert.subject.organizationName || '';
      h += '<span class="line-key">  Common Name:</span>    <span class="line-value">' + escapeHtml(cn) + '</span>\n';
    }
    if (cert.issuer) {
      const issuer = cert.issuer.organizationName || cert.issuer.commonName || '';
      h += '<span class="line-key">  Issuer:</span>         <span class="line-value">' + escapeHtml(issuer) + '</span>\n';
    }
    h += '<span class="line-key">  Valid From:</span>     <span class="line-value">' + escapeHtml(cert.not_before || 'Unknown') + '</span>\n';
    h += '<span class="line-key">  Valid Until:</span>    <span class="line-value">' + escapeHtml(cert.not_after || 'Unknown') + '</span>\n';
    if (cert.days_until_expiry !== undefined) {
      const cls = cert.expired ? 'line-error' : (cert.days_until_expiry < 30 ? 'line-warn' : 'badge-found');
      h += '<span class="line-key">  Days Remaining:</span> <span class="' + cls + '">' + cert.days_until_expiry + (cert.expired ? ' (EXPIRED!)' : '') + '</span>\n';
    }
    if (cert.san && cert.san.length > 0) {
      h += '\n<span class="line-header">  SUBJECT ALT NAMES (' + cert.san.length + ')</span>\n';
      cert.san.slice(0, 15).forEach(s => { h += '  <span class="line-value">  ├─ ' + escapeHtml(s) + '</span>\n'; });
      if (cert.san.length > 15) h += '  <span class="line-comment">  └─ ... and ' + (cert.san.length - 15) + ' more</span>\n';
    }
  }
  // Cipher & TLS
  if (data.current_cipher) {
    h += '\n<span class="line-key">  Cipher Suite:</span>   <span class="line-value">' + escapeHtml(data.current_cipher.name || '') + '</span>\n';
    h += '<span class="line-key">  Cipher Bits:</span>    <span class="line-value">' + (data.current_cipher.bits || '') + '</span>\n';
  }
  if (data.tls_version) h += '<span class="line-key">  TLS Version:</span>    <span class="line-value">' + escapeHtml(data.tls_version) + '</span>\n';
  // Protocols
  if (data.protocols) {
    h += '\n<span class="line-header">  PROTOCOL SUPPORT</span>\n';
    Object.entries(data.protocols).forEach(([proto, supported]) => {
      const icon = supported ? '✓' : '✗';
      const cls = (proto === 'TLSv1.0' || proto === 'TLSv1.1') && supported ? 'line-error' : (supported ? 'badge-found' : 'line-comment');
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(proto) + '</span>\n';
    });
  }
  // Vulnerabilities
  if (data.vulnerabilities && data.vulnerabilities.length > 0) {
    h += '\n<span class="line-header">  ⚠ VULNERABILITIES</span>\n';
    data.vulnerabilities.forEach(v => {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(v.name || '') + ' [' + escapeHtml(v.severity || '') + ']</span>\n';
      if (v.detail) h += '    <span class="line-sub">' + escapeHtml(v.detail) + '</span>\n';
    });
  }
  // Grade
  if (data.grade) {
    const gc = data.grade.startsWith('A') ? 'grade-a' : data.grade === 'B' ? 'grade-b' : data.grade === 'C' ? 'grade-c' : data.grade === 'D' ? 'grade-d' : 'grade-f';
    h += '\n<span class="line-key">  Grade:</span> <span class="badge-grade ' + gc + '">' + escapeHtml(data.grade) + '</span>';
    if (data.score !== undefined) h += ' <span class="line-value">(' + data.score + '/100)</span>';
  }
  return h || '<span class="line-comment">  No SSL certificate data</span>';
}

function renderDeepTech(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  DEEP TECH FINGERPRINT SUMMARY</span>\n';
    h += '<span class="line-key">  Technologies:</span>    <span class="line-value">' + (data.summary.total_technologies || 0) + '</span>\n';
    h += '<span class="line-key">  Categories:</span>      <span class="line-value">' + (data.summary.categories_found || 0) + '</span>\n';
    h += '<span class="line-key">  High Confidence:</span> <span class="badge-found">' + (data.summary.high_confidence || 0) + '</span>\n\n';
  }
  if (data.total_detected !== undefined) {
    h += '<span class="badge-found">  ✓ Detected ' + data.total_detected + ' technolog' + (data.total_detected !== 1 ? 'ies' : 'y') + '</span>\n\n';
  }
  // Technologies by category
  if (data.categories && typeof data.categories === 'object') {
    Object.entries(data.categories).forEach(function([category, items]) {
      if (Array.isArray(items) && items.length > 0) {
        h += '<span class="line-header">  ' + escapeHtml(category.toUpperCase()) + '</span>\n';
        items.forEach(function(item) {
          h += '  <span class="line-key">  ⬡</span> <span class="line-value">' + escapeHtml(String(item)) + '</span>\n';
        });
        h += '\n';
      }
    });
  }
  // Detailed tech list with confidence
  if (data.technologies && Array.isArray(data.technologies) && data.technologies.length > 0) {
    h += '<span class="line-header">  DETAILED DETECTION</span>\n';
    data.technologies.forEach(function(tech) {
      const confidence = tech.confidence || 0;
      const confBar = '█'.repeat(Math.ceil(confidence / 10)) + '░'.repeat(10 - Math.ceil(confidence / 10));
      const confCls = confidence >= 80 ? 'badge-found' : confidence >= 50 ? 'line-warn' : 'line-comment';
      h += '  <span class="line-key">  ⬡ ' + escapeHtml(tech.name || 'Unknown').padEnd(22) + '</span>';
      h += '<span class="' + confCls + '">' + confBar + ' ' + confidence + '%</span>';
      if (tech.version) h += ' <span class="line-value">v' + escapeHtml(tech.version) + '</span>';
      h += '\n';
      h += '    <span class="line-comment">  Category: ' + escapeHtml(tech.category || '') + ' | Method: ' + escapeHtml(tech.method || '') + '</span>\n';
    });
  }
  return h || '<span class="line-comment">  No technologies detected</span>';
}

function renderPorts(data) {
  let h = '';
  if (data.ip) {
    h += '<span class="line-key">  Target IP:</span> <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
    h += '<span class="line-key">  Scanned:</span>   <span class="line-value">' + (data.stats ? data.stats.total_scanned : 40) + ' ports</span>\n\n';
  }
  // Backend returns data.open_ports (not data.ports)
  const ports = data.open_ports || data.ports || [];
  if (ports.length > 0) {
    h += '<span class="badge-found">  ✓ ' + ports.length + ' open port(s)</span>\n\n';
    ports.forEach(p => {
      h += '  <span class="line-key">  ⚡ ' + String(p.port).padEnd(8) + '</span>';
      h += '<span class="line-value">' + (p.service || '').padEnd(14) + '</span>';
      h += '<span class="badge-open">' + (p.status || p.state || 'OPEN') + '</span>';
      if (p.banner) h += ' <span class="line-comment">' + escapeHtml(p.banner.substring(0, 80)) + '</span>';
      h += '\n';
    });
  } else { h += '<span class="line-comment">  No open ports detected (firewall active)</span>'; }
  if (data.stats && data.stats.risk_level) {
    const cls = data.stats.risk_level === 'CRITICAL' || data.stats.risk_level === 'HIGH' ? 'line-error' : data.stats.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '\n<span class="line-key">  Risk Level:</span> <span class="' + cls + '">' + data.stats.risk_level + '</span>\n';
  }
  return h;
}

function renderSecurity(data) {
  let h = '';
  if (data.score !== undefined) {
    const gc = data.grade && data.grade.startsWith('A') ? 'grade-a' : data.grade === 'B' ? 'grade-b' : data.grade === 'C' ? 'grade-c' : data.grade === 'D' ? 'grade-d' : 'grade-f';
    h += '<span class="line-key">  Security Score:</span> <span class="line-value">' + data.score + '/100</span>';
    h += ' <span class="badge-grade ' + gc + '">' + data.grade + '</span>\n\n';
  }
  // Backend returns data.headers = { HeaderName: { value, status, quality, description }, ... }
  const hdrs = data.headers || data.found || {};
  const present = [];
  const missing = [];
  const dangerous = [];
  Object.entries(hdrs).forEach(([name, info]) => {
    if (typeof info === 'object') {
      if (info.status && info.status.includes('PRESENT')) present.push({ name, ...info });
      else if (info.status && info.status.includes('MISSING')) missing.push({ name, ...info });
      else if (info.status && info.status.includes('EXPOSED')) dangerous.push({ name, ...info });
    }
  });
  if (present.length > 0) {
    h += '<span class="line-header">  ✓ PRESENT HEADERS (' + present.length + ')</span>\n';
    present.forEach(p => {
      const qBadge = p.quality === 'STRONG' ? ' 🟢' : p.quality === 'WEAK' ? ' 🟡' : '';
      h += '  <span class="badge-found">  ✓ ' + escapeHtml(p.name) + qBadge + '</span>\n';
      if (p.value) h += '    <span class="line-sub">' + escapeHtml(String(p.value).substring(0, 150)) + '</span>\n';
    });
  }
  if (dangerous.length > 0) {
    h += '\n<span class="line-header">  ⚠ INFORMATION LEAKAGE</span>\n';
    dangerous.forEach(d => {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(d.name) + ': ' + escapeHtml(String(d.value || '')) + '</span>\n';
      if (d.description) h += '    <span class="line-sub">' + escapeHtml(d.description) + '</span>\n';
    });
  }
  // Missing headers
  const missingList = data.missing || missing.map(m => m.name);
  if (missingList && missingList.length > 0) {
    h += '\n<span class="line-header">  ✗ MISSING HEADERS (' + missingList.length + ')</span>\n';
    missingList.forEach(mh => {
      const name = typeof mh === 'string' ? mh : mh.name;
      h += '  <span class="badge-missing">  ✗ ' + escapeHtml(name) + '</span>\n';
    });
  }
  return h;
}

function renderReverseDNS(data) {
  let h = '';
  h += '<span class="line-key">  Domain:</span>     <span class="line-value">' + escapeHtml(data.domain || '') + '</span>\n';
  h += '<span class="line-key">  IP Address:</span> <span class="line-value">' + escapeHtml(data.ip || '') + '</span>\n';
  // Backend returns data.ptr as array
  const ptr = data.ptr || data.reverse || [];
  if (Array.isArray(ptr)) {
    h += '<span class="line-key">  PTR Record:</span> <span class="line-value">' + escapeHtml(ptr.join(', ') || 'None') + '</span>\n';
  } else {
    h += '<span class="line-key">  PTR Record:</span> <span class="line-value">' + escapeHtml(String(ptr)) + '</span>\n';
  }
  // Shared hosting
  if (data.shared_domains && data.shared_domains.length > 0) {
    h += '\n<span class="line-header">  SHARED HOSTING (' + data.shared_domains.length + ' domains on same IP)</span>\n';
    data.shared_domains.slice(0, 50).forEach(d => {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(d) + '</span>\n';
    });
    if (data.shared_domains.length > 50) h += '  <span class="line-comment">  └─ ... and ' + (data.shared_domains.length - 50) + ' more</span>\n';
  }
  if (data.error) h += '<span class="line-error">  ' + escapeHtml(data.error) + '</span>\n';
  return h;
}

function renderShodan(data) {
  let h = '';
  // Summary stats
  if (data.summary) {
    h += '<span class="line-header">  SHODAN INTERNETDB SUMMARY</span>\n';
    h += '<span class="line-key">  Data Source:</span>    <span class="line-value">' + escapeHtml(data.summary.data_source || 'Shodan InternetDB') + '</span>\n';
    h += '<span class="line-key">  Total Ports:</span>    <span class="line-value">' + (data.summary.total_ports || 0) + '</span>\n';
    h += '<span class="line-key">  Total CVEs:</span>     <span class="line-value">' + (data.summary.total_cves || 0) + '</span>\n';
    const riskCls = data.summary.risk_level === 'CRITICAL' || data.summary.risk_level === 'HIGH' ? 'line-error' : data.summary.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>     <span class="' + riskCls + '">' + escapeHtml(data.summary.risk_level || 'LOW') + '</span>\n\n';
  }
  // IP & Risk
  if (data.ip) h += '<span class="line-key">  IP Address:</span>    <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
  if (data.risk_score !== undefined) h += '<span class="line-key">  Risk Score:</span>    <span class="line-value">' + data.risk_score + '/100</span>\n';
  if (data.risk_level) {
    const cls = data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH' ? 'line-error' : data.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>    <span class="' + cls + '">' + escapeHtml(data.risk_level) + '</span>\n';
  }
  // Hostnames
  if (data.hostnames && data.hostnames.length > 0) {
    h += '\n<span class="line-header">  HOSTNAMES (' + data.hostnames.length + ')</span>\n';
    data.hostnames.forEach(function(host) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(host) + '</span>\n';
    });
  }
  // Open Ports
  if (data.open_ports && data.open_ports.length > 0) {
    h += '\n<span class="line-header">  OPEN PORTS (' + data.open_ports.length + ')</span>\n';
    data.open_ports.forEach(function(port) {
      const isCritical = data.exposed_critical_ports && data.exposed_critical_ports.includes(port);
      const cls = isCritical ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ⚡ Port ' + port + (isCritical ? ' ⚠ CRITICAL' : '') + '</span>\n';
    });
  }
  // Exposed Critical Ports
  if (data.exposed_critical_ports && data.exposed_critical_ports.length > 0) {
    h += '\n<span class="line-header">  ⚠ EXPOSED CRITICAL PORTS</span>\n';
    data.exposed_critical_ports.forEach(function(port) {
      h += '  <span class="line-error">  ⚠ Port ' + port + ' — Critical service exposed</span>\n';
    });
  }
  // Vulnerabilities
  if (data.vulnerabilities && data.vulnerabilities.length > 0) {
    h += '\n<span class="line-header">  ⚠ VULNERABILITIES (' + data.vulnerabilities.length + ')</span>\n';
    data.vulnerabilities.forEach(function(cve) {
      const isRecent = data.recent_cves && data.recent_cves.includes(cve);
      const cls = isRecent ? 'line-error' : 'line-warn';
      h += '  <span class="' + cls + '">  ⚠ ' + escapeHtml(cve) + (isRecent ? ' [RECENT]' : '') + '</span>\n';
    });
  }
  // CPEs
  if (data.cpes && data.cpes.length > 0) {
    h += '\n<span class="line-header">  CPE IDENTIFIERS (' + data.cpes.length + ')</span>\n';
    data.cpes.forEach(function(cpe) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(cpe) + '</span>\n';
    });
  }
  // Tags
  if (data.tags && data.tags.length > 0) {
    h += '\n<span class="line-key">  Tags:</span> <span class="line-value">' + escapeHtml(data.tags.join(', ')) + '</span>\n';
  }
  return h || '<span class="line-comment">  No Shodan data available</span>';
}

function renderInfoLeak(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  INFORMATION LEAK SUMMARY</span>\n';
    h += '<span class="line-key">  Leak Categories:</span> <span class="line-value">' + (data.summary.total_leak_categories || 0) + '</span>\n';
    const riskCls = data.summary.risk_level === 'CRITICAL' || data.summary.risk_level === 'HIGH' ? 'line-error' : data.summary.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>      <span class="' + riskCls + '">' + escapeHtml(data.summary.risk_level || 'LOW') + '</span>\n\n';
  }
  if (data.leaks_found !== undefined) h += '<span class="line-key">  Total Leaks:</span>     <span class="line-value">' + data.leaks_found + '</span>\n';
  if (data.risk_score !== undefined) h += '<span class="line-key">  Risk Score:</span>      <span class="line-value">' + data.risk_score + '/100</span>\n';
  if (data.risk_level) {
    const cls = data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH' ? 'line-error' : data.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>      <span class="' + cls + '">' + escapeHtml(data.risk_level) + '</span>\n';
  }
  // Findings overview
  if (data.findings && data.findings.length > 0) {
    h += '\n<span class="line-header">  FINDINGS (' + data.findings.length + ')</span>\n';
    data.findings.forEach(function(f) {
      const cls = f.severity === 'CRITICAL' ? 'line-error' : f.severity === 'HIGH' ? 'line-error' : f.severity === 'MEDIUM' ? 'line-warn' : 'badge-found';
      h += '  <span class="' + cls + '">  ⚠ [' + escapeHtml(f.severity || 'INFO') + '] ' + escapeHtml(f.type || '') + '</span>\n';
      if (f.detail) h += '    <span class="line-sub">' + escapeHtml(f.detail) + '</span>\n';
      if (f.count) h += '    <span class="line-comment">Count: ' + f.count + '</span>\n';
    });
  }
  // HTML Comments
  if (data.html_comments && data.html_comments.length > 0) {
    h += '\n<span class="line-header">  HTML COMMENTS (' + data.html_comments.length + ')</span>\n';
    data.html_comments.slice(0, 20).forEach(function(c) {
      const cls = c.severity === 'HIGH' || c.severity === 'CRITICAL' ? 'line-error' : 'line-warn';
      h += '  <span class="' + cls + '">  ⚠ ' + escapeHtml(c.content || '') + '</span>\n';
      if (c.trigger) h += '    <span class="line-comment">Trigger: ' + escapeHtml(c.trigger) + '</span>\n';
    });
  }
  // Meta Info
  if (data.meta_info && data.meta_info.length > 0) {
    h += '\n<span class="line-header">  META INFORMATION (' + data.meta_info.length + ')</span>\n';
    data.meta_info.forEach(function(m) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(m.name || '') + ': ' + escapeHtml(m.content || '') + '</span>\n';
    });
  }
  // Exposed Emails
  if (data.exposed_emails && data.exposed_emails.length > 0) {
    h += '\n<span class="line-header">  ⚠ EXPOSED EMAILS (' + data.exposed_emails.length + ')</span>\n';
    data.exposed_emails.forEach(function(e) {
      h += '  <span class="line-warn">  ⚠ ' + escapeHtml(e) + '</span>\n';
    });
  }
  // Exposed IPs
  if (data.exposed_ips && data.exposed_ips.length > 0) {
    h += '\n<span class="line-header">  ⚠ EXPOSED INTERNAL IPS (' + data.exposed_ips.length + ')</span>\n';
    data.exposed_ips.forEach(function(ip) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(ip) + '</span>\n';
    });
  }
  // Source Maps
  if (data.source_maps && data.source_maps.length > 0) {
    h += '\n<span class="line-header">  ⚠ SOURCE MAPS (' + data.source_maps.length + ')</span>\n';
    data.source_maps.forEach(function(sm) {
      h += '  <span class="line-warn">  ⚠ ' + escapeHtml(sm) + '</span>\n';
    });
  }
  // Server Leaks
  if (data.server_leaks && data.server_leaks.length > 0) {
    h += '\n<span class="line-header">  SERVER INFORMATION LEAKS (' + data.server_leaks.length + ')</span>\n';
    data.server_leaks.forEach(function(s) {
      h += '  <span class="line-warn">  ⚠ ' + escapeHtml(s.header || '') + ': ' + escapeHtml(s.value || '') + '</span>\n';
    });
  }
  // Error Disclosure
  if (data.error_disclosure && data.error_disclosure.length > 0) {
    h += '\n<span class="line-header">  ⚠ ERROR DISCLOSURE (' + data.error_disclosure.length + ')</span>\n';
    data.error_disclosure.forEach(function(e) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(e.type || '') + ' at ' + escapeHtml(e.url || '') + ' (HTTP ' + (e.status || '') + ')</span>\n';
    });
  }
  // Secrets Found
  if (data.secrets_found && data.secrets_found.length > 0) {
    h += '\n<span class="line-header">  ⚠ SECRETS DETECTED (' + data.secrets_found.length + ')</span>\n';
    data.secrets_found.forEach(function(s) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(s.type || 'Secret') + ' (count: ' + (s.count || 1) + ')</span>\n';
    });
  }
  return h || '<span class="line-comment">  No information leaks detected</span>';
}

// ────── RENDERERS (modules 12-25) ──────
function renderEmailSec(data) {
  let h = '';
  // Backend returns data.spf = { record, status, policy, ... }, data.dmarc = { ... }, data.dkim = { status, selectors }
  // MX
  if (data.mx && data.mx.length > 0) {
    h += '<span class="line-header">  MX SERVERS</span>\n';
    data.mx.forEach(mx => {
      h += '  <span class="line-value">  ├─ [' + mx.priority + '] ' + escapeHtml(mx.server || '') + '</span>\n';
    });
    h += '\n';
  }
  // SPF
  if (data.spf) {
    const hasSpf = data.spf.status && data.spf.status.includes('FOUND');
    h += '<span class="' + (hasSpf ? 'badge-found' : 'badge-missing') + '">  ' + (hasSpf ? '✓' : '✗') + ' SPF — ' + escapeHtml(data.spf.status || '') + '</span>\n';
    if (data.spf.record) h += '    <span class="line-sub">' + escapeHtml(data.spf.record) + '</span>\n';
    if (data.spf.policy) h += '    <span class="line-comment">Policy: ' + escapeHtml(data.spf.policy) + '</span>\n';
    h += '\n';
  }
  // DMARC
  if (data.dmarc) {
    const hasDmarc = data.dmarc.status && data.dmarc.status.includes('FOUND');
    h += '<span class="' + (hasDmarc ? 'badge-found' : 'badge-missing') + '">  ' + (hasDmarc ? '✓' : '✗') + ' DMARC — ' + escapeHtml(data.dmarc.status || '') + '</span>\n';
    if (data.dmarc.record) h += '    <span class="line-sub">' + escapeHtml(data.dmarc.record) + '</span>\n';
    if (data.dmarc.policy) h += '    <span class="line-comment">Policy: ' + escapeHtml(data.dmarc.policy) + ' | Strength: ' + escapeHtml(data.dmarc.strength || '') + '</span>\n';
    h += '\n';
  }
  // DKIM
  if (data.dkim) {
    const hasDkim = data.dkim.status && data.dkim.status.includes('FOUND');
    h += '<span class="' + (hasDkim ? 'badge-found' : 'badge-missing') + '">  ' + (hasDkim ? '✓' : '✗') + ' DKIM — ' + escapeHtml(data.dkim.status || '') + '</span>\n';
    if (data.dkim.selectors && data.dkim.selectors.length > 0) {
      data.dkim.selectors.forEach(s => {
        h += '    <span class="line-sub">Selector: ' + escapeHtml(s.selector || '') + '</span>\n';
      });
    }
    h += '\n';
  }
  // Score & Grade
  if (data.score !== undefined) {
    const gc = data.grade && data.grade.startsWith('A') ? 'grade-a' : data.grade === 'B' ? 'grade-b' : data.grade === 'C' ? 'grade-c' : 'grade-f';
    h += '<span class="line-key">  Email Security Score:</span> <span class="line-value">' + data.score + '/100</span>';
    if (data.grade) h += ' <span class="badge-grade ' + gc + '">' + data.grade + '</span>';
    h += '\n';
  }
  return h || renderGeneric(data);
}

function renderWayback(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  WAYBACK MACHINE SUMMARY</span>\n';
    h += '<span class="line-key">  Archived URLs:</span>  <span class="line-value">' + (data.summary.total_archived_urls || 0) + '</span>\n';
    h += '<span class="line-key">  API Endpoints:</span>  <span class="line-value">' + (data.summary.api_endpoints || 0) + '</span>\n';
    if (data.summary.years_active) h += '<span class="line-key">  Years Active:</span>   <span class="line-value">' + escapeHtml(data.summary.years_active) + '</span>\n';
    h += '\n';
  }
  if (data.total_urls_found !== undefined) h += '<span class="badge-found">  ✓ ' + data.total_urls_found + ' total URLs discovered</span>\n\n';
  // Risk Findings
  if (data.risk_findings && data.risk_findings.length > 0) {
    h += '<span class="line-header">  ⚠ RISK FINDINGS</span>\n';
    data.risk_findings.forEach(function(rf) {
      const cls = rf.level === 'CRITICAL' ? 'line-error' : rf.level === 'HIGH' ? 'line-error' : rf.level === 'MEDIUM' ? 'line-warn' : 'badge-found';
      h += '  <span class="' + cls + '">  ⚠ [' + escapeHtml(rf.level || '') + '] ' + escapeHtml(rf.finding || '') + '</span>\n';
      if (rf.files && rf.files.length > 0) {
        rf.files.forEach(function(f) {
          h += '    <span class="line-sub">  ├─ ' + escapeHtml(f) + '</span>\n';
        });
      }
    });
    h += '\n';
  }
  // API Endpoints
  if (data.api_endpoints && data.api_endpoints.length > 0) {
    h += '<span class="line-header">  API ENDPOINTS (' + data.api_endpoints.length + ')</span>\n';
    data.api_endpoints.slice(0, 30).forEach(function(ep) {
      h += '  <span class="line-warn">  → ' + escapeHtml(ep) + '</span>\n';
    });
    if (data.api_endpoints.length > 30) h += '  <span class="line-comment">  └─ ... and ' + (data.api_endpoints.length - 30) + ' more</span>\n';
    h += '\n';
  }
  // Config Files
  if (data.config_files && data.config_files.length > 0) {
    h += '<span class="line-header">  ⚠ CONFIG FILES (' + data.config_files.length + ')</span>\n';
    data.config_files.forEach(function(f) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(f) + '</span>\n';
    });
    h += '\n';
  }
  // Admin Panels
  if (data.admin_panels && data.admin_panels.length > 0) {
    h += '<span class="line-header">  ⚠ ADMIN PANELS (' + data.admin_panels.length + ')</span>\n';
    data.admin_panels.forEach(function(p) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(p) + '</span>\n';
    });
    h += '\n';
  }
  // JS Files
  if (data.js_files && data.js_files.length > 0) {
    h += '<span class="line-header">  JAVASCRIPT FILES (' + data.js_files.length + ')</span>\n';
    data.js_files.slice(0, 20).forEach(function(f) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(f) + '</span>\n';
    });
    if (data.js_files.length > 20) h += '  <span class="line-comment">  └─ ... and ' + (data.js_files.length - 20) + ' more</span>\n';
    h += '\n';
  }
  // Unique Paths
  if (data.unique_paths && data.unique_paths.length > 0) {
    h += '<span class="line-header">  UNIQUE PATHS (' + data.unique_paths.length + ')</span>\n';
    data.unique_paths.slice(0, 30).forEach(function(p) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(p) + '</span>\n';
    });
    if (data.unique_paths.length > 30) h += '  <span class="line-comment">  └─ ... and ' + (data.unique_paths.length - 30) + ' more</span>\n';
    h += '\n';
  }
  // Interesting Parameters
  if (data.interesting_params && data.interesting_params.length > 0) {
    h += '<span class="line-header">  INTERESTING PARAMETERS (' + data.interesting_params.length + ')</span>\n';
    data.interesting_params.forEach(function(p) {
      h += '  <span class="line-key">  ⬡</span> <span class="line-value">' + escapeHtml(p) + '</span>\n';
    });
    h += '\n';
  }
  // Timeline
  if (data.timeline && Object.keys(data.timeline).length > 0) {
    h += '<span class="line-header">  ARCHIVE TIMELINE</span>\n';
    Object.entries(data.timeline).forEach(function([year, count]) {
      const bar = '█'.repeat(Math.min(Math.ceil(count / 10), 30));
      h += '  <span class="line-key">  ' + year + '</span> <span class="badge-found">' + bar + '</span> <span class="line-comment">' + count + ' URLs</span>\n';
    });
  }
  return h || '<span class="line-comment">  No Wayback Machine data found</span>';
}

function renderCloud(data) {
  let h = '';
  // Backend: data.provider, data.cdn, data.cnames, data.indicators, data.headers_sample, data.ip
  if (data.ip) h += '<span class="line-key">  IP:</span>       <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
  h += '<span class="line-key">  Provider:</span> <span class="badge-found">' + escapeHtml(data.provider || 'Unknown') + '</span>\n';
  h += '<span class="line-key">  CDN:</span>      <span class="line-value">' + escapeHtml(data.cdn || 'None detected') + '</span>\n';
  if (data.cnames && data.cnames.length > 0) {
    h += '\n<span class="line-header">  CNAME RECORDS</span>\n';
    data.cnames.forEach(cn => { h += '  <span class="line-value">  ├─ ' + escapeHtml(cn) + '</span>\n'; });
  }
  if (data.indicators && data.indicators.length > 0) {
    h += '\n<span class="line-header">  DETECTION INDICATORS</span>\n';
    data.indicators.forEach(ind => { h += '  <span class="line-value">  ├─ ' + escapeHtml(ind) + '</span>\n'; });
  }
  if (data.headers_sample && Object.keys(data.headers_sample).length > 0) {
    h += '\n<span class="line-header">  KEY HEADERS</span>\n';
    Object.entries(data.headers_sample).slice(0, 10).forEach(([k, v]) => {
      h += '  <span class="line-key">  ' + escapeHtml(k) + ':</span> <span class="line-value">' + escapeHtml(v) + '</span>\n';
    });
  }
  return h;
}

function renderWAF(data) {
  let h = '';
  // Backend: data.waf_detected (not data.detected), data.waf_name, data.waf_triggered, data.evidence, data.fingerprints
  const detected = data.waf_detected !== undefined ? data.waf_detected : data.detected;
  h += '<span class="line-key">  WAF Detected:</span> <span class="' + (detected ? 'badge-found' : 'badge-missing') + '">' + (detected ? 'YES ✓' : 'NO ✗') + '</span>\n';
  if (data.waf_name && data.waf_name !== 'None') {
    h += '<span class="line-key">  WAF Name:</span>     <span class="badge-found">' + escapeHtml(data.waf_name) + '</span>\n';
  }
  if (data.waf_triggered) {
    h += '<span class="line-key">  WAF Triggered:</span> <span class="line-warn">YES — Blocks malicious payloads</span>\n';
  }
  if (data.fingerprints && Object.keys(data.fingerprints).length > 0) {
    h += '\n<span class="line-header">  FINGERPRINTS</span>\n';
    Object.entries(data.fingerprints).forEach(([k, v]) => {
      h += '  <span class="line-key">  ' + escapeHtml(k) + ':</span> <span class="line-value">' + escapeHtml(String(v)) + '</span>\n';
    });
  }
  if (data.evidence && data.evidence.length > 0) {
    h += '\n<span class="line-header">  EVIDENCE</span>\n';
    data.evidence.forEach(e => { h += '  <span class="line-value">  ├─ ' + escapeHtml(e) + '</span>\n'; });
  }
  return h;
}

function renderThreatIntel(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  THREAT INTELLIGENCE SUMMARY</span>\n';
    h += '<span class="line-key">  Threat Score:</span>     <span class="line-value">' + (data.summary.threat_score || 0) + '/100</span>\n';
    h += '<span class="line-key">  Threat Pulses:</span>    <span class="line-value">' + (data.summary.total_threat_pulses || 0) + '</span>\n';
    h += '<span class="line-key">  Malware Families:</span> <span class="line-value">' + (data.summary.malware_families || 0) + '</span>\n';
    h += '<span class="line-key">  Attack Techniques:</span><span class="line-value"> ' + (data.summary.attack_techniques || 0) + '</span>\n\n';
  }
  // Threat Score & Risk
  if (data.threat_score !== undefined) {
    const scoreCls = data.threat_score >= 75 ? 'line-error' : data.threat_score >= 40 ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Threat Score:</span>  <span class="' + scoreCls + '">' + data.threat_score + '/100</span>\n';
  }
  if (data.risk_level) {
    const cls = data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH' ? 'line-error' : data.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>   <span class="' + cls + '">' + escapeHtml(data.risk_level) + '</span>\n';
  }
  if (data.whitelisted !== undefined) {
    h += '<span class="line-key">  Whitelisted:</span>  <span class="' + (data.whitelisted ? 'badge-found' : 'line-comment') + '">' + (data.whitelisted ? 'YES ✓' : 'NO') + '</span>\n';
  }
  if (data.pulse_count !== undefined) h += '<span class="line-key">  Pulse Count:</span>  <span class="line-value">' + data.pulse_count + '</span>\n';
  // Validation
  if (data.validation && data.validation.length > 0) {
    h += '\n<span class="line-header">  VALIDATION</span>\n';
    data.validation.forEach(function(v) {
      h += '  <span class="badge-found">  ✓ [' + escapeHtml(v.source || '') + '] ' + escapeHtml(v.message || '') + '</span>\n';
    });
  }
  // Malware Families
  if (data.malware_families && data.malware_families.length > 0) {
    h += '\n<span class="line-header">  ⚠ MALWARE FAMILIES (' + data.malware_families.length + ')</span>\n';
    data.malware_families.forEach(function(m) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(m) + '</span>\n';
    });
  }
  // Attack Techniques
  if (data.attack_techniques && data.attack_techniques.length > 0) {
    h += '\n<span class="line-header">  ATTACK TECHNIQUES (' + data.attack_techniques.length + ')</span>\n';
    data.attack_techniques.forEach(function(t) {
      h += '  <span class="line-warn">  ⚡ ' + escapeHtml(t) + '</span>\n';
    });
  }
  // Related Tags
  if (data.related_tags && data.related_tags.length > 0) {
    h += '\n<span class="line-key">  Related Tags:</span> <span class="line-value">' + escapeHtml(data.related_tags.join(', ')) + '</span>\n';
  }
  // Threat Pulses
  if (data.pulses && data.pulses.length > 0) {
    h += '\n<span class="line-header">  THREAT PULSES (' + data.pulses.length + ')</span>\n';
    data.pulses.slice(0, 15).forEach(function(p) {
      h += '  <span class="line-key">  ┌─ ' + escapeHtml(p.name || 'Unknown Pulse') + '</span>\n';
      if (p.description) h += '    <span class="line-sub">  │ ' + escapeHtml(String(p.description).substring(0, 120)) + '</span>\n';
      h += '    <span class="line-comment">  │ Author: ' + escapeHtml(p.author || '') + ' | Created: ' + escapeHtml(p.created || '') + '</span>\n';
      h += '    <span class="line-comment">  │ Indicators: ' + (p.indicator_count || 0) + '</span>\n';
      if (p.tags && p.tags.length > 0) h += '    <span class="line-comment">  │ Tags: ' + escapeHtml(p.tags.join(', ')) + '</span>\n';
      h += '    <span class="line-value">  └─────────</span>\n\n';
    });
    if (data.pulses.length > 15) h += '  <span class="line-comment">  ... and ' + (data.pulses.length - 15) + ' more pulses</span>\n';
  }
  // Passive DNS
  if (data.passive_dns && data.passive_dns.length > 0) {
    h += '\n<span class="line-header">  PASSIVE DNS (' + data.passive_dns.length + ')</span>\n';
    data.passive_dns.slice(0, 20).forEach(function(d) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(d.hostname || '') + ' → ' + escapeHtml(d.address || '') + ' [' + escapeHtml(d.record_type || '') + ']</span>\n';
      h += '    <span class="line-comment">  First: ' + escapeHtml(d.first || '') + ' | Last: ' + escapeHtml(d.last || '') + '</span>\n';
    });
    if (data.passive_dns.length > 20) h += '  <span class="line-comment">  └─ ... and ' + (data.passive_dns.length - 20) + ' more</span>\n';
  }
  return h || '<span class="line-comment">  No threat intelligence data available</span>';
}

function renderSensitivePaths(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  SENSITIVE PATHS SUMMARY</span>\n';
    h += '<span class="line-key">  Paths Tested:</span>  <span class="line-value">' + (data.summary.total_paths_tested || 0) + '</span>\n';
    h += '<span class="line-key">  Paths Found:</span>   <span class="line-value">' + (data.summary.total_found || 0) + '</span>\n';
    const riskCls = data.summary.risk_level === 'CRITICAL' || data.summary.risk_level === 'HIGH' ? 'line-error' : data.summary.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>    <span class="' + riskCls + '">' + escapeHtml(data.summary.risk_level || 'LOW') + '</span>\n';
    // Severity breakdown
    if (data.summary.severity_breakdown) {
      h += '\n<span class="line-header">  SEVERITY BREAKDOWN</span>\n';
      var sb = data.summary.severity_breakdown;
      if (sb.CRITICAL) h += '  <span class="line-error">  ⚠ CRITICAL: ' + sb.CRITICAL + '</span>\n';
      if (sb.HIGH) h += '  <span class="line-error">  ⚠ HIGH:     ' + sb.HIGH + '</span>\n';
      if (sb.MEDIUM) h += '  <span class="line-warn">  ● MEDIUM:   ' + sb.MEDIUM + '</span>\n';
      if (sb.LOW) h += '  <span class="badge-found">  ○ LOW:      ' + sb.LOW + '</span>\n';
    }
    h += '\n';
  }
  // Stats
  if (data.total_tested !== undefined) h += '<span class="line-key">  Total Tested:</span> <span class="line-value">' + data.total_tested + ' paths</span>\n';
  if (data.total_found !== undefined) h += '<span class="line-key">  Total Found:</span>  <span class="badge-found">' + data.total_found + ' accessible</span>\n';
  if (data.risk_score !== undefined) h += '<span class="line-key">  Risk Score:</span>   <span class="line-value">' + data.risk_score + '/100</span>\n';
  if (data.risk_level) {
    const cls = data.risk_level === 'CRITICAL' || data.risk_level === 'HIGH' ? 'line-error' : data.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>   <span class="' + cls + '">' + escapeHtml(data.risk_level) + '</span>\n';
  }
  // Findings
  if (data.findings && data.findings.length > 0) {
    h += '\n<span class="line-header">  DISCOVERED PATHS (' + data.findings.length + ')</span>\n';
    data.findings.forEach(function(f) {
      const sevCls = f.severity === 'CRITICAL' ? 'line-error' : f.severity === 'HIGH' ? 'line-error' : f.severity === 'MEDIUM' ? 'line-warn' : 'badge-found';
      h += '  <span class="' + sevCls + '">  ⚠ [' + escapeHtml(f.severity || 'INFO') + '] ' + escapeHtml(f.path || '') + '</span>\n';
      h += '    <span class="line-sub">  Status: ' + (f.status || '') + ' | Size: ' + (f.size || 0) + ' bytes | Category: ' + escapeHtml(f.category || '') + '</span>\n';
      if (f.description) h += '    <span class="line-comment">  ' + escapeHtml(f.description) + '</span>\n';
      h += '\n';
    });
  } else {
    h += '\n<span class="line-comment">  No sensitive paths discovered</span>\n';
  }
  return h || '<span class="line-comment">  No sensitive paths data available</span>';
}

function renderCveHunter(data) {
  let h = '';
  // Summary
  if (data.summary) {
    h += '<span class="line-header">  CVE HUNTER SUMMARY</span>\n';
    h += '<span class="line-key">  Total CVEs:</span>   <span class="line-value">' + (data.summary.total_cves || 0) + '</span>\n';
    if (data.summary.critical !== undefined) h += '<span class="line-key">  Critical:</span>     <span class="line-error">' + data.summary.critical + '</span>\n';
    if (data.summary.high !== undefined) h += '<span class="line-key">  High:</span>         <span class="line-warn">' + data.summary.high + '</span>\n';
    if (data.summary.exploitable !== undefined) h += '<span class="line-key">  Exploitable:</span>  <span class="line-error">' + data.summary.exploitable + '</span>\n';
    const riskCls = data.summary.risk_level === 'CRITICAL' ? 'line-error' : data.summary.risk_level === 'HIGH' ? 'line-error' : data.summary.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>   <span class="' + riskCls + '">' + escapeHtml(data.summary.risk_level || 'LOW') + '</span>\n\n';
  }
  // Basic info
  if (data.ip) h += '<span class="line-key">  Target IP:</span>    <span class="line-value">' + escapeHtml(data.ip) + '</span>\n';
  if (data.total_cves !== undefined) h += '<span class="line-key">  Total CVEs:</span>   <span class="line-value">' + data.total_cves + '</span>\n';
  if (data.risk_score !== undefined) h += '<span class="line-key">  Risk Score:</span>   <span class="line-value">' + data.risk_score + '/100</span>\n';
  if (data.risk_level) {
    const cls = data.risk_level === 'CRITICAL' ? 'line-error' : data.risk_level === 'HIGH' ? 'line-error' : data.risk_level === 'MEDIUM' ? 'line-warn' : 'badge-found';
    h += '<span class="line-key">  Risk Level:</span>   <span class="' + cls + '">' + escapeHtml(data.risk_level) + '</span>\n';
  }
  // Severity Breakdown
  if (data.severity_breakdown) {
    h += '\n<span class="line-header">  SEVERITY BREAKDOWN</span>\n';
    var sb = data.severity_breakdown;
    if (sb.CRITICAL) h += '  <span class="line-error">  ⚠ CRITICAL: ' + sb.CRITICAL + '</span>\n';
    if (sb.HIGH) h += '  <span class="line-error">  ⚠ HIGH:     ' + sb.HIGH + '</span>\n';
    if (sb.MEDIUM) h += '  <span class="line-warn">  ● MEDIUM:   ' + sb.MEDIUM + '</span>\n';
    if (sb.LOW) h += '  <span class="badge-found">  ○ LOW:      ' + sb.LOW + '</span>\n';
    if (sb.UNKNOWN) h += '  <span class="line-comment">  ? UNKNOWN:  ' + sb.UNKNOWN + '</span>\n';
  }
  // Exploitable CVEs
  if (data.exploitable && data.exploitable.length > 0) {
    h += '\n<span class="line-header">  ⚠ EXPLOITABLE CVES (' + data.exploitable.length + ')</span>\n';
    data.exploitable.forEach(function(cve) {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(cve) + ' — Known exploit available</span>\n';
    });
  }
  // Detailed CVE List
  if (data.cve_details && data.cve_details.length > 0) {
    h += '\n<span class="line-header">  CVE DETAILS (' + data.cve_details.length + ')</span>\n';
    data.cve_details.forEach(function(cve) {
      const sevCls = cve.severity === 'CRITICAL' ? 'line-error' : cve.severity === 'HIGH' ? 'line-error' : cve.severity === 'MEDIUM' ? 'line-warn' : cve.severity === 'LOW' ? 'badge-found' : 'line-comment';
      h += '  <span class="' + sevCls + '">  ┌─ ' + escapeHtml(cve.id || '') + ' [' + escapeHtml(cve.severity || 'UNKNOWN') + ']</span>\n';
      if (cve.cvss !== undefined) h += '    <span class="line-sub">  │ CVSS: ' + cve.cvss + '/10.0</span>\n';
      if (cve.summary) h += '    <span class="line-sub">  │ ' + escapeHtml(String(cve.summary).substring(0, 150)) + '</span>\n';
      if (cve.cwe) h += '    <span class="line-comment">  │ CWE: ' + escapeHtml(cve.cwe) + '</span>\n';
      if (cve.published) h += '    <span class="line-comment">  │ Published: ' + escapeHtml(cve.published) + '</span>\n';
      h += '    <span class="line-value">  └─────────</span>\n\n';
    });
  } else if (data.cve_list && data.cve_list.length > 0) {
    h += '\n<span class="line-header">  CVE LIST (' + data.cve_list.length + ')</span>\n';
    data.cve_list.forEach(function(cve) {
      h += '  <span class="line-warn">  ⚠ ' + escapeHtml(cve) + '</span>\n';
    });
  }
  // CPEs
  if (data.cpes && data.cpes.length > 0) {
    h += '\n<span class="line-header">  CPE IDENTIFIERS (' + data.cpes.length + ')</span>\n';
    data.cpes.forEach(function(cpe) {
      h += '  <span class="line-value">  ├─ ' + escapeHtml(cpe) + '</span>\n';
    });
  }
  return h || '<span class="line-comment">  No CVE data available</span>';
}

function renderCORS(data) {
  let h = '';
  if (data.vulnerable !== undefined) {
    h += '<span class="line-key">  CORS Status:</span> <span class="' + (data.vulnerable ? 'line-error' : 'badge-found') + '">' + (data.vulnerable ? '⚠ VULNERABLE' : '✓ SECURE') + '</span>\n';
    if (data.risk_level) h += '<span class="line-key">  Risk Level:</span>  <span class="line-value">' + escapeHtml(data.risk_level) + '</span>\n';
    h += '\n';
  }
  if (data.tests && data.tests.length > 0) {
    h += '<span class="line-header">  CORS TESTS (' + data.tests.length + ')</span>\n';
    data.tests.forEach(t => {
      if (t.error) {
        h += '  <span class="line-comment">  ○ ' + escapeHtml(t.test || '') + ' — ' + escapeHtml(t.error) + '</span>\n';
        return;
      }
      const icon = t.vulnerable ? '⚠' : '✓';
      const cls = t.vulnerable ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(t.test || t.name || '') + '</span>\n';
      h += '    <span class="line-sub">Origin: ' + escapeHtml(t.origin_sent || '') + ' → ACAO: ' + escapeHtml(t.acao_returned || 'None') + '</span>\n';
      if (t.credentials_allowed) h += '    <span class="line-error">  Credentials: ALLOWED!</span>\n';
      if (t.note) h += '    <span class="line-warn">' + escapeHtml(t.note) + '</span>\n';
    });
  }
  return h || renderGeneric(data);
}

function renderRedirect(data) {
  let h = '';
  if (data.vulnerable !== undefined) {
    h += '<span class="line-key">  Status:</span> <span class="' + (data.vulnerable ? 'line-error' : 'badge-found') + '">' + (data.vulnerable ? '⚠ VULNERABLE' : '✓ SECURE') + '</span>\n';
  }
  if (data.stats) {
    h += '<span class="line-key">  Parameters Tested:</span> <span class="line-value">' + (data.stats.parameters_tested || 0) + '</span>\n';
    h += '<span class="line-key">  Vulnerabilities:</span>   <span class="line-value">' + (data.stats.vulnerabilities || 0) + '</span>\n\n';
  }
  if (data.tests && data.tests.length > 0) {
    h += '<span class="line-header">  REDIRECT TESTS</span>\n';
    data.tests.forEach(t => {
      const icon = t.vulnerable ? '⚠' : '→';
      const cls = t.vulnerable ? 'line-error' : 'line-value';
      h += '  <span class="' + cls + '">  ' + icon + ' ?' + escapeHtml(t.parameter || t.payload || t.test || '') + ' → HTTP ' + (t.status_code || '') + '</span>\n';
      if (t.redirect_to) h += '    <span class="line-sub">→ ' + escapeHtml(t.redirect_to) + '</span>\n';
    });
  } else if (!data.tests || data.tests.length === 0) {
    h += '<span class="line-comment">  No redirect vulnerabilities found — all parameters safe</span>\n';
  }
  return h || renderGeneric(data);
}

function renderCookies(data) {
  let h = '';
  if (data.cookies && data.cookies.length > 0) {
    h += '<span class="badge-found">  ✓ ' + data.cookies.length + ' cookie(s) found</span>\n\n';
    data.cookies.forEach(c => {
      const riskCls = c.risk === 'CRITICAL' ? 'line-error' : c.risk === 'MEDIUM' ? 'line-warn' : 'badge-found';
      h += '<span class="line-key">  ┌─ ' + escapeHtml(c.name) + '</span>';
      if (c.risk) h += ' <span class="' + riskCls + '">[' + c.risk + ']</span>';
      if (c.sensitive) h += ' <span class="line-warn">⚠ SENSITIVE</span>';
      h += '\n';
      if (c.value) h += '  <span class="line-value">  │  Value: ' + escapeHtml(String(c.value).substring(0, 60)) + (String(c.value).length > 60 ? '...' : '') + '</span>\n';
      h += '  <span class="' + (c.secure ? 'badge-found' : 'badge-missing') + '">  │  Secure: ' + (c.secure ? 'YES ✓' : 'NO ✗') + '</span>\n';
      h += '  <span class="' + (c.httponly ? 'badge-found' : 'badge-missing') + '">  │  HttpOnly: ' + (c.httponly ? 'YES ✓' : 'NO ✗') + '</span>\n';
      const ss = c.samesite || 'Not set';
      h += '  <span class="' + (ss !== 'Not set' ? 'badge-found' : 'badge-missing') + '">  │  SameSite: ' + escapeHtml(ss) + '</span>\n';
      if (c.expires) h += '  <span class="line-value">  │  Expires: ' + escapeHtml(c.expires) + '</span>\n';
      if (c.issues && c.issues.length > 0) {
        c.issues.forEach(issue => {
          h += '  <span class="line-error">  │  ⚠ ' + escapeHtml(issue) + '</span>\n';
        });
      }
      if (c.flags && c.flags.length > 0) {
        h += '  <span class="badge-found">  │  Flags: ' + escapeHtml(c.flags.join(', ')) + '</span>\n';
      }
      h += '  <span class="line-value">  └─────────</span>\n\n';
    });
  } else { h += '<span class="line-comment">  No cookies found</span>'; }
  if (data.score !== undefined) {
    const gc = data.grade && data.grade.startsWith('A') ? 'grade-a' : data.grade === 'B' ? 'grade-b' : 'grade-f';
    h += '\n<span class="line-key">  Cookie Security Score:</span> <span class="line-value">' + data.score + '/100</span>';
    if (data.grade) h += ' <span class="badge-grade ' + gc + '">' + data.grade + '</span>';
  }
  return h;
}

function renderTakeover(data) {
  let h = '';
  // Backend: data.subdomains_checked (not data.results), data.vulnerable (array, not data.vulnerable_count)
  const checked = data.subdomains_checked || data.results || [];
  const vulns = data.vulnerable || [];
  if (checked.length > 0) {
    h += '<span class="badge-found">  Checked ' + checked.length + ' subdomain(s)</span>\n\n';
  }
  // Show vulnerabilities first
  if (vulns.length > 0) {
    h += '<span class="line-header">  ⚠ VULNERABLE SUBDOMAINS (' + vulns.length + ')</span>\n';
    vulns.forEach(v => {
      h += '  <span class="line-error">  ⚠ ' + escapeHtml(v.subdomain || '') + '</span>';
      if (v.cname) h += ' <span class="line-comment">→ ' + escapeHtml(v.cname) + '</span>';
      if (v.service) h += ' <span class="line-warn">[' + escapeHtml(v.service) + ']</span>';
      h += '\n';
      if (v.detail) h += '    <span class="line-sub">' + escapeHtml(v.detail) + '</span>\n';
      h += '    <span class="line-error">  Severity: ' + escapeHtml(v.severity || 'HIGH') + ' | Status: ' + escapeHtml(v.status || '') + '</span>\n';
    });
    h += '\n';
  }
  // Show all checked
  if (checked.length > 0) {
    h += '<span class="line-header">  ALL CHECKED SUBDOMAINS</span>\n';
    checked.forEach(r => {
      const icon = r.status && r.status.includes('VULNERABLE') ? '⚠' : '✓';
      const cls = r.status && r.status.includes('VULNERABLE') ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(r.subdomain || '') + '</span>';
      if (r.cname && r.cname !== 'No CNAME') h += ' <span class="line-comment">→ ' + escapeHtml(r.cname) + '</span>';
      h += '\n';
    });
  }
  h += '\n<span class="line-key">  Vulnerable Count:</span> <span class="' + (vulns.length > 0 ? 'line-error' : 'badge-found') + '">' + vulns.length + '</span>\n';
  if (data.stats) h += '<span class="line-key">  Services Checked:</span>  <span class="line-value">' + (data.stats.services_checked || 0) + '</span>\n';
  return h || renderGeneric(data);
}

function renderReputation(data) {
  let h = '';
  if (data.score !== undefined) {
    const gc = data.score >= 80 ? 'grade-a' : data.score >= 60 ? 'grade-b' : data.score >= 40 ? 'grade-c' : 'grade-f';
    h += '<span class="line-key">  Reputation Score:</span> <span class="line-value">' + data.score + '/100</span> <span class="badge-grade ' + gc + '">' + (data.grade || '') + '</span>\n';
    h += '<span class="line-key">  Blacklisted:</span>      <span class="' + (data.blacklisted ? 'line-error' : 'badge-found') + '">' + (data.blacklisted ? 'YES ⚠' : 'NO ✓') + '</span>\n\n';
  }
  // Backend: data.checks (not data.blacklists)
  const checks = data.checks || data.blacklists || [];
  if (checks.length > 0) {
    h += '<span class="line-header">  BLACKLIST CHECK (' + checks.length + ' lists)</span>\n';
    checks.forEach(bl => {
      const isListed = (bl.status && bl.status.includes('LISTED')) || bl.listed;
      const icon = isListed ? '⚠' : '✓';
      const cls = isListed ? 'line-error' : 'badge-found';
      h += '  <span class="' + cls + '">  ' + icon + ' ' + escapeHtml(bl.blacklist || bl.name || bl.source || '') + ' — ' + escapeHtml(bl.status || (bl.listed ? 'LISTED' : 'CLEAN')) + '</span>\n';
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
