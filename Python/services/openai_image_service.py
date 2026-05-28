"""OpenAI image generation service for Unreal MCP.

This module is intentionally independent from MCP and Unreal. It only knows how
to call the OpenAI Images API and write PNG files.
"""

import base64
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import requests


OPENAI_IMAGES_GENERATIONS_URL = "https://api.openai.com/v1/images/generations"
OPENAI_IMAGES_EDITS_URL = "https://api.openai.com/v1/images/edits"
DEFAULT_IMAGE_MODEL = "gpt-image-1"


def sanitize_output_name(output_name: str) -> str:
    """Return a filesystem-friendly PNG basename without an extension."""
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", output_name.strip())
    name = name.strip("._")
    return name or "AI_Texture"


def ensure_png_path(output_dir: str, output_name: str) -> str:
    """Build an absolute PNG path and create its parent directory."""
    safe_name = sanitize_output_name(output_name)
    output_path = Path(output_dir).expanduser().resolve() / f"{safe_name}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return str(output_path)


def _headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _decode_image_response(response: requests.Response, output_path: str) -> Dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        return {
            "success": False,
            "message": "OpenAI image response was not JSON",
            "status_code": response.status_code,
            "body": response.text[:1000],
        }

    if response.status_code >= 400:
        error = payload.get("error", {})
        return {
            "success": False,
            "message": error.get("message", "OpenAI image request failed"),
            "status_code": response.status_code,
            "error": error,
        }

    data = payload.get("data") or []
    if not data:
        return {"success": False, "message": "OpenAI image response did not include image data"}

    image_item = data[0]
    image_bytes: Optional[bytes] = None

    if image_item.get("b64_json"):
        image_bytes = base64.b64decode(image_item["b64_json"])
    elif image_item.get("url"):
        image_url = image_item["url"]
        image_response = requests.get(image_url, timeout=120)
        if image_response.status_code >= 400:
            return {
                "success": False,
                "message": "Failed to download generated image URL",
                "status_code": image_response.status_code,
            }
        image_bytes = image_response.content

    if not image_bytes:
        return {
            "success": False,
            "message": "OpenAI image response did not include b64_json or url",
            "response_keys": list(image_item.keys()),
        }

    with open(output_path, "wb") as image_file:
        image_file.write(image_bytes)

    return {
        "success": True,
        "image_path": output_path,
        "model": payload.get("model"),
        "revised_prompt": image_item.get("revised_prompt"),
        "size_bytes": len(image_bytes),
    }


def generate_texture_png(
    prompt: str,
    output_path: str,
    size: str = "1024x1024",
    reference_image_path: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a PNG image with GPT Image.

    If reference_image_path is provided, the Images edits endpoint is used so
    the UV layout can act as a guide image. If that endpoint is not available
    for the caller's model/org, the error is returned without falling back to a
    misleading text-only result.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "message": "OPENAI_API_KEY is not set. Set it in the MCP server environment before generating textures.",
            "error_code": "missing_openai_api_key",
        }

    selected_model = model or os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)
    Path(output_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

    try:
        if reference_image_path:
            reference_path = Path(reference_image_path).expanduser().resolve()
            if not reference_path.exists():
                return {
                    "success": False,
                    "message": f"Reference image does not exist: {reference_path}",
                    "error_code": "missing_reference_image",
                }

            with open(reference_path, "rb") as image_file:
                response = requests.post(
                    OPENAI_IMAGES_EDITS_URL,
                    headers=_headers(api_key),
                    data={
                        "model": selected_model,
                        "prompt": prompt,
                        "size": size,
                        "n": "1",
                    },
                    files={"image": (reference_path.name, image_file, "image/png")},
                    timeout=300,
                )
        else:
            response = requests.post(
                OPENAI_IMAGES_GENERATIONS_URL,
                headers={**_headers(api_key), "Content-Type": "application/json"},
                json={
                    "model": selected_model,
                    "prompt": prompt,
                    "size": size,
                    "n": 1,
                },
                timeout=300,
            )
    except requests.RequestException as exc:
        return {"success": False, "message": f"OpenAI image request failed: {exc}"}

    result = _decode_image_response(response, output_path)
    result.setdefault("model", selected_model)
    return result
