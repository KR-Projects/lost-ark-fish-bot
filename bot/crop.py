from PIL import Image
import os

# Verzeichnis, in dem sich die Bilder befinden
input_directory = ".\\true"
# Verzeichnis, in dem die verarbeiteten Bilder gespeichert werden sollen
output_directory = ".\\fish_100x200\\"
# Ziellänge und -breite für die Bilder
target_width = 100
target_height = 200

# Sicherstellen, dass das Ausgabe-Verzeichnis existiert
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Eine Schleife durch alle Dateien im Eingabe-Verzeichnis
for filename in os.listdir(input_directory):
    if filename.endswith(".bmp") or filename.endswith(".png"):
        # Bild öffnen
        with Image.open(os.path.join(input_directory, filename)) as img:
            # Bildgröße abrufen
            width, height = img.size
            # Berechnung der Position für den horizontalen Zuschnitt (zentriert)
            left = (width - target_width) / 2
            right = (width + target_width) / 2
            # Bild zuschneiden
            img_cropped = img.crop((left, 0, right, target_height))
            # Bild speichern
            img_cropped.save(os.path.join(output_directory, filename))

print("Die Verarbeitung der Bilder ist abgeschlossen.")
