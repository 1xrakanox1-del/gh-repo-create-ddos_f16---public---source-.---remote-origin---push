#!/usr/bin/env python3
"""DDOS_F16 SCANWEBS — Flask Server v6.0"""
from flask import Flask, request, jsonify, send_from_directory
import sys, json, socket, subprocess, ssl, re, os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__, static_folder='static', template_folder='templates')

# ═══════ SCANNER ENGINE ═══════
class ScanEngine:
    def __init__(self, domain):
        self.domain = domain.strip().lower()
        if not re.match(r'^[a-z0-9][a-z0-9.\-]*\.[a-z]{2,}$', self.domain):
            raise ValueError("Invalid domain format")

    def _run(self, cmd, timeout=15):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return r.stdout.strip()
        except Exception as e:
            return f"ERROR: {e}"

    def dns_recon(self):
        records = {}
        for rtype in ['A','AAAA','MX','NS','TXT','CNAME','SOA','SRV','CAA']:
            out = self._run(f"dig +short {self.domain} {rtype}")
            if out and not out.startswith("ERROR"):
                records[rtype] = [l for l in out.split('\n') if l.strip()]
        full = self._run(f"dig {self.domain} ANY +noall +answer")
        records['_raw'] = full
        return records

    def subdomain_scan(self):
        wordlist = [
            'www','mail','ftp','webmail','smtp','pop','ns1','ns2','ns3','ns4',
            'webdisk','cpanel','whm','autodiscover','autoconfig','imap','test',
            'dev','staging','api','admin','portal','blog','shop','store',
            'secure','vpn','remote','cdn','static','assets','img','images',
            'media','docs','wiki','support','help','status','monitor',
            'db','database','mysql','sql','backup','git','jenkins',
            'ci','deploy','app','beta','alpha','demo','sandbox',
            'login','sso','auth','oauth','dashboard','panel',
            'm','mobile','old','new','v1','v2','v3',
            'mx','mx1','mx2','dns','dns1','dns2',
            'relay','gateway','proxy','cache','edge','node',
            'web','web1','web2','server','host','cloud',
            'internal','intranet','extranet','corp',
            'office','exchange','owa','vpn2','ssh',
            'grafana','kibana','elastic','prometheus','nagios','zabbix',
            'jira','confluence','bitbucket','gitlab',
            'crm','erp','hr','payroll','billing',
            'analytics','tracking','logs','metrics','reports',
            'staging1','staging2','uat','qa','prod','production',
            'preview','canary','release','forum','chat','ws',
            'socket','stream','video','audio','files','download',
            'upload','share','drive','storage','s3','bucket',
            'k8s','kubernetes','docker','swarm','registry',
            'smtp2','imap2','pop3','caldav','carddav','dav',
            'webapi','restapi','graphql','grpc','rpc','soap'
        ]
        found = []
        def check(sub):
            fqdn = f"{sub}.{self.domain}"
            try:
                ip = socket.gethostbyname(fqdn)
                return {'subdomain': fqdn, 'ip': ip}
            except:
                return None
        with ThreadPoolExecutor(max_workers=30) as ex:
            futs = {ex.submit(check, s): s for s in wordlist}
            for f in as_completed(futs):
                r = f.result()
                if r:
                    found.append(r)
        return sorted(found, key=lambda x: x['subdomain'])

    def whois_lookup(self):
        return self._run(f"whois {self.domain}", timeout=20)

    def http_headers(self):
        for scheme in ['https','http']:
            h = self._run(f"curl -sI -m 10 -L {scheme}://{self.domain}")
            if h and not h.startswith("ERROR"):
                return {'scheme': scheme, 'headers': h}
        return {'error': 'Could not retrieve HTTP headers'}

    def ssl_cert(self):
        raw = self._run(
            f"echo | openssl s_client -connect {self.domain}:443 -servername {self.domain} 2>/dev/null | openssl x509 -noout -text"
        )
        expiry = self._run(
            f"echo | openssl s_client -connect {self.domain}:443 -servername {self.domain} 2>/dev/null | openssl x509 -noout -enddate"
        )
        return {'certificate': raw, 'expiry': expiry}

    def tech_detect(self):
        html = self._run(f"curl -s -m 10 -L https://{self.domain}")
        if html.startswith("ERROR"):
            html = self._run(f"curl -s -m 10 -L http://{self.domain}")
        headers = self._run(f"curl -sI -m 10 -L https://{self.domain}")
        techs = []
        patterns = {
            'WordPress': [r'wp-content', r'wp-includes'],
            'Joomla': [r'/components/com_', r'joomla'],
            'Drupal': [r'drupal', r'sites/default/files'],
            'React': [r'react\.production', r'_reactRoot', r'__NEXT_DATA__'],
            'Next.js': [r'__NEXT_DATA__', r'_next/static'],
            'Angular': [r'ng-version', r'angular\.js'],
            'Vue.js': [r'vue\.js', r'vue\.min\.js', r'Vue\.'],
            'Nuxt.js': [r'__NUXT__', r'_nuxt/'],
            'Svelte': [r'svelte', r'__svelte'],
            'jQuery': [r'jquery[.\-]', r'jQuery'],
            'Bootstrap': [r'bootstrap\.css', r'bootstrap\.min'],
            'Tailwind CSS': [r'tailwindcss'],
            'Laravel': [r'laravel_session', r'csrf-token'],
            'Django': [r'csrfmiddlewaretoken', r'__admin'],
            'Ruby on Rails': [r'csrf-param', r'rails'],
            'Express.js': [r'X-Powered-By: Express'],
            'ASP.NET': [r'asp\.net', r'__VIEWSTATE', r'X-AspNet'],
            'PHP': [r'X-Powered-By: PHP', r'\.php'],
            'Nginx': [r'[Ss]erver:\s*nginx'],
            'Apache': [r'[Ss]erver:\s*Apache'],
            'Cloudflare': [r'cf-ray', r'cloudflare'],
            'AWS': [r'AmazonS3', r'awselb', r'x-amz'],
            'Google Cloud': [r'x-goog', r'gstatic'],
            'Vercel': [r'x-vercel', r'vercel'],
            'Netlify': [r'x-nf', r'netlify'],
            'Shopify': [r'cdn\.shopify', r'shopify'],
            'Wix': [r'X-Wix', r'wix\.com'],
            'Squarespace': [r'squarespace'],
            'Google Analytics': [r'google-analytics', r'gtag\(', r'UA-\d'],
            'Google Tag Manager': [r'googletagmanager'],
            'Hotjar': [r'hotjar'],
            'Stripe': [r'stripe\.com/v'],
            'reCAPTCHA': [r'recaptcha', r'grecaptcha'],
        }
        combined = html + '\n' + headers
        for tech, regexes in patterns.items():
            for regex in regexes:
                if re.search(regex, combined, re.IGNORECASE):
                    techs.append(tech)
                    break
        return sorted(list(set(techs)))

    def robots_sitemap(self):
        data = {}
        for path in ['robots.txt','sitemap.xml']:
            out = self._run(f"curl -s -m 10 https://{self.domain}/{path}")
            if out and not out.startswith("ERROR") and '<html' not in out[:200].lower():
                data[path] = out[:8000]
        return data

    def reverse_dns(self):
        try:
            ip = socket.gethostbyname(self.domain)
            ptr = self._run(f"dig +short -x {ip}")
            return {'domain': self.domain, 'ip': ip, 'ptr': ptr if ptr else 'No PTR record'}
        except Exception as e:
            return {'error': str(e)}

    def security_headers(self):
        important = [
            'Strict-Transport-Security','Content-Security-Policy','X-Frame-Options',
            'X-Content-Type-Options','X-XSS-Protection','Referrer-Policy',
            'Permissions-Policy','Cross-Origin-Opener-Policy',
            'Cross-Origin-Resource-Policy','Cross-Origin-Embedder-Policy'
        ]
        raw = self._run(f"curl -sI -m 10 -L https://{self.domain}")
        found = {}
        missing = []
        for h in important:
            m = re.search(f'^{re.escape(h)}:\\s*(.+)$', raw, re.IGNORECASE|re.MULTILINE)
            if m:
                found[h] = m.group(1).strip()
            else:
                missing.append(h)
        grade = 'A+' if len(missing)==0 else 'A' if len(missing)<=2 else 'B' if len(missing)<=4 else 'C' if len(missing)<=6 else 'D' if len(missing)<=8 else 'F'
        return {'found':found,'missing':missing,'score':f"{len(found)}/{len(important)}",'grade':grade}

    def port_scan(self):
        ports = {
            21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',
            80:'HTTP',110:'POP3',143:'IMAP',443:'HTTPS',445:'SMB',
            993:'IMAPS',995:'POP3S',3306:'MySQL',3389:'RDP',
            5432:'PostgreSQL',5900:'VNC',6379:'Redis',
            8080:'HTTP-Alt',8443:'HTTPS-Alt',27017:'MongoDB'
        }
        try:
            ip = socket.gethostbyname(self.domain)
        except:
            return {'error':'Cannot resolve domain'}
        open_ports = []
        def scan(port, svc):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                if s.connect_ex((ip, port)) == 0:
                    s.close()
                    return {'port':port,'service':svc,'state':'OPEN'}
                s.close()
            except:
                pass
            return None
        with ThreadPoolExecutor(max_workers=20) as ex:
            futs = {ex.submit(scan,p,s):p for p,s in ports.items()}
            for f in as_completed(futs):
                r = f.result()
                if r: open_ports.append(r)
        return {'ip':ip,'ports':sorted(open_ports, key=lambda x:x['port']),'total_scanned':len(ports)}

    def geo_locate(self):
        try:
            ip = socket.gethostbyname(self.domain)
            out = self._run(f"curl -s http://ip-api.com/json/{ip}")
            data = json.loads(out)
            data['resolved_ip'] = ip
            return data
        except:
            return {'error':'Geolocation failed'}


# ═══════ SCAN MAP ═══════
SCAN_MAP = {
    'dns': 'dns_recon',
    'subdomains': 'subdomain_scan',
    'whois': 'whois_lookup',
    'headers': 'http_headers',
    'ssl': 'ssl_cert',
    'tech': 'tech_detect',
    'robots': 'robots_sitemap',
    'reverse_dns': 'reverse_dns',
    'security': 'security_headers',
    'ports': 'port_scan',
    'geo': 'geo_locate'
}


# ═══════ ROUTES ═══════
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Run a single scan module against a domain."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body'}), 400

    domain = data.get('domain', '').strip().lower()
    module_id = data.get('module', '').strip()

    if not domain:
        return jsonify({'error': 'Domain required'}), 400
    if not re.match(r'^[a-z0-9][a-z0-9.\-]*\.[a-z]{2,}$', domain):
        return jsonify({'error': 'Invalid domain format'}), 400
    if module_id not in SCAN_MAP:
        return jsonify({'error': f'Unknown module: {module_id}'}), 400

    try:
        engine = ScanEngine(domain)
        method = getattr(engine, SCAN_MAP[module_id])
        result = method()
        return jsonify(result if isinstance(result, (dict, list)) else {'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'online', 'version': '6.0', 'engine': 'DDOS_F16 SCANWEBS'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
