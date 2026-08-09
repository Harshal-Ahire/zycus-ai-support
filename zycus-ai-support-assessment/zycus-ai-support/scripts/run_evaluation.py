import json
from evaluation.report import run
print(json.dumps(run(), indent=2))
