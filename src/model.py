from pydantic import BaseModel, Field

ACCEPTED_ACTIVITIES = ["rotary_drilling", "slide_drilling"]


class Settings(BaseModel):
    PROVIDER = "osu_provider"
    WITS_COLLECTION = "wits"
    DOWN_HOLE_MOTOR_COLLECTION = "dhm_data"
    DRILL_STRING_COLLECTION = "ds_data"
    CACHE_BUCKET_NAME = "bgapptestdemo"
    CACHE_FILE_NAME = "cache.json"
    CACHE_REGION_NAME = "us-east-2"


SETTINGS = Settings()


class Wits(BaseModel):
    timestamp: int = None
    drill_string_id: str = None
    md: float = None
    wob: float = None
    rpm: float = None
    rop: float = None
    flowrate: float = None

    class Config:
        allow_population_by_field_name = True

    @staticmethod
    def parse_wits(data: dict) -> dict:
        accepted_format = dict(
            timestamp=data.get("timestamp", None),
            drill_string_id=data.get("drill_string_id", None),
            md=data.get("data", {}).get("md"),
            wob=data.get("data", {}).get("wob"),
            rpm=data.get("data", {}).get("rpm", None),
            rop=data.get("data", {}).get("rop", None),
            flowrate=data.get("data", {}).get("flowrate", None),
        )
        return Wits(**accepted_format)

    # check if all the fields are available in the record and not None in record data.
    # use Wits.__fields__.keys() to get the fields
    @staticmethod
    def check_fields(data: dict) -> bool:
        fields = Wits.__fields__.keys()
        # exclude drill_string_id and timestamp from the fields
        fields = [
            field for field in fields if field not in ["drill_string_id", "timestamp"]
        ]
        return all([data.get("data", {}).get(field) is not None for field in fields])

    @staticmethod
    def check_activity(data: dict) -> bool:
        if data.get("activity") in ACCEPTED_ACTIVITIES:
            return True


class DrillSting(BaseModel):
    drill_string_id: str = Field(..., alias="_drill_string_id")
    down_hole_motor_id: str = None

    class Config:
        allow_population_by_field_name = True


class DownholeMotor(BaseModel):
    motor_id: str = None
    motor_cof: float = None

    class Config:
        allow_population_by_field_name = True


class BitGradeData(BaseModel):
    bg: float = None


class BitGrade(BaseModel):
    id: str = None
    timestamp: int = None
    provider: str = None
    drillstring_id: str = None
    data: BitGradeData
