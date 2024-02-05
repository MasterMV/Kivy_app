from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.camera import Camera  # Import Camera widget
import face_recognition
import json
import cv2
from kivy.clock import Clock

class FaceRecognitionApp(App):
    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Create widgets
        self.label = Label(text="Select an image or capture from camera:")
        self.file_chooser = FileChooserListView(path=".")
        self.camera = Camera(resolution=(640, 480), play=True)  # Camera widget
        self.button_file = Button(text="Process from File", on_press=self.process_image_file)
        self.button_camera = Button(text="Capture from Camera", on_press=self.capture_from_camera)

        # Add widgets to the layout
        layout.add_widget(self.label)
        layout.add_widget(self.file_chooser)
        layout.add_widget(self.button_file)
        layout.add_widget(self.camera)
        layout.add_widget(self.button_camera)

        return layout

    def load_and_encode(self, image_path):
        image = face_recognition.load_image_file(image_path)
        return face_recognition.face_encodings(image)

    def process_image_file(self, instance):
        selected_file = self.file_chooser.selection and self.file_chooser.selection[0] or None

        if selected_file:
            self.process_image(selected_file)

    def process_image(self, image_path):
        # Load the database from a JSON file, or create an empty one if it doesn't exist
        try:
            with open("database.json", "r") as file:
                database = json.load(file)
        except FileNotFoundError:
            database = {}

        # Get the unknown face encodings
        unknown_face_encodings = self.load_and_encode(image_path)

        # Compare each unknown face encoding with the database
        matches = []
        for unknown_encoding in unknown_face_encodings:
            for name, data in database.items():
                if face_recognition.compare_faces([data["encoding"]], unknown_encoding)[0]:
                    matches.append((name, data["info"]))

        # Print results and handle new faces
        if matches:
            result_text = "Multiple matches found:\n"
            for name, info in matches:
                result_text += f"- It's a picture of {name}! {info}\n"
        else:
            new_name = input("Face not found in the database. Enter the person's name: ")
            new_instagram_handle = input("Enter their Instagram handle: ")
            self.add_person(image_path, new_name, new_instagram_handle, database)

        # Update the label with the result
        self.label.text = result_text

    def add_person(self, image_path, name, instagram_handle, database):
        encoding = self.load_and_encode(image_path)[0]  # Get the first encoding
        database[name] = {
            "encoding": encoding.tolist(),  # Convert encoding to a list for JSON compatibility
            "info": f"Insta handle: {instagram_handle} Insta link: https://www.instagram.com/{instagram_handle}/"
        }
        print(f"{name} added to the database!")

        # Save the updated database to the JSON file
        with open("database.json", "w") as file:
            json.dump(database, file)

    def capture_from_camera(self, instance):
        image_path = "captured_image.jpg"  # You can modify the filename as needed

        # Schedule the image capture after a short delay (adjust as needed)
        Clock.schedule_once(lambda dt: self.camera.export_to_png(image_path), 1)

    def on_stop(self):
        # Release the camera when the app is closed
        self.camera.play = False
        super(FaceRecognitionApp, self).on_stop()

if __name__ == '__main__':
    FaceRecognitionApp().run()
