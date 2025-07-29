"""Base functionality for MetricFlow tools."""

import os
import subprocess  # nosec B404

from config.config import MfCliConfig
from utils.logger import logger


def run_mf_command(command: list[str], config: MfCliConfig) -> tuple[str, str]:
    """Execute a MetricFlow command.

    Args:
        command: List of command arguments to pass to mf
        config: Configuration containing paths and settings

    Returns:
        Tuple of (stdout, stderr) from the command execution
    """
    # Commands that should always be quiet to reduce output verbosity
    verbose_commands = ["query"]

    full_command = command.copy()
    # Add --quiet flag to specific commands to reduce context window usage
    if len(full_command) > 0 and full_command[0] in verbose_commands:
        main_command = full_command[0]
        command_args = full_command[1:] if len(full_command) > 1 else []
        full_command = [main_command, "--quiet", *command_args]

    # Log the full command that will be executed
    full_command_str = f"{config.mf_path} {' '.join(full_command)}"
    logger.info("=" * 60)
    logger.info("Executing MetricFlow command:")
    logger.info(f"  Command: {full_command_str}")
    logger.info(f"  Working Dir: {config.project_dir}")
    logger.info(f"  Profiles Dir: {config.profiles_dir}")
    logger.info("=" * 60)

    # Set up environment with DBT_PROFILES_DIR
    mf_env = os.environ.copy()
    mf_env["DBT_PROFILES_DIR"] = config.profiles_dir
    logger.debug(mf_env)

    process = subprocess.Popen(  # nosec B603
        args=[config.mf_path, *full_command],
        cwd=config.project_dir,
        env=mf_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    stdout, err = process.communicate()

    # Log the return code
    if process.returncode == 0:
        logger.info(f"✓ Command completed successfully (exit code: {process.returncode})")
    else:
        logger.error(f"✗ Command failed (exit code: {process.returncode})")
        logger.error(f"ERR: {err} | {stdout}")

    return stdout, err
