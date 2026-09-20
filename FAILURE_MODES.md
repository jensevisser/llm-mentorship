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

## Fase 0 — Onbetrouwbare test door externe staat (pytest)
Voorspelling: een test die generate() aanroept met een geldig model, en verwacht dat het resultaat None is omdat ik de Ollama-server handmatig had uitgezet, zou consistent slagen.
Waarneming: bij een volgende testrun, zonder dat ik de servertoestand bewust had gewijzigd, faalde de test — Ollama bleek weer bereikbaar en generate() gaf een geldige dict terug in plaats van None.
Verklaring: de test controleerde niet zelf of Ollama bereikbaar was; hij leunde op de toevallige staat van mijn machine op het moment van draaien. Dat maakt de test niet-deterministisch: hetzelfde testbestand geeft een ander resultaat afhankelijk van iets buiten de test zelf. Een betrouwbare test moet het scenario (hier: een ConnectionError) zelf afdwingen, bijvoorbeeld met mocking, in plaats van te hopen op de juiste externe toestand. Dat is een open leerpunt voor een latere sessie.

## Fase 0 — Ontbrekende dependency (ModuleNotFoundError: requests)
Voorspelling: als een package niet geïnstalleerd is in de virtuele omgeving, geeft Python een foutmelding bij de import-regel zelf, vóór de rest van het script draait.
Waarneming: ModuleNotFoundError: No module named 'requests' — bij het draaien van ollama_client.py vóór requests was toegevoegd aan het project.
Verklaring: import zoekt in de packages die geïnstalleerd zijn in de actieve (virtuele) omgeving. requests stond daar nog niet in, in tegenstelling tot python-dotenv dat al eerder was toegevoegd. De fix is uv add requests — de package expliciet aan het project toevoegen.

## Fase 0 — Verkeerd zoekpad bij tests (ModuleNotFoundError: src)
Voorspelling: pytest zou src/ollama_client.py kunnen importeren zoals elk ander Python-bestand, zonder extra configuratie.
Waarneming: ModuleNotFoundError: No module named 'src' bij het draaien van pytest, terwijl het bestand gewoon op schijf stond.
Verklaring: pytest voegt zonder ankerpunt alleen de tests/-map toe aan het zoekpad (sys.path), niet de project-root. De import zoekt dus in tests/, waar geen src-map bestaat. Een leeg conftest.py in de root lost dit op: pytest herkent dat bestand automatisch en voegt de map waarin het staat toe aan het zoekpad, waardoor src/ zichtbaar wordt. Geen ontbrekende dependency dit keer, maar een verkeerd zoekpad — ander mechanisme dan de requests-fout hierboven, ondanks dezelfde foutklasse.

## Fase 1 — Zelfde resultaat word teruggegeven voor de Pytest als er een HTTP-fout optreed of als er een Connectiefout optreed.
Voorspelling: Als er een HTTP-fout optreed of een Connectiefout, dan geeft Pytest dezelfde: None terug.
We kunnen dan niet zien welke van de fouten er fou ging.
Waarneming:We zien dat we bij elk van de fouten "None" terugkrijgen.
Verklaring: elke foutafhandeling die we tegenkomen, hier de HTTP-fout en de Connectiefout, deze geven allebei "None terug"

## Fase 1 — Test kan twee foutsituaties niet onderscheiden (beide excepts geven None)
Voorspelling: bij een HTTP-fout (model bestaat niet) en bij een ConnectionError (server gestopt) geeft `generate()` beide `None` terug. De test kan daardoor niet zien welke van de twee fouten is opgetreden.
Waarneming: situatie A (Ollama draait, model `hallo3:14b` bestaat niet) en situatie B (Ollama gestopt) gaven allebei `1 passed`. In A ging de `HTTPError`-except af, in B de `ConnectionError`-except.
Verklaring: in `generate()` vangt elke foutsoort een eigen `except` op, maar elke tak eindigt in `return None`. Op de grens van de functie verdwijnt het onderscheid: de aanroeper, en dus pytest, ziet alleen `None`. `assert result is None` is voor beide situaties waar, dus de test slaagt in beide gevallen en zegt niets over de oorzaak. Het onderscheid overleeft alleen in de logregel, die per except verschilt, maar een test leest de log niet. Gevolg: de functie kan de gebruiker niet vertellen wat er moet gebeuren (Ollama starten of een ander model kiezen). Open leerpunt: fouten onderscheidbaar maken voor de aanroeper.