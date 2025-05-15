from PIL import Image, ImageDraw

# Open an image
image = Image.open("test_images/tree.png")
print(type(image))
print(image)
draw = ImageDraw.Draw(image)

# Draw a rectangle
draw.rectangle((50, 50, 150, 150), outline="red", width=3)

# Draw a line
draw.line((200, 50, 300, 150), fill="blue", width=5)

# Draw text
draw.text((100, 200), "Hello, Pillow!", fill="black")

# Save the modified image
image.save("modified_image.jpg")