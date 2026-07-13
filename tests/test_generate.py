import argparse
import base64
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GENERATE_PATH = ROOT / "skills/product-shots-image-gen/scripts/generate.py"
SPEC = importlib.util.spec_from_file_location("product_shots_generate", GENERATE_PATH)
generate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate)


def image_bytes(image_format="PNG", size=(32, 24), color="red"):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, image_format)
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, status_code=200, body=None, text="", content=b""):
        self.status_code = status_code
        self._body = body
        self.text = text
        self.content = content

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise generate.requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self.responses.pop(0)


class GenerateTests(unittest.TestCase):
    def parse(self, *arguments):
        return generate.build_parser().parse_args(arguments)

    def test_http_session_proxy_policy_is_explicit(self):
        default_session = generate.make_http_session()
        trusted_session = generate.make_http_session(trust_env=True)
        self.addCleanup(default_session.close)
        self.addCleanup(trusted_session.close)
        self.assertFalse(default_session.trust_env)
        self.assertTrue(trusted_session.trust_env)

    def test_validates_prompt_and_n(self):
        with self.assertRaisesRegex(generate.ArgumentError, "must not be empty"):
            generate.validate_args(self.parse("--prompt", "  ", "--model", "gpt-image-2"))
        with self.assertRaisesRegex(generate.ArgumentError, "at least 1"):
            generate.validate_args(
                self.parse("--prompt", "x", "--model", "gpt-image-2", "--n", "0")
            )

    def test_rejects_unknown_model_and_invalid_family_flags(self):
        with self.assertRaisesRegex(generate.ArgumentError, "Unknown model"):
            generate.validate_args(self.parse("--prompt", "x", "--model", "flux-pro"))
        with self.assertRaisesRegex(generate.ArgumentError, "exactly one"):
            generate.validate_args(
                self.parse(
                    "--prompt", "x", "--model", "gemini-3-pro-image-preview", "--n", "2"
                )
            )
        with self.assertRaisesRegex(generate.ArgumentError, "only valid"):
            generate.validate_args(
                self.parse(
                    "--prompt",
                    "x",
                    "--model",
                    "gemini-3-pro-image-preview",
                    "--size",
                    "1024x1024",
                )
            )

    def test_maps_four_by_five_to_supported_openai_canvas(self):
        args = generate.validate_args(
            self.parse(
                "--prompt", "x", "--model", "gpt-image-2", "--aspect-ratio", "4:5"
            )
        )
        self.assertEqual(args.effective_size, "1024x1536")

    def test_openai_multi_output_saves_every_image_and_manifest(self):
        encoded = base64.b64encode(image_bytes()).decode("ascii")
        response = FakeResponse(
            body={
                "data": [{"b64_json": encoded}, {"b64_json": encoded}, {"b64_json": encoded}],
                "usage": {"total_tokens": 42},
            }
        )
        session = FakeSession([response])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.parse(
                "--prompt",
                "three variants",
                "--model",
                "gpt-image-2",
                "--n",
                "3",
                "--output",
                str(root / "variant.jpeg"),
                "--manifest",
                str(root / "manifest.json"),
            )
            with mock.patch.object(generate, "load_api_key", return_value=("secret", "test")), mock.patch.object(
                generate, "load_base_url", return_value=("https://example.test/v1", "test")
            ):
                outputs = generate.run(args, session=session)

            self.assertEqual([path.name for path in outputs], ["variant-01.png", "variant-02.png", "variant-03.png"])
            self.assertTrue(all(path.is_file() for path in outputs))
            manifest = json.loads((root / "manifest.json").read_text())
            self.assertEqual(len(manifest["artifacts"]), 3)
            self.assertTrue(all(item["prompt"] == "three variants" for item in manifest["artifacts"]))
            self.assertEqual(
                [item["path"] for item in manifest["artifacts"]],
                ["variant-01.png", "variant-02.png", "variant-03.png"],
            )
            self.assertEqual(session.post_calls[0][1]["json"]["n"], 3)

    def test_openai_rejects_incomplete_multi_output_response(self):
        encoded = base64.b64encode(image_bytes()).decode("ascii")
        session = FakeSession([FakeResponse(body={"data": [{"b64_json": encoded}]})])
        with self.assertRaisesRegex(generate.ResponseError, "expected 2"):
            generate.generate_openai(
                session,
                "prompt",
                "gpt-image-2",
                "1024x1024",
                2,
                [],
                "secret",
                "https://example.test/v1",
            )

    def test_retry_is_bounded_and_auth_is_not_retried(self):
        retry_session = FakeSession([FakeResponse(524), FakeResponse(200)])
        with mock.patch.object(generate.time, "sleep") as sleep:
            response = generate.post_with_i2i_retry(
                retry_session, "https://example.test", headers={}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(retry_session.post_calls), 2)
        sleep.assert_called_once_with(1)

        auth_session = FakeSession([FakeResponse(401)])
        response = generate.post_with_i2i_retry(
            auth_session, "https://example.test", headers={}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(auth_session.post_calls), 1)

    def test_retry_covers_429_5xx_and_timeout(self):
        for first_response in (
            FakeResponse(429),
            FakeResponse(500),
            generate.requests.Timeout("slow"),
        ):
            with self.subTest(first_response=type(first_response).__name__):
                session = FakeSession([first_response, FakeResponse(200)])
                with mock.patch.object(generate.time, "sleep"):
                    response = generate.post_with_i2i_retry(
                        session, "https://example.test", headers={}
                    )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(session.post_calls), 2)

    def test_gemini_multimodal_payload_contains_reference(self):
        encoded = base64.b64encode(image_bytes()).decode("ascii")
        response = FakeResponse(
            body={
                "choices": [
                    {
                        "message": {
                            "content": f"![result](data:image/png;base64,{encoded})"
                        }
                    }
                ]
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "reference.png"
            reference.write_bytes(image_bytes())
            session = FakeSession([response])
            images, _ = generate.generate_gemini(
                session,
                "prompt",
                "gemini-3-pro-image-preview",
                [reference],
                "secret",
                "https://example.test/v1",
            )
        content = session.post_calls[0][1]["json"]["messages"][0]["content"]
        self.assertEqual(len(content), 2)
        self.assertTrue(content[1]["image_url"]["url"].startswith("data:image/png;base64,"))
        self.assertEqual(images, [image_bytes()])

    def test_openai_edit_payload_uses_all_references(self):
        encoded = base64.b64encode(image_bytes()).decode("ascii")
        with tempfile.TemporaryDirectory() as directory:
            references = []
            for index in range(2):
                path = Path(directory) / f"reference-{index}.png"
                path.write_bytes(image_bytes())
                references.append(path)
            session = FakeSession([FakeResponse(body={"data": [{"b64_json": encoded}]})])
            generate.generate_openai(
                session,
                "prompt",
                "gpt-image-2",
                "1024x1024",
                1,
                references,
                "secret",
                "https://example.test/v1",
            )
        files = session.post_calls[0][1]["files"]
        self.assertEqual([field for field, _ in files], ["image[]", "image[]"])

    def test_malformed_response_is_rejected(self):
        session = FakeSession([FakeResponse(body={"unexpected": []})])
        with self.assertRaisesRegex(generate.ResponseError, "expected 1"):
            generate.generate_openai(
                session,
                "prompt",
                "gpt-image-2",
                "1024x1024",
                1,
                [],
                "secret",
                "https://example.test/v1",
            )

    def test_resized_reference_is_cleaned_after_run(self):
        encoded = base64.b64encode(image_bytes()).decode("ascii")
        session = FakeSession([FakeResponse(body={"data": [{"b64_json": encoded}]})])
        captured = []
        original_resize = generate.maybe_resize

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "large.png"
            Image.new("RGB", (1500, 1200), "blue").save(reference)

            def capture(path):
                processed, temporary = original_resize(path)
                if temporary:
                    captured.append(processed)
                return processed, temporary

            args = self.parse(
                "--prompt",
                "edit",
                "--model",
                "gpt-image-2",
                "--reference-image",
                str(reference),
                "--output",
                str(root / "out"),
            )
            with mock.patch.object(generate, "load_api_key", return_value=("secret", "test")), mock.patch.object(
                generate, "load_base_url", return_value=("https://example.test/v1", "test")
            ), mock.patch.object(generate, "maybe_resize", side_effect=capture):
                generate.run(args, session=session)

        self.assertEqual(len(captured), 1)
        self.assertFalse(captured[0].exists())

    def test_preflight_conflict_happens_before_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.png"
            output.write_bytes(image_bytes())
            args = self.parse(
                "--prompt", "x", "--model", "gpt-image-2", "--output", str(output)
            )
            with mock.patch.object(generate, "load_api_key") as load_key:
                with self.assertRaisesRegex(generate.ArgumentError, "Refusing to overwrite"):
                    generate.run(args, session=FakeSession([]))
            load_key.assert_not_called()


if __name__ == "__main__":
    unittest.main()
