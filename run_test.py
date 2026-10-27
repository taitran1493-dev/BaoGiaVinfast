import subprocess, time, sys

sys.stdout.reconfigure(encoding='utf-8')

chrome_proc = subprocess.Popen([
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9222',
    '--remote-allow-origins=*',
    r'--user-data-dir=C:\Users\PC\.gemini\antigravity\scratch\vinfast-baogia\temp_profile',
    'http://localhost:8080/index.html'
])

try:
    time.sleep(3)
    res = subprocess.run(['node', r'C:\Users\PC\.gemini\antigravity\scratch\vinfast-baogia\verify_magic_studio.js'], capture_output=True, encoding='utf-8')
    print(res.stdout)
    if res.stderr: print(res.stderr)
finally:
    chrome_proc.terminate()
    chrome_proc.wait()
