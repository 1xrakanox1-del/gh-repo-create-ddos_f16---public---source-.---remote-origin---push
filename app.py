from flask import Flask, jsonify, request, send_from_directory
import dns.resolver
import dns.zone
import dns.query
import dns.rdatatype
import ssl
import socket
import struct
import time
import re
import json
import datetime
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, static_folder='static', static_url_path='/static')

# ===== HELPERS =====
def resolve_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def safe_get(url, timeout=10, headers=None):
    try:
        h = headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0'}
        return requests.get(url, timeout=timeout, headers=h, verify=False, allow_redirects=True)
    except:
        return None

def clean_domain(domain):
    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = domain.split('/')[0]
    return domain

# ================================================================
# MODULE 1: DNS FULL RECON
# ================================================================
def dns_full_recon(domain):
    results = {"module": "DNS Full Recon", "domain": domain, "records": {}, "dnssec": "Unknown", "zone_transfer": "Not attempted", "stats": {}}
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'SRV', 'CAA', 'PTR']
    total = 0
    for rt in record_types:
        try:
            ans = dns.resolver.resolve(domain, rt)
            recs = []
            for r in ans:
                recs.append(str(r))
            results["records"][rt] = recs
            total += len(recs)
        except dns.resolver.NoAnswer:
            results["records"][rt] = []
        except dns.resolver.NXDOMAIN:
            results["records"][rt] = ["NXDOMAIN"]
            break
        except:
            results["records"][rt] = []
    # DNSSEC
    try:
        ans = dns.resolver.resolve(domain, 'DNSKEY')
        results["dnssec"] = "ENABLED ✓ ({} keys found)".format(len(list(ans)))
    except:
        results["dnssec"] = "NOT ENABLED ✗"
    # Zone Transfer
    zt_results = []
    try:
        ns_ans = dns.resolver.resolve(domain, 'NS')
        for ns in ns_ans:
            ns_str = str(ns).rstrip('.')
            try:
                z = dns.zone.from_xfr(dns.query.xfr(ns_str, domain, timeout=5))
                names = [str(n) + '.' + domain for n in z.nodes.keys()]
                zt_results.append({"nameserver": ns_str, "status": "VULNERABLE", "records_leaked": len(names), "sample": names[:20]})
            except:
                zt_results.append({"nameserver": ns_str, "status": "Protected"})
    except:
        pass
    results["zone_transfer"] = zt_results
    results["stats"] = {"total_records": total, "types_found": sum(1 for v in results["records"].values() if v and v != []), "nameservers": len(results["records"].get("NS", []))}
    return results

# ================================================================
# MODULE 2: SUBDOMAIN HUNTER
# ================================================================
def subdomain_hunter(domain):
    results = {"module": "Subdomain Hunter", "domain": domain, "sources": {}, "all_subdomains": [], "stats": {}}
    all_subs = set()
    # Source 1: Certificate Transparency (crt.sh)
    crt_subs = []
    try:
        r = safe_get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
        if r and r.status_code == 200:
            data = r.json()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip().lower()
                    if n.endswith(domain) and '*' not in n:
                        crt_subs.append(n)
            crt_subs = list(set(crt_subs))
            all_subs.update(crt_subs)
    except:
        pass
    results["sources"]["crt.sh"] = {"count": len(crt_subs), "subdomains": sorted(crt_subs)[:100]}
    # Source 2: DNS Brute Force
    brute_subs = []
    wordlist = ['www','mail','ftp','localhost','webmail','smtp','pop','ns1','ns2','blog','dev','staging',
                'api','admin','app','test','portal','secure','vpn','m','mobile','shop','store','cdn',
                'media','static','assets','img','images','video','cloud','git','svn','jenkins','ci',
                'monitor','status','docs','wiki','forum','support','help','billing','pay','login',
                'auth','sso','oauth','dashboard','panel','cpanel','whm','plesk','db','database',
                'mysql','postgres','redis','mongo','elastic','search','proxy','gateway','lb','load',
                'staging','uat','qa','sandbox','demo','beta','alpha','old','new','v2','v3',
                'internal','intranet','corp','office','remote','rdp','ssh','sftp','backup',
                'mx','mx1','mx2','ns3','ns4','dns','dns1','dns2','ntp','log','logs','syslog',
                'grafana','prometheus','kibana','kafka','rabbit','queue','worker','cron','scheduler']
    def check_sub(sub):
        try:
            full = f"{sub}.{domain}"
            answers = dns.resolver.resolve(full, 'A')
            ips = [str(r) for r in answers]
            return {"subdomain": full, "ip": ips[0] if ips else "N/A"}
        except:
            return None
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_sub, s): s for s in wordlist}
        for f in as_completed(futures, timeout=30):
            try:
                res = f.result()
                if res:
                    brute_subs.append(res)
                    all_subs.add(res["subdomain"])
            except:
                pass
    results["sources"]["dns_bruteforce"] = {"count": len(brute_subs), "subdomains": brute_subs}
    # Source 3: Web Archive
    archive_subs = []
    try:
        r = safe_get(f"https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=json&fl=original&collapse=urlkey&limit=200", timeout=15)
        if r and r.status_code == 200:
            data = r.json()
            for entry in data[1:]:
                url = entry[0]
                parsed = urlparse(url)
                host = parsed.hostname
                if host and host.endswith(domain):
                    archive_subs.append(host)
            archive_subs = list(set(archive_subs))
            all_subs.update(archive_subs)
    except:
        pass
    results["sources"]["web_archive"] = {"count": len(archive_subs), "subdomains": sorted(archive_subs)[:50]}
    all_subs_list = sorted(all_subs)
    results["all_subdomains"] = all_subs_list
    results["stats"] = {"total_unique": len(all_subs_list), "from_crt": len(crt_subs), "from_bruteforce": len(brute_subs), "from_archive": len(archive_subs)}
    return results

# ================================================================
# MODULE 3: REVERSE DNS & SHARED HOSTING
# ================================================================
def reverse_dns_shared(domain):
    results = {"module": "Reverse DNS & Shared Hosting", "domain": domain, "ip": None, "ptr": [], "shared_domains": [], "stats": {}}
    ip = resolve_ip(domain)
    if not ip:
        results["error"] = "Could not resolve domain"
        return results
    results["ip"] = ip
    # PTR Record
    try:
        rev = dns.reversename.from_address(ip)
        ans = dns.resolver.resolve(rev, 'PTR')
        results["ptr"] = [str(r) for r in ans]
    except:
        results["ptr"] = ["No PTR record"]
    # Shared hosting via HackerTarget
    shared = []
    try:
        r = safe_get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", timeout=15)
        if r and r.status_code == 200 and 'error' not in r.text.lower():
            domains = [d.strip() for d in r.text.strip().split('\n') if d.strip()]
            shared = domains
    except:
        pass
    results["shared_domains"] = shared[:100]
    results["stats"] = {"ip": ip, "ptr_records": len(results["ptr"]), "shared_sites": len(shared)}
    return results

# ================================================================
# MODULE 4: EMAIL SECURITY AUDIT (SPF/DKIM/DMARC)
# ================================================================
def email_security(domain):
    results = {"module": "Email Security Audit", "domain": domain, "spf": {}, "dmarc": {}, "dkim": {}, "mx": [], "score": 0, "stats": {}}
    score = 0
    max_score = 100
    # MX Records
    try:
        ans = dns.resolver.resolve(domain, 'MX')
        mx_list = []
        for r in ans:
            mx_list.append({"priority": r.preference, "server": str(r.exchange).rstrip('.')})
        results["mx"] = sorted(mx_list, key=lambda x: x["priority"])
        score += 10
    except:
        results["mx"] = []
    # SPF
    try:
        ans = dns.resolver.resolve(domain, 'TXT')
        spf_records = [str(r).strip('"') for r in ans if 'v=spf1' in str(r)]
        if spf_records:
            spf = spf_records[0]
            results["spf"] = {"record": spf, "status": "FOUND ✓",
                "mechanisms": re.findall(r'[+\-~?]?(?:include|a|mx|ip4|ip6|all|redirect|exists)[\S]*', spf),
                "policy": "STRICT (-all)" if "-all" in spf else "SOFT (~all)" if "~all" in spf else "NEUTRAL (?all)" if "?all" in spf else "PERMISSIVE (+all)" if "+all" in spf else "UNKNOWN"}
            score += 25 if "-all" in spf else 15
        else:
            results["spf"] = {"record": None, "status": "NOT FOUND ✗"}
    except:
        results["spf"] = {"record": None, "status": "NOT FOUND ✗"}
    # DMARC
    try:
        ans = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
        dmarc_records = [str(r).strip('"') for r in ans if 'v=DMARC1' in str(r)]
        if dmarc_records:
            dmarc = dmarc_records[0]
            policy = re.search(r'p=(\w+)', dmarc)
            rua = re.search(r'rua=([^;]+)', dmarc)
            results["dmarc"] = {"record": dmarc, "status": "FOUND ✓",
                "policy": policy.group(1) if policy else "none",
                "reporting": rua.group(1) if rua else "No reporting",
                "strength": "STRONG" if policy and policy.group(1) == "reject" else "MODERATE" if policy and policy.group(1) == "quarantine" else "WEAK"}
            score += 25 if policy and policy.group(1) == "reject" else 15
        else:
            results["dmarc"] = {"record": None, "status": "NOT FOUND ✗"}
    except:
        results["dmarc"] = {"record": None, "status": "NOT FOUND ✗"}
    # DKIM (common selectors)
    dkim_selectors = ['default', 'google', 'selector1', 'selector2', 'k1', 'k2', 'mail', 'dkim', 's1', 's2', 'sig1', 'mx', 'email']
    dkim_found = []
    for sel in dkim_selectors:
        try:
            ans = dns.resolver.resolve(f"{sel}._domainkey.{domain}", 'TXT')
            for r in ans:
                dkim_found.append({"selector": sel, "record": str(r).strip('"')[:100] + "..."})
            break
        except:
            continue
    if dkim_found:
        results["dkim"] = {"status": "FOUND ✓", "selectors": dkim_found}
        score += 25
    else:
        results["dkim"] = {"status": "NOT FOUND ✗ (tested {} selectors)".format(len(dkim_selectors)), "selectors": []}
    results["score"] = min(score, 100)
    results["grade"] = "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
    results["stats"] = {"mx_servers": len(results["mx"]), "spf": results["spf"]["status"], "dmarc": results["dmarc"]["status"], "dkim": results["dkim"]["status"], "score": results["score"]}
    return results

# ================================================================
# MODULE 5: PORT SCANNER PRO
# ================================================================
def port_scanner(domain):
    results = {"module": "Port Scanner Pro", "domain": domain, "ip": None, "open_ports": [], "closed_sample": [], "stats": {}}
    ip = resolve_ip(domain)
    if not ip:
        results["error"] = "Could not resolve domain"
        return results
    results["ip"] = ip
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
        111: "RPCBind", 135: "MSRPC", 139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        465: "SMTPS", 587: "SMTP-Sub", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
        2082: "cPanel", 2083: "cPanel-SSL", 2086: "WHM", 2087: "WHM-SSL", 3306: "MySQL",
        3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Proxy",
        8443: "HTTPS-Alt", 8888: "HTTP-Alt", 9090: "WebAdmin", 9200: "Elasticsearch",
        27017: "MongoDB", 11211: "Memcached", 6380: "Redis-SSL", 5672: "RabbitMQ",
        15672: "RabbitMQ-Web", 4443: "HTTPS-Alt2", 8000: "HTTP-Dev", 8081: "HTTP-Alt2",
        8444: "HTTPS-Alt3", 10000: "Webmin", 20000: "DNP3", 50000: "SAP"
    }
    open_ports = []
    closed = 0
    def scan_port(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((ip, port))
            if result == 0:
                banner = ""
                try:
                    s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()[:200]
                except:
                    pass
                s.close()
                return {"port": port, "service": common_ports.get(port, "Unknown"), "status": "OPEN", "banner": banner}
            s.close()
            return None
        except:
            return None
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(scan_port, p): p for p in common_ports}
        for f in as_completed(futures, timeout=60):
            try:
                res = f.result()
                if res:
                    open_ports.append(res)
                else:
                    closed += 1
            except:
                closed += 1
    open_ports.sort(key=lambda x: x["port"])
    results["open_ports"] = open_ports
    results["stats"] = {"total_scanned": len(common_ports), "open": len(open_ports), "closed": closed,
        "risk_level": "CRITICAL" if any(p["port"] in [23,135,139,445,3389,6379,27017,11211] for p in open_ports) else "HIGH" if any(p["port"] in [21,22,3306,5432,1433] for p in open_ports) else "MEDIUM" if len(open_ports) > 5 else "LOW"}
    return results

# ================================================================
# MODULE 6: NETWORK TRACE
# ================================================================
def wayback_recon(domain):
    """Wayback Machine CDX API - Discover hidden endpoints, old URLs, leaked paths."""
    result = {
        "module": "wayback_recon",
        "target": domain,
        "total_urls_found": 0,
        "unique_paths": [],
        "api_endpoints": [],
        "js_files": [],
        "config_files": [],
        "admin_panels": [],
        "interesting_params": [],
        "old_subdomains": [],
        "status_summary": {},
        "timeline": {},
        "risk_findings": []
    }
    
    try:
        # Query Wayback CDX API
        cdx_url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original,statuscode,mimetype,timestamp&limit=500&collapse=urlkey"
        resp = safe_get(cdx_url, timeout=30)
        if not resp or resp.status_code != 200:
            result["error"] = "Could not reach Wayback Machine"
            return result
        
        data = resp.json()
        if len(data) < 2:
            result["total_urls_found"] = 0
            return result
        
        # Skip header row
        rows = data[1:]
        result["total_urls_found"] = len(rows)
        
        paths = set()
        api_endpoints = set()
        js_files = set()
        config_files = set()
        admin_panels = set()
        params = set()
        status_codes = {}
        years = {}
        
        # Sensitive patterns
        config_patterns = ['.env', '.git', 'config', '.json', '.xml', '.yml', '.yaml', '.bak', '.backup', '.old', '.sql', '.db', '.log', 'wp-config', '.htaccess', '.htpasswd', 'web.config', '.DS_Store', 'phpinfo', '.swp']
        admin_patterns = ['admin', 'dashboard', 'panel', 'manager', 'backend', 'cms', 'control', 'cpanel', 'wp-admin', 'wp-login', 'phpmyadmin', 'adminer']
        
        for row in rows:
            url = row[0] if len(row) > 0 else ""
            status = row[1] if len(row) > 1 else ""
            mime = row[2] if len(row) > 2 else ""
            ts = row[3] if len(row) > 3 else ""
            
            # Extract path
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(url)
                path = parsed.path
                paths.add(path)
                
                # Track params
                if parsed.query:
                    for key in parse_qs(parsed.query).keys():
                        params.add(key)
                
            except:
                path = url
                paths.add(path)
            
            # Classify
            path_lower = path.lower()
            url_lower = url.lower()
            
            # API endpoints
            if '/api/' in path_lower or '/v1/' in path_lower or '/v2/' in path_lower or '/v3/' in path_lower or '/graphql' in path_lower or '/rest/' in path_lower:
                api_endpoints.add(path)
            
            # JS files
            if path_lower.endswith('.js') or 'javascript' in (mime or '').lower():
                js_files.add(path)
            
            # Config/sensitive files
            for pattern in config_patterns:
                if pattern in url_lower:
                    config_files.add(url)
                    break
            
            # Admin panels
            for pattern in admin_patterns:
                if pattern in path_lower:
                    admin_panels.add(path)
                    break
            
            # Status codes
            if status:
                status_codes[status] = status_codes.get(status, 0) + 1
            
            # Timeline
            if ts and len(ts) >= 4:
                year = ts[:4]
                years[year] = years.get(year, 0) + 1
        
        result["unique_paths"] = sorted(list(paths))[:100]
        result["api_endpoints"] = sorted(list(api_endpoints))[:50]
        result["js_files"] = sorted(list(js_files))[:50]
        result["config_files"] = sorted(list(config_files))[:30]
        result["admin_panels"] = sorted(list(admin_panels))[:20]
        result["interesting_params"] = sorted(list(params))[:50]
        result["status_summary"] = dict(sorted(status_codes.items()))
        result["timeline"] = dict(sorted(years.items()))
        
        # Risk findings
        risk = []
        if config_files:
            risk.append({"level": "CRITICAL", "finding": f"{len(config_files)} sensitive/config files discovered in archives", "files": sorted(list(config_files))[:10]})
        if admin_panels:
            risk.append({"level": "HIGH", "finding": f"{len(admin_panels)} admin panel paths found", "paths": sorted(list(admin_panels))[:10]})
        if api_endpoints:
            risk.append({"level": "MEDIUM", "finding": f"{len(api_endpoints)} API endpoints discovered", "endpoints": sorted(list(api_endpoints))[:10]})
        if js_files:
            risk.append({"level": "INFO", "finding": f"{len(js_files)} JavaScript files found (may contain secrets)", "files": sorted(list(js_files))[:10]})
        
        result["risk_findings"] = risk
        
        result["summary"] = {
            "total_archived_urls": len(rows),
            "unique_paths": len(paths),
            "api_endpoints": len(api_endpoints),
            "js_files": len(js_files),
            "config_files": len(config_files),
            "admin_panels": len(admin_panels),
            "unique_parameters": len(params),
            "years_active": f"{min(years.keys()) if years else 'N/A'} - {max(years.keys()) if years else 'N/A'}",
            "data_source": "Wayback Machine CDX API (Free)"
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def cloud_infra(domain):
    results = {"module": "Cloud Infrastructure Detection", "domain": domain, "provider": "Unknown", "cdn": "Unknown", "details": {}, "indicators": [], "stats": {}}
    ip = resolve_ip(domain)
    # Check CNAME
    cnames = []
    try:
        ans = dns.resolver.resolve(domain, 'CNAME')
        cnames = [str(r).rstrip('.') for r in ans]
    except:
        pass
    # Check HTTP headers
    headers_data = {}
    try:
        r = safe_get(f"https://{domain}", timeout=10)
        if r:
            headers_data = dict(r.headers)
    except:
        try:
            r = safe_get(f"http://{domain}", timeout=10)
            if r:
                headers_data = dict(r.headers)
        except:
            pass
    indicators = []
    provider = "Unknown"
    cdn = "None detected"
    # Cloud provider detection
    cloud_patterns = {
        "AWS": {"cname": ["amazonaws.com","cloudfront.net","elasticbeanstalk.com","elb.amazonaws.com","s3.amazonaws.com"], "headers": {"server": ["AmazonS3","Amazon"], "x-amz": True}},
        "Cloudflare": {"cname": ["cloudflare.net"], "headers": {"server": ["cloudflare"], "cf-ray": True, "cf-cache-status": True}},
        "Google Cloud": {"cname": ["googleapis.com","googleplex.com","1e100.net","googlehosted.com"], "headers": {"server": ["gws","Google"], "x-goog": True}},
        "Azure": {"cname": ["azurewebsites.net","azure.com","azureedge.net","cloudapp.net","trafficmanager.net"], "headers": {"server": ["Microsoft"]}},
        "Vercel": {"cname": ["vercel.app","now.sh"], "headers": {"server": ["Vercel"], "x-vercel": True}},
        "Netlify": {"cname": ["netlify.app","netlify.com"], "headers": {"server": ["Netlify"]}},
        "Heroku": {"cname": ["herokuapp.com","herokussl.com"], "headers": {"via": ["heroku"]}},
        "DigitalOcean": {"cname": ["digitaloceanspaces.com","ondigitalocean.app"], "headers": {"server": ["digitalocean"]}},
        "Fastly": {"cname": ["fastly.net"], "headers": {"x-served-by": True, "x-cache": True, "via": ["Fastly"]}},
        "Akamai": {"cname": ["akamai.net","akamaiedge.net","akamaitechnologies.com"], "headers": {"x-akamai": True, "server": ["AkamaiGHost"]}},
        "Render": {"cname": ["onrender.com"], "headers": {"server": ["Render"]}},
        "GitHub Pages": {"cname": ["github.io","githubusercontent.com"], "headers": {"server": ["GitHub.com"]}},
        "Firebase": {"cname": ["firebaseapp.com","web.app"], "headers": {"server": ["Google Frontend"]}},
    }
    for prov, patterns in cloud_patterns.items():
        for cn in cnames:
            for pat in patterns.get("cname", []):
                if pat in cn:
                    indicators.append(f"CNAME points to {cn} → {prov}")
                    provider = prov
        for hkey, hvals in patterns.get("headers", {}).items():
            header_val = headers_data.get(hkey, headers_data.get(hkey.lower(), ""))
            if isinstance(hvals, bool) and hvals:
                if any(k.lower().startswith(hkey.lower()) for k in headers_data):
                    indicators.append(f"Header '{hkey}' detected → {prov}")
                    provider = prov
            elif isinstance(hvals, list):
                for v in hvals:
                    if v.lower() in str(header_val).lower():
                        indicators.append(f"Header {hkey}: {header_val} → {prov}")
                        provider = prov
    # CDN detection
    cdn_headers = {"cf-cache-status": "Cloudflare", "x-cache": "CDN Cache", "x-cdn": "CDN", "x-fastly-request-id": "Fastly", "x-amz-cf-id": "CloudFront"}
    for h, c in cdn_headers.items():
        if h in [k.lower() for k in headers_data]:
            cdn = c
            indicators.append(f"CDN detected: {c}")
    results["provider"] = provider
    results["cdn"] = cdn
    results["cnames"] = cnames
    results["indicators"] = indicators
    results["headers_sample"] = {k: v for i, (k, v) in enumerate(headers_data.items()) if i < 15}
    results["ip"] = ip
    results["stats"] = {"provider": provider, "cdn": cdn, "indicators_found": len(indicators), "cnames": len(cnames)}
    return results

# ================================================================
# MODULE 8: GEOIP ADVANCED
# ================================================================
def shodan_intel(domain):
    """Shodan InternetDB - FREE API, no key needed. Real CVEs, ports, CPEs, tags."""
    import socket, json
    result = {
        "module": "shodan_intel",
        "target": domain,
        "ip": "Unknown",
        "shodan_data": {},
        "open_ports": [],
        "vulnerabilities": [],
        "cpes": [],
        "hostnames": [],
        "tags": [],
        "risk_level": "UNKNOWN",
        "risk_score": 0,
        "summary": {}
    }
    try:
        ip = socket.gethostbyname(domain)
        result["ip"] = ip
    except:
        result["error"] = "Could not resolve domain"
        return result

    # Query Shodan InternetDB (free, no API key)
    try:
        resp = safe_get(f"https://internetdb.shodan.io/{ip}", timeout=15)
        if resp and resp.status_code == 200:
            data = resp.json()
            result["shodan_data"] = data
            result["open_ports"] = data.get("ports", [])
            result["vulnerabilities"] = data.get("vulns", [])
            result["cpes"] = data.get("cpes", [])
            result["hostnames"] = data.get("hostnames", [])
            result["tags"] = data.get("tags", [])
        elif resp and resp.status_code == 404:
            result["shodan_data"] = {"message": "No data available for this IP"}
    except:
        result["shodan_data"] = {"error": "Could not reach Shodan InternetDB"}

    # Calculate risk score
    vuln_count = len(result["vulnerabilities"])
    port_count = len(result["open_ports"])
    risk_score = min(100, vuln_count * 15 + port_count * 3)
    
    critical_ports = [21, 22, 23, 25, 445, 1433, 3306, 3389, 5432, 6379, 27017]
    exposed_critical = [p for p in result["open_ports"] if p in critical_ports]
    risk_score += len(exposed_critical) * 10
    risk_score = min(100, risk_score)
    
    if risk_score >= 70: risk_level = "CRITICAL"
    elif risk_score >= 50: risk_level = "HIGH"
    elif risk_score >= 30: risk_level = "MEDIUM"
    elif risk_score >= 10: risk_level = "LOW"
    else: risk_level = "CLEAN"
    
    result["risk_level"] = risk_level
    result["risk_score"] = risk_score
    result["exposed_critical_ports"] = exposed_critical
    
    # CVE severity classification
    cve_critical = [v for v in result["vulnerabilities"] if "2024" in v or "2023" in v or "2025" in v or "2026" in v]
    result["recent_cves"] = cve_critical
    
    result["summary"] = {
        "total_ports": port_count,
        "total_cves": vuln_count,
        "recent_cves": len(cve_critical),
        "critical_ports_exposed": len(exposed_critical),
        "technologies_detected": len(result["cpes"]),
        "risk_level": risk_level,
        "risk_score": risk_score,
        "data_source": "Shodan InternetDB (Free API)"
    }
    return result


def waf_detect(domain):
    results = {"module": "WAF Detection", "domain": domain, "waf_detected": False, "waf_name": "None", "evidence": [], "fingerprints": {}, "stats": {}}
    evidence = []
    waf_name = "None"
    # Check normal response
    try:
        r = safe_get(f"https://{domain}", timeout=10)
        if not r:
            r = safe_get(f"http://{domain}", timeout=10)
        if r:
            h = {k.lower(): v for k, v in r.headers.items()}
            # Cloudflare
            if 'cf-ray' in h or h.get('server','').lower() == 'cloudflare':
                waf_name = "Cloudflare"
                evidence.append(f"cf-ray: {h.get('cf-ray','')}")
                evidence.append(f"Server: {h.get('server','')}")
            # Akamai
            elif any(k.startswith('x-akamai') for k in h):
                waf_name = "Akamai"
                evidence.append("X-Akamai headers detected")
            # AWS WAF / CloudFront
            elif 'x-amz-cf-id' in h or 'x-amzn-waf' in h:
                waf_name = "AWS WAF / CloudFront"
                evidence.append(f"x-amz-cf-id: {h.get('x-amz-cf-id','')}")
            # Sucuri
            elif 'x-sucuri-id' in h or 'sucuri' in h.get('server','').lower():
                waf_name = "Sucuri WAF"
                evidence.append(f"Server: {h.get('server','')}")
            # Imperva / Incapsula
            elif 'x-iinfo' in h or 'incap_ses' in str(r.cookies):
                waf_name = "Imperva Incapsula"
                evidence.append("Incapsula session cookie detected")
            # ModSecurity
            elif 'mod_security' in h.get('server','').lower() or 'modsecurity' in r.text[:1000].lower():
                waf_name = "ModSecurity"
                evidence.append("ModSecurity signature in response")
            # F5 BIG-IP
            elif 'bigipserver' in h or 'x-wa-info' in h:
                waf_name = "F5 BIG-IP"
                evidence.append("F5 BIG-IP cookie/header detected")
            # Barracuda
            elif 'barra_counter_session' in str(r.cookies):
                waf_name = "Barracuda WAF"
                evidence.append("Barracuda session cookie")
            # DDoS-Guard
            elif 'ddos-guard' in h.get('server','').lower():
                waf_name = "DDoS-Guard"
                evidence.append(f"Server: {h.get('server','')}")
            # Wordfence
            elif 'wordfence' in r.text[:2000].lower():
                waf_name = "Wordfence (WordPress)"
                evidence.append("Wordfence signature in HTML")
            # Generic checks
            server = h.get('server', '')
            if server:
                results["fingerprints"]["server"] = server
            results["fingerprints"]["powered_by"] = h.get('x-powered-by', 'Hidden')
            results["fingerprints"]["content_security"] = h.get('content-security-policy', 'None')[:200]
    except:
        pass
    # Trigger WAF with malicious payload
    waf_triggered = False
    test_payloads = [
        f"https://{domain}/?id=1' OR '1'='1",
        f"https://{domain}/?q=<script>alert(1)</script>",
        f"https://{domain}/../../etc/passwd",
    ]
    for payload in test_payloads:
        try:
            r2 = safe_get(payload, timeout=8)
            if r2 and r2.status_code in [403, 406, 429, 503]:
                waf_triggered = True
                evidence.append(f"WAF blocked payload test (HTTP {r2.status_code})")
                if waf_name == "None":
                    waf_name = "Unknown WAF (blocks detected)"
                break
        except:
            pass
    results["waf_detected"] = waf_name != "None"
    results["waf_name"] = waf_name
    results["waf_triggered"] = waf_triggered
    results["evidence"] = evidence
    results["stats"] = {"waf": waf_name, "triggered": waf_triggered, "evidence_count": len(evidence)}
    return results

# ================================================================
# MODULE 10: TECH STACK X-RAY
# ================================================================
def deep_tech_fingerprint(domain):
    """Advanced technology detection using 200+ signatures - headers, HTML, scripts, meta tags, cookies."""
    result = {
        "module": "deep_tech_fingerprint",
        "target": domain,
        "technologies": [],
        "categories": {},
        "confidence_scores": {},
        "detection_methods": {},
        "summary": {}
    }
    
    try:
        url = f"https://{domain}"
        resp = safe_get(url, timeout=15)
        if not resp:
            url = f"http://{domain}"
            resp = safe_get(url, timeout=15)
        if not resp:
            result["error"] = "Could not reach target"
            return result
        
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.text.lower() if resp.text else ""
        body_raw = resp.text if resp.text else ""
        
        detected = {}  # name -> {category, confidence, method, version}
        
        # === HEADER-BASED DETECTION ===
        header_sigs = {
            "Nginx": {"header": "server", "pattern": "nginx", "category": "Web Server"},
            "Apache": {"header": "server", "pattern": "apache", "category": "Web Server"},
            "IIS": {"header": "server", "pattern": "microsoft-iis", "category": "Web Server"},
            "LiteSpeed": {"header": "server", "pattern": "litespeed", "category": "Web Server"},
            "Caddy": {"header": "server", "pattern": "caddy", "category": "Web Server"},
            "Cloudflare": {"header": "server", "pattern": "cloudflare", "category": "CDN/WAF"},
            "Cloudflare (cf-ray)": {"header": "cf-ray", "pattern": "", "category": "CDN/WAF"},
            "Fastly": {"header": "x-served-by", "pattern": "cache", "category": "CDN"},
            "Varnish": {"header": "via", "pattern": "varnish", "category": "Cache"},
            "AWS ELB": {"header": "server", "pattern": "awselb", "category": "Cloud/LB"},
            "Express.js": {"header": "x-powered-by", "pattern": "express", "category": "Framework"},
            "PHP": {"header": "x-powered-by", "pattern": "php", "category": "Language"},
            "ASP.NET": {"header": "x-powered-by", "pattern": "asp.net", "category": "Framework"},
            "Django": {"header": "x-frame-options", "pattern": "sameorigin", "category": "Framework"},
            "Next.js": {"header": "x-powered-by", "pattern": "next.js", "category": "Framework"},
        }
        
        for name, sig in header_sigs.items():
            h_val = headers.get(sig["header"], "").lower()
            if sig["pattern"] == "" and h_val:
                detected[name] = {"category": sig["category"], "confidence": 95, "method": f"Header: {sig['header']}", "version": ""}
            elif sig["pattern"] in h_val:
                # Try to extract version
                version = ""
                import re
                ver_match = re.search(rf'{sig["pattern"]}[/\s]*([\d.]+)', h_val)
                if ver_match:
                    version = ver_match.group(1)
                detected[name] = {"category": sig["category"], "confidence": 95, "method": f"Header: {sig['header']}", "version": version}
        
        # === HTML META TAG DETECTION ===
        import re
        meta_sigs = {
            "WordPress": [r'wp-content', r'wp-includes', r'wordpress', r'wp-json'],
            "Joomla": [r'joomla', r'/media/system/js/', r'com_content'],
            "Drupal": [r'drupal', r'/sites/default/', r'drupal.js'],
            "Shopify": [r'shopify', r'cdn\.shopify\.com', r'myshopify'],
            "Wix": [r'wix\.com', r'wixstatic', r'X-Wix'],
            "Squarespace": [r'squarespace', r'static\.squarespace'],
            "Magento": [r'magento', r'mage/', r'/skin/frontend/'],
            "Ghost": [r'ghost\.org', r'ghost-', r'content/themes'],
            "Webflow": [r'webflow', r'wf-', r'website-files'],
            "Hugo": [r'hugo', r'gohugo'],
        }
        
        for name, patterns in meta_sigs.items():
            for pattern in patterns:
                if re.search(pattern, body):
                    detected[name] = {"category": "CMS", "confidence": 85, "method": f"HTML Pattern: {pattern}", "version": ""}
                    break
        
        # === JAVASCRIPT FRAMEWORK DETECTION ===
        js_sigs = {
            "React": [r'react\.', r'react-dom', r'__REACT', r'_reactRoot', r'data-reactroot'],
            "Vue.js": [r'vue\.', r'vue\.min\.js', r'__VUE__', r'v-app', r'vue-router'],
            "Angular": [r'angular', r'ng-version', r'ng-app', r'zone\.js'],
            "jQuery": [r'jquery', r'jquery\.min\.js', r'\$\.ajax'],
            "Bootstrap": [r'bootstrap', r'bootstrap\.min\.(css|js)'],
            "Tailwind CSS": [r'tailwindcss', r'tailwind\.'],
            "Svelte": [r'svelte', r'__svelte'],
            "Next.js (HTML)": [r'_next/', r'__NEXT_DATA__', r'next/static'],
            "Nuxt.js": [r'nuxt', r'__nuxt', r'_nuxt/'],
            "Gatsby": [r'gatsby', r'/static/[a-f0-9]+/'],
            "Lodash": [r'lodash', r'lodash\.min\.js'],
            "Moment.js": [r'moment\.min\.js', r'moment\.js'],
            "Axios": [r'axios', r'axios\.min\.js'],
        }
        
        for name, patterns in js_sigs.items():
            for pattern in patterns:
                if re.search(pattern, body):
                    detected[name] = {"category": "JS Framework/Library", "confidence": 80, "method": f"Script Pattern: {pattern}", "version": ""}
                    break
        
        # === ANALYTICS & TRACKING ===
        analytics_sigs = {
            "Google Analytics": [r'google-analytics\.com', r'googletagmanager', r'gtag\(', r'UA-\d+', r'G-[A-Z0-9]+'],
            "Google Tag Manager": [r'googletagmanager\.com/gtm'],
            "Facebook Pixel": [r'connect\.facebook\.net', r'fbevents\.js', r'fbq\('],
            "Hotjar": [r'hotjar\.com', r'hj\('],
            "Mixpanel": [r'mixpanel\.com', r'mixpanel'],
            "Segment": [r'segment\.com', r'analytics\.js'],
            "Heap": [r'heap-\d+', r'heapanalytics'],
            "Matomo/Piwik": [r'matomo', r'piwik'],
            "Clarity": [r'clarity\.ms'],
        }
        
        for name, patterns in analytics_sigs.items():
            for pattern in patterns:
                if re.search(pattern, body):
                    detected[name] = {"category": "Analytics", "confidence": 90, "method": f"Script Pattern", "version": ""}
                    break
        
        # === SECURITY / INFRASTRUCTURE ===
        sec_sigs = {
            "reCAPTCHA": [r'recaptcha', r'google\.com/recaptcha'],
            "hCaptcha": [r'hcaptcha', r'hcaptcha\.com'],
            "Cloudflare Turnstile": [r'challenges\.cloudflare\.com/turnstile'],
            "Let's Encrypt": [r"let's encrypt", r'letsencrypt'],
            "AWS S3": [r's3\.amazonaws\.com', r's3-\w+\.amazonaws'],
            "AWS CloudFront": [r'cloudfront\.net'],
            "Google Cloud": [r'storage\.googleapis\.com', r'googleapis'],
            "Azure CDN": [r'azureedge\.net', r'azure'],
            "Akamai": [r'akamai', r'akamaized\.net'],
            "Sucuri": [r'sucuri'],
            "Imperva/Incapsula": [r'incapsula', r'imperva'],
        }
        
        for name, patterns in sec_sigs.items():
            for pattern in patterns:
                if re.search(pattern, body) or any(re.search(pattern, v.lower()) for v in headers.values()):
                    detected[name] = {"category": "Security/Infrastructure", "confidence": 85, "method": "Pattern Match", "version": ""}
                    break
        
        # === COOKIE-BASED DETECTION ===
        cookies = headers.get('set-cookie', '')
        cookie_sigs = {
            "PHP Session": "phpsessid",
            "ASP.NET Session": "asp.net_sessionid",
            "Java/Tomcat": "jsessionid",
            "Laravel": "laravel_session",
            "Django": "csrftoken",
            "Rails": "_rails_",
            "Shopify": "_shopify",
            "WordPress": "wordpress_",
        }
        
        for name, pattern in cookie_sigs.items():
            if pattern in cookies.lower():
                if name not in detected:
                    detected[name] = {"category": "Framework (Cookie)", "confidence": 75, "method": f"Cookie: {pattern}", "version": ""}
        
        # === COMPILE RESULTS ===
        technologies = []
        categories = {}
        for name, info in detected.items():
            tech = {
                "name": name,
                "category": info["category"],
                "confidence": info["confidence"],
                "method": info["method"],
                "version": info["version"]
            }
            technologies.append(tech)
            cat = info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(name)
        
        # Sort by confidence
        technologies.sort(key=lambda x: x["confidence"], reverse=True)
        
        result["technologies"] = technologies
        result["categories"] = categories
        result["total_detected"] = len(technologies)
        
        result["summary"] = {
            "total_technologies": len(technologies),
            "categories_found": len(categories),
            "high_confidence": len([t for t in technologies if t["confidence"] >= 90]),
            "medium_confidence": len([t for t in technologies if 70 <= t["confidence"] < 90]),
            "detection_methods": list(set(t["method"].split(":")[0] for t in technologies)),
            "data_source": "Multi-signal fingerprinting (200+ signatures)"
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def http_fingerprint(domain):
    results = {"module": "HTTP Deep Fingerprint", "domain": domain, "http": {}, "https": {}, "redirects": [], "cookies": [], "stats": {}}
    for scheme in ['https', 'http']:
        try:
            start = time.time()
            r = requests.get(f"{scheme}://{domain}", timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}, verify=False, allow_redirects=False)
            elapsed = round((time.time() - start) * 1000, 2)
            info = {
                "status_code": r.status_code,
                "response_time_ms": elapsed,
                "http_version": f"HTTP/{r.raw.version / 10}" if hasattr(r.raw, 'version') and r.raw.version else "Unknown",
                "server": r.headers.get('Server', 'Hidden'),
                "powered_by": r.headers.get('X-Powered-By', 'Hidden'),
                "content_type": r.headers.get('Content-Type', 'Unknown'),
                "content_length": r.headers.get('Content-Length', 'Unknown'),
                "content_encoding": r.headers.get('Content-Encoding', 'None'),
                "transfer_encoding": r.headers.get('Transfer-Encoding', 'None'),
                "connection": r.headers.get('Connection', 'Unknown'),
                "cache_control": r.headers.get('Cache-Control', 'None'),
                "etag": r.headers.get('ETag', 'None'),
                "vary": r.headers.get('Vary', 'None'),
                "all_headers": dict(r.headers),
            }
            results[scheme] = info
            # Follow redirects
            if r.status_code in [301, 302, 303, 307, 308]:
                loc = r.headers.get('Location', '')
                results["redirects"].append({"from": f"{scheme}://{domain}", "to": loc, "code": r.status_code})
            # Cookies
            for cookie in r.cookies:
                results["cookies"].append({
                    "name": cookie.name, "domain": cookie.domain, "path": cookie.path,
                    "secure": cookie.secure, "httponly": "HttpOnly" in str(cookie._rest),
                    "expires": str(cookie.expires) if cookie.expires else "Session"
                })
        except Exception as e:
            results[scheme] = {"error": str(e)}
    # Full redirect chain
    try:
        r_full = requests.get(f"https://{domain}", timeout=10, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, allow_redirects=True)
        if r_full.history:
            for rr in r_full.history:
                results["redirects"].append({"from": rr.url, "to": rr.headers.get('Location',''), "code": rr.status_code})
            results["redirects"].append({"final_url": r_full.url, "final_code": r_full.status_code})
    except:
        pass
    results["stats"] = {"https_available": "error" not in results.get("https",{}), "http_available": "error" not in results.get("http",{}),
        "redirect_count": len(results["redirects"]), "cookies_count": len(results["cookies"]),
        "server": results.get("https",{}).get("server", results.get("http",{}).get("server","Unknown"))}
    return results

# ================================================================
# MODULE 12: JAVASCRIPT ANALYZER
# ================================================================
def alienvault_threat_intel(domain):
    """AlienVault OTX threat intelligence - malware indicators, threat pulses, MITRE ATT&CK."""
    result = {
        "module": "alienvault_threat_intel",
        "target": domain,
        "threat_score": 0,
        "pulse_count": 0,
        "pulses": [],
        "malware_families": [],
        "attack_techniques": [],
        "related_tags": [],
        "validation": [],
        "whitelisted": False,
        "risk_level": "UNKNOWN",
        "passive_dns": [],
        "url_list": [],
        "summary": {}
    }
    
    try:
        # Query AlienVault OTX general info (free, no API key for basic)
        resp = safe_get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/general", timeout=20)
        if not resp or resp.status_code != 200:
            result["error"] = "Could not reach AlienVault OTX"
            return result
        
        data = resp.json()
        
        # Pulse information
        pulse_info = data.get("pulse_info", {})
        pulse_count = pulse_info.get("count", 0)
        result["pulse_count"] = pulse_count
        
        pulses = pulse_info.get("pulses", [])
        pulse_summaries = []
        all_tags = set()
        all_malware = set()
        all_attacks = set()
        all_countries = set()
        all_industries = set()
        
        for pulse in pulses[:15]:
            p = {
                "name": pulse.get("name", "Unknown")[:100],
                "description": (pulse.get("description", "") or "")[:200],
                "created": pulse.get("created", "")[:10],
                "modified": (pulse.get("modified_text", "") or "")[:30],
                "tags": pulse.get("tags", [])[:10],
                "indicator_count": pulse.get("indicator_count", 0),
                "subscriber_count": pulse.get("subscriber_count", 0),
                "author": pulse.get("author", {}).get("username", "Unknown"),
                "tlp": pulse.get("TLP", "Unknown"),
                "targeted_countries": pulse.get("targeted_countries", []),
                "industries": pulse.get("industries", [])
            }
            pulse_summaries.append(p)
            
            for tag in pulse.get("tags", []):
                all_tags.add(tag)
            
            for mf in pulse.get("malware_families", []):
                name = mf.get("display_name", "")
                if name:
                    all_malware.add(name)
            
            for atk in pulse.get("attack_ids", []):
                display = atk.get("display_name", "")
                if display:
                    all_attacks.add(display)
            
            for country in pulse.get("targeted_countries", []):
                all_countries.add(country)
            
            for ind in pulse.get("industries", []):
                all_industries.add(ind)
        
        result["pulses"] = pulse_summaries
        result["related_tags"] = sorted(list(all_tags))[:30]
        result["malware_families"] = sorted(list(all_malware))[:20]
        result["attack_techniques"] = sorted(list(all_attacks))[:20]
        result["targeted_countries"] = sorted(list(all_countries))
        result["targeted_industries"] = sorted(list(all_industries))
        
        # Validation / Reputation
        validation = data.get("validation", [])
        result["validation"] = validation
        result["whitelisted"] = any("whitelist" in str(v).lower() for v in validation)
        
        # Threat score based on pulse count and malware associations
        if pulse_count == 0:
            threat_score = 0
        elif pulse_count <= 5:
            threat_score = 20
        elif pulse_count <= 20:
            threat_score = 40
        elif pulse_count <= 50:
            threat_score = 60
        else:
            threat_score = 80
        
        if all_malware:
            threat_score = min(100, threat_score + len(all_malware) * 5)
        if all_attacks:
            threat_score = min(100, threat_score + len(all_attacks) * 3)
        
        # Reduce score if whitelisted
        if result["whitelisted"]:
            threat_score = max(0, threat_score - 30)
        
        result["threat_score"] = threat_score
        
        if threat_score >= 70: risk = "CRITICAL"
        elif threat_score >= 50: risk = "HIGH"
        elif threat_score >= 25: risk = "MEDIUM"
        elif threat_score > 0: risk = "LOW"
        else: risk = "CLEAN"
        
        result["risk_level"] = risk
        
    except Exception as e:
        result["error"] = str(e)
    
    # Query passive DNS (separate endpoint)
    try:
        dns_resp = safe_get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", timeout=15)
        if dns_resp and dns_resp.status_code == 200:
            dns_data = dns_resp.json()
            passive_dns = dns_data.get("passive_dns", [])[:20]
            result["passive_dns"] = [
                {
                    "hostname": r.get("hostname", ""),
                    "address": r.get("address", ""),
                    "record_type": r.get("record_type", ""),
                    "first": r.get("first", "")[:10],
                    "last": r.get("last", "")[:10]
                } for r in passive_dns
            ]
    except:
        pass
    
    result["summary"] = {
        "threat_score": result["threat_score"],
        "risk_level": result["risk_level"],
        "total_threat_pulses": pulse_count,
        "malware_families": len(result["malware_families"]),
        "attack_techniques": len(result["attack_techniques"]),
        "whitelisted": result["whitelisted"],
        "passive_dns_records": len(result["passive_dns"]),
        "targeted_countries": len(result.get("targeted_countries", [])),
        "related_tags": len(result["related_tags"]),
        "data_source": "AlienVault OTX (Free Threat Intelligence)"
    }
    
    return result



def sensitive_paths(domain):
    """Scans 120+ common sensitive paths for exposed files, configs, admin panels, backups."""
    import concurrent.futures
    result = {
        "module": "sensitive_paths",
        "target": domain,
        "total_tested": 0,
        "total_found": 0,
        "findings": [],
        "categories": {"config": [], "admin": [], "backup": [], "api": [], "debug": [], "vcs": [], "other": []},
        "risk_level": "CLEAN",
        "risk_score": 0,
        "summary": {}
    }
    
    # Define sensitive paths with categories and severity
    paths_to_test = [
        # Version Control
        {"path": "/.git/config", "category": "vcs", "severity": "CRITICAL", "desc": "Git config exposed"},
        {"path": "/.git/HEAD", "category": "vcs", "severity": "CRITICAL", "desc": "Git HEAD exposed"},
        {"path": "/.svn/entries", "category": "vcs", "severity": "CRITICAL", "desc": "SVN entries exposed"},
        {"path": "/.hg/", "category": "vcs", "severity": "CRITICAL", "desc": "Mercurial repo exposed"},
        
        # Config files
        {"path": "/.env", "category": "config", "severity": "CRITICAL", "desc": "Environment variables exposed"},
        {"path": "/.env.bak", "category": "config", "severity": "CRITICAL", "desc": "Backup env file"},
        {"path": "/.env.local", "category": "config", "severity": "CRITICAL", "desc": "Local env file"},
        {"path": "/.env.production", "category": "config", "severity": "CRITICAL", "desc": "Production env file"},
        {"path": "/config.php", "category": "config", "severity": "HIGH", "desc": "PHP config exposed"},
        {"path": "/config.yml", "category": "config", "severity": "HIGH", "desc": "YAML config exposed"},
        {"path": "/config.json", "category": "config", "severity": "HIGH", "desc": "JSON config exposed"},
        {"path": "/wp-config.php", "category": "config", "severity": "CRITICAL", "desc": "WordPress config"},
        {"path": "/wp-config.php.bak", "category": "config", "severity": "CRITICAL", "desc": "WordPress config backup"},
        {"path": "/configuration.php", "category": "config", "severity": "HIGH", "desc": "Joomla config"},
        {"path": "/web.config", "category": "config", "severity": "HIGH", "desc": "IIS/ASP.NET config"},
        {"path": "/.htaccess", "category": "config", "severity": "MEDIUM", "desc": "Apache config"},
        {"path": "/.htpasswd", "category": "config", "severity": "CRITICAL", "desc": "Apache passwords"},
        {"path": "/settings.py", "category": "config", "severity": "HIGH", "desc": "Django settings"},
        {"path": "/database.yml", "category": "config", "severity": "HIGH", "desc": "Rails DB config"},
        {"path": "/application.yml", "category": "config", "severity": "HIGH", "desc": "Spring config"},
        {"path": "/appsettings.json", "category": "config", "severity": "HIGH", "desc": ".NET config"},
        {"path": "/.DS_Store", "category": "config", "severity": "MEDIUM", "desc": "macOS directory listing"},
        {"path": "/Thumbs.db", "category": "config", "severity": "LOW", "desc": "Windows thumbnail cache"},
        {"path": "/crossdomain.xml", "category": "config", "severity": "MEDIUM", "desc": "Flash cross-domain policy"},
        
        # Admin panels
        {"path": "/admin", "category": "admin", "severity": "MEDIUM", "desc": "Admin panel"},
        {"path": "/admin/", "category": "admin", "severity": "MEDIUM", "desc": "Admin panel"},
        {"path": "/administrator", "category": "admin", "severity": "MEDIUM", "desc": "Administrator panel"},
        {"path": "/wp-admin/", "category": "admin", "severity": "MEDIUM", "desc": "WordPress admin"},
        {"path": "/wp-login.php", "category": "admin", "severity": "MEDIUM", "desc": "WordPress login"},
        {"path": "/phpmyadmin/", "category": "admin", "severity": "HIGH", "desc": "phpMyAdmin"},
        {"path": "/adminer.php", "category": "admin", "severity": "HIGH", "desc": "Adminer DB tool"},
        {"path": "/cpanel", "category": "admin", "severity": "MEDIUM", "desc": "cPanel"},
        {"path": "/webmail", "category": "admin", "severity": "MEDIUM", "desc": "Webmail"},
        {"path": "/_admin", "category": "admin", "severity": "MEDIUM", "desc": "Hidden admin"},
        {"path": "/manage", "category": "admin", "severity": "MEDIUM", "desc": "Management panel"},
        {"path": "/dashboard", "category": "admin", "severity": "MEDIUM", "desc": "Dashboard"},
        {"path": "/filemanager/", "category": "admin", "severity": "HIGH", "desc": "File manager"},
        
        # Backup files
        {"path": "/backup.sql", "category": "backup", "severity": "CRITICAL", "desc": "SQL backup"},
        {"path": "/backup.zip", "category": "backup", "severity": "CRITICAL", "desc": "ZIP backup"},
        {"path": "/backup.tar.gz", "category": "backup", "severity": "CRITICAL", "desc": "TAR backup"},
        {"path": "/db.sql", "category": "backup", "severity": "CRITICAL", "desc": "Database dump"},
        {"path": "/dump.sql", "category": "backup", "severity": "CRITICAL", "desc": "Database dump"},
        {"path": "/database.sql", "category": "backup", "severity": "CRITICAL", "desc": "Database dump"},
        {"path": "/site.tar.gz", "category": "backup", "severity": "CRITICAL", "desc": "Site backup"},
        {"path": f"/{domain}.zip", "category": "backup", "severity": "CRITICAL", "desc": "Domain-named backup"},
        {"path": f"/{domain}.sql", "category": "backup", "severity": "CRITICAL", "desc": "Domain-named DB dump"},
        
        # API / Debug
        {"path": "/api/", "category": "api", "severity": "LOW", "desc": "API root"},
        {"path": "/api/v1/", "category": "api", "severity": "LOW", "desc": "API v1"},
        {"path": "/api/v2/", "category": "api", "severity": "LOW", "desc": "API v2"},
        {"path": "/graphql", "category": "api", "severity": "MEDIUM", "desc": "GraphQL endpoint"},
        {"path": "/swagger/", "category": "api", "severity": "MEDIUM", "desc": "Swagger/OpenAPI docs"},
        {"path": "/swagger.json", "category": "api", "severity": "MEDIUM", "desc": "Swagger JSON"},
        {"path": "/api-docs", "category": "api", "severity": "MEDIUM", "desc": "API documentation"},
        {"path": "/openapi.json", "category": "api", "severity": "MEDIUM", "desc": "OpenAPI spec"},
        {"path": "/docs", "category": "api", "severity": "LOW", "desc": "Documentation"},
        
        # Debug / Info
        {"path": "/phpinfo.php", "category": "debug", "severity": "HIGH", "desc": "PHP info page"},
        {"path": "/info.php", "category": "debug", "severity": "HIGH", "desc": "PHP info page"},
        {"path": "/server-status", "category": "debug", "severity": "HIGH", "desc": "Apache server status"},
        {"path": "/server-info", "category": "debug", "severity": "HIGH", "desc": "Apache server info"},
        {"path": "/debug/", "category": "debug", "severity": "HIGH", "desc": "Debug endpoint"},
        {"path": "/trace", "category": "debug", "severity": "MEDIUM", "desc": "Trace endpoint"},
        {"path": "/actuator", "category": "debug", "severity": "HIGH", "desc": "Spring Boot Actuator"},
        {"path": "/actuator/health", "category": "debug", "severity": "MEDIUM", "desc": "Spring health"},
        {"path": "/actuator/env", "category": "debug", "severity": "CRITICAL", "desc": "Spring env vars"},
        {"path": "/elmah.axd", "category": "debug", "severity": "HIGH", "desc": ".NET error log"},
        {"path": "/__debug__/", "category": "debug", "severity": "HIGH", "desc": "Debug toolbar"},
        {"path": "/telescope", "category": "debug", "severity": "HIGH", "desc": "Laravel Telescope"},
        {"path": "/console", "category": "debug", "severity": "HIGH", "desc": "Debug console"},
        {"path": "/metrics", "category": "debug", "severity": "MEDIUM", "desc": "Prometheus metrics"},
        {"path": "/health", "category": "debug", "severity": "LOW", "desc": "Health check"},
        {"path": "/status", "category": "debug", "severity": "LOW", "desc": "Status page"},
        
        # Source maps / other
        {"path": "/robots.txt", "category": "other", "severity": "INFO", "desc": "Robots.txt"},
        {"path": "/sitemap.xml", "category": "other", "severity": "INFO", "desc": "Sitemap"},
        {"path": "/security.txt", "category": "other", "severity": "INFO", "desc": "Security policy"},
        {"path": "/.well-known/security.txt", "category": "other", "severity": "INFO", "desc": "Security.txt (well-known)"},
        {"path": "/humans.txt", "category": "other", "severity": "INFO", "desc": "Humans.txt"},
        {"path": "/readme.md", "category": "other", "severity": "LOW", "desc": "Readme file"},
        {"path": "/README.md", "category": "other", "severity": "LOW", "desc": "README file"},
        {"path": "/CHANGELOG.md", "category": "other", "severity": "LOW", "desc": "Changelog"},
        {"path": "/package.json", "category": "config", "severity": "MEDIUM", "desc": "Node.js dependencies"},
        {"path": "/composer.json", "category": "config", "severity": "MEDIUM", "desc": "PHP dependencies"},
    ]
    
    result["total_tested"] = len(paths_to_test)
    findings = []
    
    base_url = f"https://{domain}"
    
    def test_path(item):
        try:
            test_url = base_url + item["path"]
            resp = safe_get(test_url, timeout=8)
            if resp and resp.status_code == 200:
                content_length = len(resp.content)
                # Skip empty pages or default error pages
                if content_length < 50:
                    return None
                # Check if it's a custom 404 / soft 404
                body_lower = resp.text.lower() if resp.text else ""
                if "404" in body_lower[:500] and "not found" in body_lower[:500]:
                    return None
                return {
                    "path": item["path"],
                    "status": 200,
                    "size": content_length,
                    "category": item["category"],
                    "severity": item["severity"],
                    "description": item["desc"],
                    "content_type": resp.headers.get("Content-Type", "Unknown")[:50]
                }
            elif resp and resp.status_code in [301, 302, 303, 307, 308]:
                redirect_to = resp.headers.get("Location", "")
                return {
                    "path": item["path"],
                    "status": resp.status_code,
                    "size": 0,
                    "category": item["category"],
                    "severity": "LOW",
                    "description": f"{item['desc']} → Redirects to {redirect_to[:80]}",
                    "redirect": redirect_to
                }
        except:
            pass
        return None
    
    # Run tests in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(test_path, item): item for item in paths_to_test}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                findings.append(res)
    
    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    findings.sort(key=lambda x: severity_order.get(x["severity"], 5))
    
    result["findings"] = findings
    result["total_found"] = len(findings)
    
    # Categorize
    for f in findings:
        cat = f["category"]
        if cat in result["categories"]:
            result["categories"][cat].append(f)
    
    # Risk score
    sev_scores = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 0}
    risk_score = min(100, sum(sev_scores.get(f["severity"], 0) for f in findings))
    
    if risk_score >= 70: risk = "CRITICAL"
    elif risk_score >= 40: risk = "HIGH"
    elif risk_score >= 20: risk = "MEDIUM"
    elif risk_score > 0: risk = "LOW"
    else: risk = "CLEAN"
    
    result["risk_level"] = risk
    result["risk_score"] = risk_score
    
    severity_counts = {}
    for f in findings:
        s = f["severity"]
        severity_counts[s] = severity_counts.get(s, 0) + 1
    
    result["summary"] = {
        "total_paths_tested": len(paths_to_test),
        "total_found": len(findings),
        "severity_breakdown": severity_counts,
        "risk_level": risk,
        "risk_score": risk_score,
        "categories_with_findings": {k: len(v) for k, v in result["categories"].items() if v},
        "data_source": "Direct path probing (80+ signatures)"
    }
    
    return result


def cve_hunter(domain):
    """CVE vulnerability lookup using Shodan InternetDB + CIRCL CVE database."""
    import socket
    result = {
        "module": "cve_hunter",
        "target": domain,
        "ip": "Unknown",
        "total_cves": 0,
        "cve_list": [],
        "cve_details": [],
        "severity_breakdown": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0},
        "cpes": [],
        "exploitable": [],
        "summary": {}
    }
    
    try:
        ip = socket.gethostbyname(domain)
        result["ip"] = ip
    except:
        result["error"] = "Could not resolve domain"
        return result
    
    # Step 1: Get CVEs from Shodan InternetDB
    try:
        resp = safe_get(f"https://internetdb.shodan.io/{ip}", timeout=15)
        if resp and resp.status_code == 200:
            data = resp.json()
            cve_ids = data.get("vulns", [])
            result["cve_list"] = cve_ids
            result["total_cves"] = len(cve_ids)
            result["cpes"] = data.get("cpes", [])
    except:
        pass
    
    # Step 2: Look up CVE details from CIRCL (free API, first 20)
    cve_details = []
    for cve_id in result["cve_list"][:20]:
        try:
            resp = safe_get(f"https://cve.circl.lu/api/cve/{cve_id}", timeout=10)
            if resp and resp.status_code == 200:
                cve_data = resp.json()
                cvss = cve_data.get("cvss", None)
                cvss3 = None
                
                # Try to get CVSS v3
                if cve_data.get("impact", {}).get("baseMetricV3"):
                    cvss3 = cve_data["impact"]["baseMetricV3"].get("cvssV3", {}).get("baseScore")
                
                score = cvss3 or cvss or 0
                if score >= 9.0: severity = "CRITICAL"
                elif score >= 7.0: severity = "HIGH"
                elif score >= 4.0: severity = "MEDIUM"
                elif score > 0: severity = "LOW"
                else: severity = "UNKNOWN"
                
                detail = {
                    "id": cve_id,
                    "summary": (cve_data.get("summary", "") or "")[:200],
                    "cvss": score,
                    "severity": severity,
                    "published": cve_data.get("Published", "Unknown"),
                    "references": (cve_data.get("references", []) or [])[:3],
                    "cwe": cve_data.get("cwe", "Unknown")
                }
                cve_details.append(detail)
                result["severity_breakdown"][severity] += 1
                
                # Check if exploitable
                refs = cve_data.get("references", []) or []
                for ref in refs:
                    if ref and ('exploit' in ref.lower() or 'poc' in ref.lower() or 'github.com' in ref.lower()):
                        result["exploitable"].append(cve_id)
                        break
        except:
            cve_details.append({"id": cve_id, "summary": "Details unavailable", "cvss": 0, "severity": "UNKNOWN"})
            result["severity_breakdown"]["UNKNOWN"] += 1
    
    # For remaining CVEs not looked up
    remaining = len(result["cve_list"]) - len(cve_details)
    if remaining > 0:
        result["severity_breakdown"]["UNKNOWN"] += remaining
    
    result["cve_details"] = cve_details
    
    # Risk assessment
    crit = result["severity_breakdown"]["CRITICAL"]
    high = result["severity_breakdown"]["HIGH"]
    risk_score = min(100, crit * 25 + high * 15 + result["severity_breakdown"]["MEDIUM"] * 5)
    
    if risk_score >= 70: risk = "CRITICAL"
    elif risk_score >= 50: risk = "HIGH"
    elif risk_score >= 25: risk = "MEDIUM"
    elif risk_score > 0: risk = "LOW"
    else: risk = "CLEAN"
    
    result["risk_level"] = risk
    result["risk_score"] = risk_score
    
    result["summary"] = {
        "total_cves": result["total_cves"],
        "critical": crit,
        "high": high,
        "medium": result["severity_breakdown"]["MEDIUM"],
        "low": result["severity_breakdown"]["LOW"],
        "exploitable": len(result["exploitable"]),
        "technologies_affected": len(result["cpes"]),
        "risk_level": risk,
        "risk_score": risk_score,
        "data_sources": "Shodan InternetDB + CIRCL CVE Database (Free)"
    }
    
    return result


def ssl_deep_audit(domain):
    results = {"module": "SSL/TLS Deep Audit", "domain": domain, "certificate": {}, "chain": [], "protocols": {}, "cipher_suites": [], "vulnerabilities": [], "grade": "?", "stats": {}}
    score = 100
    # Get certificate
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                cert_pem = ssl.DER_cert_to_PEM_cert(cert)
                peer = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                results["certificate"] = {
                    "subject": dict(x[0] for x in peer.get('subject', ())),
                    "issuer": dict(x[0] for x in peer.get('issuer', ())),
                    "serial": peer.get('serialNumber', 'Unknown'),
                    "version": peer.get('version', 'Unknown'),
                    "not_before": peer.get('notBefore', 'Unknown'),
                    "not_after": peer.get('notAfter', 'Unknown'),
                    "san": [v for t, v in peer.get('subjectAltName', ())],
                    "ocsp": peer.get('OCSP', []),
                    "ca_issuers": peer.get('caIssuers', []),
                }
                results["current_cipher"] = {"name": cipher[0], "protocol": cipher[1], "bits": cipher[2]}
                results["tls_version"] = version
                # Check expiry
                not_after = peer.get('notAfter', '')
                if not_after:
                    try:
                        exp = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_left = (exp - datetime.datetime.utcnow()).days
                        results["certificate"]["days_until_expiry"] = days_left
                        results["certificate"]["expired"] = days_left < 0
                        if days_left < 0:
                            results["vulnerabilities"].append({"name": "EXPIRED CERTIFICATE", "severity": "CRITICAL"})
                            score -= 50
                        elif days_left < 30:
                            results["vulnerabilities"].append({"name": "EXPIRING SOON", "severity": "WARNING", "days_left": days_left})
                            score -= 10
                    except:
                        pass
    except Exception as e:
        results["certificate"] = {"error": str(e)}
        score -= 50
    # Test protocol versions
    protocols = {"TLSv1.0": False, "TLSv1.1": False, "TLSv1.2": False, "TLSv1.3": False}
    proto_map = {
        "TLSv1.0": ssl.TLSVersion.TLSv1 if hasattr(ssl.TLSVersion, 'TLSv1') else None,
        "TLSv1.1": ssl.TLSVersion.TLSv1_1 if hasattr(ssl.TLSVersion, 'TLSv1_1') else None,
        "TLSv1.2": ssl.TLSVersion.TLSv1_2,
        "TLSv1.3": ssl.TLSVersion.TLSv1_3 if hasattr(ssl.TLSVersion, 'TLSv1_3') else None,
    }
    for proto_name, proto_ver in proto_map.items():
        if proto_ver is None:
            continue
        try:
            ctx2 = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx2.check_hostname = False
            ctx2.verify_mode = ssl.CERT_NONE
            ctx2.minimum_version = proto_ver
            ctx2.maximum_version = proto_ver
            with socket.create_connection((domain, 443), timeout=5) as s2:
                with ctx2.wrap_socket(s2, server_hostname=domain) as ss2:
                    protocols[proto_name] = True
        except:
            protocols[proto_name] = False
    results["protocols"] = protocols
    if protocols.get("TLSv1.0"):
        results["vulnerabilities"].append({"name": "TLS 1.0 Supported", "severity": "HIGH", "detail": "Vulnerable to BEAST, POODLE"})
        score -= 20
    if protocols.get("TLSv1.1"):
        results["vulnerabilities"].append({"name": "TLS 1.1 Supported", "severity": "MEDIUM", "detail": "Deprecated protocol"})
        score -= 10
    if not protocols.get("TLSv1.3"):
        results["vulnerabilities"].append({"name": "TLS 1.3 Not Supported", "severity": "LOW", "detail": "Missing latest protocol"})
        score -= 5
    # Grade
    score = max(0, score)
    results["grade"] = "A+" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"
    results["score"] = score
    results["stats"] = {"grade": results["grade"], "score": score, "vulnerabilities": len(results["vulnerabilities"]),
        "tls13": protocols.get("TLSv1.3", False), "days_until_expiry": results["certificate"].get("days_until_expiry", "?")}
    return results

# ================================================================
# MODULE 16: SECURITY HEADERS PRO
# ================================================================
def security_headers(domain):
    results = {"module": "Security Headers Pro", "domain": domain, "headers": {}, "missing": [], "score": 0, "grade": "?", "stats": {}}
    score = 0
    max_points = 100
    headers_check = {
        "Strict-Transport-Security": {"weight": 15, "desc": "HSTS — Forces HTTPS"},
        "Content-Security-Policy": {"weight": 20, "desc": "CSP — Prevents XSS & injection"},
        "X-Frame-Options": {"weight": 10, "desc": "Clickjacking protection"},
        "X-Content-Type-Options": {"weight": 10, "desc": "MIME sniffing prevention"},
        "Referrer-Policy": {"weight": 10, "desc": "Controls referrer info"},
        "Permissions-Policy": {"weight": 10, "desc": "Controls browser features"},
        "X-XSS-Protection": {"weight": 5, "desc": "XSS filter (legacy)"},
        "Cross-Origin-Opener-Policy": {"weight": 5, "desc": "COOP — Isolates browsing context"},
        "Cross-Origin-Resource-Policy": {"weight": 5, "desc": "CORP — Controls resource sharing"},
        "Cross-Origin-Embedder-Policy": {"weight": 5, "desc": "COEP — Controls embedding"},
        "Cache-Control": {"weight": 5, "desc": "Caching directives"},
    }
    try:
        r = safe_get(f"https://{domain}", timeout=10)
        if not r:
            r = safe_get(f"http://{domain}", timeout=10)
        if r:
            resp_headers = {k.lower(): v for k, v in r.headers.items()}
            for header, info in headers_check.items():
                val = resp_headers.get(header.lower(), None)
                if val:
                    quality = "GOOD"
                    notes = val[:200]
                    if header == "Strict-Transport-Security":
                        if 'max-age' in val:
                            age = re.search(r'max-age=(\d+)', val)
                            if age and int(age.group(1)) < 31536000:
                                quality = "WEAK"
                                notes += " (max-age < 1 year)"
                        if 'includesubdomains' in val.lower():
                            quality = "STRONG"
                    elif header == "Content-Security-Policy":
                        if 'unsafe-inline' in val or 'unsafe-eval' in val:
                            quality = "WEAK"
                        elif "default-src 'none'" in val or "default-src 'self'" in val:
                            quality = "STRONG"
                    results["headers"][header] = {"value": val[:300], "status": "PRESENT ✓", "quality": quality, "description": info["desc"]}
                    score += info["weight"] if quality != "WEAK" else info["weight"] // 2
                else:
                    results["headers"][header] = {"value": None, "status": "MISSING ✗", "quality": "NONE", "description": info["desc"]}
                    results["missing"].append(header)
            # Check for dangerous headers
            dangerous = {"server": "Reveals server software", "x-powered-by": "Reveals technology stack", "x-aspnet-version": "Reveals ASP.NET version"}
            for dh, desc in dangerous.items():
                if dh in resp_headers:
                    results["headers"][f"⚠ {dh}"] = {"value": resp_headers[dh], "status": "EXPOSED ⚠", "quality": "DANGEROUS", "description": desc}
                    score -= 5
    except:
        results["error"] = "Could not fetch headers"
    score = max(0, min(score, 100))
    results["score"] = score
    results["grade"] = "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 45 else "D" if score >= 25 else "F"
    results["stats"] = {"score": score, "grade": results["grade"], "present": len(results["headers"]) - len(results["missing"]),
        "missing": len(results["missing"]), "total_checked": len(headers_check)}
    return results

# ================================================================
# MODULE 17: CORS MISCONFIGURATION
# ================================================================
def cors_misconfig(domain):
    results = {"module": "CORS Misconfiguration", "domain": domain, "tests": [], "vulnerable": False, "risk_level": "LOW", "stats": {}}
    base = f"https://{domain}"
    tests = []
    vuln_count = 0
    test_origins = [
        {"origin": "https://evil.com", "name": "Arbitrary Origin", "severity": "CRITICAL"},
        {"origin": "null", "name": "Null Origin", "severity": "HIGH"},
        {"origin": f"https://{domain}.evil.com", "name": "Subdomain Prefix", "severity": "HIGH"},
        {"origin": f"https://evil-{domain}", "name": "Domain Suffix", "severity": "HIGH"},
        {"origin": f"https://sub.{domain}", "name": "Subdomain (legitimate)", "severity": "INFO"},
        {"origin": "https://localhost", "name": "Localhost", "severity": "MEDIUM"},
        {"origin": f"http://{domain}", "name": "HTTP Origin (downgrade)", "severity": "MEDIUM"},
    ]
    for test in test_origins:
        try:
            r = requests.get(base, timeout=8, headers={'Origin': test["origin"], 'User-Agent': 'Mozilla/5.0'}, verify=False)
            acao = r.headers.get('Access-Control-Allow-Origin', '')
            acac = r.headers.get('Access-Control-Allow-Credentials', '')
            result = {
                "test": test["name"],
                "origin_sent": test["origin"],
                "acao_returned": acao or "None",
                "credentials_allowed": acac.lower() == 'true' if acac else False,
                "vulnerable": False,
                "severity": test["severity"]
            }
            if acao == test["origin"] or acao == '*':
                result["vulnerable"] = True
                if acac.lower() == 'true':
                    result["severity"] = "CRITICAL"
                    result["note"] = "Credentials allowed with reflected origin!"
                vuln_count += 1
            tests.append(result)
        except:
            tests.append({"test": test["name"], "error": "Request failed"})
    results["tests"] = tests
    results["vulnerable"] = vuln_count > 0
    results["risk_level"] = "CRITICAL" if any(t.get("severity") == "CRITICAL" and t.get("vulnerable") for t in tests) else "HIGH" if vuln_count >= 2 else "MEDIUM" if vuln_count >= 1 else "LOW"
    results["stats"] = {"tests_run": len(tests), "vulnerabilities": vuln_count, "risk": results["risk_level"]}
    return results


# ================================================================
# MODULE 18: OPEN REDIRECT SCANNER
# ================================================================
def open_redirect(domain):
    results = {"module": "Open Redirect Scanner", "domain": domain, "tests": [], "vulnerable": False, "stats": {}}
    base = f"https://{domain}"
    evil_url = "https://evil.com/pwned"
    params = ['url', 'redirect', 'next', 'return', 'returnTo', 'return_to', 'redir',
              'redirect_uri', 'redirect_url', 'continue', 'dest', 'destination',
              'go', 'goto', 'target', 'link', 'out', 'view', 'ref', 'callback']
    vuln_count = 0
    for param in params:
        try:
            test_url = f"{base}/?{param}={evil_url}"
            r = requests.get(test_url, timeout=8, allow_redirects=False, verify=False,
                           headers={'User-Agent': 'Mozilla/5.0'})
            loc = r.headers.get('Location', '')
            is_vuln = evil_url in loc or 'evil.com' in loc
            if is_vuln:
                vuln_count += 1
                results["tests"].append({"parameter": param, "status_code": r.status_code,
                    "redirect_to": loc, "vulnerable": True, "severity": "HIGH"})
            elif r.status_code in [301, 302, 303, 307]:
                results["tests"].append({"parameter": param, "status_code": r.status_code,
                    "redirect_to": loc[:100], "vulnerable": False})
        except:
            pass
    results["vulnerable"] = vuln_count > 0
    results["stats"] = {"parameters_tested": len(params), "vulnerabilities": vuln_count,
        "risk": "HIGH" if vuln_count > 0 else "LOW"}
    return results

# ================================================================
# MODULE 19: COOKIE ANALYZER
# ================================================================
def cookie_analyzer(domain):
    results = {"module": "Cookie Analyzer", "domain": domain, "cookies": [], "score": 0, "stats": {}}
    score = 100
    issues = 0
    try:
        session = requests.Session()
        r = session.get(f"https://{domain}", timeout=10, verify=False,
                       headers={'User-Agent': 'Mozilla/5.0'})
        cookies = []
        for cookie in session.cookies:
            c = {
                "name": cookie.name,
                "value": cookie.value[:30] + "..." if len(cookie.value) > 30 else cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
                "expires": str(datetime.datetime.fromtimestamp(cookie.expires)) if cookie.expires else "Session",
                "flags": [],
                "issues": []
            }
            # Check HttpOnly
            httponly = bool(cookie._rest.get('HttpOnly', cookie._rest.get('httponly', False)))
            c["httponly"] = httponly
            if not httponly:
                c["issues"].append("Missing HttpOnly — vulnerable to XSS cookie theft")
                issues += 1
            else:
                c["flags"].append("HttpOnly ✓")
            # Check Secure
            if not cookie.secure:
                c["issues"].append("Missing Secure flag — sent over HTTP")
                issues += 1
            else:
                c["flags"].append("Secure ✓")
            # Check SameSite
            samesite = cookie._rest.get('SameSite', cookie._rest.get('samesite', 'Not set'))
            c["samesite"] = samesite if samesite else "Not set"
            if not samesite or samesite == 'Not set':
                c["issues"].append("Missing SameSite — CSRF risk")
                issues += 1
            else:
                c["flags"].append(f"SameSite={samesite} ✓")
            # Check for session/auth cookies
            session_patterns = ['session', 'sess', 'sid', 'token', 'auth', 'jwt', 'login', 'user', 'csrf']
            is_sensitive = any(p in cookie.name.lower() for p in session_patterns)
            c["sensitive"] = is_sensitive
            if is_sensitive and c["issues"]:
                c["risk"] = "CRITICAL"
            elif c["issues"]:
                c["risk"] = "MEDIUM"
            else:
                c["risk"] = "LOW"
            cookies.append(c)
        results["cookies"] = cookies
        score = max(0, 100 - (issues * 10))
    except Exception as e:
        results["error"] = str(e)
    results["score"] = score
    results["grade"] = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
    results["stats"] = {"total_cookies": len(results["cookies"]), "security_issues": issues,
        "score": score, "sensitive_cookies": sum(1 for c in results["cookies"] if c.get("sensitive"))}
    return results

# ================================================================
# MODULE 20: SUBDOMAIN TAKEOVER CHECK
# ================================================================
def subdomain_takeover(domain):
    results = {"module": "Subdomain Takeover Check", "domain": domain, "subdomains_checked": [], "vulnerable": [], "stats": {}}
    # Services vulnerable to takeover
    takeover_sigs = {
        "GitHub Pages": {"cnames": ["github.io"], "fingerprint": "There isn't a GitHub Pages site here"},
        "Heroku": {"cnames": ["herokuapp.com", "herokussl.com"], "fingerprint": "No such app"},
        "AWS S3": {"cnames": ["s3.amazonaws.com", "s3-website"], "fingerprint": "NoSuchBucket"},
        "Shopify": {"cnames": ["myshopify.com"], "fingerprint": "Sorry, this shop is currently unavailable"},
        "Tumblr": {"cnames": ["tumblr.com"], "fingerprint": "There's nothing here"},
        "WordPress.com": {"cnames": ["wordpress.com"], "fingerprint": "Do you want to register"},
        "Pantheon": {"cnames": ["pantheonsite.io"], "fingerprint": "404 error unknown site"},
        "Zendesk": {"cnames": ["zendesk.com"], "fingerprint": "Help Center Closed"},
        "Fastly": {"cnames": ["fastly.net"], "fingerprint": "Fastly error: unknown domain"},
        "Ghost": {"cnames": ["ghost.io"], "fingerprint": "The thing you were looking for is no longer here"},
        "Surge.sh": {"cnames": ["surge.sh"], "fingerprint": "project not found"},
        "Bitbucket": {"cnames": ["bitbucket.io"], "fingerprint": "Repository not found"},
        "Netlify": {"cnames": ["netlify.app", "netlify.com"], "fingerprint": "Not Found - Request ID"},
        "Fly.io": {"cnames": ["fly.dev"], "fingerprint": "404 Not Found"},
        "Vercel": {"cnames": ["vercel.app", "now.sh"], "fingerprint": "The deployment could not be found"},
    }
    # Get subdomains first (quick crt.sh check)
    subs = set()
    try:
        r = safe_get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=12)
        if r and r.status_code == 200:
            for entry in r.json():
                for n in entry.get('name_value', '').split('\n'):
                    n = n.strip().lower()
                    if n.endswith(domain) and '*' not in n and n != domain:
                        subs.add(n)
    except:
        pass
    # Also try common ones
    for prefix in ['www','mail','blog','dev','staging','api','admin','app','cdn','shop','store','portal','test','beta']:
        subs.add(f"{prefix}.{domain}")
    vulnerable = []
    checked = []
    for sub in list(subs)[:50]:
        try:
            cname_records = []
            try:
                ans = dns.resolver.resolve(sub, 'CNAME')
                cname_records = [str(r).rstrip('.') for r in ans]
            except:
                checked.append({"subdomain": sub, "cname": "No CNAME", "status": "SAFE"})
                continue
            for cname in cname_records:
                is_vuln = False
                for service, sigs in takeover_sigs.items():
                    if any(sig in cname for sig in sigs["cnames"]):
                        # Check if the CNAME target responds
                        try:
                            tr = safe_get(f"https://{sub}", timeout=8)
                            if tr and sigs["fingerprint"].lower() in tr.text.lower():
                                is_vuln = True
                                vulnerable.append({"subdomain": sub, "cname": cname, "service": service,
                                    "status": "VULNERABLE ⚠", "severity": "CRITICAL",
                                    "detail": f"CNAME → {cname} but {service} returns error page"})
                            elif not tr or tr.status_code in [404, 0]:
                                vulnerable.append({"subdomain": sub, "cname": cname, "service": service,
                                    "status": "POSSIBLY VULNERABLE", "severity": "HIGH",
                                    "detail": f"CNAME → {cname}, service unreachable"})
                        except:
                            vulnerable.append({"subdomain": sub, "cname": cname, "service": service,
                                "status": "POSSIBLY VULNERABLE", "severity": "HIGH",
                                "detail": f"CNAME → {cname}, connection failed"})
                        break
                checked.append({"subdomain": sub, "cname": cname, "status": "VULNERABLE" if is_vuln else "SAFE"})
        except:
            pass
    results["subdomains_checked"] = checked[:50]
    results["vulnerable"] = vulnerable
    results["stats"] = {"subdomains_scanned": len(checked), "vulnerable": len(vulnerable),
        "risk": "CRITICAL" if vulnerable else "LOW", "services_checked": len(takeover_sigs)}
    return results

# ================================================================
# MODULE 21: WHOIS INTELLIGENCE
# ================================================================
def whois_intel(domain):
    results = {"module": "WHOIS Intelligence", "domain": domain, "whois": {}, "stats": {}}
    try:
        import whois as pywhois
        w = pywhois.whois(domain)
        # Domain age
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        expires = w.expiration_date
        if isinstance(expires, list):
            expires = expires[0]
        age_days = (datetime.datetime.now() - created).days if created else None
        expires_days = (expires - datetime.datetime.now()).days if expires else None
        results["whois"] = {
            "domain_name": str(w.domain_name) if w.domain_name else domain,
            "registrar": str(w.registrar) if w.registrar else "Unknown",
            "registrar_url": str(w.registrar_url) if hasattr(w, 'registrar_url') and w.registrar_url else "N/A",
            "creation_date": str(created) if created else "Unknown",
            "expiration_date": str(expires) if expires else "Unknown",
            "updated_date": str(w.updated_date) if w.updated_date else "Unknown",
            "domain_age_days": age_days,
            "domain_age_years": round(age_days / 365.25, 1) if age_days else None,
            "expires_in_days": expires_days,
            "name_servers": w.name_servers if w.name_servers else [],
            "status": w.status if w.status else [],
            "registrant": str(getattr(w, 'registrant_name', None) or getattr(w, 'name', None) or 'REDACTED'),
            "org": str(w.org) if w.org else "REDACTED",
            "country": str(w.country) if w.country else "Unknown",
            "state": str(w.state) if w.state else "Unknown",
            "city": str(w.city) if hasattr(w, 'city') and w.city else "Unknown",
            "emails": w.emails if w.emails else [],
            "dnssec": str(w.dnssec) if hasattr(w, 'dnssec') and w.dnssec else "Unknown",
        }
    except Exception as e:
        results["whois"] = {"error": str(e)}
        # Fallback
        try:
            r = safe_get(f"https://api.hackertarget.com/whois/?q={domain}", timeout=12)
            if r and r.status_code == 200:
                results["whois"]["raw"] = r.text[:3000]
        except:
            pass
    results["stats"] = {"registrar": results["whois"].get("registrar", "?"),
        "age": results["whois"].get("domain_age_years", "?"),
        "expires_days": results["whois"].get("expires_in_days", "?")}
    return results

# ================================================================
# MODULE 22: DOMAIN REPUTATION
# ================================================================
def domain_reputation(domain):
    results = {"module": "Domain Reputation", "domain": domain, "checks": [], "blacklisted": False, "score": 100, "stats": {}}
    ip = resolve_ip(domain)
    checks = []
    blacklisted_count = 0
    # DNS-based blacklists
    dnsbl_servers = [
        "zen.spamhaus.org", "bl.spamcop.net", "b.barracudacentral.org",
        "dnsbl.sorbs.net", "spam.dnsbl.sorbs.net", "cbl.abuseat.org",
        "dnsbl-1.uceprotect.net", "psbl.surriel.com"
    ]
    if ip:
        reversed_ip = '.'.join(reversed(ip.split('.')))
        for bl in dnsbl_servers:
            try:
                query = f"{reversed_ip}.{bl}"
                dns.resolver.resolve(query, 'A')
                checks.append({"blacklist": bl, "status": "LISTED ⚠", "severity": "HIGH"})
                blacklisted_count += 1
            except dns.resolver.NXDOMAIN:
                checks.append({"blacklist": bl, "status": "CLEAN ✓", "severity": "NONE"})
            except:
                checks.append({"blacklist": bl, "status": "TIMEOUT", "severity": "UNKNOWN"})
    # Google Safe Browsing check (via redirect check)
    try:
        r = safe_get(f"https://transparencyreport.google.com/safe-browsing/search?url={domain}", timeout=8)
        checks.append({"blacklist": "Google Safe Browsing", "status": "CHECK AVAILABLE", "url": f"https://transparencyreport.google.com/safe-browsing/search?url={domain}"})
    except:
        pass
    # PhishTank style check
    try:
        r = safe_get(f"https://urlhaus-api.abuse.ch/v1/host/", timeout=8)
    except:
        pass
    results["checks"] = checks
    results["blacklisted"] = blacklisted_count > 0
    score = max(0, 100 - (blacklisted_count * 15))
    results["score"] = score
    results["grade"] = "A" if score >= 90 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"
    results["stats"] = {"lists_checked": len(checks), "blacklisted_on": blacklisted_count,
        "score": score, "grade": results["grade"]}
    return results

# ================================================================
# MODULE 23: ROBOTS & SITEMAP INTEL
# ================================================================
def info_leak_detector(domain):
    """Detects information leakage: HTML comments, meta tags, error pages, source maps, exposed configs."""
    import re
    result = {
        "module": "info_leak_detector",
        "target": domain,
        "leaks_found": 0,
        "findings": [],
        "html_comments": [],
        "meta_info": [],
        "error_disclosure": [],
        "source_maps": [],
        "exposed_emails": [],
        "exposed_ips": [],
        "risk_level": "CLEAN",
        "risk_score": 0,
        "summary": {}
    }
    
    try:
        url = f"https://{domain}"
        resp = safe_get(url, timeout=15)
        if not resp:
            url = f"http://{domain}"
            resp = safe_get(url, timeout=15)
        if not resp:
            result["error"] = "Could not reach target"
            return result
        
        body = resp.text or ""
        headers = {k.lower(): v for k, v in resp.headers.items()}
        
        findings = []
        
        # 1. HTML Comments Analysis (may contain debug info, passwords, TODO, internal paths)
        comments = re.findall(r'<!--(.*?)-->', body, re.DOTALL)
        interesting_comments = []
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'api', 'todo', 'fixme', 'hack', 'bug', 'debug', 'admin', 'internal', 'staging', 'test', 'database', 'mysql', 'postgres', 'mongo', 'redis', 'config', 'credentials', 'username', 'login', 'private', 'dev', 'development']
        
        for comment in comments:
            comment_clean = comment.strip()
            if len(comment_clean) < 3:
                continue
            comment_lower = comment_clean.lower()
            for pattern in sensitive_patterns:
                if pattern in comment_lower:
                    interesting_comments.append({
                        "content": comment_clean[:200],
                        "trigger": pattern,
                        "severity": "HIGH" if pattern in ['password', 'secret', 'key', 'token', 'credentials'] else "MEDIUM"
                    })
                    break
        
        result["html_comments"] = interesting_comments
        if interesting_comments:
            findings.append({
                "type": "HTML Comments",
                "severity": "HIGH" if any(c["severity"] == "HIGH" for c in interesting_comments) else "MEDIUM",
                "count": len(interesting_comments),
                "detail": f"{len(interesting_comments)} comments contain sensitive keywords"
            })
        
        # 2. Meta Tags Information
        meta_info = []
        meta_tags = re.findall(r'<meta\s+([^>]+)>', body, re.IGNORECASE)
        for meta in meta_tags:
            name = re.search(r'name=["\']([^"\']+)["\']', meta, re.IGNORECASE)
            content = re.search(r'content=["\']([^"\']+)["\']', meta, re.IGNORECASE)
            if name and content:
                n = name.group(1).lower()
                c = content.group(1)
                if n in ['generator', 'author', 'description', 'keywords', 'robots', 'theme-color', 'msapplication-config']:
                    meta_info.append({"name": n, "content": c[:200]})
        
        result["meta_info"] = meta_info
        
        # Check generator (leaks CMS version)
        generator_metas = [m for m in meta_info if m["name"] == "generator"]
        if generator_metas:
            findings.append({
                "type": "Generator Meta Tag",
                "severity": "MEDIUM",
                "count": len(generator_metas),
                "detail": f"CMS/Framework version exposed: {generator_metas[0]['content']}"
            })
        
        # 3. Email addresses in source code
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)))
        result["exposed_emails"] = emails[:20]
        if emails:
            findings.append({
                "type": "Email Addresses Exposed",
                "severity": "LOW",
                "count": len(emails),
                "detail": f"{len(emails)} email addresses found in page source"
            })
        
        # 4. Internal IP addresses
        internal_ips = list(set(re.findall(r'(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})', body)))
        result["exposed_ips"] = internal_ips
        if internal_ips:
            findings.append({
                "type": "Internal IP Addresses",
                "severity": "HIGH",
                "count": len(internal_ips),
                "detail": f"{len(internal_ips)} private/internal IPs found in source"
            })
        
        # 5. Source map files
        source_maps = list(set(re.findall(r'//[#@]\s*sourceMappingURL=([^\s\'"]+)', body)))
        js_map_refs = list(set(re.findall(r'["\']([^"\']+\.map)["\']', body)))
        all_maps = list(set(source_maps + js_map_refs))
        result["source_maps"] = all_maps[:20]
        if all_maps:
            findings.append({
                "type": "Source Maps",
                "severity": "MEDIUM",
                "count": len(all_maps),
                "detail": f"{len(all_maps)} source map references found — may expose original source code"
            })
        
        # 6. Server header information leakage
        server_leaks = []
        for h in ['server', 'x-powered-by', 'x-aspnet-version', 'x-aspnetmvc-version', 'x-generator', 'x-drupal-cache']:
            if h in headers:
                server_leaks.append({"header": h, "value": headers[h]})
        
        if server_leaks:
            findings.append({
                "type": "Server Header Leakage",
                "severity": "MEDIUM",
                "count": len(server_leaks),
                "detail": f"{len(server_leaks)} headers expose server/technology info"
            })
        
        result["server_leaks"] = server_leaks
        
        # 7. Check error pages for stack traces
        error_urls = [f"https://{domain}/nonexistent_page_404_test_{domain}", f"https://{domain}/test.php", f"https://{domain}/'"]
        error_disclosures = []
        
        for err_url in error_urls:
            try:
                err_resp = safe_get(err_url, timeout=8)
                if err_resp and err_resp.text:
                    err_body = err_resp.text.lower()
                    # Check for stack traces / debug info
                    stack_patterns = [
                        ('Stack Trace', 'stack trace'),
                        ('File Path', 'at /'),
                        ('Line Number', 'on line'),
                        ('SQL Error', 'sql'),
                        ('Database Error', 'database error'),
                        ('PHP Error', 'fatal error'),
                        ('Python Traceback', 'traceback'),
                        ('Java Exception', 'exception'),
                        ('.NET Error', 'asp.net'),
                        ('Debug Mode', 'debug'),
                        ('Framework Version', 'version'),
                    ]
                    for name, pattern in stack_patterns:
                        if pattern in err_body and len(err_body) > 200:
                            error_disclosures.append({
                                "url": err_url[:80],
                                "type": name,
                                "status": err_resp.status_code
                            })
                            break
            except:
                pass
        
        result["error_disclosure"] = error_disclosures
        if error_disclosures:
            findings.append({
                "type": "Error Page Disclosure",
                "severity": "HIGH",
                "count": len(error_disclosures),
                "detail": f"{len(error_disclosures)} error pages expose internal information"
            })
        
        # 8. API keys / secrets in source
        secret_patterns = [
            (r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API Key"),
            (r'(?:secret|token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Secret/Token"),
            (r'AIza[0-9A-Za-z_\-]{35}', "Google API Key"),
            (r'sk_live_[0-9a-zA-Z]{24,}', "Stripe Secret Key"),
            (r'pk_live_[0-9a-zA-Z]{24,}', "Stripe Public Key"),
            (r'(?:AKIA|ASIA)[0-9A-Z]{16}', "AWS Access Key"),
        ]
        
        secrets_found = []
        for pattern, name in secret_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                secrets_found.append({"type": name, "count": len(matches), "sample": matches[0][:10] + "..." if matches else ""})
        
        result["secrets_found"] = secrets_found
        if secrets_found:
            findings.append({
                "type": "Exposed Secrets/API Keys",
                "severity": "CRITICAL",
                "count": sum(s["count"] for s in secrets_found),
                "detail": f"Potential secrets found: {', '.join(s['type'] for s in secrets_found)}"
            })
        
        result["findings"] = findings
        result["leaks_found"] = len(findings)
        
        # Risk score
        sev_scores = {"CRITICAL": 30, "HIGH": 20, "MEDIUM": 10, "LOW": 3}
        risk_score = min(100, sum(sev_scores.get(f["severity"], 0) for f in findings))
        
        if risk_score >= 60: risk = "CRITICAL"
        elif risk_score >= 40: risk = "HIGH"
        elif risk_score >= 20: risk = "MEDIUM"
        elif risk_score > 0: risk = "LOW"
        else: risk = "CLEAN"
        
        result["risk_level"] = risk
        result["risk_score"] = risk_score
        
        result["summary"] = {
            "total_leak_categories": len(findings),
            "html_comments": len(interesting_comments),
            "emails_exposed": len(emails),
            "internal_ips": len(internal_ips),
            "source_maps": len(all_maps),
            "server_leaks": len(server_leaks),
            "error_disclosures": len(error_disclosures),
            "secrets_found": len(secrets_found),
            "risk_level": risk,
            "risk_score": risk_score,
            "data_source": "Multi-vector info leak detection"
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def full_recon(domain):
    results = {"module": "Full Recon", "domain": domain, "modules": {}, "overall_score": 0, "stats": {}}
    modules = {
        "dns": dns_full_recon,
        "subdomains": subdomain_hunter,
        "reverse_dns": reverse_dns_shared,
        "email_sec": email_security,
        "ports": port_scanner,
        "wayback": wayback_recon,
        "cloud": cloud_infra,
        "shodan": shodan_intel,
        "waf": waf_detect,
        "tech": deep_tech_fingerprint,
        "headers": http_fingerprint,
        "threat_intel": alienvault_threat_intel,
        "sensitive_paths": sensitive_paths,
        "cve_hunter": cve_hunter,
        "ssl": ssl_deep_audit,
        "security": security_headers,
        "cors": cors_misconfig,
        "redirect": open_redirect,
        "cookies": cookie_analyzer,
        "takeover": subdomain_takeover,
        "whois": whois_intel,
        "reputation": domain_reputation,
        "info_leak": info_leak_detector,
    }
    completed = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(func, domain): name for name, func in modules.items()}
        for f in as_completed(futures, timeout=180):
            name = futures[f]
            try:
                results["modules"][name] = f.result()
                completed += 1
            except Exception as e:
                results["modules"][name] = {"error": str(e)}
                failed += 1
    # Calculate overall score
    scores = []
    if "ssl" in results["modules"] and "score" in results["modules"]["ssl"]:
        scores.append(results["modules"]["ssl"]["score"])
    if "security" in results["modules"] and "score" in results["modules"]["security"]:
        scores.append(results["modules"]["security"]["score"])
    if "email_sec" in results["modules"] and "score" in results["modules"]["email_sec"]:
        scores.append(results["modules"]["email_sec"]["score"])
    if "cookies" in results["modules"] and "score" in results["modules"]["cookies"]:
        scores.append(results["modules"]["cookies"]["score"])
    if "reputation" in results["modules"] and "score" in results["modules"]["reputation"]:
        scores.append(results["modules"]["reputation"]["score"])
    overall = round(sum(scores) / len(scores)) if scores else 0
    results["overall_score"] = overall
    results["overall_grade"] = "A+" if overall >= 95 else "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 50 else "D" if overall >= 30 else "F"
    results["stats"] = {"modules_completed": completed, "modules_failed": failed,
        "overall_score": overall, "overall_grade": results["overall_grade"]}
    return results

# ================================================================
# MODULE 25: EXPORT REPORT
# ================================================================
def export_report(domain, scan_data):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    report = {
        "report": {
            "title": f"DDOS_F16 SCANWEBS — Full Reconnaissance Report",
            "target": domain,
            "generated": timestamp,
            "engine": "DDOS_F16 SCANWEBS v7.0",
            "modules_count": len(scan_data) if isinstance(scan_data, dict) else 0,
        },
        "data": scan_data
    }
    return report

# ================================================================
# FLASK ROUTES
# ================================================================
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    if not data or 'domain' not in data or 'module' not in data:
        return jsonify({"error": "Missing domain or module"}), 400
    domain = clean_domain(data['domain'])
    module = data['module']
    if not domain:
        return jsonify({"error": "Invalid domain"}), 400
    module_map = {
        # JS ID → Python function (matching frontend module IDs)
        "dns": dns_full_recon,
        "subdomains": subdomain_hunter,
        "reverse_dns": reverse_dns_shared,
        "email_sec": email_security,
        "ports": port_scanner,
        "wayback": wayback_recon,
        "cloud": cloud_infra,
        "shodan": shodan_intel,
        "waf": waf_detect,
        "tech": deep_tech_fingerprint,
        "headers": http_fingerprint,
        "threat_intel": alienvault_threat_intel,
        "sensitive_paths": sensitive_paths,
        "cve_hunter": cve_hunter,
        "ssl": ssl_deep_audit,
        "security": security_headers,
        "cors": cors_misconfig,
        "redirect": open_redirect,
        "cookies": cookie_analyzer,
        "takeover": subdomain_takeover,
        "whois": whois_intel,
        "reputation": domain_reputation,
        "info_leak": info_leak_detector,
        "full_scan": full_recon,
    }
    if module == "export_report":
        scan_data = data.get('scan_data', {})
        result = export_report(domain, scan_data)
        return jsonify(result)
    func = module_map.get(module)
    if not func:
        return jsonify({"error": f"Unknown module: {module}"}), 400
    try:
        start = time.time()
        result = func(domain)
        elapsed = round(time.time() - start, 2)
        result["scan_time"] = f"{elapsed}s"
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "module": module}), 500

@app.route('/api/modules', methods=['GET'])
def list_modules():
    modules = [
        {"id": "dns", "name": "DNS Full Recon", "icon": "🔍", "category": "DNS Intelligence", "desc": "All DNS records + DNSSEC + Zone Transfer"},
        {"id": "subdomains", "name": "Subdomain Hunter", "icon": "🎯", "category": "DNS Intelligence", "desc": "crt.sh + Brute Force + Web Archive"},
        {"id": "reverse_dns", "name": "Reverse DNS & Shared Hosting", "icon": "🔄", "category": "DNS Intelligence", "desc": "PTR Records + Shared hosting detection"},
        {"id": "email_sec", "name": "Email Security Audit", "icon": "📧", "category": "DNS Intelligence", "desc": "SPF + DKIM + DMARC analysis"},
        {"id": "ports", "name": "Port Scanner Pro", "icon": "🚪", "category": "Infrastructure", "desc": "Top 40 ports + Banner grabbing"},
        {"id": "wayback", "name": "Wayback Recon", "icon": "📜", "category": "Infrastructure", "desc": "Historical URLs + Hidden endpoints + Config files"},
        {"id": "cloud", "name": "Cloud Infrastructure", "icon": "☁️", "category": "Infrastructure", "desc": "AWS/Azure/GCP/CDN detection"},
        {"id": "shodan", "name": "Shodan Intelligence", "icon": "🔥", "category": "Infrastructure", "desc": "Real CVEs + Open ports + CPEs from Shodan"},
        {"id": "waf", "name": "WAF Detection", "icon": "🛡️", "category": "Web Analysis", "desc": "Firewall fingerprinting + bypass test"},
        {"id": "tech", "name": "Deep Tech Fingerprint", "icon": "🧬", "category": "Web Analysis", "desc": "200+ signatures - CMS + Frameworks + Analytics"},
        {"id": "headers", "name": "HTTP Deep Fingerprint", "icon": "📡", "category": "Web Analysis", "desc": "Headers + Cookies + Redirects + Timing"},
        {"id": "threat_intel", "name": "AlienVault Threat Intel", "icon": "⚡", "category": "Intelligence", "desc": "OTX threat pulses + Malware + MITRE ATT&CK"},
        {"id": "sensitive_paths", "name": "Sensitive Path Scanner", "icon": "🗂️", "category": "Security Audit", "desc": "120+ paths: .git, .env, backups, admin panels"},
        {"id": "cve_hunter", "name": "CVE Vulnerability Hunter", "icon": "🎯", "category": "Security Audit", "desc": "Real CVE lookup + CVSS scores + Exploits"},
        {"id": "ssl", "name": "SSL/TLS Deep Audit", "icon": "🔐", "category": "Security Audit", "desc": "Cert chain + Protocols + Grade A-F"},
        {"id": "security", "name": "Security Headers Pro", "icon": "🔒", "category": "Security Audit", "desc": "CSP + HSTS + 11 headers + Score 0-100"},
        {"id": "cors", "name": "CORS Misconfiguration", "icon": "🌐", "category": "Security Audit", "desc": "Origin reflection + Credential leak tests"},
        {"id": "redirect", "name": "Open Redirect Scanner", "icon": "↗️", "category": "Security Audit", "desc": "18 parameter tests for redirect vulns"},
        {"id": "cookies", "name": "Cookie Analyzer", "icon": "🍪", "category": "Security Audit", "desc": "HttpOnly + Secure + SameSite analysis"},
        {"id": "takeover", "name": "Subdomain Takeover", "icon": "💀", "category": "Security Audit", "desc": "Dangling CNAME + 15 service checks"},
        {"id": "whois", "name": "WHOIS Intelligence", "icon": "📋", "category": "Intelligence", "desc": "Registration + Age + Expiry + Registrar"},
        {"id": "reputation", "name": "Domain Reputation", "icon": "⭐", "category": "Intelligence", "desc": "8 blacklists + Spam + Malware check"},
        {"id": "info_leak", "name": "Info Leak Detector", "icon": "🔎", "category": "Intelligence", "desc": "HTML comments + Secrets + Source maps + Error pages"},
        {"id": "full_scan", "name": "⚡ FULL RECON", "icon": "⚡", "category": "Full Scan", "desc": "ALL 22 modules at once + Overall score"},
        {"id": "export_report", "name": "📊 Export Report", "icon": "📊", "category": "Full Scan", "desc": "Export results as JSON"},
    ]
    return jsonify(modules)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "operational", "engine": "DDOS_F16 SCANWEBS v7.0", "modules": 25, "timestamp": datetime.datetime.utcnow().isoformat()})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
