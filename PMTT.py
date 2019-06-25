from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
import PIL.Image, PIL.ImageTk
import numpy, itertools

TITLE = "Pokémon Mini Tile Tool"

VERSION = "0.1.0"

class App(Tk):
    
    def __init__(self, *args, **kwargs):
        
        # Tkinter setup
        
        Tk.__init__(self)
        
        self.title(TITLE)
        
        # Widgets setup
        
        self.buttonsFrame = Frame(self)
        self.buttonsFrame.pack(side = LEFT)
        
        self.openFileButton = Button(self.buttonsFrame, text = "Open file", command = self.openFile)
        self.openFileButton.pack()
        
        self.exportButton = Button(self.buttonsFrame, text = "Export tiles", command = self.exportImage, state = DISABLED)
        self.exportButton.pack()
        
        self.openTransparencyButton = Button(self.buttonsFrame, text = "Open transparency", command = self.openTransp, state = DISABLED)
        self.openTransparencyButton.pack()
        
        self.exportSpriteButton = Button(self.buttonsFrame, text = "Export sprite", command = self.exportSprite, state = DISABLED)
        self.exportSpriteButton.pack()
        
        self.imageFrame = Frame(self)
        self.imageFrame.pack(side = RIGHT, expand = TRUE, fill = BOTH)
        
        # Variables
        
        self.labels = []
        
        self.windows = []
        
        self.image = None
        
        self.size = ()
        
        self.tiles = []
        
        self.transp = None
        
        self.spriteMapping = [5, 7, 1, 3, 6, 8, 2, 4]
        
        self.outWindow = None
        
    def createPreviewSpace(self, imgWidth, imgHeight):
        
        for i in itertools.chain.from_iterable(self.labels):
            i.destroy()
    
        self.labels = []
        
        self.windows = []
        
        width = imgWidth // 8
        height = imgHeight // 8
        
        for i in range(height):
            self.labels.append([])
        
        for i in range(width * height):
            
            self.labels[i // width].append(Label(self.imageFrame, text = i, bd = -2))
            self.labels[i // width][-1].grid(row = i // width, column = i % width)
    
    def toTiles(self):
        
        self.tiles = []
        
        for i in range(numpy.prod(self.size) // 64):
            self.tiles.append(self.image.crop(((i % (self.size[0] // 8)) * 8, (i // (self.size[0] // 8)) * 8, (i % (self.size[0] // 8)) * 8 + 8, (i // (self.size[0] // 8)) * 8 + 8)))
    
    def populatePreview(self):
        for i, j in enumerate(self.tiles):
            img = PIL.ImageTk.PhotoImage(j.resize((16, 16)))
            width, height = self.size[0] // 8, self.size[1] // 8
            self.labels[i // width][i % width].config(image = img)
            self.labels[i // width][i % width].img = img
    
    def openFile(self):
        temp = askopenfilename(title = TITLE, filetypes = [("Bitmap graphics files", (".bmp")), ("All files", (".*"))])
        if not temp:
            return
        self.image = PIL.Image.open(temp).convert("1")
        self.size = self.image.size
        if any(i % 8 for i in self.size):
            self.image = None
            self.size = ()
            showerror(TITLE, "Image dimensions must be multiples of 8!")
            return
        self.createPreviewSpace(*self.size)
        self.toTiles()
        self.populatePreview()
        self.exportButton.config(state = NORMAL)
        if self.size == (16, 16):
            self.openTransparencyButton.config(state = NORMAL)
        else:
            self.openTransparencyButton.config(state = DISABLED)
        self.exportSpriteButton.config(state = DISABLED)
    
    def exportImage(self):
        data = self.tilesToBytes(self.tiles)
        out = []
        for i in range(len(data) // 8):
            out.append("")
        for i, j in enumerate(data):
            out[i // 8] = ", ".join([out[i // 8], "0x" + hex(j).lstrip("0x").zfill(2).upper()]).lstrip(", ")
        self.outputData("\t" + ",\n\t".join(out) + ",")
    
    def tilesToBytes(self, tiles):
        byte = bytearray()
        for i in tiles:
            byte.extend(i.transpose(PIL.Image.ROTATE_90).transpose(PIL.Image.FLIP_LEFT_RIGHT).transpose(PIL.Image.FLIP_TOP_BOTTOM).tobytes())
        return byte
    
    def spriteToTiles(self):
        
        self.tiles = []
        
        for i in range(4):
            self.tiles.append(self.image.crop(((i % 2) * 8, (i // 2) * 8, (i % 2) * 8 + 8, (i // 2) * 8 + 8)))
        
        for i in range(4):
            self.tiles.append(self.transp.crop(((i % 2) * 8, (i // 2) * 8, (i % 2) * 8 + 8, (i // 2) * 8 + 8)))
        
    def openTransp(self):
        temp = askopenfilename(title = TITLE, filetypes = [("Bitmap graphics files", (".bmp")), ("All files", (".*"))])
        if not temp:
            return
        self.transp = PIL.Image.open(temp).convert("1")
        if self.transp.size != (16, 16):
            self.transp = None
            showerror(TITLE, "Image dimensions must be multiples of 8!")
            return
        self.createPreviewSpace(16, 32)
        self.spriteToTiles()
        self.populatePreview()
        self.exportSpriteButton.config(state = NORMAL)
    
    def exportSprite(self):
        spriteTiles = [self.tiles[i - 1] for i in self.spriteMapping]
        data = self.tilesToBytes(spriteTiles)
        out = []
        for i in range(len(data) // 8):
            out.append("")
        for i, j in enumerate(data):
            out[i // 8] = ", ".join([out[i // 8], "0x" + hex(j ^ 0xFF).lstrip("0x").zfill(2).upper()]).lstrip(", ")
        self.outputData("\t" + ",\n\t".join(out) + ",")
    
    def outputData(self, data):
        if self.outWindow:
            self.outWindow.destroy()
        
        self.outWindow = Toplevel()
        
        text = Text(self.outWindow)
        text.pack()
        text.insert(END, data)

App().mainloop()