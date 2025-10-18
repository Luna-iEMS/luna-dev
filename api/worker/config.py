# worker/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os

class Settings(BaseSettings):
    pg_dsn: str = Field("postgresql://postgres:postgres@db:5432/luna", alias="PG_DSN")
    sim_smartmeter_interval_sec: int = Field(60, alias="SIM_SMARTMETER_INTERVAL_SEC")
    sim_market_interval_sec: int = Field(300, alias="SIM_MARKET_INTERVAL_SEC")
    sim_markets: str = Field("EEX,APX", alias="SIM_MARKETS")
    sim_products: str = Field("BASE,PEAK", alias="SIM_PRODUCTS")

    # lokale CSV-Ablage (optional), robust resolver
    sim_output: Path = Field(Path("/data/sim"), alias="SIM_OUTPUT")

    # MinIO (optional)
    use_minio: bool = Field(False, alias="SIM_USE_MINIO")
    minio_endpoint: str = Field("minio:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field("minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field("sim", alias="MINIO_BUCKET")

    # Meter-Liste
    sim_meters: str = Field("MTR-1,MTR-2", alias="SIM_METERS")

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def resolve_output_dir(self) -> Path:
        p = Path(os.path.expandvars(str(self.sim_output))).expanduser()
        if not p.is_absolute():
            base = Path(os.environ.get("WORKDIR", Path.cwd()))
            p = (base / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

settings = Settings()
