import schedule
import time
import logging
import importlib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_websites():
    logger.info("Starting script...")
    scripts_dir = Path(__file__).parent
    scripts = [f.stem for f in scripts_dir.glob("d15*.py") if f.stem != "schedule_extraction"]

    for module_name in scripts:
        module = importlib.import_module(module_name)
        func = getattr(module, f"parse_{module_name}")
        func()


def main():
    """Run parser on schedule."""
    logger.info("Schedule")
    parse_websites()
    schedule.every(6).hours.do(parse_websites)
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    main()
