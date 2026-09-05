from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实IP。

    生产部署在 Nginx 之后，优先取 X-Real-IP（由 Nginx 用 $remote_addr 覆盖写入，
    不可被客户端伪造）；X-Forwarded-For 的首个元素可能是客户端伪造的，仅作兜底。
    """
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
