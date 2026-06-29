import datetime
from pathlib import Path
from aliyunsdkcore.client import AcsClient
from aliyunsdkcdn.request.v20180510 import SetCdnDomainSSLCertificateRequest
from .config import Settings


def get_aliyun_client(settings: Settings) -> AcsClient:
    return AcsClient(
        settings.aliyun_access_key_id,
        settings.aliyun_access_key_secret,
        "cn-hangzhou"
    )


def upload_certificate(
    client: AcsClient,
    domain_name: str,
    cert_path: Path,
    key_path: Path,
    dry_run: bool = False,
) -> None:
    if not cert_path.exists() or not key_path.exists():
        raise FileNotFoundError(
            f"Certificate or key file for domain {domain_name} is missing or empty"
        )

    with open(cert_path, "r") as f:
        cert = f.read()

    with open(key_path, "r") as f:
        key = f.read()

    if dry_run:
        print(
            f"[DRY RUN] Would upload certificate for {domain_name} with CertName: {domain_name}-{datetime.datetime.now().strftime('%Y%m%d')}"
        )
        print(f"[DRY RUN] Cert path: {cert_path}")
        print(f"[DRY RUN] Key path: {key_path}")
        return

    request = SetCdnDomainSSLCertificateRequest.SetCdnDomainSSLCertificateRequest()
    # CDN加速域名
    request.set_DomainName(domain_name)
    # 证书名称
    request.set_CertName(
        domain_name + "-" + datetime.datetime.now().strftime("%Y%m%d")
    )
    request.set_CertType("upload")
    request.set_SSLProtocol("on")
    request.set_SSLPub(cert)
    request.set_SSLPri(key)
    request.set_CertRegion("cn-hangzhou")

    response = client.do_action_with_exception(request)
    print(str(response, encoding="utf-8"))
