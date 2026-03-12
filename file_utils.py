"""Utility functions for downloading and managing files from Claude API responses."""

import os
from pathlib import Path


def extract_file_ids(response):
    """Extract file IDs from a Claude API response.

    Searches through response content blocks for code execution results
    that contain file references.

    Args:
        response: A Claude API response object.

    Returns:
        A list of file ID strings found in the response.
    """
    file_ids = []
    for content in response.content:
        if content.type == "code_execution_result":
            if hasattr(content, "content") and isinstance(content.content, list):
                for item in content.content:
                    if hasattr(item, "type") and item.type == "file":
                        file_ids.append(item.file_id)
        elif content.type == "tool_result":
            if hasattr(content, "content") and isinstance(content.content, list):
                for item in content.content:
                    if hasattr(item, "type") and item.type == "file":
                        file_ids.append(item.file_id)
    return file_ids


def get_file_info(client, file_id):
    """Get metadata about a file from the Anthropic Files API.

    Args:
        client: An Anthropic client instance.
        file_id: The ID of the file to retrieve info for.

    Returns:
        A dict with filename, size, and created_at, or None on error.
    """
    try:
        file_metadata = client.beta.files.retrieve(file_id=file_id)
        return {
            "filename": file_metadata.filename,
            "size": file_metadata.size_bytes,
            "created_at": file_metadata.created_at,
        }
    except Exception as e:
        print(f"Error retrieving file info: {e}")
        return None


def download_file(client, file_id, output_path):
    """Download a file from the Anthropic Files API.

    Args:
        client: An Anthropic client instance.
        file_id: The ID of the file to download.
        output_path: Local path where the file should be saved.

    Returns:
        True if download succeeded, False otherwise.
    """
    try:
        file_content = client.beta.files.content(file_id=file_id)
        with open(output_path, "wb") as f:
            f.write(file_content.read())
        return True
    except Exception as e:
        print(f"Error downloading file {file_id}: {e}")
        return False


def download_all_files(client, response, output_dir="outputs", prefix=""):
    """Download all files from a Claude API response.

    Args:
        client: An Anthropic client instance.
        response: A Claude API response object.
        output_dir: Directory to save files to.
        prefix: Prefix to add to filenames.

    Returns:
        A list of dicts with file_id, output_path, success, and size.
    """
    file_ids = extract_file_ids(response)
    results = []

    os.makedirs(output_dir, exist_ok=True)

    for file_id in file_ids:
        info = get_file_info(client, file_id)
        if info:
            filename = f"{prefix}{info['filename']}"
        else:
            filename = f"{prefix}{file_id}"

        output_path = os.path.join(output_dir, filename)
        success = download_file(client, file_id, output_path)

        size = os.path.getsize(output_path) if success else 0
        results.append(
            {
                "file_id": file_id,
                "output_path": output_path,
                "success": success,
                "size": size,
            }
        )

    return results


def print_download_summary(results):
    """Print a summary of download results.

    Args:
        results: List of result dicts from download_all_files.
    """
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    total_size = sum(r["size"] for r in results if r["success"])

    print(f"\nDownload Summary: {successful}/{total} files downloaded")
    print(f"Total size: {total_size / 1024:.1f} KB")

    for r in results:
        status = "OK" if r["success"] else "FAILED"
        size_str = f"{r['size'] / 1024:.1f} KB" if r["success"] else "N/A"
        print(f"  [{status}] {r['output_path']} ({size_str})")
