import requests
import threading
import dns.resolver

# ===== INPUT =====
domain = input("Enter domain: ").strip()

print("\n[+] Starting DNS Enumeration...\n")

# ===== DNS ENUMERATION =====
record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SOA']
resolver = dns.resolver.Resolver()

for record_type in record_types:
    try:
        answers = resolver.resolve(domain, record_type)
        print(f"[DNS] {record_type} records:")
        for data in answers:
            print(f"   -> {data}")
    except:
        pass

print("\n[+] Starting Subdomain Enumeration...\n")

# ===== SUBDOMAIN ENUMERATION =====
try:
    with open('subdomains.txt') as file:
        subdomains = file.read().splitlines()
except FileNotFoundError:
    print("[-] Error: subdomains.txt file not found!")
    exit()

discovered_subdomains = []
lock = threading.Lock()

def check_subdomain(subdomain):
    url = f"http://{subdomain}.{domain}"
    try:
        response = requests.get(url, timeout=3)

        if response.status_code in [200, 301, 302, 403]:
            print(f"[✔] Active: {url} (Status: {response.status_code})")

            with lock:
                discovered_subdomains.append(url)
        else:
            print(f"[-] Found but not active: {url} (Status: {response.status_code})")

    except requests.RequestException:
        pass

threads = []

for subdomain in subdomains:
    thread = threading.Thread(target=check_subdomain, args=(subdomain,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

# ===== SAVE RESULTS =====
with open('discovered_subdomains.txt', 'w') as f:
    for subdomain in discovered_subdomains:
        print(subdomain, file=f)

print("\n[+] Scan Completed. Results saved in discovered_subdomains.txt")
