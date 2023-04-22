from enum import Enum


class Activities(Enum):
    """Enum for activities"""

    ROTARY_DRILLING = "rotary_drilling"
    SLIDE_DRILLING = "slide_drilling"
    TRIPPING_IN = "tripping_in"
    TRIPPING_OUT = "tripping_out"
    CASING = "casing"
    CIRCULATING = "circulating"


class BGAppTasks(Enum):
    """Enum for app tasks"""

    CALCULATE_BG = ("calculate_bg", ["start_ts", "end_ts", "asset_id", "task"])
    RETURN_CACHE = ("return_cache", ["asset_id", "task"])
    DELETE_CACHE = ("delete_cache", ["asset_id", "task"])
    DELETE_BG_COLLECTION = ("delete_bg_collection", ["asset_id", "task"])
    RETURN_APP_SETTING = ("get_app_setting", ["asset_id", "task"])
    EDIT_APP_SETTING = ("edit_app_setting", ["asset_id", "task", "new_setting"])

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        obj.items_needed = args[1]
        return obj


if __name__ == "__main__":  # pragma: no cover
    # print(obj.get("ITEMS_NEEDED_TO_CALCULATE_BG"))
    # print(BGAppTasks.get_objects().get("ITEMS_NEEDED_TO_CALCULATE_BG"))
    print(BGAppTasks.CALCULATE_BG.value)
    print(BGAppTasks.RETURN_CACHE.value)
    print(BGAppTasks.DELETE_CACHE.value)
    print(BGAppTasks.CALCULATE_BG.items_needed)
    print(BGAppTasks.SETTING.items_needed)
