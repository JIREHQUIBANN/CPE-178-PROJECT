import flet as ft
import websockets
import asyncio
import base64
import json
from PIL import Image 
import io
import re
import pygame  # Import pygame for looping music

# Initialize pygame mixer
pygame.mixer.init()

# Function to play looping music
def play_music():
    pygame.mixer.music.load("C:\\Users\\kevin\\Downloads\\bgmflet.mp3")  # Change to your music file path
    pygame.mixer.music.play(-1)  # Loop indefinitely

def main(page: ft.Page):
    page.title = "Potato Leaf Disease Identifier"
    page.scroll = "adaptive"
    page.window.width = 600
    page.window.height = 380
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Background GIF
    background = ft.Image(
        src="C:\\Users\\kevin\\Downloads\\bgflet.gif",  
        fit=ft.ImageFit.COVER,
        width=550,
        height=320,
    )

    image_holder = ft.Image(visible=False)
    result_text = ft.Text()
    import tempfile

    def handle_loaded_file(e: ft.FilePickerResultEvent):
        if e.files and len(e.files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                with open(e.files[0].path, "rb") as image_file:
                    temp_file.write(image_file.read())
                image_holder.src = temp_file.name
                image_holder.visible = True
                page.update()

            file_path = e.files[0].path  
            print(file_path)

            img = Image.open(file_path)
            byte_io = io.BytesIO()
            img.save(byte_io, 'PNG')
            byte_io.seek(0)

            image_bytes = byte_io.read()
            image_data = base64.b64encode(image_bytes).decode("utf-8")

    filepick = ft.FilePicker(on_result=handle_loaded_file)
    page.overlay.append(filepick)

    def predict_image(e):
        if image_holder.src:
            with open(image_holder.src, "rb") as image_file:
                image_bytes = image_file.read()
                image_data = base64.b64encode(image_bytes).decode("utf-8")

            asyncio.run(send_prediction_request(image_data))
        else:
            print("No image selected")

    async def send_prediction_request(image_data):
        try:
            async with websockets.connect("ws://localhost:8000/ws") as websocket:
                await websocket.send(json.dumps({
                    "type": "predict",
                    "data": image_data
                }))
                response = await websocket.recv()
                data = json.loads(response)

                if data.get("type") == "prediction":
                    result_text.value = f"Predicted Class: {data.get('class')}" + f"\nScore: {round(data.get('score'), 2)}"
                else:
                    result_text.value = "Error occurred during prediction"
            page.update()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            print("Make sure the server is running")

    selected_image = ft.Row(
        [
            ft.Container(
                content=image_holder,
                margin=5,
                padding=5,
                border=ft.border.all(3, ft.colors.BLACK),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.WHITE,
                width=200,
                height=200,
                border_radius=10,
                ink=True,
                on_click=lambda _: filepick.pick_files(
                    allow_multiple=False, allowed_extensions=['jpg', 'png', 'jpeg']),
            ),
            ft.Container(
                content=result_text,
                margin=5,
                padding=5,
                border=ft.border.all(3, ft.colors.BLACK),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.WHITE,
                width=250,
                height=100,
                border_radius=10,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    predict_button = ft.Container(
        ft.ElevatedButton(text="Predict", width=120, height=40, on_click=predict_image),
        alignment=ft.alignment.center,
    )

    # Adding background first, then UI elements on top
    page.add(
        ft.Stack(
            [
                background,  
                ft.Column(   
                    [
                        result_text,
                        selected_image,
                        predict_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ]
        )
    )

# Start looping music
play_music()

ft.app(target=main)
