# PowerShell script to build and run the MCP Server Notebook application
# Usage: .\run-app.ps1 [build|run|restart|stop|logs|clean]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "run", "restart", "stop", "logs", "clean", "help")]
    [string]$Action = "run"
)

# Configuration
$ImageName = "mcp-server-notebook"
$ContainerName = "mcp-server-notebook-container"
$Port = "8002"
$HostPort = "8002"

function Show-Help {
    Write-Host "MCP Server Notebook Docker Management Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\run-app.ps1 [action]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  build    - Build the Docker image" -ForegroundColor White
    Write-Host "  run      - Build and run the container (default)" -ForegroundColor White
    Write-Host "  restart  - Stop and restart the container" -ForegroundColor White
    Write-Host "  stop     - Stop the running container" -ForegroundColor White
    Write-Host "  logs     - Show container logs" -ForegroundColor White
    Write-Host "  clean    - Stop container and remove image" -ForegroundColor White
    Write-Host "  help     - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\run-app.ps1                # Build and run" -ForegroundColor Gray
    Write-Host "  .\run-app.ps1 build          # Just build the image" -ForegroundColor Gray
    Write-Host "  .\run-app.ps1 logs           # View logs" -ForegroundColor Gray
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

function Build-Image {
    Write-Host "Building Docker image: $ImageName" -ForegroundColor Green
    
    # Check if main.py exists
    if (!(Test-Path "main.py")) {
        Write-Host "Error: main.py not found in current directory" -ForegroundColor Red
        return $false
    }
    
    # Check if data_types folder exists
    if (!(Test-Path "data_types")) {
        Write-Host "Error: data_types folder not found in current directory" -ForegroundColor Red
        return $false
    }
    
    try {
        docker build -t $ImageName .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Image built successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Failed to build image" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error building image: $_" -ForegroundColor Red
        return $false
    }
}

function Stop-Container {
    $existing = docker ps -q -f name=$ContainerName
    if ($existing) {
        Write-Host "Stopping existing container..." -ForegroundColor Yellow
        docker stop $ContainerName | Out-Null
        docker rm $ContainerName | Out-Null
        Write-Host "Container stopped and removed" -ForegroundColor Green
    }
}

function Start-Container {
    Write-Host "Starting container: $ContainerName" -ForegroundColor Green
    Write-Host "Port mapping: localhost:$HostPort -> container:$Port" -ForegroundColor Cyan
    
    try {
        docker run -d --name $ContainerName -p "$HostPort`:$Port" $ImageName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Container started successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Application is running at: http://localhost:$HostPort/knowledgeMCP/" -ForegroundColor Green
            Write-Host ""
            Write-Host "Useful commands:" -ForegroundColor Cyan
            Write-Host "  .\run-app.ps1 logs    - View logs" -ForegroundColor White
            Write-Host "  .\run-app.ps1 stop    - Stop container" -ForegroundColor White
            return $true
        } else {
            Write-Host "Failed to start container" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Error starting container: $_" -ForegroundColor Red
        return $false
    }
}

function Show-Logs {
    Write-Host "Showing logs for container: $ContainerName" -ForegroundColor Green
    Write-Host "Press Ctrl+C to exit log view" -ForegroundColor Yellow
    Write-Host ""
    docker logs -f $ContainerName
}

function Clean-All {
    Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow
    
    # Stop and remove container
    Stop-Container
    
    # Remove image
    $imageExists = docker images -q $ImageName
    if ($imageExists) {
        Write-Host "Removing Docker image: $ImageName" -ForegroundColor Yellow
        docker rmi $ImageName
        Write-Host "Image removed" -ForegroundColor Green
    }
    
    Write-Host "Cleanup completed" -ForegroundColor Green
}

# Main script logic
Write-Host "MCP Server Notebook Docker Manager" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

if ($Action -eq "help") {
    Show-Help
    exit 0
}

# Check prerequisites
if (!(Test-DockerInstalled)) {
    exit 1
}

if (!(Test-DockerRunning)) {
    exit 1
}

# Execute the requested action
switch ($Action) {
    "build" {
        if (Build-Image) {
            Write-Host "Build completed successfully!" -ForegroundColor Green
        } else {
            exit 1
        }
    }
    
    "run" {
        Stop-Container
        if (Build-Image) {
            if (Start-Container) {
                Write-Host "Application is running!" -ForegroundColor Green
            } else {
                exit 1
            }
        } else {
            exit 1
        }
    }
    
    "restart" {
        Stop-Container
        if (Start-Container) {
            Write-Host "Application restarted!" -ForegroundColor Green
        } else {
            exit 1
        }
    }
    
    "stop" {
        Stop-Container
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
