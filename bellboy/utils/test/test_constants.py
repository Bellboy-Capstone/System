from src.utils.constants import RunLevels


class TestRunLevels:
    def test_get_names(self):
        assert len(RunLevels.get_names()) == 3
        assert "LOCAL" in RunLevels.get_names()

    def test_get_choices(self):
        assert len(RunLevels.get_choices()) == 3
        assert RunLevels.LOCAL in RunLevels.get_choices()
