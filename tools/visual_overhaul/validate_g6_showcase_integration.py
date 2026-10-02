#!/usr/bin/env python3

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"{label}: missing {needle!r}")


def block_between(text: str, start_marker: str, end_marker: str, label: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: missing start marker {start_marker!r}")

    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f"{label}: missing end marker {end_marker!r}")

    return text[start:end]


def validate_color(color: dict, label: str) -> None:
    for channel in ("red", "green", "blue"):
        value = color.get(channel)
        if not isinstance(value, int) or not 0 <= value <= 31:
            raise SystemExit(f"{label}: invalid {channel}={value!r}")


def validate_lighting(path: str, label: str, min_keyframes: int = 8) -> list[dict]:
    lighting = json.loads((ROOT / path).read_text())
    if len(lighting) < min_keyframes:
        raise SystemExit(
            f"{label}: expected at least {min_keyframes} keyframes, got {len(lighting)}"
        )

    end_times = [entry.get("endTime") for entry in lighting]
    if any(not isinstance(value, int) for value in end_times):
        raise SystemExit(f"{label}: every endTime must be an integer")
    if end_times != sorted(end_times):
        raise SystemExit(f"{label}: endTime values are not sorted")
    if len(end_times) != len(set(end_times)):
        raise SystemExit(f"{label}: duplicate endTime values")

    for i, entry in enumerate(lighting):
        lights = entry.get("lights")
        if not isinstance(lights, list) or len(lights) != 4:
            raise SystemExit(f"{label} keyframe {i}: expected exactly four lights")

        for j, light in enumerate(lights):
            if not isinstance(light.get("enabled"), bool):
                raise SystemExit(
                    f"{label} keyframe {i} light {j}: enabled must be boolean"
                )
            validate_color(light.get("color", {}), f"{label} keyframe {i} light {j}")

            direction = light.get("direction", {})
            for axis in ("x", "y", "z"):
                value = direction.get(axis)
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise SystemExit(
                        f"{label} keyframe {i} light {j}: invalid direction {axis}={value!r}"
                    )

        for field in ("diffuseColor", "ambientColor", "specularColor", "emissionColor"):
            validate_color(entry.get(field, {}), f"{label} keyframe {i} {field}")

    return lighting


def require_nonempty_file(path: str, label: str) -> None:
    target = ROOT / path
    if not target.is_file() or target.stat().st_size == 0:
        raise SystemExit(f"{label}: missing or empty {path}")


def validate_eterna() -> dict:
    header_text = read_text("include/data/map_headers.h")
    header = block_between(
        header_text,
        "[MAP_HEADER_ETERNA_FOREST] = {",
        "[MAP_HEADER_FUEGO_IRONWORKS_OUTSIDE] = {",
        "Eterna map header",
    )

    expected_header_contract = (
        ".areaDataArchiveID = area_data_075",
        ".weather = OVERWORLD_WEATHER_CANOPY",
        ".cameraType = CAMERA_TYPE_ETERNA_FOREST",
        ".battleBG = BACKGROUND_FOREST",
    )
    for needle in expected_header_contract:
        require(header, needle, "Eterna map header")

    area_path = ROOT / "res/field/area_data/area_data_075.json"
    area = json.loads(area_path.read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_050",
        "mapTextureSet": "map_texture_set_074",
        "lightingSet": "lighting_set_010",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Eterna area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_074.nsbtx",
        "Eterna texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_010.json",
        "Eterna lighting",
    )

    camera_constants = read_text("include/constants/camera_types.h")
    require(camera_constants, "CAMERA_TYPE_ETERNA_FOREST", "Camera type enum")

    camera_source = read_text("src/overlay005/field_camera.c")
    camera = block_between(
        camera_source,
        "[CAMERA_TYPE_ETERNA_FOREST] = {",
        "[CAMERA_TYPE_UNUSED_16] = {",
        "Eterna camera profile",
    )
    for needle in (
        ".distance = FX32_CONST(545.0)",
        ".cameraAngle = { -F32_DEG_TO_IDX(58.0), 0, 0 }",
        ".verticalFov = F32_DEG_TO_IDX(10.9)",
        ".nearPlaneDist = CAMERA_DEFAULT_NEAR_CLIP",
        ".farPlaneDist = CAMERA_DEFAULT_FAR_CLIP",
    ):
        require(camera, needle, "Eterna camera profile")

    weather_constants = read_text("include/constants/overworld_weather.h")
    require(
        weather_constants,
        "#define OVERWORLD_WEATHER_CANOPY 23",
        "Canopy weather constant",
    )

    weather_source = read_text("src/overlay005/ov5_021D5EB8.c")
    for needle in (
        "#define DEEP_FOREST_MIST_ALPHA       8",
        "#define DEEP_FOREST_FOG_OFFSET       (0x6F6F - 1900)",
        "#define DEEP_FOREST_FOG_COLOR        GX_RGB(20, 24, 22)",
        "#define DEEP_FOREST_SCROLL_SCALE     FX32_CONST(0.75)",
    ):
        require(weather_source, needle, "Canopy weather treatment")

    fieldmap = read_text("src/overlay005/fieldmap.c")
    deep_forest = block_between(
        fieldmap,
        "static BOOL FieldMap_IsDeepForest(const FieldSystem *fieldSystem)\n{",
        "static void FieldMap_ApplySpecialAreaFog(FieldSystem *fieldSystem)",
        "Deep-forest classifier",
    )
    for needle in (
        "MAP_HEADER_ETERNA_FOREST",
        "MAP_HEADER_FULLMOON_ISLAND_FOREST",
        "MAP_HEADER_NEWMOON_ISLAND_FOREST",
    ):
        require(deep_forest, needle, "Deep-forest classifier")

    require(
        fieldmap,
        "else if (FieldMap_IsDeepForest(fieldSystem) == TRUE) {\n            v1 = sForestFieldEffectRenderers;",
        "Forest renderer routing",
    )

    renderer_constants = read_text("include/constants/field/field_effect_renderer.h")
    require(
        renderer_constants,
        "FIELD_EFFECT_RENDERER_FOREST_AMBIENCE",
        "Forest ambience renderer enum",
    )

    renderer_source = read_text("src/overlay005/field_effect_renderer.c")
    require(
        renderer_source,
        "{ FIELD_EFFECT_RENDERER_FOREST_AMBIENCE, ForestAmbienceRenderer_New, ForestAmbienceRenderer_Free }",
        "Forest ambience renderer handler",
    )

    forest_renderers = block_between(
        renderer_source,
        "const u32 sForestFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {",
        "const u32 sUndergroundFieldEffectRenderers[FIELD_EFFECT_RENDERER_COUNT + 1] = {",
        "Forest renderer list",
    )
    require(
        forest_renderers,
        "FIELD_EFFECT_RENDERER_FOREST_AMBIENCE",
        "Forest renderer list",
    )

    return {
        "map_header": "MAP_HEADER_ETERNA_FOREST",
        "area_data": "area_data_075",
        "texture_set": "map_texture_set_074",
        "lighting_set": "lighting_set_010",
        "weather": "OVERWORLD_WEATHER_CANOPY",
        "camera": "CAMERA_TYPE_ETERNA_FOREST",
        "forest_ambience_renderer": True,
        "lighting_keyframes": len(lighting),
    }



def validate_snow_region() -> dict:
    header_text = read_text("include/data/map_headers.h")

    snowpoint = block_between(
        header_text,
        "[MAP_HEADER_SNOWPOINT_CITY] = {",
        "[MAP_HEADER_SNOWPOINT_CITY_MART] = {",
        "Snowpoint City map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_014",
        ".weather = OVERWORLD_WEATHER_SNOWPOINT_CITY",
        ".battleBG = BACKGROUND_SNOW",
    ):
        require(snowpoint, needle, "Snowpoint City map header")

    route217 = block_between(
        header_text,
        "[MAP_HEADER_ROUTE_217] = {",
        "[MAP_HEADER_ROUTE_217_WEST_HOUSE] = {",
        "Route 217 map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_014",
        ".weather = OVERWORLD_WEATHER_BLIZZARD",
        ".battleBG = BACKGROUND_SNOW",
    ):
        require(route217, needle, "Route 217 map header")

    area = json.loads((ROOT / "res/field/area_data/area_data_014.json").read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_010",
        "mapTextureSet": "map_texture_set_014",
        "lightingSet": "lighting_set_011",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Snow-region area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_014.nsbtx",
        "Snow-region texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_011.json",
        "Snow-region lighting",
    )

    weather_constants = read_text("include/constants/overworld_weather.h")
    for needle in (
        "#define OVERWORLD_WEATHER_SNOWING      5",
        "#define OVERWORLD_WEATHER_HEAVY_SNOW   6",
        "#define OVERWORLD_WEATHER_BLIZZARD     7",
        "#define OVERWORLD_WEATHER_SNOWPOINT_CITY   (OVERWORLD_WEATHER_YEARLY_START + 4)",
    ):
        require(weather_constants, needle, "Snow weather constants")

    weather_source = read_text("src/overlay005/ov5_021D5EB8.c")
    for needle in (
        "#define LIGHT_SNOW_FOG_COLOR  GX_RGB(21, 26, 31)",
        "#define HEAVY_SNOW_FOG_COLOR  GX_RGB(19, 24, 31)",
        "#define BLIZZARD_FOG_COLOR    GX_RGB(18, 23, 31)",
    ):
        require(weather_source, needle, "Snow atmosphere treatment")

    return {
        "area_data": "area_data_014",
        "texture_set": "map_texture_set_014",
        "lighting_set": "lighting_set_011",
        "snowpoint_weather": "OVERWORLD_WEATHER_SNOWPOINT_CITY",
        "route_217_weather": "OVERWORLD_WEATHER_BLIZZARD",
        "lighting_keyframes": len(lighting),
    }


def validate_distortion_world() -> dict:
    header_text = read_text("include/data/map_headers.h")
    distortion = block_between(
        header_text,
        "[MAP_HEADER_DISTORTION_WORLD_1F] = {",
        "[MAP_HEADER_DISTORTION_WORLD_B1F] = {",
        "Distortion World map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_074",
        ".battleBG = BACKGROUND_DISTORTION_WORLD",
        ".weather = OVERWORLD_WEATHER_CLEAR",
    ):
        require(distortion, needle, "Distortion World map header")

    area = json.loads((ROOT / "res/field/area_data/area_data_074.json").read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_070",
        "mapTextureSet": "map_texture_set_073",
        "lightingSet": "lighting_set_009",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Distortion World area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_073.nsbtx",
        "Distortion World texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_009.json",
        "Distortion World lighting",
    )

    reference = {key: value for key, value in lighting[0].items() if key != "endTime"}
    for i, entry in enumerate(lighting[1:], start=1):
        current = {key: value for key, value in entry.items() if key != "endTime"}
        if current != reference:
            raise SystemExit(
                f"Distortion World lighting keyframe {i}: expected time-invariant lighting"
            )

    area_light_constants = read_text("include/constants/field/area_light.h")
    require(
        area_light_constants,
        "AREA_LIGHT_SET_DISTORTION_WORLD",
        "Distortion World area-light enum",
    )

    fieldmap = read_text("src/overlay005/fieldmap.c")
    for needle in (
        "if (FieldMap_InDistortionWorld(fieldSystem) == TRUE) {",
        "v1 = sDistWorldFieldEffectRenderers;",
        "case AREA_LIGHT_SET_DISTORTION_WORLD:",
        "color = GX_RGB(14, 8, 22);",
        "offset = 0x5000;",
        "densityTable = sDistortionFogDensity;",
    ):
        require(fieldmap, needle, "Distortion World integration")

    return {
        "area_data": "area_data_074",
        "texture_set": "map_texture_set_073",
        "lighting_set": "lighting_set_009",
        "battle_background": "BACKGROUND_DISTORTION_WORLD",
        "special_fog": True,
        "distortion_renderer_path": True,
        "lighting_keyframes": len(lighting),
    }



def validate_spear_pillar() -> dict:
    header_text = read_text("include/data/map_headers.h")
    header = block_between(
        header_text,
        "[MAP_HEADER_SPEAR_PILLAR] = {",
        "[MAP_HEADER_SPEAR_PILLAR_DISTORTED] = {",
        "Spear Pillar map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_060",
        ".weather = OVERWORLD_WEATHER_CLEAR_13",
        ".cameraType = CAMERA_TYPE_SPEAR_PILLAR",
        ".battleBG = BACKGROUND_MOUNTAIN",
    ):
        require(header, needle, "Spear Pillar map header")

    area = json.loads((ROOT / "res/field/area_data/area_data_060.json").read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_056",
        "mapTextureSet": "map_texture_set_059",
        "lightingSet": "lighting_set_012",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Spear Pillar area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_059.nsbtx",
        "Spear Pillar texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_012.json",
        "Spear Pillar lighting",
    )

    area_light_constants = read_text("include/constants/field/area_light.h")
    require(
        area_light_constants,
        "AREA_LIGHT_SET_SPEAR_PILLAR_GRADE",
        "Spear Pillar area-light enum",
    )

    fieldmap = read_text("src/overlay005/fieldmap.c")
    for needle in (
        "case AREA_LIGHT_SET_SPEAR_PILLAR:",
        "case AREA_LIGHT_SET_SPEAR_PILLAR_GRADE:",
        "color = GX_RGB(16, 18, 22);",
        "offset = 0x6000;",
        "densityTable = sSpearPillarFogDensity;",
    ):
        require(fieldmap, needle, "Spear Pillar integration")

    return {
        "area_data": "area_data_060",
        "texture_set": "map_texture_set_059",
        "lighting_set": "lighting_set_012",
        "camera": "CAMERA_TYPE_SPEAR_PILLAR",
        "special_fog": True,
        "lighting_keyframes": len(lighting),
    }


def validate_lakes() -> dict:
    header_text = read_text("include/data/map_headers.h")
    header = block_between(
        header_text,
        "[MAP_HEADER_LAKE_VERITY] = {",
        "[MAP_HEADER_VERITY_CAVERN] = {",
        "Lake Verity map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_062",
        ".weather = OVERWORLD_WEATHER_CLEAR",
        ".cameraType = CAMERA_TYPE_ZOOMED_IN",
        ".battleBG = BACKGROUND_FOREST",
    ):
        require(header, needle, "Lake Verity map header")

    area = json.loads((ROOT / "res/field/area_data/area_data_062.json").read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_058",
        "mapTextureSet": "map_texture_set_061",
        "lightingSet": "lighting_set_013",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Sinnoh lakes area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_061.nsbtx",
        "Sinnoh lakes texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_013.json",
        "Sinnoh lakes lighting",
    )

    area_light_constants = read_text("include/constants/field/area_light.h")
    require(
        area_light_constants,
        "AREA_LIGHT_SET_SINNOH_LAKES",
        "Sinnoh lakes area-light enum",
    )

    return {
        "area_data": "area_data_062",
        "texture_set": "map_texture_set_061",
        "lighting_set": "lighting_set_013",
        "camera": "CAMERA_TYPE_ZOOMED_IN",
        "lighting_keyframes": len(lighting),
    }


def validate_turnback_cave() -> dict:
    header_text = read_text("include/data/map_headers.h")
    header = block_between(
        header_text,
        "[MAP_HEADER_TURNBACK_CAVE_ENTRANCE] = {",
        "[MAP_HEADER_TURNBACK_CAVE_PILLAR_ROOM] = {",
        "Turnback Cave map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_076",
        ".weather = OVERWORLD_WEATHER_FOG",
        ".cameraType = CAMERA_TYPE_DEFAULT",
        ".battleBG = BACKGROUND_CAVE_3",
    ):
        require(header, needle, "Turnback Cave map header")

    area = json.loads((ROOT / "res/field/area_data/area_data_076.json").read_text())
    expected_area = {
        "mapPropSet": "prop_model_set_052",
        "mapTextureSet": "map_texture_set_075",
        "lightingSet": "lighting_set_014",
    }
    for key, expected in expected_area.items():
        actual = area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Turnback Cave area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_075.nsbtx",
        "Turnback Cave texture bank",
    )
    lighting = validate_lighting(
        "res/field/lighting/lighting_set_014.json",
        "Turnback Cave lighting",
    )

    area_light_constants = read_text("include/constants/field/area_light.h")
    require(
        area_light_constants,
        "AREA_LIGHT_SET_TURNBACK_CAVE",
        "Turnback Cave area-light enum",
    )

    return {
        "area_data": "area_data_076",
        "texture_set": "map_texture_set_075",
        "lighting_set": "lighting_set_014",
        "weather": "OVERWORLD_WEATHER_FOG",
        "lighting_keyframes": len(lighting),
    }


def validate_galactic_interiors() -> dict:
    header_text = read_text("include/data/map_headers.h")

    eterna_hq = block_between(
        header_text,
        "[MAP_HEADER_TEAM_GALACTIC_ETERNA_BUILDING_1F] = {",
        "[MAP_HEADER_TEAM_GALACTIC_ETERNA_BUILDING_2F] = {",
        "Galactic Eterna Building map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_058",
        ".cameraType = CAMERA_TYPE_INTERIOR_ORTHOGRAPHIC",
        ".battleBG = BACKGROUND_INDOORS_2",
    ):
        require(eterna_hq, needle, "Galactic Eterna Building map header")

    warehouse = block_between(
        header_text,
        "[MAP_HEADER_VEILSTONE_CITY_GALACTIC_WAREHOUSE] = {",
        "[MAP_HEADER_VEILSTONE_CITY_PRIZE_EXCHANGE] = {",
        "Galactic Warehouse map header",
    )
    for needle in (
        ".areaDataArchiveID = area_data_077",
        ".cameraType = CAMERA_TYPE_INTERIOR_ORTHOGRAPHIC",
        ".battleBG = BACKGROUND_INDOORS_2",
    ):
        require(warehouse, needle, "Galactic Warehouse map header")

    main_area = json.loads((ROOT / "res/field/area_data/area_data_058.json").read_text())
    expected_main = {
        "mapPropSet": "prop_model_set_054",
        "mapTextureSet": "map_texture_set_057",
        "lightingSet": "lighting_set_006",
    }
    for key, expected in expected_main.items():
        actual = main_area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Galactic main area data: {key} expected {expected!r}, got {actual!r}"
            )

    warehouse_area = json.loads((ROOT / "res/field/area_data/area_data_077.json").read_text())
    expected_warehouse = {
        "mapPropSet": "prop_model_set_027",
        "mapTextureSet": "map_texture_set_076",
        "lightingSet": "lighting_set_001",
    }
    for key, expected in expected_warehouse.items():
        actual = warehouse_area.get(key)
        if actual != expected:
            raise SystemExit(
                f"Galactic warehouse area data: {key} expected {expected!r}, got {actual!r}"
            )

    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_057.nsbtx",
        "Galactic main texture bank",
    )
    require_nonempty_file(
        "res/field/maps/texture_sets/map_texture_set_076.nsbtx",
        "Galactic warehouse texture bank",
    )

    main_lighting = validate_lighting(
        "res/field/lighting/lighting_set_006.json",
        "Galactic main lighting",
    )

    grade_report = json.loads(
        (ROOT / "docs/visual_overhaul/G4G_GALACTIC_GRADE_REPORT.json").read_text()
    )
    results = grade_report.get("results", {})
    for key in ("main", "lab", "warehouse"):
        result = results.get(key, {})
        if not result.get("changed_palettes"):
            raise SystemExit(f"Galactic grade report: {key} has no changed palettes")
        if not result.get("visual_textures"):
            raise SystemExit(f"Galactic grade report: {key} has no changed visual textures")

    return {
        "main_area_data": "area_data_058",
        "main_texture_set": "map_texture_set_057",
        "main_lighting_set": "lighting_set_006",
        "warehouse_area_data": "area_data_077",
        "warehouse_texture_set": "map_texture_set_076",
        "warehouse_lighting_set": "lighting_set_001",
        "main_lighting_keyframes": len(main_lighting),
        "grade_report_sections": sorted(results),
    }


def main() -> None:
    report = {
        "eterna": validate_eterna(),
        "snow_region": validate_snow_region(),
        "distortion_world": validate_distortion_world(),
        "spear_pillar": validate_spear_pillar(),
        "lakes": validate_lakes(),
        "turnback_cave": validate_turnback_cave(),
        "galactic_interiors": validate_galactic_interiors(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
