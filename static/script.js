// ===== DDOS_F16 SCANWEBS v7.0 — Engine =====
let currentModule = 'dns_recon';
let scanCount = 0;
let scanHistory = {};
let isScanning = false;
let startTime = Date.now();

// ===== MATRIX RAIN =====
const canvas = document.getElementById('matrixCanvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const chars = 'DDOSf16アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF'.split('');
    const drops = Array(Math.floor(canvas.width / 14)).fill(1);
    function drawMatrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        drops.forEach((y, i) => {
            const char = chars[Math.floor(Math.random() * chars.length)];
            ctx.globalAlpha = Math.random() * 0.3 + 0.1;
            ctx.fillText(char, i * 14, y * 14);
            if (y * 14 > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        });
        ctx.globalAlpha = 1;
    }
    setInterval(drawMatrix, 50);
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });
}

// ===== MODULE DATA =====
const MODULE_INFO = {
    dns_recon: { name: 'DNS Full Recon', icon: '🔍', cat: 'DNS Intelligence' },
    subdomain_hunter: { name: 'Subdomain Hunter', icon: '🎯', cat: 'DNS Intelligence' },
    reverse_dns: { name: 'Reverse DNS', icon: '🔄', cat: 'DNS Intelligence' },
    email_security: { name: 'Email Security', icon: '📧', cat: 'DNS Intelligence' },
    port_scanner: { name: 'Port Scanner Pro', icon: '🚪', cat: 'Infrastructure' },
    network_trace: { name: 'Network Trace', icon: '🛤️', cat: 'Infrastructure' },
    cloud_infra: { name: 'Cloud Infrastructure', icon: '☁️', cat: 'Infrastructure' },
    geoip: { name: 'GeoIP Advanced', icon: '🌍', cat: 'Infrastructure' },
    waf_detect: { name: 'WAF Detection', icon: '🛡️', cat: 'Web Analysis' },
    tech_stack: { name: 'Tech Stack X-Ray', icon: '⚙️', cat: 'Web Analysis' },
    http_fingerprint: { name: 'HTTP Fingerprint', icon: '📡', cat: 'Web Analysis' },
    js_analyzer: { name: 'JS Analyzer', icon: '📜', cat: 'Web Analysis' },
    link_extractor: { name: 'Link Extractor', icon: '🔗', cat: 'Web Analysis' },
    cms_scanner: { name: 'CMS Scanner', icon: '🏗️', cat: 'Web Analysis' },
    ssl_audit: { name: 'SSL/TLS Audit', icon: '🔐', cat: 'Security Audit' },
    security_headers: { name: 'Security Headers', icon: '🔒', cat: 'Security Audit' },
    cors_misconfig: { name: 'CORS Check', icon: '🌐', cat: 'Security Audit' },
    open_redirect: { name: 'Open Redirect', icon: '↗️', cat: 'Security Audit' },
    cookie_analyzer: { name: 'Cookie Analyzer', icon: '🍪', cat: 'Security Audit' },
    subdomain_takeover: { name: 'Subdomain Takeover', icon: '💀', cat: 'Security Audit' },
    whois_intel: { name: 'WHOIS Intel', icon: '📋', cat: 'Intelligence' },
    domain_reputation: { name: 'Domain Reputation', icon: '⭐', cat: 'Intelligence' },
    robots_sitemap: { name: 'Robots & Sitemap', icon: '🤖', cat: 'Intelligence' },
    full_recon: { name: 'FULL RECON', icon: '⚡', cat: 'Full Scan' },
};

// ===== SIDEBAR =====
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    document.getElementById('mainContent').classList.toggle('expanded');
}
function toggleCategory(cat) {
    const el = document.getElementById('cat-' + cat);
    el.classList.toggle('open');
}
function filterModules() {
    const q = document.getElementById('moduleSearch').value.toLowerCase();
    document.querySelectorAll('.module-item').forEach(item => {
        const name = item.querySelector('.mod-name').textContent.toLowerCase();
        item.style.display = name.includes(q) ? '' : 'none';
    });
}
function selectModule(mod) {
    currentModule = mod;
    document.querySelectorAll('.module-item').forEach(el => el.classList.remove('active'));
    const el = document.querySelector(`[data-module="${mod}"]`);
    if (el) el.classList.add('active');
    const info = MODULE_INFO[mod];
    if (info) {
        document.getElementById('activeModuleName').textContent = info.name;
        document.getElementById('activeModuleIcon').textContent = info.icon;
    }
}

// ===== SCROLL REVEAL =====
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));
}

// ===== SCANNING =====
async function startScan() {
    if (isScanning) return;
    const domain = document.getElementById('domainInput').value.trim();
    if (!domain) { shakeInput(); return; }
    isScanning = true;
    scanCount++;
    document.getElementById('scanCount').textContent = scanCount;
    const btn = document.getElementById('scanBtn');
    btn.classList.add('scanning');
    btn.querySelector('.btn-text').textContent = 'SCANNING...';
    // Show terminal
    document.getElementById('terminalSection').style.display = 'block';
    document.getElementById('inlineStats').style.display = 'flex';
    const term = document.getElementById('terminalOutput');
    const info = MODULE_INFO[currentModule] || { name: currentModule, icon: '🔍' };
    // Update stats
    document.getElementById('statTarget').textContent = domain;
    document.getElementById('statModule').textContent = info.name;
    document.getElementById('statScore').textContent = '...';
    document.getElementById('statTime').textContent = '...';
    document.getElementById('terminalTitle').textContent = `root@ddos-f16:~# ${currentModule} ${domain}`;
    // Print header
    printLine(term, `\n╔══════════════════════════════════════════════════════╗`, 'cyan');
    printLine(term, `║  ${info.icon} ${info.name.toUpperCase().padEnd(48)}║`, 'cyan');
    printLine(term, `║  Target: ${domain.padEnd(43)}║`, 'green');
    printLine(term, `╚══════════════════════════════════════════════════════╝`, 'cyan');
    printLine(term, `\n[${timestamp()}] Initializing ${info.name}...`, 'dim');
    printLine(term, `[${timestamp()}] Connecting to target...`, 'dim');
    // API Call
    try {
        const startT = Date.now();
        const resp = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain, module: currentModule })
        });
        const data = await resp.json();
        const elapsed = ((Date.now() - startT) / 1000).toFixed(1);
        document.getElementById('statTime').textContent = elapsed + 's';
        if (data.error) {
            printLine(term, `\n[ERROR] ${data.error}`, 'red');
        } else {
            // Store results
            scanHistory[currentModule] = data;
            // Render results
            renderResults(term, data, currentModule);
            // Update score
            const score = data.score || data.overall_score || data.stats?.score || '—';
            const grade = data.grade || data.overall_grade || data.stats?.grade || '';
            document.getElementById('statScore').textContent = grade ? `${score} (${grade})` : String(score);
        }
        printLine(term, `\n[${timestamp()}] Scan completed in ${elapsed}s`, 'green');
        printLine(term, `[${timestamp()}] ════════════════════════════════════════`, 'dim');
    } catch (err) {
        printLine(term, `\n[ERROR] Connection failed: ${err.message}`, 'red');
    }
    isScanning = false;
    btn.classList.remove('scanning');
    btn.querySelector('.btn-text').textContent = 'INITIATE SCAN';
    term.scrollTop = term.scrollHeight;
}

// ===== RENDER RESULTS AS TREE =====
function renderResults(term, data, module) {
    printLine(term, '', '');
    if (data.stats) {
        printLine(term, `┌─ STATS ──────────────────────────────`, 'yellow');
        renderObject(term, data.stats, '│  ');
        printLine(term, `└──────────────────────────────────────`, 'yellow');
        printLine(term, '', '');
    }
    // Module-specific rendering
    const renderers = {
        dns_recon: renderDNS,
        subdomain_hunter: renderSubdomains,
        reverse_dns: renderReverseIP,
        email_security: renderEmailSec,
        port_scanner: renderPorts,
        network_trace: renderTrace,
        cloud_infra: renderCloud,
        geoip: renderGeo,
        waf_detect: renderWAF,
        tech_stack: renderTechStack,
        http_fingerprint: renderHTTP,
        js_analyzer: renderJS,
        link_extractor: renderLinks,
        cms_scanner: renderCMS,
        ssl_audit: renderSSL,
        security_headers: renderSecHeaders,
        cors_misconfig: renderCORS,
        open_redirect: renderRedirect,
        cookie_analyzer: renderCookies,
        subdomain_takeover: renderTakeover,
        whois_intel: renderWhois,
        domain_reputation: renderReputation,
        robots_sitemap: renderRobots,
        full_recon: renderFullRecon,
    };
    const renderer = renderers[module];
    if (renderer) {
        renderer(term, data);
    } else {
        renderGeneric(term, data);
    }
}

// ===== MODULE RENDERERS =====
function renderDNS(term, data) {
    printLine(term, `┌─ DNS RECORDS ────────────────────────`, 'cyan');
    if (data.records) {
        const keys = Object.keys(data.records);
        keys.forEach((rt, i) => {
            const recs = data.records[rt];
            const isLast = i === keys.length - 1;
            const prefix = isLast ? '└─' : '├─';
            if (Array.isArray(recs) && recs.length > 0) {
                printLine(term, `${prefix} ${rt} (${recs.length})`, 'green');
                recs.forEach((r, j) => {
                    const sub = isLast ? '   ' : '│  ';
                    const subPre = j === recs.length - 1 ? '└─' : '├─';
                    printLine(term, `${sub}${subPre} ${r}`, 'white');
                });
            } else {
                printLine(term, `${prefix} ${rt}: (none)`, 'dim');
            }
        });
    }
    printLine(term, `\n├─ DNSSEC: ${data.dnssec || 'Unknown'}`, data.dnssec?.includes('ENABLED') ? 'green' : 'red');
    if (data.zone_transfer && data.zone_transfer.length > 0) {
        printLine(term, `└─ ZONE TRANSFER:`, 'yellow');
        data.zone_transfer.forEach(zt => {
            const color = zt.status === 'VULNERABLE' ? 'red' : 'green';
            printLine(term, `   ├─ ${zt.nameserver}: ${zt.status}`, color);
            if (zt.records_leaked) printLine(term, `   └─ LEAKED ${zt.records_leaked} records!`, 'red');
        });
    }
}

function renderSubdomains(term, data) {
    printLine(term, `┌─ SUBDOMAIN SOURCES ──────────────────`, 'cyan');
    if (data.sources) {
        Object.entries(data.sources).forEach(([src, info]) => {
            printLine(term, `├─ ${src}: ${info.count} found`, info.count > 0 ? 'green' : 'dim');
            const subs = info.subdomains || [];
            subs.slice(0, 10).forEach((s, i) => {
                const sub = typeof s === 'string' ? s : `${s.subdomain} → ${s.ip}`;
                printLine(term, `│  ${i === Math.min(subs.length, 10) - 1 ? '└─' : '├─'} ${sub}`, 'white');
            });
            if (subs.length > 10) printLine(term, `│  └─ ... +${subs.length - 10} more`, 'dim');
        });
    }
    printLine(term, `└─ TOTAL UNIQUE: ${data.all_subdomains?.length || 0}`, 'yellow');
}

function renderReverseIP(term, data) {
    printLine(term, `├─ IP: ${data.ip}`, 'green');
    printLine(term, `├─ PTR: ${(data.ptr || []).join(', ')}`, 'white');
    printLine(term, `├─ SHARED DOMAINS (${(data.shared_domains||[]).length}):`, 'cyan');
    (data.shared_domains || []).slice(0, 20).forEach((d, i) => {
        printLine(term, `│  ${i < 19 ? '├─' : '└─'} ${d}`, 'white');
    });
}

function renderEmailSec(term, data) {
    printLine(term, `┌─ EMAIL SECURITY ─────────────────────`, 'cyan');
    printLine(term, `├─ SPF: ${data.spf?.status || 'N/A'}`, data.spf?.status?.includes('✓') ? 'green' : 'red');
    if (data.spf?.record) printLine(term, `│  └─ ${data.spf.record}`, 'dim');
    if (data.spf?.policy) printLine(term, `│  └─ Policy: ${data.spf.policy}`, 'white');
    printLine(term, `├─ DMARC: ${data.dmarc?.status || 'N/A'}`, data.dmarc?.status?.includes('✓') ? 'green' : 'red');
    if (data.dmarc?.policy) printLine(term, `│  └─ Policy: ${data.dmarc.policy} (${data.dmarc.strength})`, 'white');
    printLine(term, `├─ DKIM: ${data.dkim?.status || 'N/A'}`, data.dkim?.status?.includes('✓') ? 'green' : 'red');
    printLine(term, `├─ MX SERVERS:`, 'cyan');
    (data.mx || []).forEach((mx, i) => {
        printLine(term, `│  ${i < (data.mx.length - 1) ? '├─' : '└─'} [${mx.priority}] ${mx.server}`, 'white');
    });
    printLine(term, `└─ SCORE: ${data.score}/100 (Grade: ${data.grade})`, data.score >= 70 ? 'green' : data.score >= 40 ? 'yellow' : 'red');
}

function renderPorts(term, data) {
    printLine(term, `┌─ PORT SCAN ──────────────────────────`, 'cyan');
    printLine(term, `├─ Target IP: ${data.ip}`, 'white');
    printLine(term, `├─ OPEN PORTS (${(data.open_ports||[]).length}):`, 'green');
    (data.open_ports || []).forEach((p, i) => {
        const color = [23,135,139,445,3389,6379,27017].includes(p.port) ? 'red' : 'green';
        printLine(term, `│  ├─ :${p.port} ${p.service} [${p.status}]`, color);
        if (p.banner) printLine(term, `│  │  └─ ${p.banner.substring(0, 80)}`, 'dim');
    });
    printLine(term, `└─ Risk: ${data.stats?.risk_level || 'N/A'}`, data.stats?.risk_level === 'CRITICAL' ? 'red' : 'yellow');
}

function renderTrace(term, data) {
    printLine(term, `┌─ NETWORK TRACE TO ${data.ip} ─────────`, 'cyan');
    (data.hops || []).forEach(h => {
        const rtt = h.rtt_ms ? `${h.rtt_ms}ms` : '* * *';
        printLine(term, `├─ ${String(h.ttl).padStart(2)} │ ${h.ip.padEnd(16)} │ ${rtt.padEnd(10)} │ ${h.hostname}`, h.ip === '*' ? 'dim' : 'white');
    });
    printLine(term, `└─ Reached: ${data.stats?.destination_reached ? 'YES ✓' : 'NO ✗'}`, data.stats?.destination_reached ? 'green' : 'red');
}

function renderCloud(term, data) {
    printLine(term, `┌─ CLOUD INFRASTRUCTURE ───────────────`, 'cyan');
    printLine(term, `├─ Provider: ${data.provider || 'Unknown'}`, data.provider !== 'Unknown' ? 'green' : 'dim');
    printLine(term, `├─ CDN: ${data.cdn || 'None'}`, 'white');
    printLine(term, `├─ IP: ${data.ip || 'N/A'}`, 'white');
    if (data.cnames?.length) {
        printLine(term, `├─ CNAME Chain:`, 'cyan');
        data.cnames.forEach(c => printLine(term, `│  └─ ${c}`, 'white'));
    }
    printLine(term, `├─ EVIDENCE:`, 'yellow');
    (data.indicators || []).forEach(ind => printLine(term, `│  ├─ ${ind}`, 'green'));
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderGeo(term, data) {
    printLine(term, `┌─ GEOIP INTELLIGENCE ─────────────────`, 'cyan');
    if (data.geo) {
        Object.entries(data.geo).forEach(([k, v]) => {
            if (v && v !== 'N/A' && v !== 'Unknown' && v !== false) {
                printLine(term, `├─ ${k.replace(/_/g,' ').toUpperCase()}: ${v}`, 'white');
            }
        });
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderWAF(term, data) {
    printLine(term, `┌─ WAF DETECTION ──────────────────────`, 'cyan');
    printLine(term, `├─ WAF Detected: ${data.waf_detected ? 'YES ⚠' : 'NO'}`, data.waf_detected ? 'yellow' : 'green');
    printLine(term, `├─ WAF Name: ${data.waf_name}`, data.waf_detected ? 'red' : 'dim');
    printLine(term, `├─ Triggered by payload: ${data.waf_triggered ? 'YES' : 'NO'}`, 'white');
    if (data.evidence?.length) {
        printLine(term, `├─ EVIDENCE:`, 'yellow');
        data.evidence.forEach(e => printLine(term, `│  ├─ ${e}`, 'white'));
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderTechStack(term, data) {
    printLine(term, `┌─ TECHNOLOGY STACK ───────────────────`, 'cyan');
    if (data.technologies) {
        Object.entries(data.technologies).forEach(([cat, items]) => {
            printLine(term, `├─ ${cat.toUpperCase()}:`, 'yellow');
            items.forEach(item => printLine(term, `│  ├─ ${item}`, 'green'));
        });
    }
    printLine(term, `└─ Total: ${data.stats?.total_technologies || 0} technologies`, 'cyan');
}

function renderHTTP(term, data) {
    printLine(term, `┌─ HTTP FINGERPRINT ───────────────────`, 'cyan');
    ['https', 'http'].forEach(scheme => {
        if (data[scheme] && !data[scheme].error) {
            printLine(term, `├─ ${scheme.toUpperCase()}:`, 'yellow');
            const d = data[scheme];
            printLine(term, `│  ├─ Status: ${d.status_code}`, 'white');
            printLine(term, `│  ├─ Server: ${d.server}`, 'white');
            printLine(term, `│  ├─ Powered: ${d.powered_by}`, 'white');
            printLine(term, `│  ├─ Response: ${d.response_time_ms}ms`, 'green');
            printLine(term, `│  └─ Encoding: ${d.content_encoding}`, 'white');
        }
    });
    if (data.redirects?.length) {
        printLine(term, `├─ REDIRECTS:`, 'yellow');
        data.redirects.forEach(r => printLine(term, `│  ├─ ${r.code||''} ${r.from||''} → ${r.to || r.final_url || ''}`, 'white'));
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderJS(term, data) {
    printLine(term, `┌─ JAVASCRIPT ANALYSIS ────────────────`, 'cyan');
    printLine(term, `├─ SCRIPTS (${(data.scripts||[]).length}):`, 'yellow');
    (data.scripts||[]).slice(0,10).forEach(s => printLine(term, `│  ├─ ${s}`, 'dim'));
    if (data.secrets_found?.length) {
        printLine(term, `├─ ⚠ SECRETS FOUND (${data.secrets_found.length}):`, 'red');
        data.secrets_found.forEach(s => printLine(term, `│  ├─ [${s.severity}] ${s.type}: ${s.value}`, s.severity === 'CRITICAL' ? 'red' : 'yellow'));
    }
    if (data.api_endpoints?.length) {
        printLine(term, `├─ API ENDPOINTS (${data.api_endpoints.length}):`, 'green');
        data.api_endpoints.forEach(e => printLine(term, `│  ├─ ${e}`, 'white'));
    }
    printLine(term, `└─ Risk: ${data.stats?.risk_level || 'LOW'}`, data.stats?.risk_level === 'CRITICAL' ? 'red' : 'green');
}

function renderLinks(term, data) {
    printLine(term, `┌─ LINK EXTRACTION ────────────────────`, 'cyan');
    printLine(term, `├─ INTERNAL (${(data.internal_links||[]).length}):`, 'green');
    (data.internal_links||[]).slice(0,10).forEach(l => printLine(term, `│  ├─ ${l}`, 'white'));
    printLine(term, `├─ EXTERNAL (${(data.external_links||[]).length}):`, 'yellow');
    (data.external_links||[]).slice(0,10).forEach(l => printLine(term, `│  ├─ ${l}`, 'white'));
    if (data.hidden_paths?.length) {
        printLine(term, `├─ HIDDEN PATHS (${data.hidden_paths.length}):`, 'red');
        data.hidden_paths.slice(0,10).forEach(p => printLine(term, `│  ├─ ${p}`, 'yellow'));
    }
    if (data.emails?.length) {
        printLine(term, `├─ EMAILS:`, 'cyan');
        data.emails.forEach(e => printLine(term, `│  ├─ ${e}`, 'white'));
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderCMS(term, data) {
    printLine(term, `┌─ CMS DETECTION ──────────────────────`, 'cyan');
    printLine(term, `├─ CMS: ${data.cms}`, data.cms !== 'Unknown' ? 'green' : 'dim');
    printLine(term, `├─ Version: ${data.version}`, 'white');
    if (data.details?.plugins?.length) {
        printLine(term, `├─ PLUGINS (${data.details.plugins.length}):`, 'yellow');
        data.details.plugins.forEach(p => printLine(term, `│  ├─ ${p}`, 'white'));
    }
    if (data.details?.themes?.length) {
        printLine(term, `├─ THEMES:`, 'yellow');
        data.details.themes.forEach(t => printLine(term, `│  ├─ ${t}`, 'white'));
    }
    if (data.vulnerabilities?.length) {
        printLine(term, `├─ ⚠ VULNERABILITIES:`, 'red');
        data.vulnerabilities.forEach(v => printLine(term, `│  ├─ [${v.severity}] ${v.type}: ${v.detail}`, 'red'));
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderSSL(term, data) {
    printLine(term, `┌─ SSL/TLS AUDIT ──────────────────────`, 'cyan');
    printLine(term, `├─ GRADE: ${data.grade} (Score: ${data.score}/100)`, data.score >= 80 ? 'green' : data.score >= 50 ? 'yellow' : 'red');
    if (data.certificate && !data.certificate.error) {
        const c = data.certificate;
        printLine(term, `├─ CERTIFICATE:`, 'yellow');
        printLine(term, `│  ├─ Subject: ${JSON.stringify(c.subject||{})}`, 'white');
        printLine(term, `│  ├─ Issuer: ${JSON.stringify(c.issuer||{})}`, 'white');
        printLine(term, `│  ├─ Valid: ${c.not_before} → ${c.not_after}`, 'white');
        printLine(term, `│  ├─ Days until expiry: ${c.days_until_expiry}`, c.days_until_expiry > 30 ? 'green' : 'red');
        printLine(term, `│  └─ SANs: ${(c.san||[]).join(', ')}`, 'dim');
    }
    if (data.protocols) {
        printLine(term, `├─ PROTOCOLS:`, 'yellow');
        Object.entries(data.protocols).forEach(([p, v]) => {
            printLine(term, `│  ├─ ${p}: ${v ? 'ENABLED' : 'DISABLED'}`, p.includes('1.0') || p.includes('1.1') ? (v ? 'red' : 'green') : (v ? 'green' : 'dim'));
        });
    }
    if (data.vulnerabilities?.length) {
        printLine(term, `├─ VULNERABILITIES:`, 'red');
        data.vulnerabilities.forEach(v => printLine(term, `│  ├─ [${v.severity}] ${v.name}${v.detail ? ': '+v.detail : ''}`, 'red'));
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderSecHeaders(term, data) {
    printLine(term, `┌─ SECURITY HEADERS ───────────────────`, 'cyan');
    printLine(term, `├─ SCORE: ${data.score}/100 (Grade: ${data.grade})`, data.score >= 70 ? 'green' : data.score >= 40 ? 'yellow' : 'red');
    if (data.headers) {
        Object.entries(data.headers).forEach(([h, info]) => {
            const color = info.status?.includes('✓') ? 'green' : info.status?.includes('⚠') ? 'yellow' : 'red';
            printLine(term, `├─ ${h}: ${info.status}`, color);
            if (info.value && info.quality && info.quality !== 'NONE') {
                printLine(term, `│  └─ Quality: ${info.quality}`, info.quality === 'STRONG' ? 'green' : info.quality === 'WEAK' ? 'red' : 'white');
            }
        });
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderCORS(term, data) {
    printLine(term, `┌─ CORS ANALYSIS ──────────────────────`, 'cyan');
    printLine(term, `├─ Risk: ${data.risk_level}`, data.risk_level === 'CRITICAL' ? 'red' : data.risk_level === 'LOW' ? 'green' : 'yellow');
    (data.tests||[]).forEach(t => {
        if (t.error) return;
        const color = t.vulnerable ? 'red' : 'green';
        printLine(term, `├─ ${t.test}: ${t.vulnerable ? 'VULNERABLE ⚠' : 'SAFE ✓'}`, color);
        if (t.vulnerable) printLine(term, `│  └─ ACAO: ${t.acao_returned}, Credentials: ${t.credentials_allowed}`, 'red');
    });
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderRedirect(term, data) {
    printLine(term, `┌─ OPEN REDIRECT SCAN ─────────────────`, 'cyan');
    printLine(term, `├─ Vulnerable: ${data.vulnerable ? 'YES ⚠' : 'NO ✓'}`, data.vulnerable ? 'red' : 'green');
    (data.tests||[]).filter(t => t.vulnerable).forEach(t => {
        printLine(term, `├─ ⚠ ${t.parameter}: Redirects to ${t.redirect_to}`, 'red');
    });
    printLine(term, `└─ Parameters tested: ${data.stats?.parameters_tested || 0}`, 'dim');
}

function renderCookies(term, data) {
    printLine(term, `┌─ COOKIE ANALYSIS ────────────────────`, 'cyan');
    printLine(term, `├─ Score: ${data.score}/100 (${data.grade})`, data.score >= 70 ? 'green' : 'red');
    (data.cookies||[]).forEach(c => {
        printLine(term, `├─ ${c.name} [${c.risk}]`, c.risk === 'CRITICAL' ? 'red' : c.risk === 'MEDIUM' ? 'yellow' : 'green');
        printLine(term, `│  ├─ Domain: ${c.domain}, Path: ${c.path}`, 'dim');
        printLine(term, `│  ├─ Flags: ${(c.flags||[]).join(', ') || 'NONE'}`, 'white');
        if (c.issues?.length) c.issues.forEach(iss => printLine(term, `│  ├─ ⚠ ${iss}`, 'red'));
    });
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderTakeover(term, data) {
    printLine(term, `┌─ SUBDOMAIN TAKEOVER ─────────────────`, 'cyan');
    printLine(term, `├─ Scanned: ${data.stats?.subdomains_scanned || 0} subdomains`, 'white');
    if (data.vulnerable?.length) {
        printLine(term, `├─ ⚠ VULNERABLE (${data.vulnerable.length}):`, 'red');
        data.vulnerable.forEach(v => {
            printLine(term, `│  ├─ ${v.subdomain} → ${v.cname}`, 'red');
            printLine(term, `│  │  └─ Service: ${v.service} | ${v.status}`, 'yellow');
        });
    } else {
        printLine(term, `├─ No takeover vulnerabilities found ✓`, 'green');
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderWhois(term, data) {
    printLine(term, `┌─ WHOIS INTELLIGENCE ─────────────────`, 'cyan');
    if (data.whois) {
        const w = data.whois;
        if (w.error) {
            printLine(term, `├─ Error: ${w.error}`, 'red');
            if (w.raw) printLine(term, `├─ Raw:\n${w.raw.substring(0, 500)}`, 'dim');
        } else {
            Object.entries(w).forEach(([k, v]) => {
                if (v && v !== 'Unknown' && v !== 'REDACTED' && v !== 'N/A' && !Array.isArray(v)) {
                    printLine(term, `├─ ${k.replace(/_/g,' ').toUpperCase()}: ${v}`, 'white');
                } else if (Array.isArray(v) && v.length > 0) {
                    printLine(term, `├─ ${k.replace(/_/g,' ').toUpperCase()}:`, 'yellow');
                    v.slice(0,5).forEach(item => printLine(term, `│  ├─ ${item}`, 'white'));
                }
            });
        }
    }
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderReputation(term, data) {
    printLine(term, `┌─ DOMAIN REPUTATION ──────────────────`, 'cyan');
    printLine(term, `├─ Score: ${data.score}/100 (${data.grade})`, data.score >= 70 ? 'green' : 'red');
    printLine(term, `├─ Blacklisted: ${data.blacklisted ? 'YES ⚠' : 'NO ✓'}`, data.blacklisted ? 'red' : 'green');
    (data.checks||[]).forEach(c => {
        const color = c.status?.includes('CLEAN') ? 'green' : c.status?.includes('LISTED') ? 'red' : 'dim';
        printLine(term, `├─ ${c.blacklist}: ${c.status}`, color);
    });
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderRobots(term, data) {
    printLine(term, `┌─ ROBOTS & SITEMAP ───────────────────`, 'cyan');
    const rb = data.robots_txt || {};
    printLine(term, `├─ robots.txt: ${rb.exists ? 'EXISTS ✓' : 'NOT FOUND'}`, rb.exists ? 'green' : 'dim');
    if (rb.exists) {
        printLine(term, `├─ Rules: ${rb.total_rules || 0}`, 'white');
        printLine(term, `├─ Disallowed (${(rb.disallowed_paths||[]).length}):`, 'yellow');
        (rb.disallowed_paths||[]).slice(0,10).forEach(p => printLine(term, `│  ├─ ${p}`, 'white'));
        if (rb.interesting_paths?.length) {
            printLine(term, `├─ ⚠ INTERESTING PATHS:`, 'red');
            rb.interesting_paths.forEach(p => printLine(term, `│  ├─ ${p}`, 'yellow'));
        }
    }
    printLine(term, `├─ SITEMAPS (${(data.sitemaps||[]).length}):`, 'cyan');
    (data.sitemaps||[]).forEach(sm => {
        printLine(term, `│  ├─ ${sm.url} (${sm.urls_count} URLs)`, 'green');
    });
    printLine(term, `└──────────────────────────────────────`, 'cyan');
}

function renderFullRecon(term, data) {
    printLine(term, `\n╔══════════════════════════════════════════════════════╗`, 'yellow');
    printLine(term, `║  ⚡ FULL RECONNAISSANCE REPORT                       ║`, 'yellow');
    printLine(term, `║  Overall Score: ${String(data.overall_score).padEnd(4)} Grade: ${(data.overall_grade||'?').padEnd(24)}║`, 'yellow');
    printLine(term, `╚══════════════════════════════════════════════════════╝`, 'yellow');
    if (data.modules) {
        Object.entries(data.modules).forEach(([mod, result]) => {
            const info = MODULE_INFO[mod] || { icon: '📊', name: mod };
            const hasError = result.error;
            printLine(term, `\n${info.icon} ${info.name.toUpperCase()} ${hasError ? '[FAILED]' : '[OK]'}`, hasError ? 'red' : 'green');
            if (result.stats) {
                Object.entries(result.stats).forEach(([k, v]) => {
                    printLine(term, `  ├─ ${k}: ${v}`, 'white');
                });
            }
        });
    }
}

function renderGeneric(term, data) {
    renderObject(term, data, '');
}

// ===== HELPERS =====
function renderObject(term, obj, prefix) {
    Object.entries(obj).forEach(([k, v]) => {
        if (k === 'module' || k === 'domain' || k === 'stats' || k === 'scan_time') return;
        if (v === null || v === undefined) return;
        if (typeof v === 'object' && !Array.isArray(v)) {
            printLine(term, `${prefix}├─ ${k}:`, 'yellow');
            renderObject(term, v, prefix + '│  ');
        } else if (Array.isArray(v)) {
            printLine(term, `${prefix}├─ ${k} (${v.length}):`, 'yellow');
            v.slice(0, 15).forEach((item, i) => {
                if (typeof item === 'object') {
                    printLine(term, `${prefix}│  ├─ [${i}]:`, 'dim');
                    renderObject(term, item, prefix + '│  │  ');
                } else {
                    printLine(term, `${prefix}│  ├─ ${item}`, 'white');
                }
            });
            if (v.length > 15) printLine(term, `${prefix}│  └─ ... +${v.length - 15} more`, 'dim');
        } else {
            printLine(term, `${prefix}├─ ${k}: ${v}`, 'white');
        }
    });
}

function printLine(term, text, color) {
    const line = document.createElement('div');
    line.className = `term-line ${color || ''}`;
    line.textContent = text;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
}

function timestamp() {
    const d = new Date();
    return d.toTimeString().split(' ')[0];
}

function shakeInput() {
    const el = document.querySelector('.input-hud');
    el.classList.add('shake');
    setTimeout(() => el.classList.remove('shake'), 500);
}

function clearTerminal() {
    const term = document.getElementById('terminalOutput');
    term.innerHTML = `<div class="term-line dim">[${timestamp()}] Terminal cleared.</div>`;
}

function exportResults() {
    if (Object.keys(scanHistory).length === 0) {
        alert('No scan results to export. Run a scan first.');
        return;
    }
    const blob = new Blob([JSON.stringify(scanHistory, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ddos_f16_report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
}

// ===== CLOCK & UPTIME =====
function updateClock() {
    const now = new Date();
    document.getElementById('topTime').textContent = now.toUTCString().split(' ').slice(4).join(' ') + ' UTC';
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const sec = String(elapsed % 60).padStart(2, '0');
    document.getElementById('uptime').textContent = `${min}:${sec}`;
}
setInterval(updateClock, 1000);

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    updateClock();
    // Open first category
    document.getElementById('cat-dns').classList.add('open');
    selectModule('dns_recon');
});
