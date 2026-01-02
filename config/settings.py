"""
Configuration Settings for SemEval Translation Project
======================================================
Centralized configuration management
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Data paths
ORIGINAL_DATA_DIR = DATA_DIR / "original"
TRANSLATED_DATA_DIR = DATA_DIR / "translated"
SAMPLES_DATA_DIR = DATA_DIR / "samples"

# Output paths
REPORTS_DIR = OUTPUT_DIR / "reports"
CHECKPOINTS_DIR = OUTPUT_DIR / "checkpoints"


@dataclass
class TranslationConfig:
    """Main configuration for translation system"""

    # Model settings
    model_name: str = "gemini-2.5-flash"
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    temperature: float = 0.1

    # Batch processing
    batch_size: int = 10
    requests_per_second: int = 9
    max_retries: int = 3

    # Checkpoint settings
    checkpoint_every: int = 5
    resume: bool = True

    @property
    def delay_between_requests(self) -> float:
        """Calculate delay between requests in seconds"""
        return 1.0 / self.requests_per_second


@dataclass
class DatasetConfig:
    """Dataset-specific configuration"""

    # Original dataset
    original_file: str = "clapnq.jsonl"
    sample_file: str = "clapnq_sample_500.jsonl"

    # Output files
    translated_file: str = "clapnq_translated_batch.jsonl"
    pt_br_file: str = "clapnq_pt_br.jsonl"
    comparison_file: str = "comparacao.md"

    # Processing limits
    sample_size: int = 500
    limit: int = None  # None = process all


# Default configurations
DEFAULT_TRANSLATION_CONFIG = TranslationConfig()
DEFAULT_DATASET_CONFIG = DatasetConfig()


def get_config(config_type="translation"):
    """
    Get configuration object

    Args:
        config_type: Type of config ('translation', 'dataset')

    Returns:
        Configuration object
    """
    if config_type == "translation":
        return DEFAULT_TRANSLATION_CONFIG
    elif config_type == "dataset":
        return DEFAULT_DATASET_CONFIG
    else:
        raise ValueError(f"Unknown config type: {config_type}")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        ORIGINAL_DATA_DIR,
        TRANSLATED_DATA_DIR,
        SAMPLES_DATA_DIR,
        OUTPUT_DIR,
        REPORTS_DIR,
        CHECKPOINTS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
