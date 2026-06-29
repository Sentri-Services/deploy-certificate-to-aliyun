from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_base_domain(domain: str) -> str:
    """
    Extract the root/base domain (second-level domain) from a given domain name.
    Handles common double-level TLD suffixes (e.g. .com.cn, .co.uk).
    """
    parts = domain.strip().split(".")
    if len(parts) <= 2:
        return domain
    # Common double-level TLDs
    if parts[-2] in ("com", "net", "org", "co", "gov", "edu") and parts[-1] in ("cn", "uk", "jp", "tw", "hk"):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


class Settings(BaseSettings):
    aliyun_access_key_id: str = Field(validation_alias="ALIYUN_ACCESS_KEY_ID")
    aliyun_access_key_secret: str = Field(validation_alias="ALIYUN_ACCESS_KEY_SECRET")
    aliyun_cdn_domains: str = Field(validation_alias="ALIYUN_CDN_DOMAINS")
    working_dir: Path = Field(validation_alias="WORKING_DIR")
    email: str = Field(validation_alias="EMAIL")
    dry_run: bool = Field(default=False, validation_alias="DRY_RUN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cdn_domains_list(self) -> List[str]:
        return [d.strip() for d in self.aliyun_cdn_domains.split(",") if d.strip()]

    @property
    def domains_list(self) -> List[str]:
        # Automatically extract unique root domains from CDN domains
        extracted = []
        for cdn_domain in self.cdn_domains_list:
            base = get_base_domain(cdn_domain)
            if base not in extracted:
                extracted.append(base)
        return extracted

    @property
    def ssl_domains_list(self) -> List[str]:
        # Automatically construct wildcard domain SANs for each root domain
        # e.g., for example.com -> example.com, *.example.com
        ssl_list = []
        for domain in self.domains_list:
            ssl_list.extend([domain, f"*.{domain}"])
        return ssl_list


def get_settings() -> Settings:
    return Settings()
