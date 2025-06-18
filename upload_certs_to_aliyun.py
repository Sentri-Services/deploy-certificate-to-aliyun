import datetime
import os
from pathlib import Path
from aliyunsdkcore.client import AcsClient
from aliyunsdkcdn.request.v20180510 import SetCdnDomainSSLCertificateRequest


def get_env_var(key):
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} not set")
    return value


def upload_certificate(client, domain_name, cert_path, key_path):
    if not cert_path.exists() or not key_path.exists():
        raise FileNotFoundError(
            f"Certificate or key file for domain {domain_name} is missing or empty"
        )

    with open(cert_path, "r") as f:
        cert = f.read()

    with open(key_path, "r") as f:
        key = f.read()

    request = SetCdnDomainSSLCertificateRequest.SetCdnDomainSSLCertificateRequest()
    # CDN加速域名
    request.set_DomainName(domain_name)
    # 证书名称
    request.set_CertName(domain_name + datetime.datetime.now().strftime("%Y%m%d"))
    request.set_CertType("upload")
    request.set_SSLProtocol("on")
    request.set_SSLPub(cert)
    request.set_SSLPri(key)
    request.set_CertRegion("cn-hangzhou")

    response = client.do_action_with_exception(request)
    print(str(response, encoding="utf-8"))


def main():
    access_key_id = get_env_var("ALIYUN_ACCESS_KEY_ID")
    access_key_secret = get_env_var("ALIYUN_ACCESS_KEY_SECRET")
    domains = get_env_var("DOMAINS").split(",")
    cdn_domains = get_env_var("ALIYUN_CDN_DOMAINS").split(",")
    working_dir = get_env_var("WORKING_DIR")
    working_dir = Path(working_dir)
    assert working_dir.exists()

    client = AcsClient(access_key_id, access_key_secret, "cn-hangzhou")

    for cdn_domain in cdn_domains:
        for domain in domains:
            if cdn_domain.endswith(domain):
                break
        cert_path = working_dir / f".lego/certificates/{domain}.crt"
        key_path = working_dir / f".lego/certificates/{domain}.key"

        assert cert_path.exists(), f"Certificate file {cert_path} does not exist"
        assert key_path.exists(), f"Key file {key_path} does not exist"
        upload_certificate(client, cdn_domain, cert_path, key_path)


if __name__ == "__main__":
    main()
