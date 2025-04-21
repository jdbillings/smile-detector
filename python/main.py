import cv2
from tkinter import Tk, Label
from PIL import Image, ImageTk

def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    video_label.after(10, update_frame)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create GUI window
root = Tk()
root.title("Webcam Viewer")
video_label = Label(root)
video_label.pack()

# Start updating frames
update_frame()

# Run the GUI loop
root.mainloop()

# Release the webcam when the GUI is closed
cap.release()
cv2.destroyAllWindows()