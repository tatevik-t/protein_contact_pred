import os
import logging


def setup_logging(output_dir: str) -> None:
    """Setup logging configuration."""
    os.makedirs(output_dir, exist_ok=True)

    # Configure logging
    log_file = os.path.join(output_dir, "pipeline.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


