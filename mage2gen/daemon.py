import time
import os
import sys
import logging
from mage2gen.config.parser import parse_and_generate
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Mage2Gen] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ConfigHandler(FileSystemEventHandler):
    """
    Watches for changes to m2g.yaml and triggers the generation process.
    """
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.config_file = "m2g.yaml"

    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        if filename == self.config_file:
            logger.info(f"⚡ Configuration change detected: {filename}")
            self.process_config(event.src_path)

    def on_created(self, event):
        self.on_modified(event)

    # [FIX] Added to handle atomic saves (vim/IDEs often do move/rename)
    def on_moved(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.dest_path)
        if filename == self.config_file:
            logger.info(f"⚡ Configuration moved/renamed: {filename}")
            self.process_config(event.dest_path)

    def process_config(self, file_path):
        """
        Triggers the YAML Interpreter.
        """
        try:
            # Small debounce/safety delay for atomic writes
            time.sleep(0.1)
            
            logger.info("Reading configuration...")
            parse_and_generate(file_path, self.output_dir)
            
        except Exception as e:
            logger.error(f"❌ Error reading config: {str(e)}")

def start_daemon():
    # 1. Output Directory (Where code is generated)
    output_dir = os.environ.get("MAGE2GEN_OUTPUT")
    
    if not output_dir:
        logger.warning("⚠️  MAGE2GEN_OUTPUT not set. Defaulting to './generated' to avoid clutter.")
        output_dir = os.path.join(os.getcwd(), "generated")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Watch Directory (Where m2g.yaml lives)
    watch_dir = os.environ.get("MAGE2GEN_WATCH_DIR", os.getcwd())
    
    logger.info(f"🚀 Mage2Gen Daemon starting...")
    logger.info(f"👀 Watching directory: {watch_dir}")
    logger.info(f"📂 Writing code to:   {output_dir}")
    logger.info(f"📄 Target file:      m2g.yaml")

    event_handler = ConfigHandler(output_dir)
    
    # [FIX] Initial Scan: Check if file exists immediately
    initial_config = os.path.join(watch_dir, "m2g.yaml")
    if os.path.exists(initial_config):
        logger.info(f"🔎 Found existing config on startup: {initial_config}")
        event_handler.process_config(initial_config)
    else:
        logger.info("ℹ️  No m2g.yaml found. Waiting for creation...")

    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping daemon...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    start_daemon()