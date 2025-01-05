import schedule
import time
import logging
import d15p954
import d15t3pn
import d15ca4v

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_websites():
    logger.info("Starting script...")
    d15p954.parse_castleknock_dublin_anglican()
    d15t3pn.parse_castleknock_website()
    d15ca4v.parse_laurel_lodge()


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
