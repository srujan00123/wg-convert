import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main() -> int:
    app = Path(__file__).parent / "src" / "wg_convert" / "app.py"
    sys.argv = ["streamlit", "run", str(app), *sys.argv[1:]]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
