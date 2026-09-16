"""
Conversión de PowerPoint a imágenes PNG.

Pipeline: PPTX/PPT → PDF (LibreOffice headless) → PNG por diapositiva (PyMuPDF)

Requiere LibreOffice instalado en el servidor (soffice).
"""
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    pymupdf = None
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class PowerPointConversionError(Exception):
    """Error durante la conversión de PowerPoint."""


def find_libreoffice(custom_path=None):
    """Localiza el binario de LibreOffice en el sistema."""
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return str(path)

    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found

    windows_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for candidate in windows_paths:
        if Path(candidate).exists():
            return candidate

    return None


class PowerPointConverter:
    """Convierte presentaciones PowerPoint a imágenes PNG por diapositiva."""

    def __init__(self, libreoffice_path=None, dpi=150, timeout=300):
        self.libreoffice_path = find_libreoffice(libreoffice_path)
        self.dpi = dpi
        self.timeout = timeout

    def ensure_available(self):
        if not self.libreoffice_path:
            raise PowerPointConversionError(
                "LibreOffice no está instalado o no se encontró en el sistema. "
                "Instale LibreOffice para importar archivos PowerPoint."
            )

    def convert_to_slide_images(self, input_path: Path, work_dir: Path | None = None) -> list[Path]:
        """
        Convierte un archivo PPTX/PPT a una lista de PNGs (una por diapositiva).
        Retorna rutas absolutas ordenadas.
        """
        self.ensure_available()
        input_path = Path(input_path)

        if not input_path.exists():
            raise PowerPointConversionError("El archivo PowerPoint no existe.")

        cleanup_dir = None
        if work_dir is None:
            cleanup_dir = tempfile.TemporaryDirectory()
            work_dir = Path(cleanup_dir.name)

        work_dir = Path(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            pdf_path = self._convert_to_pdf(input_path, work_dir)
            images = self._pdf_to_pngs(pdf_path, work_dir / "slides")
            if not images:
                raise PowerPointConversionError("La conversión no produjo diapositivas.")
            return images
        finally:
            if cleanup_dir is not None:
                cleanup_dir.cleanup()

    def _convert_to_pdf(self, input_path: Path, output_dir: Path) -> Path:
        cmd = [
            self.libreoffice_path,
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--nodefault",
            "--nofirststartwizard",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(input_path.resolve()),
        ]

        logger.info("Ejecutando LibreOffice: %s", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PowerPointConversionError(
                f"La conversión excedió el tiempo límite ({self.timeout}s)."
            ) from exc

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise PowerPointConversionError(
                f"LibreOffice no pudo convertir el archivo. {detail}".strip()
            )

        pdf_path = output_dir / f"{input_path.stem}.pdf"
        if not pdf_path.exists():
            pdfs = sorted(output_dir.glob("*.pdf"))
            if not pdfs:
                raise PowerPointConversionError(
                    "No fue posible procesar este archivo PowerPoint. No se generó PDF."
                )
            pdf_path = pdfs[0]

        return pdf_path

    def _pdf_to_pngs(self, pdf_path: Path, slides_dir: Path) -> list[Path]:
        if not PYMUPDF_AVAILABLE:
            raise PowerPointConversionError(
                "PyMuPDF no está disponible en este servidor. La importación de PowerPoint está deshabilitada."
            )

        slides_dir.mkdir(parents=True, exist_ok=True)
        images = []

        try:
            doc = pymupdf.open(str(pdf_path))
        except Exception as exc:
            raise PowerPointConversionError(
                "El PDF generado está corrupto o no es legible."
            ) from exc

        zoom = self.dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)

        try:
            for index in range(len(doc)):
                page = doc.load_page(index)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                png_path = slides_dir / f"{index + 1:03d}.png"
                pixmap.save(str(png_path))
                images.append(png_path)
        finally:
            doc.close()

        return images
