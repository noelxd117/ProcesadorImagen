from PIL import Image
import os
from typing import Optional, Dict, Any

class ImageProcessor:
    """Procesador de imágenes usando Pillow"""
    
    def __init__(self):
        self.supported_formats = {
            'jpeg': 'JPEG',
            'jpg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
            'webp': 'WEBP',
            'bmp': 'BMP',
            'tiff': 'TIFF'
        }
    
    def process(
        self,
        input_path: str,
        output_path: str,
        process_type: str,
        **kwargs
    ) -> str:

        img = Image.open(input_path)

        save_format = None

        if process_type == "redimensionar":
            img = self._resize(img, **kwargs)

        elif process_type == "convertir":
            img, output_path, save_format = self._convert_format(
                img,
                output_path,
                **kwargs
            )

        elif process_type == "filtro":
            img = self._apply_filter(img, **kwargs)

        elif process_type == "miniatura":
            img = self._create_thumbnail(img, **kwargs)

        else:
            raise ValueError(f"Tipo de procesamiento no soportado: {process_type}")

        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not save_format:

            original_ext = os.path.splitext(input_path)[1].lower().replace(".", "")

            if original_ext in self.supported_formats:
                save_format = self.supported_formats[original_ext]
                base_path = os.path.splitext(output_path)[0]
                output_path = f"{base_path}.{original_ext}"
            else:
                save_format = "PNG"
                output_path = f"{output_path}.png"

        # Guardar imagen
        if save_format in ["JPEG", "WEBP"]:
            img.save(output_path, format=save_format, quality=95)

        else:
            img.save(output_path, format=save_format)

        return output_path
    
    def _resize(self, img: Image.Image, width: int = 800, height: int = 600, **kwargs) -> Image.Image:
        """Redimensionar imagen"""
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    def _convert_format(
        self,
        img: Image.Image,
        output_path: str,
        format: str = "png",
        **kwargs
    ):
        """Convertir formato de imagen"""

        format = format.lower()

        if format not in self.supported_formats:
            raise ValueError(f"Formato no soportado: {format}")

        pil_format = self.supported_formats[format]

        # Convertir transparencia para JPEG
        if format in ["jpeg", "jpg", "bmp"] and img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img

        # Cambiar extensión
        base_path = os.path.splitext(output_path)[0]
        output_path = f"{base_path}.{format}"

        return img, output_path, pil_format
    
    def _apply_filter(self, img: Image.Image, filter_type: str = "blur", intensity: int = 2, **kwargs) -> Image.Image:
        """Aplicar filtro a la imagen"""
        from PIL import ImageFilter, ImageEnhance
        
        if filter_type == "blur":
            return img.filter(ImageFilter.GaussianBlur(radius=intensity))
        elif filter_type == "sharpen":
            enhancer = ImageEnhance.Sharpness(img)
            return enhancer.enhance(1.0 + intensity * 0.1)
        elif filter_type == "brightness":
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.0 + intensity * 0.1)
        elif filter_type == "contrast":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.0 + intensity * 0.1)
        elif filter_type == "grayscale":
            return img.convert("L")
        else:
            raise ValueError(f"Filtro no soportado: {filter_type}")
    
    def _create_thumbnail(self, img: Image.Image, size: int = 200, **kwargs) -> Image.Image:
        """Crear miniatura de imagen"""
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        return img
