import os
import unittest
from unittest.mock import patch

from flask.testing import FlaskCliRunner

from pulse import create_app
from pulse.main import main


class ApplicationTests(unittest.TestCase):
    def test_environment_selection(self):
        for mode, debug, testing in [
            ("development", False, False),
            ("testing", False, True),
            ("production", False, False),
        ]:
            with self.subTest(mode=mode), patch.dict(os.environ, {"APP_ENV": mode}):
                app = create_app()
                self.assertEqual(app.debug, debug)
                self.assertEqual(app.testing, testing)

    def test_invalid_environment(self):
        with patch.dict(os.environ, {"APP_ENV": "unknown"}):
            with self.assertRaisesRegex(ValueError, "Unknown APP_ENV"):
                create_app()

    def test_explicit_configuration_overrides_environment(self):
        class CustomConfig:
            TESTING = True
            SECRET_KEY = "test"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

        with patch.dict(os.environ, {"APP_ENV": "unknown"}):
            app = create_app(CustomConfig)
        self.assertTrue(app.testing)
        self.assertEqual(app.config["SECRET_KEY"], "test")

    def test_cli_help_and_routes(self):
        runner = FlaskCliRunner(create_app("pulse.config.TestingConfig"))
        for args, expected in [
            (["--help"], "run"),
            (["run", "--help"], "--port"),
            (["routes"], "/questions/<int:id>"),
        ]:
            with self.subTest(args=args):
                result = runner.invoke(main, args)
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn(expected, result.output)

    def test_cli_server_options(self):
        runner = FlaskCliRunner(create_app("pulse.config.TestingConfig"))
        for debug_flag, debug in [("--debug", True), ("--no-debug", False)]:
            with self.subTest(debug=debug), patch("flask.cli.run_simple") as server:
                result = runner.invoke(
                    main,
                    ["run", debug_flag, "--host", "127.0.0.2", "--port", "8001"],
                )
                self.assertEqual(result.exit_code, 0, result.output)
                server.assert_called_once()
                self.assertEqual(server.call_args.args[:2], ("127.0.0.2", 8001))
                self.assertEqual(server.call_args.kwargs["use_debugger"], debug)
                self.assertEqual(server.call_args.kwargs["use_reloader"], debug)
