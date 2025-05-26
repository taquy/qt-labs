from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
import sys
import cv2
import numpy as np
from PIL import Image

# Global QApplication instance
_app = None

def get_application():
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication(sys.argv)
    return _app

def show_retry_popup():
    # Get the global QApplication instance
    app = get_application()
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Action Required")
    window.setFixedSize(300, 150)
    
    # Create central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add label
    label = QLabel("What would you like to do?")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    # Variable to store the result
    result = [None]
    
    def on_button_click(action):
        result[0] = action
        window.close()
    
    # Create buttons
    button_layout = QVBoxLayout()
    continue_btn = QPushButton("Continue")
    retry_btn = QPushButton("Retry")
    stop_btn = QPushButton("Stop")
    
    continue_btn.clicked.connect(lambda: on_button_click("continue"))
    retry_btn.clicked.connect(lambda: on_button_click("retry"))
    stop_btn.clicked.connect(lambda: on_button_click("stop"))
    
    button_layout.addWidget(continue_btn)
    button_layout.addWidget(retry_btn)
    button_layout.addWidget(stop_btn)
    
    layout.addLayout(button_layout)
    
    # Show window
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Process events until window is closed
    while window.isVisible():
        app.processEvents()
        if result[0] is not None:  # If we have a result, break the loop
            break
    
    return result[0]

def show_image_and_prompt(pil_image):
    if pil_image is None:
        print("❌ No image provided to show_image_and_prompt")
        return None
        
    # Get the global QApplication instance
    app = get_application()
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("CAPTCHA Input")
    window.setFixedSize(400, 300)
    
    # Create central widget and layout
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    try:
        # Convert PIL image to NumPy array and ensure it's contiguous
        image_np = np.array(pil_image)
        if not image_np.flags['C_CONTIGUOUS']:
            image_np = np.ascontiguousarray(image_np)
        
        # Convert to BGR format that OpenCV expects
        if image_np.ndim == 2:  # If grayscale
            img = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
        elif image_np.ndim == 3:  # If RGB
            if image_np.shape[2] == 4:  # If RGBA
                img = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
            else:  # If RGB
                img = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            print(f"❌ Unexpected image dimensions: {image_np.ndim}")
            return None
        
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
        
        submit_button.clicked.connect(on_submit)
        input_field.returnPressed.connect(on_submit)
        
        # Show window
        window.show()
        window.raise_()
        window.activateWindow()
        
        # Process events until window is closed
        while window.isVisible():
            app.processEvents()
            if result[0] is not None:  # If we have a result, break the loop
                break
        
        print(f"✅ You entered: {result[0]}")
        return result[0]
        
    except Exception as e:
        print(f"❌ Error processing image: {str(e)}")
        return None

# if __name__ == "__main__":
#     pil_image = Image.open('cards/IMG_7779.PNG')
#     show_image_and_prompt(pil_image)