# Ref Buddy
An application that helps to organize, navigate and <b>study</b> big collection of images.<br/>
Something like booru.org, but with handy tools for artists.

I personally use it to study life drawing and navigate through more than 80,000 reference images I collected over the years!

This app is currently in active development.

### Features
- **Shows images in any browser** one by one (multiple options to limit next image by the same folder or some tag);
- **Zooming in** to an image;
- **Grayscale filter** (turn grayscale on the fly + adjustable contrast) to better see light and shadows (multiple levels);
- "Cursor as grayscale value hint" adjustable by "light stops" (trust me it is handy);
- Image **tagging**;
- Generates tiny preview/thumbnail for each image and stores it to quicken library navigation;
- Split gif, webp or mp4 frame by frame (requires ffmpeg library to be installed);
- Duplicates search (the features is a mess atm... but it works!).

### Setup
Download this project first.<br/>
You'll need ```python``` ``` version 3.10 or higher``` to be installed beforehand. Other setup should be handled automatically by the run script.

Open file ```.env``` and replace:
- ```IMAGES_PATH``` should point to where images are;
- ```THUMB_PATH``` will be used to store generated thumbs;
- ```TMP_PATH``` will be used when duplicates search is initiated

### How to run
1. Run the script.<br/>
Windows: run ```run_ref_buddy.cmd```<br/>
Mac/Linux: run ```run_ref_buddy.sh```
2. Import images using menu ```File -> import images```
3. Generate previews ```Tools -> generate thumbs```
4. Hit ```Launch server``` button and then ```Go to gallery```

You'll need to import images and generate thumbs only once (or more if you add images to the library later)

### Some hotkeys
#### Image view:
- ```arrow right``` next random image (or just refresh the page); 
- ```arrow left``` previous image;
- ```Enter``` start timer. Timer is just a guide, it won't do anything other that counting;
- ```Space``` toggle ```same folder``` checkbox;
- ```F``` flip image;
- hold ```X``` and click on image to insert #color under cursor into swatch area. Holding ```X``` and then pressing ```G``` will toggle swatch between grayscale and color;
- ```Mouse wheel up/down``` zoom in/out. Left click on image to exit zoom mode;
- ```0```, ```1```,```2```,```3```,```4```,```5```,```6``` to enter grayscale mode and switch contrast modes. ```0``` turn image back to its original color, ```1``` is the strongest contrst, ```6``` is just a grayscale; 
- ```SHIFT``` + ```3```,```4```,```5```,```6```,```7``` change cursor over the image to become "grayscale value hint". 
```5``` is neutral 50% brightness. Rest of the numbers switch cursor brightness according to "light stops" in photography: 
```4``` is two times less light than ```5```, ```6``` is two times more light that ```5```, etc.

#### Folder view:
- ```S``` to toggle image selection mode;
- ```Ctrl+A``` to select all the images currently displayed when selection mode is on;
- ```T``` to toggle tags list view.

### Troubleshooting
- On Mac/Linux you might need to do ```chmod +x run_ref_buddy.sh``` first.
- If app works... it is a miracle!