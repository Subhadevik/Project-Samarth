#!/usr/bin/env python3
"""
Project Samarth Deployment Script
Automated deployment to various platforms
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step):
    """Print formatted step"""
    print(f"\n📝 {step}")
    print("-" * 40)

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"▶️  {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success: {result.stdout.strip()}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip()}")
        return False, e.stderr

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_step("Checking Prerequisites")
    
    checks = [
        ("python --version", "Python installation"),
        ("pip --version", "Pip installation"),
        ("git --version", "Git installation")
    ]
    
    all_good = True
    for command, description in checks:
        success, output = run_command(command, f"Checking {description}")
        if not success:
            all_good = False
    
    # Check if required files exist
    required_files = [
        "requirements.txt",
        "Procfile",
        "backend/main.py",
        "frontend/index.html"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ Found: {file}")
        else:
            print(f"   ❌ Missing: {file}")
            all_good = False
    
    return all_good

def deploy_local():
    """Deploy locally for testing"""
    print_header("Local Deployment")
    
    print_step("Installing Dependencies")
    run_command("pip install -r requirements.txt", "Installing Python packages")
    
    print_step("Starting Local Server")
    print("🌍 Starting Project Samarth locally...")
    print("   Access at: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    
    os.chdir("backend")
    os.system("python main.py")

def deploy_docker():
    """Deploy using Docker"""
    print_header("Docker Deployment")
    
    print_step("Building Docker Image")
    success, _ = run_command("docker build -t project-samarth .", "Building Docker image")
    if not success:
        return False
    
    print_step("Starting Docker Container")
    success, _ = run_command(
        "docker run -d -p 5000:5000 --name samarth-container project-samarth",
        "Starting container"
    )
    if not success:
        return False
    
    print("🌍 Project Samarth is running in Docker!")
    print("   Access at: http://localhost:5000")
    print("   Stop with: docker stop samarth-container")
    return True

def deploy_docker_compose():
    """Deploy using Docker Compose"""
    print_header("Docker Compose Deployment")
    
    print_step("Starting Services")
    success, _ = run_command("docker-compose up -d", "Starting all services")
    if not success:
        return False
    
    print("🌍 Project Samarth is running with Docker Compose!")
    print("   Access at: http://localhost")
    print("   View logs: docker-compose logs -f")
    print("   Stop with: docker-compose down")
    return True

def deploy_heroku():
    """Deploy to Heroku"""
    print_header("Heroku Deployment")
    
    # Check if git repo exists
    if not os.path.exists('.git'):
        print_step("Initializing Git Repository")
        run_command("git init", "Initializing git")
        run_command("git add .", "Adding files")
        run_command('git commit -m "Initial commit for Heroku"', "Initial commit")
    
    print_step("Creating Heroku App")
    app_name = f"project-samarth-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    success, output = run_command(f"heroku create {app_name}", "Creating Heroku app")
    if not success:
        return False
    
    print_step("Deploying to Heroku")
    success, _ = run_command("git push heroku main", "Pushing to Heroku")
    if not success:
        # Try master branch
        success, _ = run_command("git push heroku master", "Pushing to Heroku (master)")
    
    if success:
        print(f"🌍 Project Samarth deployed to Heroku!")
        print(f"   URL: https://{app_name}.herokuapp.com")
        run_command("heroku open", "Opening app in browser")
        return True
    return False

def deploy_railway():
    """Deploy to Railway"""
    print_header("Railway Deployment")
    
    print_step("Initializing Railway Project")
    success, _ = run_command("railway login", "Logging into Railway")
    if not success:
        print("   Please install Railway CLI: npm install -g @railway/cli")
        return False
    
    success, _ = run_command("railway init", "Initializing project")
    if not success:
        return False
    
    print_step("Deploying to Railway")
    success, output = run_command("railway up", "Deploying to Railway")
    if success:
        print("🌍 Project Samarth deployed to Railway!")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Deploy Project Samarth")
    parser.add_argument(
        "platform",
        choices=["local", "docker", "docker-compose", "heroku", "railway"],
        help="Deployment platform"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip prerequisite checks"
    )
    
    args = parser.parse_args()
    
    print_header("Project Samarth Deployment Tool")
    print("🇮🇳 Intelligent Agricultural Q&A System")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    if not args.skip_checks:
        if not check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above.")
            sys.exit(1)
        print("\n✅ All prerequisites met!")
    
    # Deploy based on platform
    deployment_functions = {
        "local": deploy_local,
        "docker": deploy_docker,
        "docker-compose": deploy_docker_compose,
        "heroku": deploy_heroku,
        "railway": deploy_railway
    }
    
    success = deployment_functions[args.platform]()
    
    if success and args.platform != "local":
        print_header("Deployment Complete!")
        print("✅ Project Samarth has been successfully deployed!")
        print("\n📊 Features available:")
        print("   • Natural language agricultural queries")
        print("   • Real-time data from data.gov.in")
        print("   • Interactive visualizations")
        print("   • Complete data traceability")
        print("   • High-performance caching")
    elif args.platform == "local":
        pass  # Local deployment handles its own messaging
    else:
        print("\n❌ Deployment failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        sys.exit(1)