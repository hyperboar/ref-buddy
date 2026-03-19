from launcher import create_window


def test_launcher_launches(config_path_testing_fresh_func):
    window = create_window(testing=True)
    assert window is not None
    window.quit()