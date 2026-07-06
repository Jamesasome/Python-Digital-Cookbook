from PyQt6 import QtWidgets, QtCore, QtGui
from config import constants

class RecipeDelegate(QtWidgets.QStyledItemDelegate):
    
    def __init__(self, parent=None, colour_func=None, open_callback=None):
        super().__init__(parent)
        self.colour_func = colour_func
        self.open_callback = open_callback

    def sizeHint(self, option, index):
        return QtCore.QSize(option.rect.width(), constants.RECIPE_DELEGATE_SIZEHINT)

    def paint(self, painter, option, index):
        painter.save()

        rect = option.rect
        name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        recipe_id = index.data(QtCore.Qt.ItemDataRole.UserRole)

        if not name:
            painter.restore()
            return

        color = self.colour_func(recipe_id) if self.colour_func else QtGui.QColor("#f0f0f0")

        if option.state & QtWidgets.QStyle.StateFlag.State_MouseOver:
            color = color.lighter(constants.RECIPE_DELEGATE_PAINT_HOVER_LIGHT)

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(rect.adjusted(*constants.RECIPE_DELEGATE_CARD_RECT), 10, 10)

        
        painter.setPen(QtGui.QColor("#222"))
        painter.drawText(
            rect.adjusted(*constants.RECIPE_DELEGATE_PAINT_TEXT_CARD_ADJUST),
            QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft,
            name
        )

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if not index.isValid():
            return False

        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self.open_callback:
                    self.open_callback(
                        index.data(QtCore.Qt.ItemDataRole.UserRole)
                    )
                return True

        return False
