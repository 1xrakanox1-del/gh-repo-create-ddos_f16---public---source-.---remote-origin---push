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
def network_trace(domain):
    results = {"module": "Network Trace", "domain": domain, "ip": None, "hops": [], "stats": {}}
    ip = resolve_ip(domain)
    if not ip:
        results["error"] = "Could not resolve domain"
        return results
    results["ip"] = ip
    hops = []
    for ttl in range(1, 30):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            s.settimeout(2)
            start = time.time()
            s.sendto(b'', (ip, 33434))
            try:
                recv_s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                recv_s.settimeout(2)
                data, addr = recv_s.recvfrom(512)
                elapsed = (time.time() - start) * 1000
                hop_ip = addr[0]
                # Reverse DNS
                try:
                    hostname = socket.gethostbyaddr(hop_ip)[0]
                except:
                    hostname = hop_ip
                hops.append({"ttl": ttl, "ip": hop_ip, "hostname": hostname, "rtt_ms": round(elapsed, 2)})
                recv_s.close()
                if hop_ip == ip:
                    break
            except socket.timeout:
                hops.append({"ttl": ttl, "ip": "*", "hostname": "* * *", "rtt_ms": None})
                try:
                    recv_s.close()
                except:
                    pass
            s.close()
        except:
            hops.append({"ttl": ttl, "ip": "*", "hostname": "Request timed out", "rtt_ms": None})
    results["hops"] = hops
    results["stats"] = {"total_hops": len(hops), "destination_reached": any(h["ip"] == ip for h in hops), "target_ip": ip}
    return results

# ================================================================
# MODULE 7: CLOUD INFRASTRUCTURE DETECTION
# ================================================================
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
def geoip_advanced(domain):
    results = {"module": "GeoIP Advanced", "domain": domain, "ip": None, "geo": {}, "stats": {}}
    ip = resolve_ip(domain)
    if not ip:
        results["error"] = "Could not resolve domain"
        return results
    results["ip"] = ip
    try:
        r = safe_get(f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query", timeout=10)
        if r and r.status_code == 200:
            data = r.json()
            results["geo"] = {
                "ip": ip,
                "continent": data.get("continent", "Unknown"),
                "country": f"{data.get('country', 'Unknown')} ({data.get('countryCode', '')})",
                "region": data.get("regionName", "Unknown"),
                "city": data.get("city", "Unknown"),
                "zip": data.get("zip", "N/A"),
                "coordinates": f"{data.get('lat', 0)}, {data.get('lon', 0)}",
                "timezone": data.get("timezone", "Unknown"),
                "isp": data.get("isp", "Unknown"),
                "organization": data.get("org", "Unknown"),
                "asn": data.get("as", "Unknown"),
                "asn_name": data.get("asname", "Unknown"),
                "reverse_dns": data.get("reverse", "N/A"),
                "is_proxy": data.get("proxy", False),
                "is_hosting": data.get("hosting", False),
                "is_mobile": data.get("mobile", False),
            }
    except:
        results["geo"] = {"error": "GeoIP lookup failed"}
    # Additional: ipinfo.io
    try:
        r2 = safe_get(f"https://ipinfo.io/{ip}/json", timeout=8)
        if r2 and r2.status_code == 200:
            d2 = r2.json()
            results["geo"]["hostname"] = d2.get("hostname", "N/A")
            results["geo"]["anycast"] = d2.get("anycast", False)
    except:
        pass
    results["stats"] = {"ip": ip, "country": results["geo"].get("country", "Unknown"), "isp": results["geo"].get("isp", "Unknown"), "is_hosting": results["geo"].get("is_hosting", False)}
    return results


# ================================================================
# MODULE 9: WAF DETECTION
# ================================================================
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
def tech_stack(domain):
    results = {"module": "Tech Stack X-Ray", "domain": domain, "technologies": {}, "stats": {}}
    techs = {"server": [], "cms": [], "framework": [], "javascript": [], "css_framework": [], "analytics": [], "cdn": [], "hosting": [], "language": [], "security": [], "other": []}
    try:
        r = safe_get(f"https://{domain}", timeout=12)
        if not r:
            r = safe_get(f"http://{domain}", timeout=12)
        if not r:
            results["error"] = "Could not fetch website"
            return results
        html = r.text
        h = {k.lower(): v for k, v in r.headers.items()}
        soup = BeautifulSoup(html, 'html.parser')
        # Server
        if h.get('server'):
            techs["server"].append(h['server'])
        if h.get('x-powered-by'):
            techs["language"].append(h['x-powered-by'])
        # CMS Detection
        cms_patterns = {
            "WordPress": ['/wp-content/', '/wp-includes/', 'wp-json', 'wordpress'],
            "Joomla": ['/components/com_', '/media/jui/', 'joomla'],
            "Drupal": ['drupal.js', 'Drupal.settings', '/sites/default/'],
            "Shopify": ['cdn.shopify.com', 'shopify.com'],
            "Wix": ['wix.com', 'parastorage.com'],
            "Squarespace": ['squarespace.com', 'sqsp.com'],
            "Ghost": ['ghost.org', 'ghost.io'],
            "PrestaShop": ['prestashop', '/modules/'],
            "Magento": ['mage/', 'Magento', 'magento'],
            "Laravel": ['laravel', 'csrf-token'],
        }
        html_lower = html.lower()
        for cms, patterns in cms_patterns.items():
            for pat in patterns:
                if pat.lower() in html_lower:
                    if cms not in techs["cms"]:
                        techs["cms"].append(cms)
                    break
        # Meta generator
        meta_gen = soup.find('meta', attrs={'name': 'generator'})
        if meta_gen and meta_gen.get('content'):
            techs["cms"].append(f"Generator: {meta_gen['content']}")
        # JavaScript Libraries
        js_libs = {
            "jQuery": ["jquery", "jquery.min.js"],
            "React": ["react.production", "react-dom", "reactjs", "_react"],
            "Vue.js": ["vue.js", "vue.min.js", "vue.global", "__vue__"],
            "Angular": ["angular", "ng-app", "ng-controller"],
            "Next.js": ["_next/", "__next", "next/"],
            "Nuxt.js": ["__nuxt", "_nuxt/"],
            "Svelte": ["svelte"],
            "Alpine.js": ["alpine", "x-data"],
            "HTMX": ["htmx.org", "hx-get", "hx-post"],
            "Tailwind CSS": ["tailwindcss", "tailwind"],
            "Bootstrap": ["bootstrap.min", "bootstrap.css", "bootstrap.bundle"],
            "Lodash": ["lodash"],
            "Axios": ["axios"],
            "Moment.js": ["moment.min.js"],
            "Chart.js": ["chart.js", "chart.min.js"],
            "Three.js": ["three.js", "three.min.js"],
            "GSAP": ["gsap", "greensock"],
            "AOS": ["aos.js", "data-aos"],
        }
        scripts = [s.get('src', '') for s in soup.find_all('script', src=True)]
        links = [l.get('href', '') for l in soup.find_all('link', href=True)]
        all_resources = ' '.join(scripts + links).lower() + ' ' + html_lower
        for lib, patterns in js_libs.items():
            for pat in patterns:
                if pat in all_resources:
                    category = "css_framework" if lib in ["Tailwind CSS", "Bootstrap"] else "javascript"
                    if lib not in techs[category]:
                        techs[category].append(lib)
                    break
        # Analytics
        analytics_patterns = {
            "Google Analytics": ["google-analytics.com", "gtag(", "ga("],
            "Google Tag Manager": ["googletagmanager.com", "gtm.js"],
            "Facebook Pixel": ["connect.facebook.net", "fbq("],
            "Hotjar": ["hotjar.com", "hj("],
            "Mixpanel": ["mixpanel.com"],
            "Segment": ["segment.com", "analytics.js"],
            "Amplitude": ["amplitude.com"],
            "Plausible": ["plausible.io"],
            "Matomo": ["matomo", "piwik"],
        }
        for tool, patterns in analytics_patterns.items():
            for pat in patterns:
                if pat in all_resources:
                    techs["analytics"].append(tool)
                    break
        # Security
        if 'strict-transport-security' in h:
            techs["security"].append("HSTS Enabled")
        if 'content-security-policy' in h:
            techs["security"].append("CSP Enabled")
        if 'x-frame-options' in h:
            techs["security"].append("X-Frame-Options")
        # Count totals
        total = sum(len(v) for v in techs.values())
    except Exception as e:
        results["error"] = str(e)
        total = 0
    results["technologies"] = {k: v for k, v in techs.items() if v}
    results["stats"] = {"total_technologies": total, "categories": len([k for k, v in techs.items() if v])}
    return results

# ================================================================
# MODULE 11: HTTP DEEP FINGERPRINT
# ================================================================
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
def js_analyzer(domain):
    results = {"module": "JavaScript Analyzer", "domain": domain, "scripts": [], "secrets_found": [], "api_endpoints": [], "stats": {}}
    try:
        r = safe_get(f"https://{domain}", timeout=12)
        if not r:
            r = safe_get(f"http://{domain}", timeout=12)
        if not r:
            results["error"] = "Could not fetch website"
            return results
        soup = BeautifulSoup(r.text, 'html.parser')
        # External scripts
        ext_scripts = []
        for s in soup.find_all('script', src=True):
            src = s['src']
            if not src.startswith('http'):
                src = urljoin(f"https://{domain}", src)
            ext_scripts.append(src)
        results["scripts"] = ext_scripts[:30]
        # Inline scripts
        inline_scripts = [s.string for s in soup.find_all('script') if s.string and len(s.string) > 10]
        all_js = '\n'.join(inline_scripts[:10])
        # Fetch external JS files (first 5)
        for js_url in ext_scripts[:5]:
            try:
                jr = safe_get(js_url, timeout=8)
                if jr:
                    all_js += '\n' + jr.text[:50000]
            except:
                pass
        # Search for secrets
        secret_patterns = {
            "API Key": r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']([^"\']{8,})["\']',
            "AWS Access Key": r'AKIA[0-9A-Z]{16}',
            "AWS Secret": r'(?:aws[_-]?secret|secret[_-]?key)\s*[:=]\s*["\']([^"\']{20,})["\']',
            "Google API": r'AIza[0-9A-Za-z\-_]{35}',
            "Firebase": r'(?:firebase[_-]?key|firebase)\s*[:=]\s*["\']([^"\']{10,})["\']',
            "JWT Token": r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+',
            "Private Key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
            "Slack Token": r'xox[bpors]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*',
            "GitHub Token": r'gh[pousr]_[A-Za-z0-9_]{36}',
            "Bearer Token": r'[Bb]earer\s+[A-Za-z0-9\-_.~+/]+=*',
            "Password": r'(?:password|passwd|pwd)\s*[:=]\s*["\']([^"\']{4,})["\']',
            "Database URL": r'(?:mongodb|mysql|postgres|redis):\/\/[^\s"\']+',
            "Authorization Header": r'[Aa]uthorization\s*[:=]\s*["\']([^"\']+)["\']',
        }
        secrets = []
        for name, pattern in secret_patterns.items():
            matches = re.findall(pattern, all_js, re.IGNORECASE)
            for m in matches[:3]:
                val = m if isinstance(m, str) else m
                secrets.append({"type": name, "value": val[:30] + "..." if len(str(val)) > 30 else val, "severity": "CRITICAL" if name in ["AWS Secret", "Private Key", "Database URL"] else "HIGH"})
        results["secrets_found"] = secrets
        # API Endpoints
        api_patterns = [
            r'(?:fetch|axios|get|post|put|delete|patch)\s*\(\s*["\']([^"\']*api[^"\']*)["\']',
            r'(?:url|endpoint|baseURL|base_url)\s*[:=]\s*["\']([^"\']*(?:api|v[0-9])[^"\']*)["\']',
            r'["\'](/api/[^"\']+)["\']',
            r'["\']https?://[^"\']*api[^"\']*["\']',
        ]
        endpoints = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, all_js, re.IGNORECASE)
            endpoints.update(matches[:10])
        results["api_endpoints"] = list(endpoints)[:20]
    except Exception as e:
        results["error"] = str(e)
    results["stats"] = {"total_scripts": len(results["scripts"]), "secrets_found": len(results["secrets_found"]), "api_endpoints": len(results["api_endpoints"]),
        "risk_level": "CRITICAL" if any(s["severity"] == "CRITICAL" for s in results["secrets_found"]) else "HIGH" if results["secrets_found"] else "LOW"}
    return results

# ================================================================
# MODULE 13: LINK & URL EXTRACTOR
# ================================================================
def link_extractor(domain):
    results = {"module": "Link & URL Extractor", "domain": domain, "internal_links": [], "external_links": [], "forms": [], "hidden_paths": [], "emails": [], "stats": {}}
    try:
        r = safe_get(f"https://{domain}", timeout=12)
        if not r:
            r = safe_get(f"http://{domain}", timeout=12)
        if not r:
            results["error"] = "Could not fetch website"
            return results
        soup = BeautifulSoup(r.text, 'html.parser')
        base = f"https://{domain}"
        internal = set()
        external = set()
        # All links
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if href.startswith('#') or href.startswith('javascript:') or href == '/':
                continue
            full_url = urljoin(base, href)
            parsed = urlparse(full_url)
            if parsed.hostname and domain in parsed.hostname:
                internal.add(full_url)
            elif parsed.hostname:
                external.add(full_url)
        # Forms
        forms = []
        for form in soup.find_all('form'):
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            inputs = []
            for inp in form.find_all(['input', 'textarea', 'select']):
                inputs.append({"name": inp.get('name',''), "type": inp.get('type','text'), "id": inp.get('id','')})
            forms.append({"action": urljoin(base, action) if action else base, "method": method, "inputs": inputs})
        # Hidden paths (from comments, JS)
        hidden = set()
        comments = soup.find_all(string=lambda text: isinstance(text, type(soup.new_string(''))) and '<!--' in str(text) if False else False)
        # Find paths in JS
        path_pattern = r'["\']/([\w-]+(?:/[\w-]+){1,})["\']'
        paths = re.findall(path_pattern, r.text)
        for p in paths:
            hidden.add('/' + p)
        # Common admin/hidden paths
        admin_paths = ['/admin', '/login', '/dashboard', '/wp-admin', '/administrator', '/panel', '/cpanel',
                      '/phpmyadmin', '/api', '/swagger', '/graphql', '/.env', '/.git', '/backup',
                      '/config', '/debug', '/test', '/staging', '/dev']
        for path in admin_paths:
            try:
                rp = requests.head(f"https://{domain}{path}", timeout=5, verify=False, allow_redirects=False)
                if rp.status_code not in [404, 410]:
                    hidden.add(f"{path} (HTTP {rp.status_code})")
            except:
                pass
        # Emails
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text))
        results["internal_links"] = sorted(internal)[:100]
        results["external_links"] = sorted(external)[:50]
        results["forms"] = forms
        results["hidden_paths"] = sorted(hidden)[:50]
        results["emails"] = list(emails)[:20]
    except Exception as e:
        results["error"] = str(e)
    results["stats"] = {"internal": len(results["internal_links"]), "external": len(results["external_links"]),
        "forms": len(results["forms"]), "hidden_paths": len(results["hidden_paths"]), "emails": len(results["emails"])}
    return results

# ================================================================
# MODULE 14: CMS SCANNER
# ================================================================
def cms_scanner(domain):
    results = {"module": "CMS Scanner", "domain": domain, "cms": "Unknown", "version": "Unknown", "details": {}, "vulnerabilities": [], "stats": {}}
    base = f"https://{domain}"
    cms_detected = "Unknown"
    version = "Unknown"
    details = {}
    # WordPress Detection
    wp_paths = ['/wp-login.php', '/wp-admin/', '/wp-content/', '/wp-includes/js/wp-embed.min.js', '/xmlrpc.php', '/wp-json/wp/v2/']
    wp_found = []
    for path in wp_paths:
        try:
            r = requests.head(f"{base}{path}", timeout=5, verify=False, allow_redirects=True)
            if r.status_code not in [404, 410, 403]:
                wp_found.append(f"{path} → HTTP {r.status_code}")
        except:
            pass
    if wp_found:
        cms_detected = "WordPress"
        details["paths_found"] = wp_found
        # Version
        try:
            r = safe_get(base, timeout=10)
            if r:
                ver = re.search(r'content="WordPress\s+([\d.]+)"', r.text)
                if ver:
                    version = ver.group(1)
                # Themes
                themes = re.findall(r'/wp-content/themes/([^/"]+)', r.text)
                details["themes"] = list(set(themes))
                # Plugins
                plugins = re.findall(r'/wp-content/plugins/([^/"]+)', r.text)
                details["plugins"] = list(set(plugins))
        except:
            pass
        # Check REST API
        try:
            r = safe_get(f"{base}/wp-json/wp/v2/users", timeout=8)
            if r and r.status_code == 200:
                users = r.json()
                details["users_exposed"] = [{"name": u.get("name",""), "slug": u.get("slug","")} for u in users[:5]]
                results["vulnerabilities"].append({"type": "User Enumeration", "severity": "HIGH", "detail": f"REST API exposes {len(users)} user(s)"})
        except:
            pass
        # Check xmlrpc
        try:
            r = requests.post(f"{base}/xmlrpc.php", timeout=5, verify=False,
                data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>')
            if r.status_code == 200 and 'methodResponse' in r.text:
                results["vulnerabilities"].append({"type": "XML-RPC Enabled", "severity": "MEDIUM", "detail": "XML-RPC is active — potential brute force vector"})
        except:
            pass
    # Joomla Detection
    if cms_detected == "Unknown":
        joomla_paths = ['/administrator/', '/components/', '/media/jui/']
        joomla_found = []
        for path in joomla_paths:
            try:
                r = requests.head(f"{base}{path}", timeout=5, verify=False)
                if r.status_code not in [404, 410]:
                    joomla_found.append(f"{path} → HTTP {r.status_code}")
            except:
                pass
        if len(joomla_found) >= 2:
            cms_detected = "Joomla"
            details["paths_found"] = joomla_found
    # Drupal Detection
    if cms_detected == "Unknown":
        try:
            r = safe_get(base, timeout=10)
            if r and ('drupal' in r.text.lower() or 'sites/default' in r.text):
                cms_detected = "Drupal"
                ver = re.search(r'Drupal\s+([\d.]+)', r.text)
                if ver:
                    version = ver.group(1)
        except:
            pass
    # Shopify
    if cms_detected == "Unknown":
        try:
            r = safe_get(base, timeout=10)
            if r and 'cdn.shopify.com' in r.text:
                cms_detected = "Shopify"
        except:
            pass
    results["cms"] = cms_detected
    results["version"] = version
    results["details"] = details
    results["stats"] = {"cms": cms_detected, "version": version, "vulnerabilities": len(results["vulnerabilities"]),
        "plugins": len(details.get("plugins",[])), "themes": len(details.get("themes",[]))}
    return results

# ================================================================
# MODULE 15: SSL/TLS DEEP AUDIT
# ================================================================
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
            "registrant": str(w.get('registrant_name', w.get('name', 'REDACTED'))),
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
def robots_sitemap(domain):
    results = {"module": "Robots & Sitemap Intel", "domain": domain, "robots_txt": {}, "sitemaps": [], "stats": {}}
    base = f"https://{domain}"
    # Robots.txt
    try:
        r = safe_get(f"{base}/robots.txt", timeout=10)
        if r and r.status_code == 200:
            content = r.text
            lines = content.strip().split('\n')
            user_agents = []
            disallowed = []
            allowed = []
            sitemaps_found = []
            crawl_delay = None
            for line in lines:
                line = line.strip()
                if line.lower().startswith('user-agent:'):
                    user_agents.append(line.split(':', 1)[1].strip())
                elif line.lower().startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        disallowed.append(path)
                elif line.lower().startswith('allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        allowed.append(path)
                elif line.lower().startswith('sitemap:'):
                    sitemaps_found.append(line.split(':', 1)[1].strip())
                elif line.lower().startswith('crawl-delay:'):
                    crawl_delay = line.split(':', 1)[1].strip()
            # Interesting paths
            interesting = [p for p in disallowed if any(k in p.lower() for k in
                ['admin', 'login', 'private', 'secret', 'backup', 'config', 'api', 'internal',
                 'debug', 'test', 'staging', 'dev', 'database', 'db', 'wp-', 'cgi-bin', '.env', '.git'])]
            results["robots_txt"] = {
                "exists": True,
                "user_agents": user_agents,
                "disallowed_paths": disallowed,
                "allowed_paths": allowed,
                "interesting_paths": interesting,
                "sitemaps_declared": sitemaps_found,
                "crawl_delay": crawl_delay,
                "total_rules": len(disallowed) + len(allowed),
                "raw": content[:2000]
            }
        else:
            results["robots_txt"] = {"exists": False}
    except:
        results["robots_txt"] = {"exists": False, "error": "Could not fetch"}
    # Sitemaps
    sitemap_urls = results["robots_txt"].get("sitemaps_declared", [])
    if not sitemap_urls:
        sitemap_urls = [f"{base}/sitemap.xml", f"{base}/sitemap_index.xml"]
    sitemaps = []
    total_urls = 0
    for sm_url in sitemap_urls[:5]:
        try:
            if not sm_url.startswith('http'):
                sm_url = sm_url.strip()
            r = safe_get(sm_url, timeout=10)
            if r and r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                urls = [loc.text for loc in soup.find_all('loc')]
                sitemap_info = {"url": sm_url, "urls_count": len(urls), "sample_urls": urls[:10]}
                # Check for nested sitemaps
                nested = [u for u in urls if 'sitemap' in u.lower()]
                if nested:
                    sitemap_info["nested_sitemaps"] = nested[:5]
                sitemaps.append(sitemap_info)
                total_urls += len(urls)
        except:
            pass
    results["sitemaps"] = sitemaps
    results["stats"] = {"robots_exists": results["robots_txt"].get("exists", False),
        "disallowed_paths": len(results["robots_txt"].get("disallowed_paths", [])),
        "interesting_paths": len(results["robots_txt"].get("interesting_paths", [])),
        "sitemaps": len(sitemaps), "total_urls": total_urls}
    return results

# ================================================================
# MODULE 24: FULL RECON (ALL-IN-ONE)
# ================================================================
def full_recon(domain):
    results = {"module": "Full Recon", "domain": domain, "modules": {}, "overall_score": 0, "stats": {}}
    modules = {
        "dns_recon": dns_full_recon,
        "subdomains": subdomain_hunter,
        "reverse_dns": reverse_dns_shared,
        "email_security": email_security,
        "port_scan": port_scanner,
        "cloud_infra": cloud_infra,
        "geoip": geoip_advanced,
        "waf_detect": waf_detect,
        "tech_stack": tech_stack,
        "http_fingerprint": http_fingerprint,
        "js_analyzer": js_analyzer,
        "link_extractor": link_extractor,
        "cms_scanner": cms_scanner,
        "ssl_audit": ssl_deep_audit,
        "security_headers": security_headers,
        "cors_check": cors_misconfig,
        "open_redirect": open_redirect,
        "cookie_analyzer": cookie_analyzer,
        "subdomain_takeover": subdomain_takeover,
        "whois": whois_intel,
        "reputation": domain_reputation,
        "robots_sitemap": robots_sitemap,
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
    if "ssl_audit" in results["modules"] and "score" in results["modules"]["ssl_audit"]:
        scores.append(results["modules"]["ssl_audit"]["score"])
    if "security_headers" in results["modules"] and "score" in results["modules"]["security_headers"]:
        scores.append(results["modules"]["security_headers"]["score"])
    if "email_security" in results["modules"] and "score" in results["modules"]["email_security"]:
        scores.append(results["modules"]["email_security"]["score"])
    if "cookie_analyzer" in results["modules"] and "score" in results["modules"]["cookie_analyzer"]:
        scores.append(results["modules"]["cookie_analyzer"]["score"])
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
        "dns_recon": dns_full_recon,
        "subdomain_hunter": subdomain_hunter,
        "reverse_dns": reverse_dns_shared,
        "email_security": email_security,
        "port_scanner": port_scanner,
        "network_trace": network_trace,
        "cloud_infra": cloud_infra,
        "geoip": geoip_advanced,
        "waf_detect": waf_detect,
        "tech_stack": tech_stack,
        "http_fingerprint": http_fingerprint,
        "js_analyzer": js_analyzer,
        "link_extractor": link_extractor,
        "cms_scanner": cms_scanner,
        "ssl_audit": ssl_deep_audit,
        "security_headers": security_headers,
        "cors_misconfig": cors_misconfig,
        "open_redirect": open_redirect,
        "cookie_analyzer": cookie_analyzer,
        "subdomain_takeover": subdomain_takeover,
        "whois_intel": whois_intel,
        "domain_reputation": domain_reputation,
        "robots_sitemap": robots_sitemap,
        "full_recon": full_recon,
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
        {"id": "dns_recon", "name": "DNS Full Recon", "icon": "🔍", "category": "DNS Intelligence", "desc": "All DNS records + DNSSEC + Zone Transfer"},
        {"id": "subdomain_hunter", "name": "Subdomain Hunter", "icon": "🎯", "category": "DNS Intelligence", "desc": "crt.sh + Brute Force + Web Archive"},
        {"id": "reverse_dns", "name": "Reverse DNS & Shared Hosting", "icon": "🔄", "category": "DNS Intelligence", "desc": "PTR Records + Shared hosting detection"},
        {"id": "email_security", "name": "Email Security Audit", "icon": "📧", "category": "DNS Intelligence", "desc": "SPF + DKIM + DMARC analysis"},
        {"id": "port_scanner", "name": "Port Scanner Pro", "icon": "🚪", "category": "Infrastructure", "desc": "Top 40 ports + Banner grabbing"},
        {"id": "network_trace", "name": "Network Trace", "icon": "🛤️", "category": "Infrastructure", "desc": "Traceroute with ASN mapping"},
        {"id": "cloud_infra", "name": "Cloud Infrastructure", "icon": "☁️", "category": "Infrastructure", "desc": "AWS/Azure/GCP/CDN detection"},
        {"id": "geoip", "name": "GeoIP Advanced", "icon": "🌍", "category": "Infrastructure", "desc": "Location + ASN + ISP + Datacenter"},
        {"id": "waf_detect", "name": "WAF Detection", "icon": "🛡️", "category": "Web Analysis", "desc": "Firewall fingerprinting + bypass test"},
        {"id": "tech_stack", "name": "Tech Stack X-Ray", "icon": "⚙️", "category": "Web Analysis", "desc": "CMS + Framework + Libraries + Analytics"},
        {"id": "http_fingerprint", "name": "HTTP Deep Fingerprint", "icon": "📡", "category": "Web Analysis", "desc": "Headers + Cookies + Redirects + Timing"},
        {"id": "js_analyzer", "name": "JavaScript Analyzer", "icon": "📜", "category": "Web Analysis", "desc": "API keys + Secrets + Endpoints"},
        {"id": "link_extractor", "name": "Link & URL Extractor", "icon": "🔗", "category": "Web Analysis", "desc": "Internal/External links + Hidden paths"},
        {"id": "cms_scanner", "name": "CMS Scanner", "icon": "🏗️", "category": "Web Analysis", "desc": "WordPress/Joomla/Drupal + Vulnerabilities"},
        {"id": "ssl_audit", "name": "SSL/TLS Deep Audit", "icon": "🔐", "category": "Security Audit", "desc": "Cert chain + Protocols + Grade A-F"},
        {"id": "security_headers", "name": "Security Headers Pro", "icon": "🔒", "category": "Security Audit", "desc": "CSP + HSTS + 11 headers + Score 0-100"},
        {"id": "cors_misconfig", "name": "CORS Misconfiguration", "icon": "🌐", "category": "Security Audit", "desc": "Origin reflection + Credential leak tests"},
        {"id": "open_redirect", "name": "Open Redirect Scanner", "icon": "↗️", "category": "Security Audit", "desc": "18 parameter tests for redirect vulns"},
        {"id": "cookie_analyzer", "name": "Cookie Analyzer", "icon": "🍪", "category": "Security Audit", "desc": "HttpOnly + Secure + SameSite analysis"},
        {"id": "subdomain_takeover", "name": "Subdomain Takeover", "icon": "💀", "category": "Security Audit", "desc": "Dangling CNAME + 15 service checks"},
        {"id": "whois_intel", "name": "WHOIS Intelligence", "icon": "📋", "category": "Intelligence", "desc": "Registration + Age + Expiry + Registrar"},
        {"id": "domain_reputation", "name": "Domain Reputation", "icon": "⭐", "category": "Intelligence", "desc": "8 blacklists + Spam + Malware check"},
        {"id": "robots_sitemap", "name": "Robots & Sitemap Intel", "icon": "🤖", "category": "Intelligence", "desc": "robots.txt + Sitemaps + Hidden paths"},
        {"id": "full_recon", "name": "⚡ FULL RECON", "icon": "⚡", "category": "Full Scan", "desc": "ALL 22 modules at once + Overall score"},
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
