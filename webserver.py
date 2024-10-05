import os
import http.server
import socketserver
import logging
from datetime import datetime, timedelta
import time
import random
from collections import defaultdict

PORT = 8078
DIRECTORY = "/opt/Threatintel"
REAL_LOG_FILE_PATH = "/var/log/Web_Server.log"

# Configurable Rate Limit
RATE_LIMIT = 10  # 10 requests per second
BLOCK_DURATION = 60  # Block IP for 60 seconds

ALLOWED_IPS = [
    "127.0.0.1",  # Example allowed IP
    "10.1.1.1",  # Another example allowed IP
    "10.1.1.2"
]

# Get the system's timezone
LOCAL_TIMEZONE = time.strftime('%Z')

# Configure logging for real logs
logging.basicConfig(filename=REAL_LOG_FILE_PATH, level=logging.INFO, 
                    format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')

# Dictionary to track request counts and block times
request_counts = defaultdict(lambda: {'count': 0, 'timestamp': datetime.now()})
blocked_ips = {}

class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    server_version = ""  # Empty server version to prevent disclosure
    sys_version = ""

    def log_message(self, format, *args):
        # Add timestamp with system's local timezone to the real logs
        now = datetime.now()
        logging.info("%s - - [%s] %s\n" %
                     (self.client_address[0],
                      now.strftime('%Y-%m-%d %H:%M:%S ') + LOCAL_TIMEZONE,
                      format % args))

    def do_GET(self):
        client_ip = self.client_address[0]

        # Check if the IP is currently blocked
        if client_ip in blocked_ips:
            block_until = blocked_ips[client_ip]
            if datetime.now() < block_until:
                self.send_response(403)
                self.end_headers()
                self.log_message("Blocked IP %s attempted GET request during block period", client_ip)
                return
            else:
                # Unblock the IP if the block period has expired
                del blocked_ips[client_ip]

        # Rate limiting check
        current_time = datetime.now()
        time_difference = (current_time - request_counts[client_ip]['timestamp']).total_seconds()

        if time_difference > 1:
            # Reset the request count if more than 1 second has passed
            request_counts[client_ip] = {'count': 1, 'timestamp': current_time}
        else:
            request_counts[client_ip]['count'] += 1

        if request_counts[client_ip]['count'] > RATE_LIMIT:
            # Block the IP for BLOCK_DURATION seconds
            blocked_ips[client_ip] = datetime.now() + timedelta(seconds=BLOCK_DURATION)
            self.send_response(403)
            self.end_headers()
            self.log_message("Blocked IP %s for exceeding rate limit", client_ip)
            return

        # Add random delay to slow down automated scans
        time.sleep(random.uniform(1, 3))

        if client_ip in ALLOWED_IPS:
            if self.path.endswith(".csv"):
                requested_path = self.translate_path(self.path)
                # Ensure the requested path is within the allowed directory
                if os.path.commonpath([requested_path, DIRECTORY]) == DIRECTORY:
                    self.log_message("GET request for %s", self.path)
                    super().do_GET()
                else:
                    self.send_response(403)
                    self.end_headers()
                    self.log_message("Forbidden GET request from %s", self.path)
            else:
                self.send_response(403)
                self.end_headers()
                self.log_message("Forbidden GET request for non-CSV file from %s", self.path)
        else:
            # Respond with random fake data to confuse attackers
            self.send_fake_response()
            self.log_message("Suspicious GET request from unauthorized IP %s", client_ip)

    def do_POST(self):
        self.send_fake_response()
        self.log_message("Blocked POST request")

    def do_PUT(self):
        self.send_fake_response()
        self.log_message("Blocked PUT request")

    def do_DELETE(self):
        self.send_fake_response()
        self.log_message("Blocked DELETE request")

    def do_PATCH(self):
        self.send_fake_response()
        self.log_message("Blocked PATCH request")

    def send_fake_response(self):
        # Respond with a random HTTP status code to confuse scanners
        random_status = random.choice([200, 301, 302, 404, 500])
        self.send_response(random_status)
        self.end_headers()
        # Send a fake response body (optional)
        self.wfile.write(b"No content is Available")

    def translate_path(self, path):
        # Sanitize the path to prevent directory traversal
        sanitized_path = os.path.normpath(os.path.join(DIRECTORY, path.lstrip("/")))
        return sanitized_path if os.path.commonpath([sanitized_path, DIRECTORY]) == DIRECTORY else DIRECTORY

Handler = SecureHTTPRequestHandler
Handler.directory = DIRECTORY

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
