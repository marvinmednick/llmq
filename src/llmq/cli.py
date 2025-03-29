"""
Command line interface for the LLM Query tool.
"""

import argparse
import sys
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class StepConfig(BaseModel):
    name: str
    prompt_file: str
    variables: Dict[str, str]
    output_key: str
    service_type: Optional[str] = None


class PipelineConfig(BaseModel):
    steps: List[StepConfig]


class Config(BaseModel):
    log_level: str = "INFO"
    check_config: bool = False
    output_file: Optional[str] = None
    save_intermediate: bool = False  # New flag
    intermediate_dir: str = "intermediate_results"  # New directory config
    service_type: str = "azure_openai"
    pipeline: PipelineConfig


def load_config(config_file: str) -> Config:
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)
    return Config(**config_data)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Execute LLM queries using a configuration-based pipeline."
    )

    parser.add_argument(
        "--config", type=str, required=True, help="Path to YAML configuration file"
    )

    # Optional CLI overrides
    parser.add_argument(
        "--output",
        dest="output_file",
        type=str,
        help="Override the output file specified in the config",
    )

    parser.add_argument(
        "--check_config",
        action="store_true",
        help="Validate the configuration without executing",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Override the log level specified in the config",
    )
    #
    # Add new arguments
    parser.add_argument(
        "--save-intermediate",
        action="store_true",
        help="Save intermediate step results to files",
    )

    parser.add_argument(
        "--intermediate-dir", type=str, help="Directory for intermediate results"
    )

    args = parser.parse_args()

    # Load the configuration file
    config = load_config(args.config)

    # Override with CLI arguments if provided
    if args.output_file:
        config.output_file = args.output_file
    if args.check_config:
        config.check_config = args.check_config
    if args.log_level:
        config.log_level = args.log_level
    if args.save_intermediate:
        config.save_intermediate = True
    if args.intermediate_dir:
        config.intermediate_dir = args.intermediate_dir

    return config
