"""Module for constructing and interacting with PDF reports for Pylinac."""
from datetime import datetime
from typing import List, Union, Sequence, Tuple
import io
import os.path as osp

from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from .typing import NumberLike
from .. import __version__


class PylinacCanvas:

    def __init__(self, filename: str, page_title: str, font: str="Helvetica", metadata: dict=None, metadata_location: tuple=(2, 25.5)):
        self.canvas = Canvas(filename, pagesize=A4)
        self._font = font
        self._title = page_title
        self._metadata = metadata
        self._metadata_location = metadata_location
        self._generate_pylinac_template_theme()
        self._add_metadata()

    def add_new_page(self) -> None:
        self.canvas.showPage()
        self._generate_pylinac_template_theme()
        self._add_metadata()

    def _add_metadata(self) -> None:
        if self._metadata is None:
            return
        else:
            text = ['Metadata:']
            for key, value in self._metadata.items():
                text.append(f"{key}: {value}")
            self.add_text(text=text, location=self._metadata_location)

    def _generate_pylinac_template_theme(self) -> None:
        # draw logo and header separation line
        self.canvas.drawImage(osp.join(osp.dirname(osp.dirname(osp.abspath(__file__))), 'files', 'Pylinac Full cropped.png'),
                         1 * cm, 26.5 * cm, width=5 * cm, height=3 * cm, preserveAspectRatio=True)
        self.canvas.line(1 * cm, 26.5 * cm, 20 * cm, 26.5 * cm)
        # draw title
        self.add_text(text=self._title, location=(7, 28), font_size=24)
        # draw "generated by pylinac" tag
        date = datetime.now().strftime("%B %d, %Y, %H:%M")
        self.add_text(f"Generated with Pylinac v{__version__} on {date}", location=(0.5, 0.5), font_size=8)

    def add_text(self, text: Union[str, List[str]], location: Tuple[NumberLike, NumberLike], font_size: int=10) -> None:
        """Generic text drawing function.

        Parameters
        ----------
        location : Sequence of two numbers
            The first item is the distance from left edge in cm
            The second item is the distance from bottom edge in cm.
        text : str, list of strings
            Text data; if str, prints single line.
            If list of strings, each list item is printed on its own line.
        font_size : int
            Text font size.
        """
        textobj = self.canvas.beginText()
        textobj.setTextOrigin(location[0]*cm, location[1]*cm)
        textobj.setFont(self._font, int(font_size))
        if isinstance(text, str):
            textobj.textLine(text)
        elif isinstance(text, list):
            for line in text:
                textobj.textLine(line)
        self.canvas.drawText(textobj)

    def add_image(self, image_data: io.BytesIO, location: Sequence, dimensions: Sequence, preserve_aspect_ratio: bool=True) -> None:
        image_data.seek(0)
        image = ImageReader(Image.open(image_data))
        self.canvas.drawImage(image, location[0]*cm, location[1]*cm, width=dimensions[0]*cm,
                              height=dimensions[1]*cm, preserveAspectRatio=preserve_aspect_ratio)

    def finish(self) -> None:
        self.canvas.showPage()
        self.canvas.save()
