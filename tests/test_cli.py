from subprocess import run


def test_cli_help():
    res = run(["nbp_rates", "--help"], capture_output=True)
    output = res.stdout.decode("utf-8")

    assert res.returncode == 0
    assert output.startswith("usage: nbp_rates [-h] [--select-period SELECT_PERIOD]")

    assert "Generate work log based on gitlab actions annotated with issue link." in output
    assert "--select-period" in output
    assert "--currency" in output
    assert "--now" in output
    assert "--best-exchange" in output
    assert "--backend" in output
    assert "--start" in output
    assert "--end" in output
    assert "--predict" in output
    assert "--graph" in output
