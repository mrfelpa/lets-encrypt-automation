
# System Requirements

- Python 3.6+
- Administrator/root access
- Internet connection

# Installation

- Clone this repository:

        git clone https://github.com/mrfelpa/lets-encrypt-automation.git

- Navigate to the project directory:

        cd lets-encrypt-automation

# Operating Modes

- ***Nginx Mode***

- Uses Certbot's Nginx plugin to obtain and install the certificate. ***Recommended if you are using Nginx as a web server.
Standalone Mode***

- Certbot temporarily starts its own web server to validate the domain and obtain the certificate. Use this mode if you are not running a web server or if the server is not supported by Certbot.

***Logs***

- The script generates detailed logs ***in certbot_install.log***, useful for troubleshooting and auditing.
