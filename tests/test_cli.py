import os
import subprocess
import pytest
import shutil

# Assuming pipo is installed in editable mode, so its commands are available
# Or, we can call it directly via python -m pipo.pipo.main

@pytest.fixture
def temp_project_dir(tmp_path):
    """Creates a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    # Create a dummy requirements.txt for dockerize to work
    (project_dir / "requirements.txt").write_text("requests\n")
    # Create a dummy app.py for dockerize to work
    (project_dir / "app.py").write_text("print('hello')\n")
    # Create a dummy test file for pipo test to find
    test_subdir = project_dir / "tests"
    test_subdir.mkdir()
    (test_subdir / "test_dummy.py").write_text("def test_always_passes(): assert True\n")
    return project_dir

def run_pipo_command(command, cwd=None):
    """Helper to run pipo commands."""
    # Assuming pipo is installed in editable mode, so 'pipo' command is available
    # If not, use: [sys.executable, "-m", "pipo.pipo.main"]
    result = subprocess.run(
        ["pipo"] + command,
        capture_output=True,
        text=True,
        check=False, # Don't raise CalledProcessError for non-zero exit codes
        cwd=cwd
    )
    return result

def test_pipo_test_command_success(temp_project_dir):
    """Test 'pipo test' command successfully runs tests."""
    result = run_pipo_command(["test", str(temp_project_dir)])
    assert result.returncode == 0
    assert "Tests completed successfully!" in result.stdout
    assert "1 passed" in result.stdout # From the dummy test

def test_pipo_test_command_no_tests_found(tmp_path):
    """Test 'pipo test' command when no tests are found."""
    project_dir = tmp_path / "no_tests_project"
    project_dir.mkdir()
    result = run_pipo_command(["test", str(project_dir)])
    # Pytest exits with 5 if no tests are collected
    assert result.returncode == 1

def test_pipo_init_ci_command_github_actions(temp_project_dir):
    """Test 'pipo init-ci' command generates GitHub Actions config."""
    result = run_pipo_command(["init-ci", str(temp_project_dir), "--platform", "github-actions"])
    assert result.returncode == 0
    assert "CI configuration for github-actions successfully generated" in result.stdout

    ci_config_path = temp_project_dir / ".github" / "workflows" / "ci.yml"
    assert ci_config_path.exists()

    content = ci_config_path.read_text()
    assert "name: CI/CD Pipeline" in content
    assert "on:" in content
    assert "jobs:" in content
    assert "pipo test ." in content
    assert "pipo dockerize ." in content

def test_pipo_init_ci_command_with_docker_image_name(temp_project_dir):
    """Test 'pipo init-ci' command generates config with custom Docker image name."""
    custom_image_name = "my_user/my_custom_app"
    result = run_pipo_command(["init-ci", str(temp_project_dir), "--docker-image-name", custom_image_name])
    assert result.returncode == 0
    ci_config_path = temp_project_dir / ".github" / "workflows" / "ci.yml"
    content = ci_config_path.read_text()
    assert f"docker-image-name: '{custom_image_name}'" in content

def test_pipo_init_ci_command_with_push_docker_image(temp_project_dir):
    """Test 'pipo init-ci' command generates config with push-docker-image enabled."""
    result = run_pipo_command(["init-ci", str(temp_project_dir), "--push-docker-image"])
    assert result.returncode == 0
    ci_config_path = temp_project_dir / ".github" / "workflows" / "ci.yml"
    content = ci_config_path.read_text()
    assert "push-docker-image: true" in content

def test_pipo_init_ci_command_unsupported_platform(temp_project_dir):
    """Test 'pipo init-ci' command with an unsupported platform."""
    result = run_pipo_command(["init-ci", str(temp_project_dir), "--platform", "unsupported-ci"])
    assert result.returncode == 2
    assert "invalid choice: 'unsupported-ci' (choose from 'github-actions')" in result.stderr
