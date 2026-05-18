import time
import os
from nexa.commands.django.generate import handle as generate_handler
from nexa.core.runtime.logger import logger

def handle(args):
    """
    Watch mode for Nexa. Monitors nexa.yaml and regenerates on change.
    """
    schema_file = "nexa.yaml"
    if not os.path.exists(schema_file):
        logger.error(f"Cannot start dev mode: {schema_file} not found.")
        return

    logger.step("Nexa Dev: Watch mode started...")
    logger.info(f"Monitoring {schema_file} for changes...")

    last_mtime = os.path.getmtime(schema_file)
    
    # Initial generation
    generate_handler(args)

    try:
        while True:
            current_mtime = os.path.getmtime(schema_file)
            if current_mtime != last_mtime:
                logger.step("Change detected in nexa.yaml! Regenerating...")
                try:
                    generate_handler(args)
                    logger.success("Auto-regeneration complete.")
                except Exception as e:
                    logger.error(f"Regeneration failed: {str(e)}")
                
                last_mtime = current_mtime
            
            time.sleep(1) # Poll every second
    except KeyboardInterrupt:
        logger.info("\nStopping Nexa Dev mode. Goodbye!")
