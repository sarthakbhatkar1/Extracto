from pathlib import Path
from typing import List

from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

from daemon.constants.enums import StepMethod
from daemon.utils.status_utils import start_step, complete_step, fail_step


class DoclingParser:
    def __init__(self):
        pdf_options = PdfPipelineOptions(
            do_ocr=True,
            extract_tables=True,
            extract_images=False
        )

        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.PPTX,
                InputFormat.TXT
            ],
            pdf_pipeline_options=pdf_options
        )

    def parse_documents(self, task, document_paths: List[str]) -> str:
        try:
            start_step(task, StepMethod.PARSING)

            parsed_texts = []

            for path in document_paths:
                result = self.converter.convert(Path(path))
                doc = result.document
                parsed_texts.append(doc.export_to_markdown())

            complete_step(task, StepMethod.PARSING)
            return "\n\n".join(parsed_texts)

        except Exception as e:
            fail_step(task, StepMethod.PARSING, str(e))
            raise
