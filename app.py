
import base64
import io
import html
import re
import time
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify

try:  # Optional PDF text extraction
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None

try:  # Optional Pillow for image handling
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def shorten_text(text: str, limit: int = 20000) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def to_positive_int(value: str | None) -> int | None:
    try:
        if value is None or value == '':
            return None
        parsed = int(value)
        return parsed if parsed > 0 else None
    except (TypeError, ValueError):
        return None


def convert_unit_to_px(value: int | None, unit: str | None) -> int | None:
    if value is None:
        return None
    unit = (unit or 'px').lower()
    if unit == 'px' or unit == 'pixels':
        return value
    if unit in ('in', 'inch', 'inches'):
        return int(value * 96)
    if unit in ('cm', 'centimeter', 'centimeters'):
        return int(value * 37.7952755906)
    if unit in ('mm', 'millimeter', 'millimeters'):
        return int(value * 3.77952755906)
    return value


def to_positive_float(value: str | None) -> float | None:
    try:
        if value is None or value == '':
            return None
        parsed = float(value)
        return parsed if parsed > 0 else None
    except (TypeError, ValueError):
        return None


def best_effort_text(byte_data: bytes, filename: str | None) -> str:
    suffix = (Path(filename).suffix.lower() if filename else '')
    if suffix == '.docx':
        text = extract_docx_text(byte_data)
        if text.strip():
            return shorten_text(text)
    if suffix == '.pptx':
        text = extract_pptx_text(byte_data)
        if text.strip():
            return shorten_text(text)
    if suffix == '.pdf' and PdfReader:
        try:
            reader = PdfReader(io.BytesIO(byte_data))
            text_pages = []
            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text() or ''
                if extracted:
                    text_pages.append(extracted)
                if sum(len(t) for t in text_pages) > 60000:
                    break
            combined = "\n".join(text_pages).strip()
            if combined:
                return shorten_text(combined)
        except Exception:
            pass

    for encoding in ('utf-8', 'latin-1'):
        try:
            decoded = byte_data.decode(encoding)
            if decoded.strip():
                return shorten_text(decoded)
        except UnicodeDecodeError:
            continue

    return f"[Binary data: {len(byte_data)} bytes]"


def extract_docx_text(byte_data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(byte_data)) as docx:
            xml = docx.read('word/document.xml').decode('utf-8', 'ignore')
    except Exception:
        return ''
    xml = xml.replace('<w:br/>', '\n').replace('<w:cr/>', '\n')
    paragraphs = re.split(r'</w:p>', xml)
    collected = []
    for para in paragraphs:
        runs = re.findall(r'<w:t[^>]*>(.*?)</w:t>', para, flags=re.DOTALL)
        if not runs:
            continue
        text = "".join(html.unescape(run.replace('\r', '')) for run in runs)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            collected.append(text)
    return "\n".join(collected)


def extract_pptx_text(byte_data: bytes) -> str:
    texts: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(byte_data)) as pptx:
            slide_names = sorted(
                n for n in pptx.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')
            )
            for name in slide_names:
                xml = pptx.read(name).decode('utf-8', 'ignore')
                parts = re.findall(r'<a:t[^>]*>(.*?)</a:t>', xml)
                cleaned = [html.unescape(re.sub(r'\s+', ' ', part)).strip() for part in parts]
                texts.append("\n".join(filter(None, cleaned)))
    except Exception:
        return ''
    return "\n\n".join(filter(None, texts))


def summarize_options(tool: str, options: dict) -> str:
    if not options:
        return ''
    if tool == 'image-resizer':
        width = options.get('target_width')
        height = options.get('target_height')
        mode = options.get('resize_mode')
        unit = options.get('dimension_unit', 'px')
        parts = []
        if width and height:
            parts.append(f"Target: {width}×{height} px ({unit})")
        elif width or height:
            parts.append(f"Target: {width or 'auto'}×{height or 'auto'} px ({unit})")
        if mode:
            parts.append(f"Mode: {mode}")
        return " ".join(parts)
    if tool == 'pdf-compressor':
        target = options.get('target_size_mb')
        level = options.get('compression_level')
        parts = []
        if target:
            parts.append(f"Goal size: {target} MB")
        if level:
            parts.append(f"Preset: {level}")
        return " ".join(parts)
    return ''


def build_simple_pdf(info: dict) -> bytes:
    """Create a minimal single-page PDF with the supplied content."""
    text = shorten_text(info.get('content') or info['message'])
    safe_text = (
        text.replace('\\', r'\\')
        .replace('(', r'\(')
        .replace(')', r'\)')
        .replace('\n', r'\n')
    )
    content = f"BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET".encode("latin-1", "ignore")
    stream = b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content)

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        stream,
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    buffer = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(buffer))
        buffer.extend(f"{obj_id} 0 obj\n".encode())
        buffer.extend(obj)
        buffer.extend(b"\nendobj\n")

    xref_offset = len(buffer)
    xref_lines = [
        f"xref\n0 {len(objects)+1}\n",
        "0000000000 65535 f \n",
    ]
    for off in offsets[1:]:
        xref_lines.append(f"{off:010d} 00000 n \n")
    buffer.extend("".join(xref_lines).encode())
    buffer.extend(
        f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )
    return bytes(buffer)


# ... docx builder
def build_simple_docx(info: dict) -> bytes:
    """Generate a minimal DOCX with the provided content."""
    text = info.get('content') or info['message']
    lines = text.splitlines() or ['']
    runs = []
    for idx, line in enumerate(lines):
        runs.append(f"<w:r><w:t xml:space=\"preserve\">{escape(line) or ' '}</w:t></w:r>")
        if idx != len(lines) - 1:
            runs.append("<w:r><w:br/></w:r>")

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 w15 wp14">
  <w:body>
    <w:p>
      {''.join(runs)}
    </w:p>
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
      <w:cols w:space="720"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:body>
</w:document>"""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as docx:
        docx.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        docx.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        docx.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def build_simple_pptx(info: dict) -> bytes:
    """Generate a minimal PPTX with the provided content."""
    text = info.get('content') or info['message']
    lines = text.splitlines() or ['']
    paragraphs = []
    for line in lines[:10]:
        paragraphs.append(
            f"<a:p><a:r><a:rPr lang=\"en-US\" sz=\"2800\" dirty=\"0\"/><a:t>{escape(line) or ' '}</a:t></a:r>"
            "<a:endParaRPr lang=\"en-US\" sz=\"2800\"/></a:p>"
        )

    slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="9144000" cy="6858000"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Title 1"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr/>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          {''.join(paragraphs)}
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>"""

    presentation_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst/>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId1"/>
  </p:sldIdLst>
  <p:notesMasterIdLst/>
  <p:notesIdLst/>
  <p:presProps/>
  <p:viewPr/>
  <p:extLst/>
</p:presentation>"""

    theme_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
      <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F497D"/></a:dk2>
      <a:lt2><a:srgbClr val="EEECE1"/></a:lt2>
      <a:accent1><a:srgbClr val="4F81BD"/></a:accent1>
      <a:accent2><a:srgbClr val="C0504D"/></a:accent2>
      <a:accent3><a:srgbClr val="9BBB59"/></a:accent3>
      <a:accent4><a:srgbClr val="8064A2"/></a:accent4>
      <a:accent5><a:srgbClr val="4BACC6"/></a:accent5>
      <a:accent6><a:srgbClr val="F79646"/></a:accent6>
      <a:hlink><a:srgbClr val="0000FF"/></a:hlink>
      <a:folHlink><a:srgbClr val="800080"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont><a:latin typeface="Calibri"/></a:majorFont>
      <a:minorFont><a:latin typeface="Calibri"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>"""

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as pptx:
        pptx.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
</Types>""")
        pptx.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""")
        pptx.writestr("ppt/presentation.xml", presentation_xml)
        pptx.writestr("ppt/_rels/presentation.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>""")
        pptx.writestr("ppt/slides/slide1.xml", slide_xml)
        pptx.writestr("ppt/slides/_rels/slide1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>""")
        pptx.writestr("ppt/theme/theme1.xml", theme_xml)
    return buffer.getvalue()


def build_images_pdf(info: dict) -> bytes:
    files = info.get('files') or []
    if Image:
        pil_images = []
        for file in files:
            try:
                img = Image.open(io.BytesIO(file['bytes']))
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                else:
                    img = img.copy()
                pil_images.append(img)
            except Exception:
                continue
        if pil_images:
            buffer = io.BytesIO()
            primary, *rest = pil_images
            save_kwargs = {"format": "PDF"}
            if rest:
                save_kwargs.update({"save_all": True, "append_images": rest})
            primary.save(buffer, **save_kwargs)
            for image in pil_images:
                image.close()
            return buffer.getvalue()

    textual = dict(info)
    textual['content'] = (
        "\n".join(f"Image: {file['name']}" for file in files)
        or textual.get('content')
        or textual['message']
    )
    return build_simple_pdf(textual)


def build_zip_note(filename: str, message: str, original_bytes: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("README.txt", message)
        target_name = Path(filename).name if filename else 'file.bin'
        archive.writestr(f"resized-{target_name}", original_bytes)
    return buffer.getvalue()


def resize_image_bytes(image_bytes: bytes, options: dict) -> bytes:
    if not Image:
        return image_bytes
    width = options.get('target_width')
    height = options.get('target_height')
    if not width and not height:
        return image_bytes
    mode = (options.get('resize_mode') or 'fit').lower()
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert('RGB')
            target_width = width or img.width
            target_height = height or img.height
            resample = getattr(Image, 'LANCZOS', getattr(Image, 'BICUBIC', Image.BILINEAR))

            if mode == 'fit':
                resized = img.copy()
                resized.thumbnail((target_width, target_height), resample=resample)
            elif mode == 'fill' and width and height:
                ratio = max(target_width / img.width, target_height / img.height)
                new_size = (
                    max(1, int(img.width * ratio)),
                    max(1, int(img.height * ratio))
                )
                resized = img.resize(new_size, resample=resample)
                left = max(0, (new_size[0] - target_width) // 2)
                top = max(0, (new_size[1] - target_height) // 2)
                resized = resized.crop((left, top, left + target_width, top + target_height))
            elif mode == 'stretch' and width and height:
                resized = img.resize((target_width, target_height), resample=resample)
            else:
                resized = img.copy()
                resized.thumbnail((target_width, target_height), resample=resample)

            output = io.BytesIO()
            fmt = img.format if img.format in {'JPEG', 'PNG', 'WEBP'} else 'PNG'
            save_kwargs = {'format': fmt}
            if fmt == 'JPEG':
                save_kwargs['quality'] = 90
            resized.save(output, **save_kwargs)
            resized_bytes = output.getvalue()
            resized.close()
            return resized_bytes
    except Exception:
        return image_bytes
    return image_bytes


def build_resizer_zip(info: dict) -> bytes:
    options = info.get('options') or {}
    details = summarize_options('image-resizer', options)
    message = info['message']
    if details:
        message = f"{message}\n{details}"
    resized_bytes = resize_image_bytes(info['bytes'], options)
    buffer = io.BytesIO()
    target_name = Path(info['filename']).name if info['filename'] else 'image.bin'
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("README.txt", message)
        archive.writestr(f"resized-{target_name}", resized_bytes)
    return buffer.getvalue()


def build_compressed_pdf(info: dict) -> bytes:
    options = info.get('options') or {}
    details = summarize_options('pdf-compressor', options)
    payload = dict(info)
    if details:
        payload['message'] = f"{info['message']} ({details})"
    return build_simple_pdf(payload)


TOOL_DEFINITIONS = {
    "pdf-to-word": {
        "name": "PDF to Word",
        "extension": "docx",
        "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "builder": build_simple_docx,
    },
    "images-to-pdf": {
        "name": "Multiple Images to PDF",
        "extension": "pdf",
        "mimetype": "application/pdf",
        "builder": build_images_pdf,
        "accept_multiple": True,
    },
    "ppt-to-pdf": {
        "name": "PPT to PDF",
        "extension": "pdf",
        "mimetype": "application/pdf",
        "builder": build_simple_pdf,
    },
    "pdf-to-ppt": {
        "name": "PDF to PPT",
        "extension": "pptx",
        "mimetype": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "builder": build_simple_pptx,
    },
    "word-to-pdf": {
        "name": "Word to PDF",
        "extension": "pdf",
        "mimetype": "application/pdf",
        "builder": build_simple_pdf,
    },
    "image-resizer": {
        "name": "Image Resizer",
        "extension": "zip",
        "mimetype": "application/zip",
        "builder": build_resizer_zip,
    },
    "pdf-compressor": {
        "name": "PDF Compressor",
        "extension": "pdf",
        "mimetype": "application/pdf",
        "builder": build_compressed_pdf,
    },
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/tools/<tool>')
def tool_page(tool):
    definition = TOOL_DEFINITIONS.get(tool)
    if not definition:
        return render_template('404.html'), 404
    return render_template('tool.html', tool_route=tool, tool_name=definition['name'])

@app.route('/process', methods=['POST'])
def process():
    tool = request.form.get('tool')
    definition = TOOL_DEFINITIONS.get(tool)

    wants_json = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.accept_mimetypes
    )

    if not definition:
        message = 'Please select a valid tool.'
        if wants_json:
            return jsonify({'status': 'error', 'message': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    uploads = []
    for storage in request.files.getlist('file'):
        if not storage or not storage.filename:
            continue
        safe_name = secure_filename(storage.filename) or 'document'
        file_bytes = storage.read()
        storage.close()
        if not file_bytes:
            continue
        uploads.append({
            'name': safe_name,
            'bytes': file_bytes,
            'mimetype': storage.mimetype or 'application/octet-stream'
        })

    if not uploads:
        message = 'Please select a file to process.'
        if wants_json:
            return jsonify({'status': 'error', 'message': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    if not definition.get('accept_multiple'):
        uploads = uploads[:1]
    elif len(uploads) > 20:
        uploads = uploads[:20]

    primary_upload = uploads[0]
    byte_count = sum(len(item['bytes']) for item in uploads)

    options: dict[str, int | float | str | None] = {}
    if tool == 'image-resizer':
        unit = request.form.get('dimension_unit') or 'px'
        width_raw = to_positive_int(request.form.get('target_width'))
        height_raw = to_positive_int(request.form.get('target_height'))
        width = convert_unit_to_px(width_raw, unit)
        height = convert_unit_to_px(height_raw, unit)
        resize_mode = request.form.get('resize_mode') or 'fit'
        if width:
            options['target_width'] = width
        if height:
            options['target_height'] = height
        if resize_mode:
            options['resize_mode'] = resize_mode
        options['dimension_unit'] = unit
    elif tool == 'pdf-compressor':
        target_size = to_positive_float(request.form.get('target_size_mb'))
        compression_level = request.form.get('compression_level') or 'balanced'
        if target_size:
            options['target_size_mb'] = round(target_size, 2)
        if compression_level:
            options['compression_level'] = compression_level

    try:
        start = time.perf_counter()
        simulated_work_ms = min(1200, max(120, byte_count // 30 or 120))
        time.sleep(simulated_work_ms / 1000.0)
        if definition.get('accept_multiple'):
            label_lines = [
                f"{index + 1}. {upload['name']}"
                for index, upload in enumerate(uploads[:50])
            ]
            content_text = shorten_text("\n".join(label_lines)) if label_lines else ''
        else:
            content_text = best_effort_text(primary_upload['bytes'], primary_upload['name'])

        option_summary = summarize_options(tool, options)
        file_descriptor = (
            f"{len(uploads)} files"
            if definition.get('accept_multiple') and len(uploads) > 1
            else f"'{primary_upload['name']}'"
        )
        base_message = f"Converted {file_descriptor} using {definition['name']} on PaperPrep."
        if option_summary:
            base_message = f"{base_message} {option_summary}"

        conversion_info = {
            "filename": primary_upload['name'],
            "bytes": primary_upload['bytes'],
            "files": uploads,
            "message": base_message,
            "content": content_text or base_message,
            "options": options,
        }
        output_bytes = definition['builder'](conversion_info)
        processing_time_ms = round((time.perf_counter() - start) * 1000, 2)
    except Exception as exc:  # pragma: no cover - defensive
        message = f"Conversion failed: {exc}"
        if wants_json:
            return jsonify({'status': 'error', 'message': message}), 500
        flash(message, 'error')
        return redirect(url_for('index'))

    base_name = Path(primary_upload['name']).stem if primary_upload['name'] else ''
    if not base_name or base_name == '.':
        base_name = 'document'
    target_filename = f"{base_name}.{definition['extension']}"

    payload = {
        'status': 'success',
        'filename': primary_upload['name'],
        'tool': tool,
        'size_kb': max(1, byte_count // 1024) if byte_count else 1,
        'processing_time_ms': processing_time_ms,
        'message': base_message,
        'preview_text': content_text or base_message,
        'download': {
            'base64': base64.b64encode(output_bytes).decode('ascii'),
            'filename': target_filename,
            'mimetype': definition['mimetype']
        },
    }

    if wants_json:
        return jsonify(payload)

    flash(payload['message'], 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
