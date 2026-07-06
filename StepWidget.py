from PyQt6 import QtWidgets, QtCore
from config import constants

class StepWidget(QtWidgets.QWidget):
    request_delete = QtCore.pyqtSignal(object)
    height_changed = QtCore.pyqtSignal()

    def __init__(self, text="", step_number=1):
        super().__init__()

        self.step_number = step_number

        # =========================
        # LAYOUT
        # =========================
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(constants.STEP_WIDGET_LAYOUT_SPACING)

        # =========================
        # LABEL
        # =========================
        self.label = QtWidgets.QLabel(f"Step {step_number}:")
        self.label.setFixedWidth(constants.STEP_WIDGET_WIDTH)
        self.label.setStyleSheet("font-weight: bold;")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)

        # =========================
        # AUTO-EXPANDING TEXT EDIT
        # =========================
        self.step_input = QtWidgets.QTextEdit()
        self.step_input.setPlainText(text)
        self.step_input.setAcceptRichText(False)

        self.step_input.setLineWrapMode(
            QtWidgets.QTextEdit.LineWrapMode.WidgetWidth
        )

        self.step_input.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.step_input.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ccc;
                padding: 4px;
            }
        """)

        # =========================
        # HEIGHT CONTROL
        # =========================
        self.min_height = constants.STEP_WIDGET_MIN_HEIGHT
        self.max_height = constants.STEP_WIDGET_MAX_HEIGHT

        self.step_input.setMinimumHeight(self.min_height)

        self.step_input.textChanged.connect(self.adjust_height)

        # initial sizing after layout settles
        QtCore.QTimer.singleShot(0, self.adjust_height)

        # =========================
        # DELETE BUTTON
        # =========================
        self.delete_btn = QtWidgets.QPushButton("✕")
        self.delete_btn.setFixedWidth(constants.STEP_DELETE_BTN_WIDTH)
        self.delete_btn.clicked.connect(self.on_delete)

        # =========================
        # ASSEMBLE
        # =========================
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.step_input, 1)
        self.layout.addWidget(self.delete_btn)

    # =====================================================
    # AUTO RESIZE LOGIC
    # =====================================================
    def adjust_height(self):
        doc_height = self.step_input.document().size().height()

        new_height = int(doc_height + constants.STEP_WIDGET_ADJUST_HEIGHT_NEW_HEIGHT_PADDING)  # padding
        new_height = max(self.min_height, min(self.max_height, new_height))

        if self.step_input.height() != new_height:
            self.step_input.setFixedHeight(new_height)
            self.height_changed.emit()

    # =====================================================
    # SAFE TEXT ACCESS
    # =====================================================
    def text(self):
        return self.step_input.toPlainText().strip()

    # =====================================================
    # DELETE HANDLER
    # =====================================================
    def on_delete(self):
        self.request_delete.emit(self)

    # =====================================================
    # STEP LABEL UPDATE
    # =====================================================
    def set_step_number(self, n):
        self.step_number = n
        self.label.setText(f"Step {n}:")