from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
import sys
import cv2

# Global QApplication instance
_app = None

def show_image_and_prompt(image_path):
    global _app
    
    # Initialize QApplication if it doesn't exist
    if _app is None:
        _app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("CAPTCHA Input")
    window.setFixedSize(400, 300)
    
    # Create central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Load and display image
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    bytes_per_line = 3 * width
    q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    pixmap = QPixmap.fromImage(q_img)
    
    # Scale image to fit window while maintaining aspect ratio
    scaled_pixmap = pixmap.scaled(380, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # Create image label
    image_label = QLabel()
    image_label.setPixmap(scaled_pixmap)
    image_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(image_label)
    
    # Create input field
    input_field = QLineEdit()
    input_field.setPlaceholderText("Enter CAPTCHA here...")
    layout.addWidget(input_field)
    
    # Create submit button
    submit_button = QPushButton("Submit")
    layout.addWidget(submit_button)
    
    # Variable to store the result
    result = [None]
    
    def on_submit():
        result[0] = input_field.text()
        window.hide()  # Hide the window first
        window.close()  # Then close it
        window.deleteLater()  # Clean up resources
        _app.quit()  # Quit the application
    
    submit_button.clicked.connect(on_submit)
    input_field.returnPressed.connect(on_submit)
    
    # Show window
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Process events until window is closed
    while window.isVisible():
        _app.processEvents()
        if result[0] is not None:  # If we have a result, break the loop
            break
    
    print(f"✅ You entered: {result[0]}")
    return result[0]


# show_image_and_prompt("cards/IMG_7779.PNG")