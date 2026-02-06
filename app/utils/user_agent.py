from typing import Dict


def parse_user_agent(user_agent: str) -> Dict[str, str]:
    ua = user_agent or ""

    browser = "Unknown"
    if "Edg/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "Chrome/" in ua and "Safari/" in ua:
        browser = "Chrome"
    elif "Firefox/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua and "Chrome/" not in ua:
        browser = "Safari"
    elif "MSIE" in ua or "Trident/" in ua:
        browser = "Internet Explorer"

    os_name = "Unknown"
    if "Windows NT 10" in ua:
        os_name = "Windows 10/11"
    elif "Windows NT 6.3" in ua:
        os_name = "Windows 8.1"
    elif "Windows NT 6.2" in ua:
        os_name = "Windows 8"
    elif "Windows NT 6.1" in ua:
        os_name = "Windows 7"
    elif "Mac OS X" in ua and "like Mac OS X" not in ua:
        os_name = "macOS"
    elif "Android" in ua:
        os_name = "Android"
    elif "iPhone" in ua or "iPad" in ua:
        os_name = "iOS"
    elif "Linux" in ua:
        os_name = "Linux"

    return {"browser": browser, "os": os_name}
