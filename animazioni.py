from PyQt5.QtCore import QPropertyAnimation, QRect

def animate_transition(tab_widget, from_index, to_index):
    current_widget = tab_widget.widget(from_index)
    next_widget = tab_widget.widget(to_index)
    
    current_rect = current_widget.geometry()
    next_rect = QRect(current_rect)
    
    if to_index > from_index:
        next_rect.moveLeft(current_rect.width())
    else:
        next_rect.moveLeft(-current_rect.width())
    
    next_widget.setGeometry(next_rect)
    next_widget.show()
    
    animation = QPropertyAnimation(next_widget, b"geometry")
    animation.setDuration(500)
    animation.setStartValue(next_rect)
    animation.setEndValue(current_rect)
    animation.start()
    
    animation.finished.connect(lambda: current_widget.hide())