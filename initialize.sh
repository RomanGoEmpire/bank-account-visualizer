#!/bin/bash
REQUIRED_PYTHON_VERSION=3.12


to_green() {
    echo -e "\e[32m$1\e[0m"
}

to_yellow() {
    echo -e "\e[33m$1\e[0m"
}

to_red() {
    echo -e "\e[31m$1\e[0m"
}  

is_pyenv_installed() {
    if command -v pyenv >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

is_correct_python_version_installed() {
    if pyenv versions --bare | grep -q "^$REQUIRED_PYTHON_VERSION"; then
        return 0
    else
        return 1
    fi
}

install_python() {
    to_green "Installing Python $REQUIRED_PYTHON_VERSION"
    pyenv install "$REQUIRED_PYTHON_VERSION" || { echo "pyenv install failed"; exit 1; }
    pyenv global "$REQUIRED_PYTHON_VERSION"
    to_green "Python $REQUIRED_PYTHON_VERSION is installed"
}

install_pyenv() {
    #check if brew is installed
    if  command -v brew >/dev/null 2>&1; then
        to_green "Using brew to install pyenv"
        brew update
        brew install pyenv
    else
        to_yellow "brew is not available. Installing pyenv using curl"
        curl https://pyenv.run | bash
    fi
    
}

check_python_version() {
  local py_version=$(python --version 2>&1 | cut -d' ' -f2)
  local major_minor_version=$(echo "$py_version" | cut -d'.' -f1,2)
 
  if [ "$major_minor_version" = "$REQUIRED_PYTHON_VERSION" ]; then
    return 0
  else
    return 1
  fi
}


venv_exists() {
    if [ -d "venv" ]; then
        return 0
    else
        return 1
    fi
}

create_venv() {
    to_green "Creating venv"
    python3 -m venv venv
}

activate_venv() {
    to_green "Activating venv"
    source venv/bin/activate
}

install_requirements() {
    to_green "Installing requirements"
    pip install -r requirements.txt 
}

create_env_file() {
    if [ ! -f ".env" ]; then
        to_green "Creating .env file"
        touch .env
    else
        to_green ".env file already exists"
    fi
}

main() {

    # Install pyenv if it is not installed
    if ! is_pyenv_installed; then
        to_yellow "pyenv is not installed"
        install_pyenv
    else
        to_green "pyenv is already installed"
    fi

    # Install Python if it is not installed
    if ! is_correct_python_version_installed; then
        to_red "Python $REQUIRED_PYTHON_VERSION is not installed"
        install_python
    else
        to_green "Python $REQUIRED_PYTHON_VERSION is already installed"
    fi
    
    if check_python_version;then
        to_green "Python version is activated"
    else
        to_red "Incorrect Python version is active. Change it to $REQUIRED_PYTHON_VERSION"
        py --version

        return
    fi

    if ! venv_exists; then
        to_yellow "venv is not installed"
            create_venv
    fi

    activate_venv
    install_requirements
    create_env_file

    pyenv versions
}

main

