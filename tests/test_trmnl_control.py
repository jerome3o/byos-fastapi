import tempfile

import pytest

from app.trmnl_control import TRMNLController, create_image


@pytest.fixture
def controller():
    """Create a TRMNLController with temporary directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db_file:
            yield TRMNLController(db_file.name, temp_dir)


def test_controller_create_image(controller):
    """Test creating an image through the controller."""
    filename = controller.create_image("Test content")
    assert filename is not None
    assert isinstance(filename, str)


def test_controller_create_image_with_device_id(controller):
    """Test creating an image for a specific device."""
    device_id = "AA:BB:CC:DD:EE:FF"
    filename = controller.create_image("Test content", device_id=device_id)
    assert device_id.replace(":", "") in filename or device_id in filename


def test_controller_html_image(controller):
    """Test creating an image from HTML."""
    html_content = "<h1>Test</h1><p>HTML content</p>"
    filename = controller.create_html_image(html_content)
    assert filename is not None


def test_global_create_image_function():
    """Test the global create_image function."""
    # This will use default temporary paths
    filename = create_image("Global function test")
    assert filename is not None
    assert isinstance(filename, str)


def test_controller_schedule_update(controller):
    """Test scheduling updates (without actually running them)."""

    def test_update():
        return "Scheduled update content"

    # This should not raise an exception
    controller.schedule_update(test_update, interval_minutes=1)

    # Verify that a job was scheduled
    assert len(controller.scheduled_jobs) > 0


def test_controller_scheduler_lifecycle(controller):
    """Test starting and stopping the scheduler."""
    controller.start_scheduler()
    assert controller._scheduler_running is True

    controller.stop_scheduler()
    assert controller._scheduler_running is False
    assert len(controller.scheduled_jobs) == 0
