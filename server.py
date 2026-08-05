#!/usr/bin/env python3
# ==============================================================================
# AlphaEvolve Real Terminal Bridge & Web Dashboard Server
# ==============================================================================
import http.server
import socketserver
import json
import subprocess
import os

PORT = 8080
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DEMO_DIR = os.path.join(PROJECT_ROOT, "web_demo")

class AlphaEvolveServerHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Route requests to web_demo directory
        clean_path = path.split('?')[0].split('#')[0]
        if clean_path == '/' or clean_path == '':
            return os.path.join(WEB_DEMO_DIR, "index.html")
        
        target = os.path.join(WEB_DEMO_DIR, clean_path.lstrip('/'))
        if os.path.exists(target):
            return target
            
        root_target = os.path.join(PROJECT_ROOT, clean_path.lstrip('/'))
        if os.path.exists(root_target):
            return root_target
            
    def do_GET(self):
        if self.path.startswith('/api/view-file'):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            filename = query.get('file', ['program.v'])[0]
            scenario = query.get('scenario', ['verilog_fir'])[0]

            folder_name = "verilog_fir_filter" if scenario == 'verilog_fir' else "circle_packing"
            base_dir = os.path.join(PROJECT_ROOT, "examples", folder_name)

            if filename in ['program.v', 'program.py']:
                if scenario == 'verilog_fir' and filename == 'program.v':
                    real_file = os.path.join(base_dir, "src", "program.v")
                else:
                    real_file = os.path.join(base_dir, "src", "program.py")
            elif filename == 'evaluate.py':
                real_file = os.path.join(base_dir, "src", "evaluate.py")
            elif filename == 'run_evolution.py':
                real_file = os.path.join(base_dir, "src", "run_evolution.py")
            elif filename == '.env':
                real_file = os.path.join(base_dir, ".env")
            elif filename == 'instructions.md':
                real_file = os.path.join(base_dir, "instructions.md")
            else:
                real_file = os.path.join(base_dir, filename)

            content = ""
            if os.path.exists(real_file):
                with open(real_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                content = f"# Error: File not found on disk: {real_file}"

            response_data = {"filename": filename, "content": content, "real_path": real_file}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        if self.path == '/api/terminal':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                cmd = data.get('command', '').strip()
                
                if not cmd:
                    response_data = {"output": "Error: Empty command"}
                else:
                    # Execute REAL shell command in examples/circle_packing directory with venv
                    shell_cmd = f"source .venv/bin/activate 2>/dev/null || true; cd examples/circle_packing 2>/dev/null || true; {cmd}"
                    
                    process = subprocess.run(
                        shell_cmd,
                        shell=True,
                        executable="/bin/bash",
                        cwd=PROJECT_ROOT,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    stdout = process.stdout
                    stderr = process.stderr
                    
                    output = stdout
                    if stderr:
                        if output:
                            output += "\n" + stderr
                        else:
                            output = stderr
                            
                    if not output and process.returncode == 0:
                        output = "(Command executed successfully with no output)"
                        
                    response_data = {"output": output, "returncode": process.returncode}
                    
            except subprocess.TimeoutExpired:
                response_data = {"output": "Error: Command timed out after 30 seconds."}
            except Exception as e:
                response_data = {"output": f"Execution Error: {str(e)}"}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            return
            
        super().do_POST()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    os.chdir(PROJECT_ROOT)
    handler = AlphaEvolveServerHandler
    with ReusableTCPServer(("", PORT), handler) as httpd:
        print(f"🚀 AlphaEvolve Real Terminal & Web Server running at http://localhost:{PORT}")
        httpd.serve_forever()
