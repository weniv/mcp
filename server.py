from mcp.server.fastmcp import FastMCP
import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# MCP 서버 생성
mcp = FastMCP(name="enhanced_server")

BASE_PATH = "c:/test"

# 기본 폴더 생성 (없으면)
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

# ========== 폴더 관련 기능 ==========


@mcp.tool()
def create_folder(folder_name: str) -> str:
    """
    c:/test/ 아래 폴더를 생성합니다.

    Parameters
    ----------
    folder_name : str
        생성할 폴더 이름

    Returns
    -------
    str
        생성 결과 메시지
    """
    folder_path = os.path.join(BASE_PATH, folder_name)
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return f"폴더 '{folder_name}' 가 생성되었습니다."
        else:
            return f"폴더 '{folder_name}' 는 이미 존재합니다."
    except Exception as e:
        return f"폴더 생성 중 오류 발생: {str(e)}"


@mcp.tool()
def delete_folder(folder_name: str, force: bool = False) -> str:
    """
    c:/test/ 아래 폴더를 삭제합니다.

    Parameters
    ----------
    folder_name : str
        삭제할 폴더 이름
    force : bool
        True일 경우 내용이 있어도 강제 삭제

    Returns
    -------
    str
        삭제 결과 메시지
    """
    folder_path = os.path.join(BASE_PATH, folder_name)
    try:
        if os.path.exists(folder_path):
            if force:
                shutil.rmtree(folder_path)
                return f"폴더 '{folder_name}' 와 모든 내용이 삭제되었습니다."
            else:
                os.rmdir(folder_path)
                return f"폴더 '{folder_name}' 가 삭제되었습니다."
        else:
            return f"폴더 '{folder_name}' 는 존재하지 않습니다."
    except OSError as e:
        if "Directory not empty" in str(e):
            return f"폴더 '{folder_name}' 가 비어있지 않습니다. force=True로 강제 삭제하세요."
        return f"폴더 삭제 중 오류 발생: {str(e)}"
    except Exception as e:
        return f"폴더 삭제 중 오류 발생: {str(e)}"


@mcp.tool()
def list_folders() -> list:
    """
    c:/test/ 아래 폴더 목록을 반환합니다.

    Returns
    -------
    list
        폴더 목록
    """
    try:
        folders = [
            f
            for f in os.listdir(BASE_PATH)
            if os.path.isdir(os.path.join(BASE_PATH, f))
        ]
        return folders
    except Exception as e:
        return [f"오류 발생: {str(e)}"]


# ========== 파일 관련 기능 ==========


@mcp.tool()
def create_file(file_name: str, content: str = "", folder_name: str = "") -> str:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 파일을 생성합니다.

    Parameters
    ----------
    file_name : str
        생성할 파일 이름
    content : str
        파일 내용 (기본값: 빈 문자열)
    folder_name : str
        폴더 이름 (기본값: 빈 문자열, 루트에 생성)

    Returns
    -------
    str
        생성 결과 메시지
    """
    try:
        if folder_name:
            file_path = os.path.join(BASE_PATH, folder_name, file_name)
            # 폴더가 없으면 생성
            folder_path = os.path.join(BASE_PATH, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        else:
            file_path = os.path.join(BASE_PATH, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        location = f"/{folder_name}/" if folder_name else "/"
        return f"파일 '{file_name}' 가 {location}에 생성되었습니다."
    except Exception as e:
        return f"파일 생성 중 오류 발생: {str(e)}"


@mcp.tool()
def read_file(file_name: str, folder_name: str = "") -> str:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 파일을 읽습니다.

    Parameters
    ----------
    file_name : str
        읽을 파일 이름
    folder_name : str
        폴더 이름 (기본값: 빈 문자열, 루트에서 읽기)

    Returns
    -------
    str
        파일 내용 또는 오류 메시지
    """
    try:
        if folder_name:
            file_path = os.path.join(BASE_PATH, folder_name, file_name)
        else:
            file_path = os.path.join(BASE_PATH, file_name)

        if not os.path.exists(file_path):
            return f"파일 '{file_name}' 를 찾을 수 없습니다."

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content
    except Exception as e:
        return f"파일 읽기 중 오류 발생: {str(e)}"


@mcp.tool()
def write_file(
    file_name: str, content: str, folder_name: str = "", append: bool = False
) -> str:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 파일에 내용을 씁니다.

    Parameters
    ----------
    file_name : str
        쓸 파일 이름
    content : str
        파일에 쓸 내용
    folder_name : str
        폴더 이름 (기본값: 빈 문자열)
    append : bool
        True일 경우 내용을 추가, False일 경우 덮어쓰기

    Returns
    -------
    str
        쓰기 결과 메시지
    """
    try:
        if folder_name:
            file_path = os.path.join(BASE_PATH, folder_name, file_name)
            # 폴더가 없으면 생성
            folder_path = os.path.join(BASE_PATH, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        else:
            file_path = os.path.join(BASE_PATH, file_name)

        mode = "a" if append else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)

        action = "추가" if append else "덮어쓰기"
        location = f"/{folder_name}/" if folder_name else "/"
        return f"파일 '{file_name}' 에 내용을 {action} 했습니다. (위치: {location})"
    except Exception as e:
        return f"파일 쓰기 중 오류 발생: {str(e)}"


@mcp.tool()
def delete_file(file_name: str, folder_name: str = "") -> str:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 파일을 삭제합니다.

    Parameters
    ----------
    file_name : str
        삭제할 파일 이름
    folder_name : str
        폴더 이름 (기본값: 빈 문자열)

    Returns
    -------
    str
        삭제 결과 메시지
    """
    try:
        if folder_name:
            file_path = os.path.join(BASE_PATH, folder_name, file_name)
        else:
            file_path = os.path.join(BASE_PATH, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            location = f"/{folder_name}/" if folder_name else "/"
            return f"파일 '{file_name}' 가 {location}에서 삭제되었습니다."
        else:
            return f"파일 '{file_name}' 를 찾을 수 없습니다."
    except Exception as e:
        return f"파일 삭제 중 오류 발생: {str(e)}"


@mcp.tool()
def list_files(folder_name: str = "") -> list:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 파일 목록을 반환합니다.

    Parameters
    ----------
    folder_name : str
        폴더 이름 (기본값: 빈 문자열, 루트 폴더)

    Returns
    -------
    list
        파일 목록
    """
    try:
        if folder_name:
            target_path = os.path.join(BASE_PATH, folder_name)
        else:
            target_path = BASE_PATH

        if not os.path.exists(target_path):
            return [f"폴더 '{folder_name}' 를 찾을 수 없습니다."]

        files = [
            f
            for f in os.listdir(target_path)
            if os.path.isfile(os.path.join(target_path, f))
        ]
        return files
    except Exception as e:
        return [f"오류 발생: {str(e)}"]


# ========== 디렉토리 구조 출력 ==========


@mcp.tool()
def show_directory_tree(folder_name: str = "") -> str:
    """
    c:/test/ 또는 c:/test/폴더명/ 아래 디렉토리 구조를 트리 형태로 출력합니다.

    Parameters
    ----------
    folder_name : str
        폴더 이름 (기본값: 빈 문자열, 루트부터 출력)

    Returns
    -------
    str
        디렉토리 트리 구조
    """

    def generate_tree(path, prefix="", is_last=True):
        items = []
        try:
            entries = sorted(os.listdir(path))
            dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
            all_items = dirs + files

            for i, item in enumerate(all_items):
                is_last_item = i == len(all_items) - 1
                current_prefix = "└── " if is_last_item else "├── "
                items.append(f"{prefix}{current_prefix}{item}")

                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    extension = "    " if is_last_item else "│   "
                    items.extend(
                        generate_tree(item_path, prefix + extension, is_last_item)
                    )

        except PermissionError:
            items.append(f"{prefix}└── [권한 없음]")
        except Exception as e:
            items.append(f"{prefix}└── [오류: {str(e)}]")

        return items

    try:
        if folder_name:
            target_path = os.path.join(BASE_PATH, folder_name)
            root_name = folder_name
        else:
            target_path = BASE_PATH
            root_name = "test"

        if not os.path.exists(target_path):
            return f"폴더 '{folder_name}' 를 찾을 수 없습니다."

        tree_lines = [root_name]
        tree_lines.extend(generate_tree(target_path))

        return "\n".join(tree_lines)
    except Exception as e:
        return f"디렉토리 트리 생성 중 오류 발생: {str(e)}"


# ========== 크롤링 기능 ==========


@mcp.tool()
def simple_crawl(url: str, save_to_file: str = "", folder_name: str = "") -> str:
    """
    주어진 URL을 크롤링하여 텍스트 내용을 추출합니다.

    Parameters
    ----------
    url : str
        크롤링할 URL
    save_to_file : str
        저장할 파일 이름 (기본값: 빈 문자열, 저장하지 않음)
    folder_name : str
        저장할 폴더 이름 (기본값: 빈 문자열)

    Returns
    -------
    str
        크롤링 결과 또는 오류 메시지
    """
    try:
        # User-Agent 설정
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.content, "html.parser")

        # 불필요한 태그 제거
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()

        # 텍스트 추출
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        clean_text = "\n".join(lines)

        # 기본 정보
        title = soup.find("title")
        title_text = title.get_text().strip() if title else "제목 없음"

        result = f"URL: {url}\n제목: {title_text}\n크롤링 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{clean_text}"

        # 파일 저장
        if save_to_file:
            if folder_name:
                file_path = os.path.join(BASE_PATH, folder_name, save_to_file)
                folder_path = os.path.join(BASE_PATH, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            else:
                file_path = os.path.join(BASE_PATH, save_to_file)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)

            location = f"/{folder_name}/" if folder_name else "/"
            return f"크롤링 완료! 결과가 '{save_to_file}' 파일에 저장되었습니다. (위치: {location})\n\n미리보기:\n{result[:500]}..."

        return result[:1000] + "..." if len(result) > 1000 else result

    except requests.RequestException as e:
        return f"HTTP 요청 오류: {str(e)}"
    except Exception as e:
        return f"크롤링 중 오류 발생: {str(e)}"


@mcp.tool()
def crawl_links(url: str, save_to_file: str = "", folder_name: str = "") -> str:
    """
    주어진 URL에서 모든 링크를 추출합니다.

    Parameters
    ----------
    url : str
        크롤링할 URL
    save_to_file : str
        저장할 파일 이름 (기본값: 빈 문자열, 저장하지 않음)
    folder_name : str
        저장할 폴더 이름 (기본값: 빈 문자열)

    Returns
    -------
    str
        링크 목록 또는 오류 메시지
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # 모든 링크 추출
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            text = a_tag.get_text(strip=True)

            # 절대 URL로 변환
            absolute_url = urljoin(url, href)

            # 유효한 URL인지 확인
            parsed = urlparse(absolute_url)
            if parsed.scheme in ["http", "https"]:
                links.append(
                    {"url": absolute_url, "text": text[:100] if text else "텍스트 없음"}
                )

        # 중복 제거
        unique_links = []
        seen_urls = set()
        for link in links:
            if link["url"] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link["url"])

        # 결과 포맷팅
        result_lines = [
            f"URL: {url}",
            f"링크 추출 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"총 {len(unique_links)}개의 고유 링크 발견\n",
        ]

        for i, link in enumerate(unique_links, 1):
            result_lines.append(f"{i}. {link['text']}")
            result_lines.append(f"   → {link['url']}\n")

        result = "\n".join(result_lines)

        # 파일 저장
        if save_to_file:
            if folder_name:
                file_path = os.path.join(BASE_PATH, folder_name, save_to_file)
                folder_path = os.path.join(BASE_PATH, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            else:
                file_path = os.path.join(BASE_PATH, save_to_file)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)

            location = f"/{folder_name}/" if folder_name else "/"
            return f"링크 추출 완료! 결과가 '{save_to_file}' 파일에 저장되었습니다. (위치: {location})\n\n미리보기:\n{result[:500]}..."

        return result[:1000] + "..." if len(result) > 1000 else result

    except requests.RequestException as e:
        return f"HTTP 요청 오류: {str(e)}"
    except Exception as e:
        return f"링크 추출 중 오류 발생: {str(e)}"


@mcp.tool()
def read_hwp(file_name: str) -> str:
    """한글 문서(.hwp)를 읽어 텍스트로 반환합니다.

    olefile 라이브러리를 사용하여 한글 문서의 텍스트 내용을 추출합니다.

    Args:
        file_name (str): 읽을 한글 문서의 이름
            예: 'document.hwp'

    Returns:
        str: 한글 문서에서 추출한 텍스트 내용 또는 오류 메시지
    """
    import os
    import olefile

    # 상대 경로인 경우 현재 디렉토리 기준으로 절대 경로 변환
    file_path = os.path.join("c:/test", file_name)

    try:
        # 한글 파일 열기
        if not olefile.isOleFile(file_path):
            return f"오류: '{file_path}'는 올바른 한글 문서 형식이 아닙니다."

        ole = olefile.OleFileIO(file_path)

        # 텍스트 스트림 읽기
        if ole.exists("PrvText"):
            text_stream = ole.openstream("PrvText")
            text_data = text_stream.read().decode("utf-16-le", errors="replace")
            ole.close()
            return text_data
        else:
            ole.close()
            return "텍스트 내용을 추출할 수 없습니다. 지원되지 않는 한글 문서 형식일 수 있습니다."

    except Exception as e:
        return f"한글 문서 읽기 오류: {str(e)}"


@mcp.tool()
def write_md_to_hwpx(md_content: str, output_filename: str) -> str:
    """
    마크다운 문자열을 .hwpx 파일로 변환합니다.
    간단한 구조로, 책 예제용 기본 기능만 제공합니다.
    """
    import os
    import tempfile
    import shutil
    from gen import create_mimetype_file, create_settings_xml, create_version_xml
    from gen import create_preview_text, create_container_files, create_content_hpf
    from gen import create_header_xml, create_section_xml
    from bs4 import BeautifulSoup
    import markdown
    import zipfile

    try:
        # 임시 폴더 생성
        temp_dir = tempfile.mkdtemp()

        # 마크다운 → HTML → soup
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, "html.parser")

        # 제목 추출
        h1 = soup.find("h1")
        title = h1.text if h1 else "문서"

        # 구조 생성
        os.makedirs(os.path.join(temp_dir, "META-INF"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Contents"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Preview"), exist_ok=True)

        # 각 구성 요소 생성
        create_mimetype_file(temp_dir)
        create_settings_xml(temp_dir)
        create_version_xml(temp_dir)
        create_preview_text(temp_dir, soup)
        create_container_files(temp_dir)
        create_content_hpf(temp_dir, title)
        create_header_xml(temp_dir)
        create_section_xml(temp_dir, soup)

        # 압축 → HWPX 저장
        output_path = os.path.join("c:/test", output_filename)
        with zipfile.ZipFile(output_path, "w") as zip_file:
            zip_file.write(
                os.path.join(temp_dir, "mimetype"),
                "mimetype",
                compress_type=zipfile.ZIP_STORED,
            )
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file != "mimetype":
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_file.write(
                            file_path, arcname, compress_type=zipfile.ZIP_DEFLATED
                        )

        shutil.rmtree(temp_dir)
        return f"{output_filename} 파일로 변환 완료!"
    except Exception as e:
        return f"변환 실패: {e}"


# 서버 실행
if __name__ == "__main__":
    mcp.run()
