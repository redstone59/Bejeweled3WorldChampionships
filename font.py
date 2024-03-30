# Mostly stolen from StackOverflow (text colour customisation added)
# https://stackoverflow.com/questions/11993290/truly-custom-font-in-tkinter/73428832#73428832
# Thanks to just_a_kid_coder_123 for this answer!

# I don't know why VSCode hates this code so much.

from PIL import Image, ImageFont, ImageDraw

def hex_to_tuple(colour_code: str):
    if len(colour_code) != 7: raise ValueError(f"Invalid colour code {colour_code}")
    
    colour_code = colour_code.removeprefix("#")
    split_colour = [colour_code[i:i+2] for i in range(0, 6, 2)]
    
    for i in range(len(split_colour)):
        split_colour[i] = int(split_colour[i], 16)
    
    return tuple(split_colour)

class RenderFont:
    def __init__(self, filename):
        """
        constructor for RenderFont
        filename: the filename to the ttf font file
        fill: the color of the text
        """
        self._file = filename
        self._image = None

    def get_render(self, font_size, txt, type_="normal", colour = (255, 255, 255), align = "mm"):
        """
        returns a transparent PIL image that contains the text
        font_size: the size of text
        txt: the actual text
        type_: the type of the text, "normal" or "bold"
        """
        if type(txt) is not str:
            raise TypeError("text must be a string")

        if type(font_size) is not int:
            raise TypeError("font_size must be a int")
        
        if type(colour) is not tuple:
            colour = hex_to_tuple(colour)

        width = len(txt)*font_size
        height = (font_size+5) * ("\n".count(txt) + 20)

        font = ImageFont.truetype(font=self._file, size=font_size)
        self._image = Image.new(mode='RGBA', size=(width, height), color=(255, 255, 255))

        rgba_data = self._image.getdata()
        newdata = []

        for item in rgba_data:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newdata.append((255, 255, 255, 0))

            else:
                newdata.append(item)

        self._image.putdata(newdata)

        draw = ImageDraw.Draw(im=self._image)

        if type_ == "normal":
            draw.text(xy=(width/2, height/2), text=txt, font=font, fill=colour, anchor=align)
        elif type_ == "bold":
            draw.text(xy=(width/2, height/2), text=txt, font=font, fill=colour, anchor=align, 
            stroke_width=1, stroke_fill=colour)

        return self._image