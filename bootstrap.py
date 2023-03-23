from pathlib import Path
import streamlit.web.bootstrap
from streamlit import config as _config

proj_dir = Path(__file__).parent
filename = proj_dir / "app" / "app.py"

_config.set_option("server.headless", True)
args = []

# streamlit.cli.main_run(filename, args)
streamlit.web.bootstrap.run(str(filename), "", args, "")
