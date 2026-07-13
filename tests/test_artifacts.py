import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module(
    "product_shots_validator",
    "skills/product-shots-image-gen/scripts/validate_artifacts.py",
)
fit_canvas = load_module(
    "product_shots_fit_canvas",
    "skills/product-shots-image-gen/scripts/fit_canvas.py",
)


class ArtifactTests(unittest.TestCase):
    def test_detects_extension_content_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.jpeg"
            Image.new("RGB", (100, 100), "white").save(path, "PNG")
            result = validator.validate_image(path)
        self.assertIn("does not match PNG", result["errors"][0])

    def test_white_border_and_occupancy_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "main.png"
            image = Image.new("RGB", (100, 100), "white")
            for y in range(10, 90):
                for x in range(15, 85):
                    image.putpixel((x, y), (10, 10, 10))
            image.save(path)
            result = validator.validate_image(
                path, require_white_border=True, min_occupancy=0.75
            )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["white_border_fraction"], 1.0)
        self.assertEqual(result["occupancy_heuristic"]["height_fraction"], 0.8)

    def test_manifest_reports_missing_slot_and_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path = root / "main.png"
            Image.new("RGB", (20, 20), "white").save(image_path)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workflow": "amazon-listing",
                        "mode": "builtin",
                        "status": "complete",
                        "artifacts": [
                            {"slot": "main", "status": "complete", "path": "main.png"}
                        ],
                    }
                )
            )
            result, paths = validator.validate_manifest(
                manifest_path, {"main", "secondary-01"}
            )
        self.assertEqual(paths, [image_path])
        self.assertTrue(any("has no prompt" in error for error in result["errors"]))
        self.assertTrue(any("secondary-01" in error for error in result["errors"]))

    def test_fit_canvas_modes_produce_exact_dimensions(self):
        source = Image.new("RGB", (200, 100), "red")
        contained = fit_canvas.fit_image(source, 100, 100, "contain", "#ffffff")
        covered = fit_canvas.fit_image(source, 100, 100, "cover", "#ffffff")
        self.assertEqual(contained.size, (100, 100))
        self.assertEqual(covered.size, (100, 100))
        self.assertEqual(contained.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(covered.getpixel((0, 0)), (255, 0, 0))

    def test_seven_slot_manifest_smoke(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = []
            slots = ["main"] + [f"secondary-{index:02d}" for index in range(1, 7)]
            for slot in slots:
                path = root / f"{slot}.png"
                Image.new("RGB", (32, 32), "white").save(path)
                artifacts.append(
                    {
                        "slot": slot,
                        "status": "complete",
                        "path": path.name,
                        "prompt": f"prompt for {slot}",
                    }
                )
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workflow": "amazon-listing",
                        "mode": "builtin",
                        "status": "complete",
                        "artifacts": artifacts,
                    }
                )
            )
            result, paths = validator.validate_manifest(manifest_path, set(slots))
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(paths), 7)


if __name__ == "__main__":
    unittest.main()
