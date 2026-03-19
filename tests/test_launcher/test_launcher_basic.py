import os

import pytest

from launcher import create_window


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="No display")
def test_launcher_launches(config_path_testing_fresh_func):
    window = create_window(testing=True)
    assert window is not None
    window.quit()