# PowerShell script to build and run the MCP Server Notebook application with AI Agent and Web Interface
# Usage: .\run-app.ps1 [build|run|restart|stop|logs|clean]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "run", "restart", "stop", "logs", "clean", "help")]
    [string]$Action = "run"
)

# Configuration
$ComposeProjectName = "mcp-notebook-stack"

function Show-Help {
    Write-Host "MCP Server Notebook Stack Docker Management Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run-app.ps1 [action]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  build    - Build all Docker images" -ForegroundColor White
    Write-Host "  run      - Build and run all containers (default)" -ForegroundColor White
    Write-Host "  restart  - Stop and restart all containers" -ForegroundColor White
    Write-Host "  stop     - Stop all running containers" -ForegroundColor White
    Write-Host "  logs     - Show logs from all containers" -ForegroundColor White
    Write-Host "  clean    - Stop all containers and remove images" -ForegroundColor White
    Write-Host "  help     - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Cyan
    Write-Host "  - MCP Server (port 9002)" -ForegroundColor White
    Write-Host "  - AI Agent (port 9001)" -ForegroundColor White
    Write-Host "  - Web Interface (port 9003)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\run-app.ps1                # Build and run all services" -ForegroundColor Gray
    Write-Host "  .\run-app.ps1 build          # Just build all images" -ForegroundColor Gray
    Write-Host "  .\run-app.ps1 logs           # View logs from all services" -ForegroundColor Gray
}

function Test-DockerInstalled {
    try {
        $null = docker --version
        return $true
    }
    catch {
        Write-Host "Error: Docker is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
}

function Test-DockerComposeInstalled {
    try {
        $null = docker-compose --version
        return $true
    }
    catch {
        Write-Host "Error: Docker Compose is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Docker Compose" -ForegroundColor Yellow
        return $false
    }
}

function Test-DockerRunning {
    try {
        $null = docker info 2>$null
        return $true
    }
    catch {
        Write-Host "Error: Docker is not running" -ForegroundColor Red
        Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
        return $false
    }
}

function Build-Images {
    Write-Host "Building all Docker images..." -ForegroundColor Green
    Write-Host "This may take a while. Showing build progress..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check if docker-compose.yml exists
    if (!(Test-Path "docker-compose.yml")) {
        Write-Host "Error: docker-compose.yml not found in current directory" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Running: docker-compose -p $ComposeProjectName build" -ForegroundColor Blue
    
    try {
        # Execute the command with real-time output
        $process = Start-Process -FilePath "docker-compose" -ArgumentList "-p", $ComposeProjectName, "build" -NoNewWindow -PassThru -Wait
        
        if ($process.ExitCode -ne 0) {
            Write-Host ""
            Write-Host "Failed to build images (Exit code: $($process.ExitCode))" -ForegroundColor Red
            return $false
        }
        else {
            Write-Host ""
            Write-Host "All images built successfully!" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "Error building images: $_" -ForegroundColor Red
        return $false
    }
}

function Stop-Containers {
    Write-Host "Stopping all containers..." -ForegroundColor Yellow
    
    Write-Host "Running: docker-compose -p $ComposeProjectName down" -ForegroundColor Blue
    
    try {
        # Execute the command with real-time output
        $process = Start-Process -FilePath "docker-compose" -ArgumentList "-p", $ComposeProjectName, "down" -NoNewWindow -PassThru -Wait
        
        if ($process.ExitCode -ne 0) {
            Write-Host "Error stopping containers (Exit code: $($process.ExitCode))" -ForegroundColor Red
        }
        else {
            Write-Host "All containers stopped successfully" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Error stopping containers: $_" -ForegroundColor Red
    }
}

function Start-Containers {
    Write-Host "Starting all containers..." -ForegroundColor Green
    
    Write-Host "Running: docker-compose -p $ComposeProjectName up -d" -ForegroundColor Blue
    
    try {
        # Execute the command with real-time output
        $process = Start-Process -FilePath "docker-compose" -ArgumentList "-p", $ComposeProjectName, "up", "-d" -NoNewWindow -PassThru -Wait
        
        if ($process.ExitCode -ne 0) {
            Write-Host "Failed to start containers (Exit code: $($process.ExitCode))" -ForegroundColor Red
            return $false
        }
        else {
            Write-Host "All containers started successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Services are now running:" -ForegroundColor Green
            Write-Host "  🌐 Web Interface: http://localhost:9003" -ForegroundColor Cyan
            Write-Host "  🤖 AI Agent API:  http://localhost:9001" -ForegroundColor Cyan
            Write-Host "  📔 MCP Server:    http://localhost:9002" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Useful commands:" -ForegroundColor Yellow
            Write-Host "  .\run-app.ps1 logs    - View logs from all services" -ForegroundColor White
            Write-Host "  .\run-app.ps1 stop    - Stop all containers" -ForegroundColor White
            return $true
        }
    }
    catch {
        Write-Host "Error starting containers: $_" -ForegroundColor Red
        return $false
    }
}

function Show-Logs {
    Write-Host "Showing logs for all containers..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to exit log view" -ForegroundColor Yellow
    Write-Host ""
    docker-compose -p $ComposeProjectName logs -f
}

function Clean-All {
    Write-Host "Cleaning up all Docker resources..." -ForegroundColor Yellow
    
    # Stop and remove containers
    try {
        docker-compose -p $ComposeProjectName down --rmi all --volumes
        Write-Host "All containers and images removed" -ForegroundColor Green
    }
    catch {
        Write-Host "Error during cleanup: $_" -ForegroundColor Red
    }
    
    Write-Host "Cleanup completed" -ForegroundColor Green
}

# Main script logic
Write-Host "MCP Notebook Stack Docker Manager" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

if ($Action -eq "help") {
    Show-Help
    exit 0
}

# Check prerequisites
if (!(Test-DockerInstalled)) {
    exit 1
}

if (!(Test-DockerComposeInstalled)) {
    exit 1
}

if (!(Test-DockerRunning)) {
    exit 1
}

# Execute the requested action
switch ($Action) {
    "build" {
        if (Build-Images) {
            Write-Host "Build completed successfully!" -ForegroundColor Green
        } else {
            exit 1
        }
    }
    
    "run" {
        Stop-Containers
        if (Build-Images) {
            if (Start-Containers) {
                Write-Host "All services are running!" -ForegroundColor Green
            } else {
                exit 1
            }
        } else {
            exit 1
        }
    }
    
    "restart" {
        Stop-Containers
        if (Start-Containers) {
            Write-Host "All services restarted!" -ForegroundColor Green
        } else {
            exit 1
        }
    }
    
    "stop" {
        Stop-Containers
    }
    
    "logs" {
        Show-Logs
    }
    
    "clean" {
        Clean-All
    }
    
    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
