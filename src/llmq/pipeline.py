"""
Pipeline execution for chaining multiple LLM queries.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
from loguru import logger

from llmq.services.llm_service import get_llm_chain
from llmq.cli import Config


def execute_pipeline(config: Config) -> Dict[str, str]:
    """
    Execute a pipeline of LLM queries.

    Args:
        config: Full configuration including pipeline details

    Returns:
        Dictionary of outputs from all steps
    """
    outputs = {}

    # Create intermediate directory if needed
    if config.save_intermediate:
        Path(config.intermediate_dir).mkdir(parents=True, exist_ok=True)

    for step in config.pipeline.steps:
        logger.info(f"Executing pipeline step: {step.name}")

        # Resolve variable references and load file contents
        input_variables = resolve_variables(step.variables, outputs)

        # Get LLM chain for this step
        chain = get_llm_chain(
            step.service_type or config.service_type, step.prompt_file
        )

        # Execute the chain
        print(f"Querying LLM for step: {step.name}...")
        response = chain.invoke(input_variables)

        # Store the output
        outputs[step.output_key] = response
        logger.debug(f"Step {step.name} output saved as '{step.output_key}'")

        # Save intermediate result if enabled
        if config.save_intermediate:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{step.output_key}.txt"
            filepath = Path(config.intermediate_dir) / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response)
            logger.info(f"Saved intermediate result to {filepath}")

    return outputs


def resolve_variables(
    variables: Dict[str, str], outputs: Dict[str, str]
) -> Dict[str, str]:
    """Resolve variable references and load file contents."""
    resolved = {}
    for key, value in variables.items():
        if value.startswith("$outputs."):
            output_key = value.split(".", 1)[1]
            resolved[key] = outputs.get(output_key, "")
        elif Path(value).is_file():
            with open(value, "r") as f:
                resolved[key] = f.read()
        else:
            resolved[key] = value
    return resolved


def validate_pipeline(config: Config) -> List[str]:
    """Validate a pipeline configuration."""
    errors = []
    available_outputs = set()

    for step in config.pipeline.steps:
        # Check prompt file exists
        if not Path(step.prompt_file).exists():
            errors.append(
                f"Step '{step.name}': Prompt file not found: {step.prompt_file}"
            )

        # Check variable references
        for var_name, var_value in step.variables.items():
            if var_value.startswith("$outputs."):
                output_key = var_value.split(".", 1)[1]
                if output_key not in available_outputs:
                    errors.append(
                        f"Step '{step.name}': Referenced output '{output_key}' "
                        f"is not produced by any previous step"
                    )
            elif not Path(var_value).is_file():
                # This is not necessarily an error, but we'll log a warning
                logger.warning(
                    f"Step '{step.name}': Variable '{var_name}' value '{var_value}' is not a file path"
                )

        # Add this step's output to available outputs
        available_outputs.add(step.output_key)

    return errors
