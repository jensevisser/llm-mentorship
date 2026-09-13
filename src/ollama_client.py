import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL")

if OLLAMA_URL is None:
    raise ValueError("OLLAMA_URL ontbreekt in .env-bestand")


def generate(
    prompt: str,
    model: str = "qwen3:14b",
) -> dict | None:

    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(url=OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.ConnectionError as e:
        print(f" We kunnen geen verbinding krijgen met de Ollama Server: {e}")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"De server is bereikt, maar deze geeft een foutcode: {e}")
        return None


def generate_stream(prompt: str, model: str = "qwen3:14b") -> str | None:

    try:
        payload = {"model": model, "prompt": prompt, "stream": True}
        response = requests.post(url=OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                full_response = full_response + chunk["response"]
        return full_response

    except requests.exceptions.ConnectionError as e:
        print(f"We kunnen geen verbinding krijgen met de Ollama Server: {e}")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"De server is bereikt, maar deze geeft een foutcode: {e}")
        return None

    except json.JSONDecodeError as e:
        print(
            f"De stream is onderbroken. Er is al wel wat binnen gekomen, maar niet afgemaakt. \nDatgene wat we binnen hebben word teruggegeven. foutcode: {e}"
        )
        return full_response


if __name__ == "__main__":
    data = generate_stream("Vertel in één zin wat een multimeter doet.")
    print(data)
