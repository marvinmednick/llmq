"""
Main entry point for the LLM Query tool using LangChain.
"""

import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from llmq.cli import parse_args
from llmq.pipeline import execute_pipeline, validate_pipeline

# Load environment variables
load_dotenv()


def setup_logging(log_level: str):
    logger.remove()
    logger.add("logs/llmq.log", rotation="10 MB", level=log_level)
    logger.add(
        sys.stderr,
        level="WARNING",
        format="<yellow>{time:HH:mm:ss}</yellow> | <level>{level: <8}</level> | <level>{message}</level>",
    )


def main():
    """Main entry point for the application."""
    config = parse_args()

    # Setup logging
    setup_logging(config.log_level)

    try:
        # Validate pipeline if requested
        if config.check_config:
            print("Validating pipeline configuration...")
            errors = validate_pipeline(config)
            if errors:
                print("Validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
            print("Validation successful.")
            return 0

        # Execute pipeline
        outputs = execute_pipeline(config)

        # Get the final output (from the last step)
        final_output_key = config.pipeline.steps[-1].output_key
        final_output = outputs[final_output_key]

        # Save or print the final result
        if config.output_file:
            output_path = Path(config.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_output)
            print(f"Response saved to {config.output_file}")
        else:
            print("\nLLM Response:")
            print("-" * 40)
            print(final_output)
            print("-" * 40)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        logger.exception(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
