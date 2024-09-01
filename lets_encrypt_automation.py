import os
import platform
import subprocess
import logging
import re
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.progress import Progress

console = Console()
logging.basicConfig(filename='certbot_install.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUPPORTED_OS = ["Linux", "Windows"]
CERTBOT_INSTALL_COMMANDS = {
    "Linux": ["apt-get", "install", "-y", "certbot", "python3-certbot-nginx"],
    "Windows": ["choco", "install", "certbot"]
}

def is_supported_os():
    return platform.system() in SUPPORTED_OS

def check_dependencies():
    os_name = platform.system()
    if os_name == "Linux":
        try:
            subprocess.run(["apt-get", "--version"], check=True)
        except subprocess.CalledProcessError:
            console.print("[bold red]apt-get is not installed. Please install it before continuing.[/bold red]")
            exit(1)
    elif os_name == "Windows":
        try:
            subprocess.run(["choco", "--version"], check=True)
        except subprocess.CalledProcessError:
            console.print("[bold red]Chocolatey is not installed. Please install it before continuing.[/bold red]")
            exit(1)

def install_certbot():
    os_name = platform.system()
    console.print(f"[bold green]Installing Certbot on {os_name}...[/bold green]")
    
    try:
        if os_name == "Linux":
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(CERTBOT_INSTALL_COMMANDS["Linux"], check=True)
        elif os_name == "Windows":
            subprocess.run(CERTBOT_INSTALL_COMMANDS["Windows"], check=True)
        console.print(f"[bold green]Certbot installed successfully on {os_name}![/bold green]")
        logging.info(f"Certbot installed successfully on {os_name}.")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error installing Certbot on {os_name}: {e}[/bold red]")
        logging.error(f"Error installing Certbot on {os_name}: {e}")
        exit(2)

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_domain(domain):
    domain_regex = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$'
    return re.match(domain_regex, domain) is not None

def validate_input(domain, email):
    if not domain or not email:
        console.print("[bold red]Domain and email cannot be empty.[/bold red]")
        return False
    if not validate_email(email):
        console.print("[bold red]Invalid email format. Please enter a valid email.[/bold red]")
        return False
    if not validate_domain(domain):
        console.print("[bold red]Invalid domain format. Please enter a valid domain.[/bold red]")
        return False
    return True

def obtain_certificate(domain, email, mode):
    
    console.print(f"[bold blue]Obtaining certificate for {domain} using {mode} mode...[/bold blue]")
    with Progress() as progress:
        task = progress.add_task("[cyan]Obtaining certificate...", total=None)
        try:
            command = ["certbot", "certonly", f"--{mode}", "-d", domain, "--email", email, "--agree-tos", "--non-interactive"]
            subprocess.run(command, check=True)
            progress.update(task, advance=1)
            console.print("[bold green]Certificate obtained successfully![/bold green]")
            logging.info(f"Certificate obtained successfully for {domain} using {mode} mode.")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error obtaining certificate: {e}[/bold red]")
            logging.error(f"Error obtaining certificate for {domain}: {e}")
            exit(4)

def confirm_action(action):
    return Prompt.ask(f"[bold yellow]Are you sure you want to {action}? (yes/no)[/bold yellow]").lower() == "yes"

def show_help():
  
    console.print(Text("Help - Let's Encrypt Certificate Automation", style="bold magenta"))
    console.print("""
This script automates the installation and configuration of Let's Encrypt digital certificates on both Linux and Windows environments.

Usage:
- Follow the prompts to enter your domain and email address.
- Confirm actions when prompted.
- Ensure you have administrative privileges to install packages.

For more information, visit: https://certbot.eff.org/
""")

def main():
    console.print(Text("Let's Encrypt Certificate Automation", style="bold magenta"))

    if Prompt.ask("[bold yellow]Do you need help? (yes/no)[/bold yellow]").lower() == "yes":
        show_help()
        exit(0)

    if not is_supported_os():
        console.print("[bold red]Unsupported operating system.[/bold red]")
        logging.error("Unsupported operating system.")
        exit(1)

    check_dependencies()

    if not confirm_action("proceed with the installation of Certbot"):
        console.print("[bold red]Installation aborted by user.[/bold red]")
        exit(0)

    install_certbot()

    while True:
        domain = Prompt.ask("Enter your domain name (e.g., example.com)")
        email = Prompt.ask("Enter your email address for notifications")

        if validate_input(domain, email):
            break 
        else:
            console.print("[bold yellow]Please try entering your details again.[/bold yellow]")

    mode = Prompt.ask("[bold cyan]Choose the mode for obtaining the certificate (nginx/standalone)[/bold cyan]")
    while mode not in ["nginx", "standalone"]:
        console.print("[bold red]Invalid mode selected. Please choose either 'nginx' or 'standalone'.[/bold red]")
        mode = Prompt.ask("[bold cyan]Choose the mode for obtaining the certificate (nginx/standalone)[/bold cyan]")

    if not confirm_action(f"obtain a certificate for {domain} using {mode} mode"):
        console.print("[bold red]Certificate request aborted by user.[/bold red]")
        exit(0)

    obtain_certificate(domain, email, mode)

    console.print("[bold green]Setup complete! Your SSL certificate is ready to use.[/bold green]")
    logging.info("Setup complete. SSL certificate is ready to use.")

if __name__ == "__main__":
    main()
