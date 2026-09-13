## Fase 0 — Connectiefout (Ollama niet actief)
Voorspelling: requests.post() geeft een ConnectionError, want de server is onbereikbaar.
Waarneming: requests.exceptions.ConnectionError — "Max retries exceeded... Connection refused" (Errno 111)
Verklaring: Ollama-daemon was gestopt (systemctl stop ollama), dus er luisterde niets op poort 11434. requests kon geen TCP-verbinding opzetten, dus kwam er nooit een response terug — de fout ontstaat al vóór er sprake is van een HTTP-antwoord.

## Fase 0 — HTTP-fout (onbekend model)
Voorspelling: response.raise_for_status() geeft een HTTPError, want de server antwoordt met een foutcode.
Waarneming: requests.exceptions.HTTPError — "404 Client Error: Not Found for url: http://localhost:11434/api/generate"
Verklaring: Ollama draaide wel en ontving het verzoek, maar het model "hallo3:14b" bestaat niet lokaal. De server stuurde een geldig HTTP-antwoord terug, alleen met statuscode 404 in plaats van 200 — de verbinding werkte, de gevraagde actie niet.

## Fase 0 — Ontbrekende .env-waarde (OLLAMA_URL)
Voorspelling: os.getenv() geeft None terug als de sleutel ontbreekt, zonder crash.
Waarneming: eerste poging (zonder expliciete check) gaf pas verderop een cryptische requests.exceptions.MissingSchema ("Invalid URL 'None': No scheme supplied"), drie lagen diep in requests. Na het toevoegen van een expliciete check bij het laden ontstaat in plaats daarvan een duidelijke ValueError("OLLAMA_URL ontbreekt in .env-bestand"), direct bij het opstarten.
Verklaring: os.getenv() faalt inderdaad stil (geen crash, gewoon None). Het probleem is de vertraagde, indirecte crash die daarna ontstaat — pas bij gebruik van de waarde, niet bij het ontbreken ervan. Een expliciete check direct na het laden verplaatst de fout naar de plek waar de oorzaak zit (fail fast), in plaats van een cryptische fout drie lagen verderop in een library.