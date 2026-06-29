from .config import get_settings
from .lego import obtain_certificates, get_cert_name
from .aliyun import get_aliyun_client, upload_certificate
import shutil


def main() -> None:
    # 1. Load settings and validate
    settings = get_settings()

    # 2. Invoke lego to obtain/check certificates
    obtain_certificates(settings)

    # 3. Initialize Aliyun client
    client = get_aliyun_client(settings)

    # 4. Upload certificates for each CDN domain
    for cdn_domain in settings.cdn_domains_list:
        matched_domain = None
        for domain in settings.domains_list:
            if cdn_domain.endswith(domain):
                matched_domain = domain
                break

        if not matched_domain:
            print(
                f"Skipping upload for {cdn_domain}: No matching domain in DOMAINS config"
            )
            continue

        cert_name = get_cert_name(matched_domain, settings.ssl_domains_list)
        cert_path = settings.working_dir / f".lego/certificates/{cert_name}.crt"
        key_path = settings.working_dir / f".lego/certificates/{cert_name}.key"

        assert cert_path.exists(), f"Certificate file {cert_path} does not exist"
        assert key_path.exists(), f"Key file {key_path} does not exist"
        try:
            print(f"Uploading certificate {cert_name} for CDN domain {cdn_domain}")
            upload_certificate(
                client, cdn_domain, cert_path, key_path, dry_run=settings.dry_run
            )
        except Exception as e:
            print(f"Failed to upload certificate for {cdn_domain}: {e}")
            continue

    # 5. Clean up .lego directory after successful upload
    lego_dir = settings.working_dir / ".lego"
    if lego_dir.exists():
        print(f"Removing .lego directory at {lego_dir}")
        shutil.rmtree(lego_dir)


if __name__ == "__main__":
    main()
