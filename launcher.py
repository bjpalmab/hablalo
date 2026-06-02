#!/usr/bin/env python3
"""
Launcher script for hablalo
Automatically checks prerequisites, downloads models, and runs the application
"""

import os
import sys
import subprocess
import json
import argparse

# Available models from whisper.cpp
AVAILABLE_MODELS = {
    "tiny": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
        "size": "75 MB",
        "description": "Fastest, least accurate"
    },
    "base": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
        "size": "142 MB",
        "description": "Good balance of speed and accuracy"
    },
    "small": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
        "size": "466 MB",
        "description": "More accurate, slower"
    },
    "medium": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
        "size": "1.5 GB",
        "description": "Very accurate, quite slow"
    },
    "large-v3": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
        "size": "3.1 GB",
        "description": "Most accurate, slowest"
    }
}


def check_python():
    """Check if Python is installed and version"""
    print("🔍 Checking Python installation...")
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    except Exception as e:
        print(f"❌ Error checking Python: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python dependencies...")
    required = ["sounddevice", "numpy", "keyboard"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not found")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        response = input("Install missing packages now? (y/n): ").strip().lower()
        if response == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✓ Dependencies installed successfully")
                return True
            except Exception as e:
                print(f"❌ Error installing dependencies: {e}")
                return False
        else:
            print("⚠️  Please install dependencies manually: pip install -r requirements.txt")
            return False
    
    print("✓ All dependencies installed")
    return True


def check_whisper_executable():
    """Check if whisper.cpp executable exists"""
    print("\n🔍 Checking whisper.cpp executable...")
    
    # Check common locations
    locations = ["./main", "./main.exe", "../main", "../main.exe"]
    
    for loc in locations:
        if os.path.exists(loc):
            print(f"✓ Found whisper.cpp at {loc}")
            return True
    
    print("❌ whisper.cpp executable not found")
    print("\nTo compile whisper.cpp:")
    print("1. Clone the repository: git clone https://github.com/ggerganov/whisper.cpp.git")
    print("2. Navigate to the folder: cd whisper.cpp")
    print("3. Compile: make (Linux/Mac) or follow Windows instructions in README.md")
    print("4. Copy the 'main' executable to this folder")
    
    response = input("\nDo you want to clone and compile whisper.cpp now? (y/n): ").strip().lower()
    if response == 'y':
        return clone_whisper_cpp()
    
    return False


def clone_whisper_cpp():
    """Clone and compile whisper.cpp"""
    print("\n📦 Cloning whisper.cpp repository...")
    
    try:
        # Clone repository
        result = subprocess.run(
            ["git", "clone", "https://github.com/ggerganov/whisper.cpp.git"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Error cloning: {result.stderr}")
            return False
        
        print("✓ Repository cloned")
        
        # Try to compile (this works on Linux/Mac, Windows needs different approach)
        print("\n🔨 Attempting to compile whisper.cpp...")
        os.chdir("whisper.cpp")
        
        result = subprocess.run(["make"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ whisper.cpp compiled successfully")
            # Copy executable to parent directory
            import shutil
            if os.path.exists("main"):
                shutil.copy("main", "../main")
                print("✓ Executable copied to project root")
            os.chdir("..")
            return True
        else:
            print(f"⚠️  Compilation failed: {result.stderr}")
            print("\nFor Windows, please follow manual compilation instructions:")
            print("1. Install Visual Studio Build Tools or Visual Studio Community")
            print("2. Open whisper.cpp folder in Visual Studio")
            print("3. Build the solution")
            print("4. Copy main.exe to this folder")
            os.chdir("..")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists("whisper.cpp"):
            os.chdir("..")
        return False


def check_models():
    """Check if whisper models exist"""
    print("\n🔍 Checking whisper models...")
    
    models_dir = "./models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"✓ Created models directory: {models_dir}")
    
    # Check for existing models
    existing_models = [f for f in os.listdir(models_dir) if f.endswith(".bin")]
    
    if existing_models:
        print(f"✓ Found {len(existing_models)} model(s): {', '.join(existing_models)}")
        return True
    
    print("❌ No models found in ./models/")
    print("\nAvailable models:")
    for name, info in AVAILABLE_MODELS.items():
        print(f"  • {name}: {info['size']} - {info['description']}")
    
    response = input("\nDownload a model now? (y/n): ").strip().lower()
    if response == 'y':
        return download_model()
    
    return False


def download_model(model_name=None):
    """Download a whisper model"""
    if not model_name:
        print("\nSelect a model to download:")
        models = list(AVAILABLE_MODELS.keys())
        for i, name in enumerate(models, 1):
            info = AVAILABLE_MODELS[name]
            print(f"  {i}. {name} ({info['size']}) - {info['description']}")
        
        try:
            choice = input("\nEnter model number (or name): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    model_name = models[idx]
                else:
                    print("❌ Invalid choice")
                    return False
            elif choice in AVAILABLE_MODELS:
                model_name = choice
            else:
                print("❌ Invalid model name")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    if model_name not in AVAILABLE_MODELS:
        print(f"❌ Unknown model: {model_name}")
        return False
    
    model_info = AVAILABLE_MODELS[model_name]
    filename = f"ggml-{model_name}.bin" if not model_name.startswith("ggml-") else f"{model_name}.bin"
    filepath = f"./models/{filename}"
    
    print(f"\n📥 Downloading {model_name} model ({model_info['size']})...")
    print(f"   URL: {model_info['url']}")
    print(f"   Destination: {filepath}")
    
    try:
        import urllib.request
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            print(f"\r   Progress: {percent:.1f}% ({downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB)", end="")
        
        urllib.request.urlretrieve(
            model_info["url"],
            filepath,
            reporthook=report_progress
        )
        
        print(f"\n✓ Model downloaded successfully: {filepath}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        print("\nAlternative: Download manually from:")
        print(f"  {model_info['url']}")
        print(f"Save as: {filepath}")
        return False


def load_config():
    """Load or create configuration"""
    config_file = "config.json"
    
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"✓ Loaded configuration from {config_file}")
            return config
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
    
    # Create default config
    print("ℹ️  Creating default configuration...")
    config = {
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_duration": 3,
            "device_id": None,
            "silence_threshold": 0.01,
            "silence_duration": 1.5
        },
        "whisper": {
            "executable": "./main",
            "model": "./models/ggml-base.bin",
            "language": "auto",
            "threads": 8,
            "no_timestamps": True
        },
        "output": {
            "log_file": "transcriptions.txt",
            "save_chunks": False,
            "output_format": "txt",
            "show_visualization": True
        },
        "performance": {
            "timeout_seconds": 60,
            "queue_size": 10,
            "process_threads": 2
        },
        "logging": {
            "verbose": True,
            "show_devices": True,
            "timestamps": True
        }
    }
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"✓ Created {config_file}")
        return config
    except Exception as e:
        print(f"❌ Error creating config: {e}")
        return None


def run_app(args):
    """Run the main application"""
    print("\n🚀 Starting application...")
    
    cmd = [sys.executable, "main.py"]
    
    if args.get("config"):
        cmd.extend(["--config", args["config"]])
    if args.get("device") is not None:
        cmd.extend(["--device", str(args["device"])])
    if args.get("language"):
        cmd.extend(["--language", args["language"]])
    if args.get("model"):
        cmd.extend(["--model", args["model"]])
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✓ Application stopped")
    except Exception as e:
        print(f"❌ Error running application: {e}")


def interactive_setup():
    """Interactive setup wizard"""
    print("=" * 60)
    print("🎙️  hablalo - Interactive Setup Wizard")
    print("=" * 60)
    
    config = {}
    
    # Language selection
    print("\n🌐 Select language:")
    languages = ["auto", "es", "en", "fr", "de", "it"]
    for i, lang in enumerate(languages, 1):
        names = {"auto": "Auto-detect", "es": "Spanish", "en": "English", 
                "fr": "French", "de": "German", "it": "Italian"}
        print(f"  {i}. {names[lang]} ({lang})")
    
    try:
        choice = input("\nEnter language number (or code): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(languages):
                config["language"] = languages[idx]
        elif choice in languages:
            config["language"] = choice
        else:
            config["language"] = "auto"
    except:
        config["language"] = "auto"
    
    print(f"✓ Language set to: {config['language']}")
    
    return config


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(description="Launcher for hablalo speech-to-text app")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    parser.add_argument("--download-model", choices=list(AVAILABLE_MODELS.keys()), help="Download specific model")
    parser.add_argument("--check", action="store_true", help="Only check prerequisites")
    parser.add_argument("--config", help="Use specific config file")
    parser.add_argument("--device", type=int, help="Audio device ID")
    parser.add_argument("--language", choices=["auto", "es", "en", "fr", "de", "it"], help="Language code")
    parser.add_argument("--model", help="Path to whisper model")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎙️  hablalo - Speech-to-Text Launcher")
    print("=" * 60)
    
    # Run interactive setup if requested
    if args.setup:
        interactive_setup()
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check whisper executable
    has_executable = check_whisper_executable()
    
    # Check/download models
    if args.download_model:
        download_model(args.download_model)
    else:
        check_models()
    
    # Load/create config
    config = load_config()
    
    if args.check:
        print("\n✅ Prerequisites check complete!")
        if has_executable and config:
            print("✓ Ready to run!")
            print("\nRun with: python launcher.py")
        else:
            print("⚠️  Some components are missing. Complete the setup first.")
        sys.exit(0)
    
    # Run application
    run_app(vars(args))


if __name__ == "__main__":
    main()
