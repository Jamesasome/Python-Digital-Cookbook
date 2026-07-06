import sys
import logging
from pathlib import Path
from RecipeApp import RecipeApp
from PyQt6 import QtWidgets, QtGui


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    logging.basicConfig(
        level=logging.INFO,
        filename="cookbook.log",
        format="%(asctime)s %(levelname)s %(message)s"
    )

    w = RecipeApp()

    icon_path = Path("./icon.png")

    try:
        if icon_path.exists():
            w.setWindowIcon(QtGui.QIcon(str(icon_path)))
        else:
            logging.warning("Icon file not found: %s", icon_path)

    except Exception:
        logging.exception("Failed to set application icon")

    w.show()
    sys.exit(app.exec())