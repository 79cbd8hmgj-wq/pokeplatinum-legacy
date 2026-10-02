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

    texture_path = ROOT / "res/field/maps/texture_sets/map_texture_set_074.nsbtx"
    if not texture_path.is_file() or texture_path.stat().st_size == 0:
        raise SystemExit("Eterna texture bank map_texture_set_074.nsbtx is missing or empty")

    lighting_path = ROOT / "res/field/lighting/lighting_set_010.json"
    lighting = json.loads(lighting_path.read_text())
    if len(lighting) < 8:
        raise SystemExit(f"Eterna lighting: expected a full day cycle, got {len(lighting)} keyframes")

    end_times = [entry.get("endTime") for entry in lighting]
    if any(not isinstance(value, int) for value in end_times):
        raise SystemExit("Eterna lighting: every endTime must be an integer")
    if end_times != sorted(end_times):
        raise SystemExit("Eterna lighting: endTime values are not sorted")
    if len(end_times) != len(set(end_times)):
        raise SystemExit("Eterna lighting: duplicate endTime values")

    for i, entry in enumerate(lighting):
        lights = entry.get("lights")
        if not isinstance(lights, list) or len(lights) != 4:
            raise SystemExit(f"Eterna lighting keyframe {i}: expected exactly four lights")

        for j, light in enumerate(lights):
            if not isinstance(light.get("enabled"), bool):
                raise SystemExit(
                    f"Eterna lighting keyframe {i} light {j}: enabled must be boolean"
                )
            validate_color(light.get("color", {}), f"Eterna lighting keyframe {i} light {j}")

            direction = light.get("direction", {})
            for axis in ("x", "y", "z"):
                value = direction.get(axis)
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise SystemExit(
                        f"Eterna lighting keyframe {i} light {j}: invalid direction {axis}={value!r}"
                    )

        for field in ("diffuseColor", "ambientColor", "specularColor", "emissionColor"):
            validate_color(entry.get(field, {}), f"Eterna lighting keyframe {i} {field}")

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


def main() -> None:
    report = {"eterna": validate_eterna()}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
