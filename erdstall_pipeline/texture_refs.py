from pathlib import Path


def _replace_texture_lines(header_text: str, texture_paths: list[str]) -> str:
    lines = header_text.splitlines(keepends=True)

    texture_line_indices = []
    for i, line in enumerate(lines):
        lower = line.lower()
        if "dummy.png" in lower or ("texture" in lower and ".png" in lower) or ("texture" in lower and ".jpg" in lower):
            texture_line_indices.append(i)

    if not texture_line_indices:
        return header_text

    if len(texture_paths) < len(texture_line_indices):
        raise ValueError(
            f"Not enough texture files. Header expects {len(texture_line_indices)}, found {len(texture_paths)}."
        )

    for idx, tex_idx in enumerate(texture_line_indices):
        old_line = lines[tex_idx]
        tex = texture_paths[idx].replace("\\", "/")
        if old_line.endswith("\r\n"):
            newline = "\r\n"
        else:
            newline = "\n"

        if "TextureFile" in old_line:
            prefix = old_line.split("TextureFile")[0] + "TextureFile "
            lines[tex_idx] = f"{prefix}{tex}{newline}"
        else:
            # fallback
            lines[tex_idx] = f"comment TextureFile {tex}{newline}"

    return "".join(lines)


def patch_texture_references(mesh_file: str, texture_dir: str) -> None:
    mesh_path = Path(mesh_file)
    tex_dir = Path(texture_dir)

    if not mesh_path.exists():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
    if not tex_dir.exists():
        raise FileNotFoundError(f"Texture dir not found: {tex_dir}")

    texture_files = sorted(
        [p for p in tex_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    )
    if not texture_files:
        raise FileNotFoundError(f"No texture images found in: {tex_dir}")

    rel_paths = [f"textures/{p.name}" for p in texture_files]

    raw = mesh_path.read_bytes()
    marker = b"end_header"
    idx = raw.find(marker)
    if idx == -1:
        raise ValueError("PLY header not found")

    header_end = raw.find(b"\n", idx)
    if header_end == -1:
        header_end = idx + len(marker)

    header = raw[:header_end + 1].decode("utf-8", errors="ignore")
    body = raw[header_end + 1:]

    new_header = _replace_texture_lines(header, rel_paths)
    mesh_path.write_bytes(new_header.encode("utf-8") + body)