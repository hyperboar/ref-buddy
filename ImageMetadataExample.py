import sqlite3

test_data = [
    ImageMetadata('/path/to/image1.jpg', 0, 0, 'front'),
    ImageMetadata('/path/to/image2.jpg', 1, 10, 'side'),
    ImageMetadata('/path/to/image3.jpg', 5, 60, 'angled'),
    ImageMetadata('/path/to/image4.jpg', 2, 30, 'back'),
    ImageMetadata('/path/to/image5.jpg', 3, 20, 'front'),
]




conn = sqlite3.connect('example.db')

ImageMetadata.create(conn, test_data[0])
#############
image_metadata = ImageMetadata.read(conn, 1)
print(image_metadata.to_tuple())  # output: ('/path/to/image1.jpg', 0, 0, 'front')



###############
image_metadata = ImageMetadata.read(conn, 1)

with open('example.html', 'w') as f:
    f.write(image_metadata.to_html())


#######

folder_path = '/path/to/images/folder'
db_file = 'example.db'

importer = ImageMetadataImporter(folder_path, db_file)
importer.import_metadata()

##############

metadata = ImageMetadata.get_random_by_facing('front')
if metadata is not None:
    print(f"Random image: {metadata.path}")
else:
    print("No images found with facing 'front'")