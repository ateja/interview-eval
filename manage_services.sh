#!/bin/bash

# Configuration
VENV_PATH="$(pwd)"  # Use current directory since venv is in ./bin/activate
SERVICES=(
    "ws_vsearch.py"
    "ws_prompt_renderer.py"
    "ws_pdf_to_json.py"
    "ws_interview_copilot.py"
)
LOG_DIR="logs"
PID_DIR="pids"
LOG_FILE="$LOG_DIR/services.log"  # Single log file for all services

# Create log and pid directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a package is installed
check_package() {
    local package=$1
    
    # Handle special cases
    case $package in
        "faiss-cpu")
            package="faiss-cpu"
            ;;
        "sentence-transformers")
            package="sentence-transformers"
            ;;
        *)
            # Remove version specifications if present
            package=$(echo $package | cut -d'=' -f1)
            ;;
    esac
    
    if ! source "$VENV_PATH/bin/activate" && $VENV_PATH/bin/pip show "$package" >/dev/null 2>&1; then
        echo "Checking package: $package"
        return 1
    fi
    return 0
}

# Function to verify environment setup
verify_environment() {
    echo "Checking virtual environment at: $VENV_PATH"
    
    # Check if virtual environment exists
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
        echo "Please set up your virtual environment first."
        exit 1
    fi
    
    # Check required packages
    local missing_packages=()
    while IFS= read -r package; do
        if [ -n "$package" ] && [[ ! "$package" =~ ^# ]]; then
            if ! check_package "$package"; then
                missing_packages+=("$package")
            fi
        fi
    done < requirements.txt
    
    if [ ${#missing_packages[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required packages. Please install them first:${NC}"
        echo "Run: $VENV_PATH/bin/pip install -r requirements.txt"
        echo -e "${RED}Missing packages:${NC}"
        printf '%s\n' "${missing_packages[@]}"
        exit 1
    fi
}

# Function to start a service
start_service() {
    local service=$1
    local pid_file="$PID_DIR/${service%.py}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null; then
            echo -e "${YELLOW}$service is already running (PID: $pid)${NC}"
            return
        fi
    fi
    
    echo -e "${GREEN}Starting $service...${NC}"
    echo "[$(date)] Starting $service" >> "$LOG_FILE"
    # Use bash -c to properly handle source and environment variables
    bash -c "source $VENV_PATH/bin/activate && python3 $service" < /dev/null >> "$LOG_FILE" 2>&1 &
    echo $! > "$pid_file"
    sleep 2
    if ps -p $(cat "$pid_file") > /dev/null; then
        echo -e "${GREEN}$service started successfully (PID: $(cat "$pid_file"))${NC}"
        echo "[$(date)] $service started successfully (PID: $(cat "$pid_file"))" >> "$LOG_FILE"
    else
        echo -e "${RED}Failed to start $service. Check logs at $LOG_FILE${NC}"
        echo "[$(date)] Failed to start $service" >> "$LOG_FILE"
    fi
}

# Function to stop a service
stop_service() {
    local service=$1
    local pid_file="$PID_DIR/${service%.py}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null; then
            echo -e "${YELLOW}Stopping $service (PID: $pid)...${NC}"
            echo "[$(date)] Stopping $service (PID: $pid)" >> "$LOG_FILE"
            kill "$pid"
            rm "$pid_file"
            echo -e "${GREEN}$service stopped${NC}"
            echo "[$(date)] $service stopped" >> "$LOG_FILE"
        else
            echo -e "${YELLOW}$service is not running${NC}"
            rm "$pid_file"
        fi
    else
        echo -e "${YELLOW}$service is not running${NC}"
    fi
}

# Function to check service status
check_status() {
    local service=$1
    local pid_file="$PID_DIR/${service%.py}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null; then
            echo -e "${GREEN}$service is running (PID: $pid)${NC}"
        else
            echo -e "${RED}$service is not running (stale PID file)${NC}"
        fi
    else
        echo -e "${RED}$service is not running${NC}"
    fi
}

# Function to tail logs
tail_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${GREEN}Tailing logs for all services...${NC}"
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}No log file found${NC}"
    fi
}

# Main script logic
case "$1" in
    "start")
        verify_environment
        if [ $# -gt 1 ]; then
            # Start specific services provided as arguments
            shift  # Remove the first argument (start)
            for service in "$@"; do
                # Check if the service exists in the SERVICES array
                if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
                    start_service "$service"
                else
                    echo -e "${RED}Error: $service is not a valid service${NC}"
                    echo "Available services: ${SERVICES[@]}"
                fi
            done
        else
            # Start all services if no specific service is provided
            for service in "${SERVICES[@]}"; do
                start_service "$service"
            done
        fi
        ;;
    "stop")
        if [ $# -gt 1 ]; then
            # Stop specific services provided as arguments
            shift  # Remove the first argument (stop)
            for service in "$@"; do
                if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
                    stop_service "$service"
                else
                    echo -e "${RED}Error: $service is not a valid service${NC}"
                    echo "Available services: ${SERVICES[@]}"
                fi
            done
        else
            # Stop all services if no specific service is provided
            for service in "${SERVICES[@]}"; do
                stop_service "$service"
            done
        fi
        ;;
    "restart")
        verify_environment
        if [ $# -gt 1 ]; then
            # Restart specific services provided as arguments
            shift  # Remove the first argument (restart)
            for service in "$@"; do
                if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
                    stop_service "$service"
                    sleep 2
                    start_service "$service"
                else
                    echo -e "${RED}Error: $service is not a valid service${NC}"
                    echo "Available services: ${SERVICES[@]}"
                fi
            done
        else
            # Restart all services if no specific service is provided
            for service in "${SERVICES[@]}"; do
                stop_service "$service"
                sleep 2
                start_service "$service"
            done
        fi
        ;;
    "status")
        verify_environment
        if [ $# -gt 1 ]; then
            # Check status of specific services provided as arguments
            shift  # Remove the first argument (status)
            for service in "$@"; do
                if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
                    check_status "$service"
                else
                    echo -e "${RED}Error: $service is not a valid service${NC}"
                    echo "Available services: ${SERVICES[@]}"
                fi
            done
        else
            # Check status of all services if no specific service is provided
            for service in "${SERVICES[@]}"; do
                check_status "$service"
            done
        fi
        ;;
    "logs")
        tail_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac 